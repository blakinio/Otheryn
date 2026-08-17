"""Independent verification for one chunk-centric full-world certification shard."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
from typing import Any, Mapping

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_SCOPE = "world-chunk-shard"
EXPECTED_ENV_EXPORT_VERSION = 3


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != PNG_MAGIC or header[12:16] != b"IHDR":
        raise ValueError(f"{path}: invalid PNG header")
    return struct.unpack(">II", header[16:24])


def _chunk_text(chunk: Mapping[str, object]) -> str:
    return f"z{int(chunk['z'])}/{int(chunk['chunkX'])}_{int(chunk['chunkY'])}"


def _verify_png(root: Path, relative: str, checksum: str, width: int, height: int, errors: list[str], label: str) -> None:
    path = root / relative
    if not path.is_file():
        errors.append(f"{label}: missing {relative}")
        return
    try:
        if _sha256(path) != checksum:
            errors.append(f"{label}: checksum mismatch {relative}")
        if _png_dimensions(path) != (width, height):
            errors.append(f"{label}: PNG dimensions mismatch {relative}")
    except (OSError, ValueError) as error:
        errors.append(f"{label}: {error}")


def _verify_environment_checkpoint(root: Path, checkpoint_path: Path, errors: list[str], label: str) -> None:
    try:
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{label}: invalid checkpoint: {error}")
        return
    if not isinstance(checkpoint, Mapping):
        errors.append(f"{label}: checkpoint is not a JSON object")
        return
    if int(checkpoint.get("exportVersion", -1)) != EXPECTED_ENV_EXPORT_VERSION:
        errors.append(f"{label}: unexpected environment exportVersion")
    fingerprint = checkpoint.get("fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        errors.append(f"{label}: invalid environment fingerprint")
    try:
        instances = int(checkpoint.get("instances", -1))
        fallbacks = int(checkpoint.get("staticFallbacks", -1))
    except (TypeError, ValueError):
        errors.append(f"{label}: invalid environment counters")
        return
    if instances < 0 or fallbacks < 0:
        errors.append(f"{label}: negative environment counters")
    assets = checkpoint.get("assets", [])
    checksums = checkpoint.get("assetChecksums", {})
    if not isinstance(assets, list) or not isinstance(checksums, Mapping):
        errors.append(f"{label}: invalid environment asset metadata")
        return
    if set(map(str, assets)) != set(map(str, checksums.keys())):
        errors.append(f"{label}: environment asset checksum coverage mismatch")
    for relative_value in assets:
        relative = str(relative_value)
        path = root / relative
        expected = checksums.get(relative)
        if not path.is_file():
            errors.append(f"{label}: missing environment asset {relative}")
        elif not isinstance(expected, str) or _sha256(path) != expected:
            errors.append(f"{label}: environment asset checksum mismatch {relative}")
    shard = checkpoint.get("shard")
    shard_checksum = checkpoint.get("shardChecksum")
    if instances == 0:
        if shard is not None or shard_checksum is not None:
            errors.append(f"{label}: empty environment checkpoint unexpectedly references a shard")
        return
    if not isinstance(shard, str) or not isinstance(shard_checksum, str):
        errors.append(f"{label}: populated environment checkpoint is missing shard metadata")
        return
    shard_path = root / shard
    if not shard_path.is_file():
        errors.append(f"{label}: missing environment shard {shard}")
        return
    if _sha256(shard_path) != shard_checksum:
        errors.append(f"{label}: environment shard checksum mismatch {shard}")
        return
    try:
        payload = json.loads(shard_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{label}: invalid environment shard {shard}: {error}")
        return
    records = payload.get("records", []) if isinstance(payload, Mapping) else []
    if not isinstance(records, list) or len(records) != instances:
        errors.append(f"{label}: environment shard record count mismatch {shard}")


def verify_world_shard(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return {"ok": False, "errors": ["missing manifest.json"]}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"ok": False, "errors": [f"manifest.json: {error}"]}
    if not isinstance(manifest, Mapping):
        return {"ok": False, "errors": ["manifest.json is not a JSON object"]}
    certification = manifest.get("certification", {})
    if not isinstance(certification, Mapping):
        errors.append("manifest certification is missing")
        certification = {}
    if certification.get("scope") != EXPECTED_SCOPE:
        errors.append(f"manifest certification scope must be {EXPECTED_SCOPE}")
    chunks_value = manifest.get("chunks", [])
    if not isinstance(chunks_value, list):
        return {"ok": False, "errors": [*errors, "manifest chunks is not a list"]}
    floors: Counter[int] = Counter()
    missing_sprites: Counter[int] = Counter()
    chunk_keys: list[str] = []
    seen_detail: set[str] = set()
    seen_overview: set[str] = set()
    seen_low: set[str] = set()
    for index, raw in enumerate(chunks_value):
        label = f"chunk[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label}: invalid manifest chunk")
            continue
        try:
            text = _chunk_text(raw)
            chunk_keys.append(text)
            floors[int(raw["z"])] += 1
            missing_value = raw.get("missingSprites", {})
            if isinstance(missing_value, Mapping):
                missing_sprites.update({int(key): int(value) for key, value in missing_value.items()})
            detail = str(raw["path"])
            overview = str(raw["overviewPath"])
            low = str(raw["lowOverviewPath"])
            if detail in seen_detail:
                errors.append(f"{label}: duplicate detail path {detail}")
            if overview in seen_overview:
                errors.append(f"{label}: duplicate overview path {overview}")
            if low in seen_low:
                errors.append(f"{label}: duplicate low overview path {low}")
            seen_detail.add(detail)
            seen_overview.add(overview)
            seen_low.add(low)
            _verify_png(root, detail, str(raw["checksum"]), int(raw["imageWidth"]), int(raw["imageHeight"]), errors, label)
            _verify_png(root, overview, str(raw["overviewChecksum"]), int(raw["overviewImageWidth"]), int(raw["overviewImageHeight"]), errors, label)
            _verify_png(root, low, str(raw["lowOverviewChecksum"]), int(raw["lowOverviewImageWidth"]), int(raw["lowOverviewImageHeight"]), errors, label)
        except (KeyError, TypeError, ValueError, OSError) as error:
            errors.append(f"{label}: {error}")
    if len(chunk_keys) != len(set(chunk_keys)):
        errors.append("manifest contains duplicate chunk keys")
    disk_detail = {path.relative_to(root).as_posix() for path in (root / "tiles").glob("z*/*.png")}
    disk_overview = {path.relative_to(root).as_posix() for path in (root / "overview").glob("z*/*.png")}
    disk_low = {path.relative_to(root).as_posix() for path in (root / "overview-low").glob("z*/*.png")}
    if disk_detail != seen_detail:
        errors.append(f"detail file set differs from manifest: disk={len(disk_detail)} manifest={len(seen_detail)}")
    if disk_overview != seen_overview:
        errors.append(f"overview file set differs from manifest: disk={len(disk_overview)} manifest={len(seen_overview)}")
    if disk_low != seen_low:
        errors.append(f"low overview file set differs from manifest: disk={len(disk_low)} manifest={len(seen_low)}")
    environment_index_path = root / "data/environment-animations/index.json"
    if not environment_index_path.is_file():
        errors.append("missing data/environment-animations/index.json")
        environment: Mapping[str, object] = {}
    else:
        try:
            loaded = json.loads(environment_index_path.read_text(encoding="utf-8"))
            environment = loaded if isinstance(loaded, Mapping) else {}
            if not isinstance(loaded, Mapping):
                errors.append("environment index is not a JSON object")
        except (OSError, json.JSONDecodeError) as error:
            environment = {}
            errors.append(f"environment index: {error}")
    if environment:
        if int(environment.get("schemaVersion", -1)) != 2:
            errors.append("environment index schemaVersion must be 2")
        statistics = environment.get("statistics", {})
        if not isinstance(statistics, Mapping):
            errors.append("environment index statistics is missing")
        elif int(statistics.get("completedChunks", -1)) != len(chunk_keys):
            errors.append(f"environment completedChunks disagrees with manifest: reported={statistics.get('completedChunks')!r} manifest={len(chunk_keys)}")
    expected_checkpoints: set[str] = set()
    for text in chunk_keys:
        floor, name = text.split("/", 1)
        relative = f"data/environment-animations/checkpoints/{floor}/{name}.json"
        expected_checkpoints.add(relative)
        checkpoint_path = root / relative
        if not checkpoint_path.is_file():
            errors.append(f"{text}: missing environment checkpoint")
            continue
        _verify_environment_checkpoint(root, checkpoint_path, errors, text)
    checkpoint_root = root / "data/environment-animations/checkpoints"
    disk_checkpoints = {path.relative_to(root).as_posix() for path in checkpoint_root.glob("z*/*.json")}
    if disk_checkpoints != expected_checkpoints:
        errors.append(f"environment checkpoint set differs from manifest: disk={len(disk_checkpoints)} expected={len(expected_checkpoints)}")
    statistics_path = root / "data/shard-statistics.json"
    if not statistics_path.is_file():
        errors.append("missing data/shard-statistics.json")
    else:
        try:
            statistics = json.loads(statistics_path.read_text(encoding="utf-8"))
            if int(statistics.get("chunks", -1)) != len(chunk_keys):
                errors.append("shard-statistics chunk count disagrees with manifest")
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            errors.append(f"data/shard-statistics.json: {error}")
    return {
        "ok": not errors,
        "errors": errors,
        "chunks": len(chunk_keys),
        "chunkKeys": sorted(chunk_keys),
        "floors": {str(key): int(value) for key, value in sorted(floors.items())},
        "missingSprites": {str(key): int(value) for key, value in sorted(missing_sprites.items())},
        "sources": dict(manifest.get("sources", {})) if isinstance(manifest.get("sources"), Mapping) else {},
        "certification": dict(certification),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("atlas", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify_world_shard(args.atlas)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
