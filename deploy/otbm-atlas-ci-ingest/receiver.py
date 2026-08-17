"""Authenticated, write-only Atlas CI bundle receiver.

This service is intentionally narrow: a deployment workflow can upload bounded
parts for one named bundle and finalize them into a safely extracted directory.
There is no shell, file-read, listing, or arbitrary-path API.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import shutil
import tarfile
import tempfile
import threading
from typing import Any

BUNDLE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
PART_RE = re.compile(r"^part-[0-9]{4,6}$")
PUT_RE = re.compile(r"^/v1/bundles/([^/]+)/parts/([^/]+)$")
COMPLETE_RE = re.compile(r"^/v1/bundles/([^/]+)/complete$")
MAX_PART_BYTES = 64 * 1024 * 1024
MAX_BUNDLE_BYTES = 4 * 1024 * 1024 * 1024
MAX_PARTS = 128
MAX_MANIFEST_BYTES = 1024 * 1024
COPY_BLOCK = 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(COPY_BLOCK):
            digest.update(block)
    return digest.hexdigest()


def _safe_name(value: str, pattern: re.Pattern[str], label: str) -> str:
    if not pattern.fullmatch(value):
        raise ValueError(f"invalid {label}")
    return value


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def safe_extract_tar(archive: Path, destination: Path) -> list[str]:
    """Extract only normal files/directories below destination.

    Symlinks, hardlinks, devices, absolute paths, traversal and duplicate member
    paths are rejected before any payload is committed.
    """
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(destination)

    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
    members_seen: set[str] = set()
    extracted: list[str] = []
    try:
        with tarfile.open(archive, mode="r:") as package:
            members = package.getmembers()
            for member in members:
                name = member.name.replace("\\", "/")
                if not name or name.startswith("/") or name.startswith("../") or "/../" in f"/{name}/":
                    raise ValueError(f"unsafe archive member: {member.name!r}")
                if name in members_seen:
                    raise ValueError(f"duplicate archive member: {name}")
                members_seen.add(name)
                if member.issym() or member.islnk() or member.isdev() or member.isfifo():
                    raise ValueError(f"unsupported archive member type: {name}")
                target = staging / name
                if not _inside(staging, target):
                    raise ValueError(f"archive member escapes destination: {name}")
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    raise ValueError(f"unsupported archive member type: {name}")
                source = package.extractfile(member)
                if source is None:
                    raise ValueError(f"archive file cannot be read: {name}")
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = target.with_name(f".{target.name}.tmp")
                with temporary.open("wb") as output:
                    shutil.copyfileobj(source, output, COPY_BLOCK)
                os.replace(temporary, target)
                extracted.append(name)
        os.replace(staging, destination)
        return sorted(extracted)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def _json_object(payload: bytes) -> dict[str, Any]:
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON payload must be an object")
    return value


class Receiver:
    def __init__(self, root: Path, token: str, max_part_bytes: int = MAX_PART_BYTES) -> None:
        self.root = root.resolve()
        self.token = token
        self.max_part_bytes = max_part_bytes
        self.parts = self.root / "parts"
        self.bundles = self.root / "bundles"
        self.receipts = self.root / "receipts"
        self._locks_guard = threading.Lock()
        self._completion_locks: dict[str, threading.Lock] = {}
        for path in (self.parts, self.bundles, self.receipts):
            path.mkdir(parents=True, exist_ok=True)

    def authorized(self, header: str | None) -> bool:
        prefix = "Bearer "
        if not header or not header.startswith(prefix):
            return False
        return hmac.compare_digest(header[len(prefix):], self.token)

    def _completion_lock(self, bundle: str) -> threading.Lock:
        with self._locks_guard:
            return self._completion_locks.setdefault(bundle, threading.Lock())

    def part_path(self, bundle: str, part: str) -> Path:
        bundle = _safe_name(bundle, BUNDLE_RE, "bundle id")
        part = _safe_name(part, PART_RE, "part id")
        return self.parts / bundle / part

    def store_part(self, bundle: str, part: str, stream: Any, length: int, expected_sha256: str) -> dict[str, Any]:
        if length < 0 or length > self.max_part_bytes:
            raise ValueError(f"part size must be 0..{self.max_part_bytes}")
        if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
            raise ValueError("X-Atlas-SHA256 must be lowercase SHA-256")
        target = self.part_path(bundle, part)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_file():
            actual = _sha256(target)
            if target.stat().st_size == length and actual == expected_sha256:
                return {"status": "reused", "bundle": bundle, "part": part, "bytes": length, "sha256": actual}
            raise FileExistsError(f"part already exists with different bytes: {bundle}/{part}")
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{part}.", suffix=".tmp", dir=target.parent)
        temporary = Path(temporary_name)
        digest = hashlib.sha256()
        remaining = length
        try:
            with os.fdopen(descriptor, "wb") as output:
                while remaining:
                    block = stream.read(min(COPY_BLOCK, remaining))
                    if not block:
                        raise ValueError("request body ended before Content-Length")
                    output.write(block)
                    digest.update(block)
                    remaining -= len(block)
                output.flush()
                os.fsync(output.fileno())
            actual = digest.hexdigest()
            if actual != expected_sha256:
                raise ValueError("part SHA-256 mismatch")
            os.replace(temporary, target)
            return {"status": "stored", "bundle": bundle, "part": part, "bytes": length, "sha256": actual}
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass

    def complete(self, bundle: str, manifest: dict[str, Any]) -> dict[str, Any]:
        bundle = _safe_name(bundle, BUNDLE_RE, "bundle id")
        with self._completion_lock(bundle):
            return self._complete_locked(bundle, manifest)

    def _complete_locked(self, bundle: str, manifest: dict[str, Any]) -> dict[str, Any]:
        receipt_path = self.receipts / f"{bundle}.json"
        if receipt_path.is_file():
            return _json_object(receipt_path.read_bytes())
        if manifest.get("schemaVersion") != 1 or manifest.get("bundleId") != bundle:
            raise ValueError("bundle manifest identity mismatch")
        kind = manifest.get("kind")
        producer_sha = manifest.get("producerSha")
        archive_sha = manifest.get("archiveSha256")
        parts = manifest.get("parts")
        if not isinstance(kind, str) or kind not in {"shard", "global", "fixture"}:
            raise ValueError("invalid bundle kind")
        if not isinstance(producer_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", producer_sha):
            raise ValueError("producerSha must be a lowercase 40-hex commit SHA")
        if not isinstance(archive_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", archive_sha):
            raise ValueError("archiveSha256 must be lowercase SHA-256")
        if not isinstance(parts, list) or not parts or len(parts) > MAX_PARTS:
            raise ValueError(f"bundle parts must contain 1..{MAX_PARTS} records")

        normalized: list[dict[str, Any]] = []
        expected_names: list[str] = []
        archive_bytes = 0
        for index, raw in enumerate(parts):
            if not isinstance(raw, dict):
                raise ValueError("invalid part record")
            name = _safe_name(str(raw.get("name", "")), PART_RE, "part id")
            if name != f"part-{index:04d}":
                raise ValueError("bundle parts must be contiguous and ordered")
            size = int(raw.get("bytes", -1))
            sha = str(raw.get("sha256", ""))
            if size < 0 or size > self.max_part_bytes or not re.fullmatch(r"[0-9a-f]{64}", sha):
                raise ValueError("invalid part metadata")
            archive_bytes += size
            if archive_bytes > MAX_BUNDLE_BYTES:
                raise ValueError(f"bundle archive exceeds {MAX_BUNDLE_BYTES} bytes")
            path = self.part_path(bundle, name)
            if not path.is_file() or path.stat().st_size != size or _sha256(path) != sha:
                raise ValueError(f"part verification failed: {name}")
            normalized.append({"name": name, "bytes": size, "sha256": sha})
            expected_names.append(name)

        part_root = self.parts / bundle
        disk_names = sorted(path.name for path in part_root.iterdir() if path.is_file())
        if disk_names != expected_names:
            raise ValueError("received part set differs from completion manifest")

        archive = self.root / f".{bundle}.tar.tmp"
        digest = hashlib.sha256()
        try:
            with archive.open("wb") as output:
                for record in normalized:
                    path = part_root / record["name"]
                    with path.open("rb") as source:
                        while block := source.read(COPY_BLOCK):
                            output.write(block)
                            digest.update(block)
                output.flush()
                os.fsync(output.fileno())
            if digest.hexdigest() != archive_sha:
                raise ValueError("reconstructed archive SHA-256 mismatch")
            destination = self.bundles / bundle
            files = safe_extract_tar(archive, destination)
            receipt = {
                "schemaVersion": 1,
                "bundleId": bundle,
                "kind": kind,
                "producerSha": producer_sha,
                "shardIndex": manifest.get("shardIndex"),
                "archiveSha256": archive_sha,
                "archiveBytes": archive_bytes,
                "parts": normalized,
                "files": len(files),
                "status": "COMPLETE",
            }
            temporary = receipt_path.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            os.replace(temporary, receipt_path)
            shutil.rmtree(part_root, ignore_errors=True)
            return receipt
        finally:
            try:
                archive.unlink()
            except FileNotFoundError:
                pass


class Handler(BaseHTTPRequestHandler):
    server_version = "AtlasCIIngest/1"
    receiver: Receiver

    def _send(self, status: int, value: dict[str, Any]) -> None:
        payload = (json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def _auth(self) -> bool:
        if self.receiver.authorized(self.headers.get("Authorization")):
            return True
        self._send(HTTPStatus.UNAUTHORIZED, {"status": "UNAUTHORIZED"})
        return False

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self._send(HTTPStatus.NOT_FOUND, {"status": "NOT_FOUND"})
            return
        if not self._auth():
            return
        self._send(HTTPStatus.OK, {"status": "READY"})

    def do_PUT(self) -> None:  # noqa: N802
        if not self._auth():
            return
        match = PUT_RE.fullmatch(self.path)
        if not match:
            self._send(HTTPStatus.NOT_FOUND, {"status": "NOT_FOUND"})
            return
        try:
            length_header = self.headers.get("Content-Length")
            if length_header is None:
                raise ValueError("Content-Length is required")
            length = int(length_header)
            expected = self.headers.get("X-Atlas-SHA256", "")
            result = self.receiver.store_part(match.group(1), match.group(2), self.rfile, length, expected)
            self._send(HTTPStatus.OK, result)
        except FileExistsError as error:
            self._send(HTTPStatus.CONFLICT, {"status": "CONFLICT", "error": str(error)})
        except (OSError, TypeError, ValueError) as error:
            self._send(HTTPStatus.BAD_REQUEST, {"status": "REJECTED", "error": str(error)})

    def do_POST(self) -> None:  # noqa: N802
        if not self._auth():
            return
        match = COMPLETE_RE.fullmatch(self.path)
        if not match:
            self._send(HTTPStatus.NOT_FOUND, {"status": "NOT_FOUND"})
            return
        try:
            length_header = self.headers.get("Content-Length")
            if length_header is None:
                raise ValueError("Content-Length is required")
            length = int(length_header)
            if length < 0 or length > MAX_MANIFEST_BYTES:
                raise ValueError("completion manifest is too large")
            payload = self.rfile.read(length)
            if len(payload) != length:
                raise ValueError("request body ended before Content-Length")
            result = self.receiver.complete(match.group(1), _json_object(payload))
            self._send(HTTPStatus.OK, result)
        except FileExistsError as error:
            self._send(HTTPStatus.CONFLICT, {"status": "CONFLICT", "error": str(error)})
        except (OSError, tarfile.TarError, UnicodeError, TypeError, ValueError, json.JSONDecodeError) as error:
            self._send(HTTPStatus.BAD_REQUEST, {"status": "REJECTED", "error": str(error)})

    def log_message(self, format: str, *args: Any) -> None:
        # Deliberately omit Authorization and request headers. The default line is
        # useful for bounded operational logs without exposing the bearer token.
        super().log_message(format, *args)


def serve(root: Path, token_file: Path, host: str, port: int, max_part_bytes: int) -> None:
    token = token_file.read_text(encoding="utf-8").strip()
    if len(token) < 32:
        raise ValueError("bearer token must contain at least 32 characters")
    receiver = Receiver(root, token, max_part_bytes=max_part_bytes)
    handler = type("AtlasHandler", (Handler,), {"receiver": receiver})
    server = ThreadingHTTPServer((host, port), handler)
    print(json.dumps({"status": "READY", "host": host, "port": port, "root": str(root.resolve())}, sort_keys=True), flush=True)
    server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--max-part-bytes", type=int, default=MAX_PART_BYTES)
    args = parser.parse_args()
    serve(args.root, args.token_file, args.host, args.port, args.max_part_bytes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
