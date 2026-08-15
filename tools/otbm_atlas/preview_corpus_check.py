"""Read-only deployment preflight for a generated OTBM Atlas corpus."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CANONICAL_MAP_SHA256 = "3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034"
CANONICAL_ASSETS_SHA256 = "4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7"
CURRENT_V3_DESKTOP_ASSETS_SHA256 = "4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2"
KNOWN_CURRENT_V3_ASSET_SHA256 = {CANONICAL_ASSETS_SHA256, CURRENT_V3_DESKTOP_ASSETS_SHA256}

REQUIRED_VIEWER_FILES = (
    "index.html",
    "viewer-app.js",
    "viewer-runtime.js",
    "creature-animation-runtime.js",
)
REQUIRED_FACTUAL_FILES = (
    "data/search-index.json",
    "data/spawns.json",
    "data/mechanics.json",
    "data/houses.json",
    "data/statistics.json",
    "data/factual-layers.json",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path, issues: list[str], label: str) -> dict[str, Any] | None:
    if not path.is_file():
        issues.append(f"missing {label}: {path.as_posix()}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        issues.append(f"invalid {label}: {path.as_posix()}: {error}")
        return None
    if not isinstance(value, dict):
        issues.append(f"invalid {label}: {path.as_posix()}: expected JSON object")
        return None
    return value


def _check_relative_file(root: Path, relative: object, issues: list[str], label: str) -> Path | None:
    if not isinstance(relative, str) or not relative:
        issues.append(f"missing {label} path")
        return None
    path = root / relative
    if not path.is_file():
        issues.append(f"missing {label}: {relative}")
        return None
    return path


def _check_hashed_file(
    root: Path,
    relative: object,
    expected_checksum: object,
    issues: list[str],
    label: str,
    verify_checksums: bool,
) -> None:
    path = _check_relative_file(root, relative, issues, label)
    if path is None or not verify_checksums:
        return
    if not isinstance(expected_checksum, str) or len(expected_checksum) != 64:
        issues.append(f"missing or invalid {label} checksum: {relative}")
        return
    actual = _sha256(path)
    if actual != expected_checksum:
        issues.append(f"checksum mismatch for {label}: {relative}: expected {expected_checksum}, got {actual}")


def _verify_detail_corpus(
    root: Path,
    expected_chunks: int,
    expected_map_sha: str,
    verify_checksums: bool,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    issues: list[str] = []
    manifest = _read_json(root / "manifest.json", issues, "manifest")
    result: dict[str, Any] = {"ready": False, "issues": issues, "chunks": 0, "floors": []}
    if manifest is None:
        return None, result

    schema = manifest.get("schemaVersion")
    chunks = manifest.get("chunks")
    sources = manifest.get("sources")
    if schema != 3:
        issues.append(f"unexpected Atlas schemaVersion: {schema!r}; expected 3")
    if not isinstance(chunks, list):
        issues.append("manifest chunks is not an array")
        chunks = []
    if len(chunks) != expected_chunks:
        issues.append(f"unexpected detail chunk count: {len(chunks)}; expected {expected_chunks}")
    floors = sorted({int(chunk.get("z")) for chunk in chunks if isinstance(chunk, dict) and isinstance(chunk.get("z"), int)})
    if expected_chunks == 3494 and floors != list(range(16)):
        issues.append(f"unexpected populated floors: {floors}; expected 0..15")

    if not isinstance(sources, dict):
        issues.append("manifest sources is not an object")
        sources = {}
    map_sha = str(sources.get("mapSha256", ""))
    assets_sha = str(sources.get("assetsSha256", ""))
    if expected_map_sha and map_sha != expected_map_sha:
        issues.append(f"unexpected mapSha256: {map_sha or 'MISSING'}; expected {expected_map_sha}")
    if sources.get("atlasVersion") != 3:
        issues.append(f"unexpected sources.atlasVersion: {sources.get('atlasVersion')!r}; expected 3")
    if manifest.get("chunkSize") != 128 or sources.get("chunkSize") != 128:
        issues.append("unexpected chunk size; expected manifest and source chunkSize 128")
    if assets_sha not in KNOWN_CURRENT_V3_ASSET_SHA256:
        issues.append(f"unrecognized current-v3 assetsSha256: {assets_sha or 'MISSING'}")

    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            issues.append(f"invalid chunk record at index {index}")
            continue
        _check_hashed_file(root, chunk.get("path"), chunk.get("checksum"), issues, "detail chunk", verify_checksums)
        _check_hashed_file(root, chunk.get("overviewPath"), chunk.get("overviewChecksum"), issues, "overview chunk", verify_checksums)
        _check_hashed_file(root, chunk.get("lowOverviewPath"), chunk.get("lowOverviewChecksum"), issues, "low overview chunk", verify_checksums)

    result.update(
        {
            "ready": not issues,
            "chunks": len(chunks),
            "floors": floors,
            "schemaVersion": schema,
            "mapSha256": map_sha,
            "assetsSha256": assets_sha,
            "assetsProvenance": (
                "canonical-git-bytes"
                if assets_sha == CANONICAL_ASSETS_SHA256
                else "verified-current-v3-desktop-worktree-bytes"
                if assets_sha == CURRENT_V3_DESKTOP_ASSETS_SHA256
                else "unknown"
            ),
            "checksumsVerified": verify_checksums,
        }
    )
    return manifest, result


def _verify_viewer(root: Path) -> dict[str, Any]:
    issues = [f"missing viewer file: {relative}" for relative in REQUIRED_VIEWER_FILES if not (root / relative).is_file()]
    return {"ready": not issues, "issues": issues, "files": list(REQUIRED_VIEWER_FILES)}


def _verify_factual_data(root: Path) -> dict[str, Any]:
    issues = [f"missing factual/browser data file: {relative}" for relative in REQUIRED_FACTUAL_FILES if not (root / relative).is_file()]
    shard_root = root / "data" / "chunks"
    shards = list(shard_root.glob("z*/*.json")) if shard_root.is_dir() else []
    if not shards:
        issues.append("missing spatial browser shards under data/chunks/z*/*.json")
    return {"ready": not issues, "issues": issues, "spatialShards": len(shards)}


def _verify_creature_kind(root: Path, kind: str) -> dict[str, Any]:
    issues: list[str] = []
    index_path = root / "data" / f"{kind}-sprites" / "index.json"
    index = _read_json(index_path, issues, f"{kind} sprite index")
    sprite_count = animation_count = frame_count = 0
    if index is not None:
        sprites = index.get("sprites", [])
        animations = index.get("animations", [])
        if not isinstance(sprites, list):
            issues.append(f"invalid {kind} sprite index sprites array")
            sprites = []
        if not isinstance(animations, list):
            issues.append(f"invalid {kind} sprite index animations array")
            animations = []
        sprite_count = len(sprites)
        animation_count = len(animations)
        for relative in sprites:
            _check_relative_file(root, relative, issues, f"{kind} sprite")
        for relative in animations:
            path = _check_relative_file(root, relative, issues, f"{kind} animation manifest")
            if path is None:
                continue
            animation = _read_json(path, issues, f"{kind} animation manifest")
            if animation is None:
                continue
            groups = animation.get("groups", {})
            if not isinstance(groups, dict):
                issues.append(f"invalid {kind} animation groups: {relative}")
                continue
            for group in groups.values():
                if not isinstance(group, dict):
                    continue
                frames = group.get("frames", {})
                if not isinstance(frames, dict):
                    continue
                for paths in frames.values():
                    if not isinstance(paths, list):
                        continue
                    for frame_relative in paths:
                        frame_count += 1
                        _check_relative_file(root, frame_relative, issues, f"{kind} animation frame")
    return {
        "ready": not issues,
        "issues": issues,
        "sprites": sprite_count,
        "animations": animation_count,
        "animationFrames": frame_count,
    }


def _verify_creatures(root: Path) -> dict[str, Any]:
    npc = _verify_creature_kind(root, "npc")
    monster = _verify_creature_kind(root, "monster")
    return {"ready": npc["ready"] and monster["ready"], "npc": npc, "monster": monster}


def _verify_environment_animations(root: Path) -> dict[str, Any]:
    issues: list[str] = []
    animation_root = root / "data" / "environment-animations"
    index = _read_json(animation_root / "index.json", issues, "environment animation index")
    shard_count = record_count = referenced_files = 0
    if index is not None:
        if index.get("schemaVersion") not in (1, 2):
            issues.append(f"unsupported environment animation schemaVersion: {index.get('schemaVersion')!r}")
        shards = sorted((animation_root / "chunks").glob("z*/*.json")) if (animation_root / "chunks").is_dir() else []
        shard_count = len(shards)
        expected_shards = index.get("statistics", {}).get("chunks") if isinstance(index.get("statistics"), dict) else None
        if isinstance(expected_shards, int) and expected_shards != shard_count:
            issues.append(f"environment animation shard count mismatch: index={expected_shards}, files={shard_count}")
        for shard_path in shards:
            shard = _read_json(shard_path, issues, "environment animation shard")
            if shard is None:
                continue
            records = shard.get("records", [])
            if not isinstance(records, list):
                issues.append(f"invalid environment animation records array: {shard_path.as_posix()}")
                continue
            record_count += len(records)
            for record in records:
                if not isinstance(record, dict):
                    issues.append(f"invalid environment animation record: {shard_path.as_posix()}")
                    continue
                references: list[object] = []
                frames = record.get("frames", [])
                if isinstance(frames, list):
                    references.extend(frames)
                else:
                    issues.append(f"invalid environment animation frames array: {shard_path.as_posix()}")
                references.append(record.get("underlay"))
                if record.get("overdraw") is not None:
                    references.append(record.get("overdraw"))
                for relative in references:
                    referenced_files += 1
                    _check_relative_file(root, relative, issues, "environment animation asset")
    return {
        "ready": not issues,
        "issues": issues,
        "shards": shard_count,
        "records": record_count,
        "referencedFiles": referenced_files,
        "dependencyTask": "docs/agents/tasks/active/OTH-20260815-atlas-environment-animation-export-performance.md",
    }


def inspect_corpus(
    root: Path,
    *,
    expected_chunks: int = 3494,
    expected_map_sha: str = CANONICAL_MAP_SHA256,
    verify_checksums: bool = True,
) -> dict[str, Any]:
    root = root.resolve()
    _manifest, detail = _verify_detail_corpus(root, expected_chunks, expected_map_sha, verify_checksums)
    viewer = _verify_viewer(root)
    factual = _verify_factual_data(root)
    creatures = _verify_creatures(root)
    environment = _verify_environment_animations(root)
    browser_core_ready = all(section["ready"] for section in (detail, viewer, factual, creatures))
    return {
        "schemaVersion": 1,
        "root": str(root),
        "detailCorpus": detail,
        "viewer": viewer,
        "factualData": factual,
        "creatures": creatures,
        "environmentAnimations": environment,
        "browserCoreReady": browser_core_ready,
        "fullBrowserReady": browser_core_ready and environment["ready"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("atlas", type=Path, help="generated Atlas directory")
    parser.add_argument("--expected-chunks", type=int, default=3494)
    parser.add_argument("--expected-map-sha", default=CANONICAL_MAP_SHA256)
    parser.add_argument("--skip-checksums", action="store_true", help="check paths and metadata without hashing image payloads")
    parser.add_argument("--require-browser-core", action="store_true", help="fail unless detail/overview, viewer, factual data and creature assets are ready")
    parser.add_argument("--require-environment", action="store_true", help="fail unless environment-animation index, shards and referenced files are ready")
    args = parser.parse_args()
    report = inspect_corpus(
        args.atlas,
        expected_chunks=args.expected_chunks,
        expected_map_sha=args.expected_map_sha,
        verify_checksums=not args.skip_checksums,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_browser_core and not report["browserCoreReady"]:
        return 2
    if args.require_environment and not report["environmentAnimations"]["ready"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
