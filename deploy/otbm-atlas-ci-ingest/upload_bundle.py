"""Create and upload one Atlas bundle to the authenticated CI ingest receiver."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tarfile
import tempfile
import time
from typing import Any, Iterable
from urllib import error, request

PART_BYTES = 48 * 1024 * 1024
COPY_BLOCK = 1024 * 1024
RETRIES = 5
BUNDLE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
PRODUCER_RE = re.compile(r"^[0-9a-f]{40}$")
EXCLUDED_NAMES = {".spool", ".incremental-state"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(COPY_BLOCK):
            digest.update(block)
    return digest.hexdigest()


def _included_paths(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_NAMES for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"symlinks are not permitted in Atlas bundles: {relative}")
        if path.is_file():
            yield path


def build_archive(root: Path, archive: Path) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    files = list(_included_paths(root))
    if not files:
        raise ValueError("Atlas bundle contains no files")
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, mode="w", format=tarfile.PAX_FORMAT) as package:
        directories: set[str] = set()
        for path in files:
            relative = path.relative_to(root).as_posix()
            parent = Path(relative).parent
            for directory in reversed(parent.parents):
                if directory == Path("."):
                    continue
                directories.add(directory.as_posix())
            if parent != Path("."):
                directories.add(parent.as_posix())
        for relative in sorted(directories):
            info = tarfile.TarInfo(relative)
            info.type = tarfile.DIRTYPE
            info.mode = 0o755
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            package.addfile(info)
        for path in files:
            relative = path.relative_to(root).as_posix()
            stat = path.stat()
            info = tarfile.TarInfo(relative)
            info.size = stat.st_size
            info.mode = 0o644
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            with path.open("rb") as source:
                package.addfile(info, source)
    return {"files": len(files), "bytes": archive.stat().st_size, "sha256": _sha256(archive)}


def split_archive(archive: Path, directory: Path, part_bytes: int) -> list[dict[str, Any]]:
    if part_bytes <= 0:
        raise ValueError("part size must be positive")
    directory.mkdir(parents=True, exist_ok=True)
    parts: list[dict[str, Any]] = []
    with archive.open("rb") as source:
        index = 0
        while True:
            payload = source.read(part_bytes)
            if not payload:
                break
            name = f"part-{index:04d}"
            path = directory / name
            path.write_bytes(payload)
            parts.append({"name": name, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "path": path})
            index += 1
    if not parts:
        raise ValueError("archive split produced no parts")
    return parts


def _decode_response(response: Any) -> dict[str, Any]:
    payload = response.read()
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("receiver response must be a JSON object")
    return value


def _call(method: str, url: str, token: str, payload: bytes | None = None, headers: dict[str, str] | None = None, retries: int = RETRIES) -> dict[str, Any]:
    headers = dict(headers or {})
    headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        headers["Content-Length"] = str(len(payload))
    transient = {408, 425, 429, 500, 502, 503, 504}
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = request.Request(url, data=payload, headers=headers, method=method)
            with request.urlopen(req, timeout=300) as response:
                if response.status < 200 or response.status >= 300:
                    raise RuntimeError(f"receiver returned HTTP {response.status}")
                return _decode_response(response)
        except error.HTTPError as exc:
            last = exc
            if exc.code not in transient:
                body = exc.read().decode("utf-8", errors="replace")[:1000]
                raise RuntimeError(f"receiver rejected request HTTP {exc.code}: {body}") from exc
        except (error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            last = exc
        if attempt + 1 < retries:
            time.sleep(min(30, 2 ** attempt))
    raise RuntimeError(f"receiver request failed after {retries} attempts: {last}")


def upload_bundle(root: Path, base_url: str, token: str, bundle_id: str, producer_sha: str, kind: str, shard_index: int | None, part_bytes: int = PART_BYTES) -> dict[str, Any]:
    if not BUNDLE_RE.fullmatch(bundle_id):
        raise ValueError("invalid bundle id")
    if not PRODUCER_RE.fullmatch(producer_sha):
        raise ValueError("producer SHA must be lowercase 40-hex")
    if kind not in {"shard", "global", "fixture"}:
        raise ValueError("invalid bundle kind")
    if kind == "shard" and shard_index is None:
        raise ValueError("shard bundle requires --shard-index")
    if kind != "shard" and shard_index is not None:
        raise ValueError("only shard bundles may set shard index")
    base_url = base_url.rstrip("/")
    health = _call("GET", f"{base_url}/health", token)
    if health.get("status") != "READY":
        raise RuntimeError(f"receiver is not ready: {health}")

    with tempfile.TemporaryDirectory(prefix="atlas-ci-upload-") as temporary_text:
        temporary = Path(temporary_text)
        archive = temporary / "bundle.tar"
        archive_info = build_archive(root, archive)
        parts = split_archive(archive, temporary / "parts", part_bytes)
        manifest_parts: list[dict[str, Any]] = []
        for part in parts:
            payload = Path(part["path"]).read_bytes()
            result = _call(
                "PUT",
                f"{base_url}/v1/bundles/{bundle_id}/parts/{part['name']}",
                token,
                payload,
                headers={"Content-Type": "application/octet-stream", "X-Atlas-SHA256": str(part["sha256"])},
            )
            if result.get("sha256") != part["sha256"] or int(result.get("bytes", -1)) != part["bytes"]:
                raise RuntimeError(f"receiver part acknowledgement mismatch: {part['name']}")
            manifest_parts.append({"name": part["name"], "bytes": part["bytes"], "sha256": part["sha256"]})

        manifest: dict[str, Any] = {
            "schemaVersion": 1,
            "bundleId": bundle_id,
            "kind": kind,
            "producerSha": producer_sha,
            "archiveSha256": archive_info["sha256"],
            "parts": manifest_parts,
        }
        if shard_index is not None:
            manifest["shardIndex"] = shard_index
        payload = (json.dumps(manifest, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")
        receipt = _call(
            "POST",
            f"{base_url}/v1/bundles/{bundle_id}/complete",
            token,
            payload,
            headers={"Content-Type": "application/json"},
        )
        expected = {
            "bundleId": bundle_id,
            "kind": kind,
            "producerSha": producer_sha,
            "archiveSha256": archive_info["sha256"],
            "status": "COMPLETE",
        }
        for key, value in expected.items():
            if receipt.get(key) != value:
                raise RuntimeError(f"receiver completion acknowledgement mismatch for {key}: {receipt.get(key)!r} != {value!r}")
        if shard_index is not None and int(receipt.get("shardIndex", -1)) != shard_index:
            raise RuntimeError("receiver shard-index acknowledgement mismatch")
        return {
            "bundleId": bundle_id,
            "kind": kind,
            "shardIndex": shard_index,
            "sourceFiles": archive_info["files"],
            "archiveBytes": archive_info["bytes"],
            "archiveSha256": archive_info["sha256"],
            "parts": len(manifest_parts),
            "receipt": receipt,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--url", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--producer-sha", required=True)
    parser.add_argument("--kind", choices=("shard", "global", "fixture"), required=True)
    parser.add_argument("--shard-index", type=int)
    parser.add_argument("--part-bytes", type=int, default=PART_BYTES)
    args = parser.parse_args()
    result = upload_bundle(
        args.root,
        args.url,
        args.token,
        args.bundle_id,
        args.producer_sha,
        args.kind,
        args.shard_index,
        args.part_bytes,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
