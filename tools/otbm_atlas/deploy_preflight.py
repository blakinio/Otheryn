"""Deployment preflight for an already-generated canonical OTBM Atlas."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .verify import verify_atlas
from .viewer import VIEWER_HTML

EXPECTED_ATLAS_VERSION = 3
EXPECTED_CHUNK_SIZE = 128
EXPECTED_CHUNKS = 3494
EXPECTED_FLOORS = tuple(range(16))
EXPECTED_MAP_SHA256 = "3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034"
KNOWN_ASSET_SHA256 = {
    "4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7": "canonical-git-bytes",
    "4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2": "validated-windows-worktree-crlf-non-render-input",
}
REQUIRED_VIEWER_FILES = (
    "index.html",
    "viewer-app.js",
    "viewer-runtime.js",
    "creature-animation-runtime.js",
    "manifest.json",
    "data/search-index.json",
    "data/statistics.json",
    "data/spawns.json",
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _expected_viewer_bytes() -> dict[str, bytes]:
    source = Path(__file__).parent
    return {
        "index.html": VIEWER_HTML.encode("utf-8"),
        "viewer-app.js": (source / "viewer_app.js").read_bytes(),
        "viewer-runtime.js": (source / "viewer_runtime.js").read_bytes(),
        "creature-animation-runtime.js": (source / "creature_animation_runtime.js").read_bytes(),
    }


def _referenced_creature_paths(spawns: dict[str, Any]) -> tuple[set[str], set[str], int, int]:
    sprites: set[str] = set()
    animations: set[str] = set()
    static_records = 0
    animated_records = 0
    for kind in ("npcSpawns", "monsterSpawns", "supplementalNpcSpawns", "supplementalMonsterSpawns"):
        records = spawns.get(kind, [])
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, dict):
                continue
            sprite = record.get("sprite")
            animation = record.get("spriteAnimation")
            if isinstance(sprite, str) and sprite:
                sprites.add(sprite)
                static_records += 1
            if isinstance(animation, str) and animation:
                animations.add(animation)
                animated_records += 1
    return sprites, animations, static_records, animated_records


def _image_paths(value: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(value, dict):
        for child in value.values():
            paths.update(_image_paths(child))
    elif isinstance(value, list):
        for child in value:
            paths.update(_image_paths(child))
    elif isinstance(value, str) and value.lower().endswith((".png", ".webp")):
        paths.add(value)
    return paths


def _validate_spatial(root: Path, errors: list[str]) -> dict[str, Any]:
    statistics_path = root / "data/statistics.json"
    search_path = root / "data/search-index.json"
    if not statistics_path.is_file() or not search_path.is_file():
        return {"status": "UNKNOWN"}
    try:
        statistics = _read_json(statistics_path)
        search = _read_json(search_path)
        shard_paths = sorted((root / "data/chunks").glob("z*/*.json"))
        invalid_shards: list[str] = []
        for path in shard_paths:
            try:
                shard = _read_json(path)
                if not isinstance(shard, dict) or shard.get("schemaVersion") != 1:
                    invalid_shards.append(path.relative_to(root).as_posix())
            except (OSError, TypeError, json.JSONDecodeError):
                invalid_shards.append(path.relative_to(root).as_posix())
        records = search.get("records", []) if isinstance(search, dict) else []
        reported = statistics.get("spatialData", {}) if isinstance(statistics, dict) else {}
        if isinstance(reported, dict) and "shards" in reported and int(reported["shards"]) != len(shard_paths):
            errors.append(f"spatial shard count differs from statistics: disk={len(shard_paths)} reported={reported['shards']}")
        if isinstance(reported, dict) and "searchRecords" in reported and int(reported["searchRecords"]) != len(records):
            errors.append(f"search record count differs from statistics: disk={len(records)} reported={reported['searchRecords']}")
        if invalid_shards:
            errors.append(f"{len(invalid_shards)} spatial shard JSON files are invalid")
        return {
            "status": "READY" if not invalid_shards else "INVALID",
            "shards": len(shard_paths),
            "searchRecords": len(records),
            "invalidShards": invalid_shards,
        }
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"spatial data cannot be validated: {error}")
        return {"status": "INVALID", "error": str(error)}


def _validate_environment(root: Path) -> tuple[dict[str, Any], list[str]]:
    relative_index = "data/environment-animations/index.json"
    index_path = root / relative_index
    if not index_path.is_file():
        return {"status": "MISSING", "path": relative_index}, []
    environment_errors: list[str] = []
    try:
        index = _read_json(index_path)
        schema = index.get("schemaVersion") if isinstance(index, dict) else None
        if schema not in (1, 2):
            return {"status": "INVALID", "path": relative_index, "schemaVersion": schema}, ["environment-animation index schema must be 1 or 2"]
        chunk_paths = sorted((root / "data/environment-animations/chunks").glob("z*/*.json"))
        records_count = 0
        animation_keys: set[str] = set()
        missing_assets: set[str] = set()
        invalid_chunks: list[str] = []
        for chunk_path in chunk_paths:
            try:
                shard = _read_json(chunk_path)
                records = shard.get("records", []) if isinstance(shard, dict) else []
                if not isinstance(records, list) or shard.get("schemaVersion") not in (1, 2):
                    invalid_chunks.append(chunk_path.relative_to(root).as_posix())
                    continue
                for record in records:
                    if not isinstance(record, dict):
                        invalid_chunks.append(chunk_path.relative_to(root).as_posix())
                        continue
                    records_count += 1
                    if record.get("animationKey") is not None:
                        animation_keys.add(str(record["animationKey"]))
                    references = set(str(value) for value in record.get("frames", []) if isinstance(value, str))
                    for key in ("underlay", "overdraw"):
                        value = record.get(key)
                        if isinstance(value, str):
                            references.add(value)
                    for relative in references:
                        if not (root / relative).is_file():
                            missing_assets.add(relative)
            except (OSError, TypeError, json.JSONDecodeError):
                invalid_chunks.append(chunk_path.relative_to(root).as_posix())
        statistics = index.get("statistics", {}) if isinstance(index, dict) else {}
        if isinstance(statistics, dict):
            if "instances" in statistics and int(statistics["instances"]) != records_count:
                environment_errors.append(f"environment instance count differs: records={records_count} index={statistics['instances']}")
            if "uniqueAnimations" in statistics and int(statistics["uniqueAnimations"]) != len(animation_keys):
                environment_errors.append(f"environment unique-animation count differs: records={len(animation_keys)} index={statistics['uniqueAnimations']}")
            if "chunks" in statistics and int(statistics["chunks"]) != len(chunk_paths):
                environment_errors.append(f"environment chunk count differs: disk={len(chunk_paths)} index={statistics['chunks']}")
        if invalid_chunks:
            environment_errors.append(f"{len(set(invalid_chunks))} environment-animation shard JSON files are invalid")
        if missing_assets:
            environment_errors.append(f"{len(missing_assets)} environment-animation referenced assets are missing")
        return {
            "status": "READY" if not environment_errors else "INVALID",
            "path": relative_index,
            "schemaVersion": schema,
            "statistics": statistics,
            "validatedChunks": len(chunk_paths),
            "validatedInstances": records_count,
            "validatedUniqueAnimations": len(animation_keys),
            "missingReferencedAssets": sorted(missing_assets),
            "invalidChunks": sorted(set(invalid_chunks)),
        }, environment_errors
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        return {"status": "INVALID", "path": relative_index, "error": str(error)}, [f"environment-animation index cannot be validated: {error}"]


def deployment_preflight(root: Path, *, verify_chunks: bool = True, require_environment_animations: bool = False) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    requirement_errors: list[str] = []
    warnings: list[str] = []

    missing_runtime = [relative for relative in REQUIRED_VIEWER_FILES if not (root / relative).is_file()]
    errors.extend(f"missing runtime file: {relative}" for relative in missing_runtime)

    expected_viewer = _expected_viewer_bytes()
    viewer_files: dict[str, str] = {}
    viewer_mismatches: list[str] = []
    for relative, expected in expected_viewer.items():
        path = root / relative
        if not path.is_file():
            viewer_files[relative] = "MISSING"
            continue
        matches = path.read_bytes() == expected
        viewer_files[relative] = "CURRENT" if matches else "STALE_OR_MODIFIED"
        if not matches:
            viewer_mismatches.append(relative)
    errors.extend(f"generated viewer differs from current repository runtime: {relative}" for relative in viewer_mismatches)
    viewer = {"status": "CURRENT" if not missing_runtime and not viewer_mismatches else "NOT_CURRENT", "files": viewer_files}

    manifest: dict[str, Any] = {}
    identity: dict[str, Any] = {"status": "UNKNOWN"}
    manifest_path = root / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = _read_json(manifest_path)
            chunks = manifest.get("chunks", []) if isinstance(manifest, dict) else []
            floors = sorted({int(chunk["z"]) for chunk in chunks if isinstance(chunk, dict) and "z" in chunk})
            sources = manifest.get("sources", {}) if isinstance(manifest, dict) and isinstance(manifest.get("sources"), dict) else {}
            assets_sha = sources.get("assetsSha256")
            identity = {
                "status": "CHECKED",
                "schemaVersion": manifest.get("schemaVersion"),
                "chunkSize": manifest.get("chunkSize"),
                "chunks": len(chunks) if isinstance(chunks, list) else None,
                "floors": floors,
                "mapSha256": sources.get("mapSha256"),
                "assetsSha256": assets_sha,
                "assetsProvenance": KNOWN_ASSET_SHA256.get(str(assets_sha)),
            }
            checks = (
                (manifest.get("schemaVersion") == EXPECTED_ATLAS_VERSION, f"schemaVersion must be {EXPECTED_ATLAS_VERSION}"),
                (manifest.get("chunkSize") == EXPECTED_CHUNK_SIZE, f"chunkSize must be {EXPECTED_CHUNK_SIZE}"),
                (isinstance(chunks, list) and len(chunks) == EXPECTED_CHUNKS, f"chunk count must be {EXPECTED_CHUNKS}"),
                (floors == list(EXPECTED_FLOORS), "populated floors must be Z0..Z15"),
                (sources.get("mapSha256") == EXPECTED_MAP_SHA256, "map SHA-256 is not the canonical certified world"),
                (str(assets_sha) in KNOWN_ASSET_SHA256, "asset SHA-256 is not an accepted verified Atlas-v3 provenance"),
                (sources.get("atlasVersion") == EXPECTED_ATLAS_VERSION, f"sources.atlasVersion must be {EXPECTED_ATLAS_VERSION}"),
            )
            errors.extend(message for ok, message in checks if not ok)
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
            errors.append(f"manifest.json cannot be validated: {error}")

    verification: dict[str, Any] = {"status": "SKIPPED"}
    if verify_chunks and manifest_path.is_file():
        try:
            verification = verify_atlas(root)
            verification["status"] = "PASS" if verification.get("ok") else "FAIL"
            if not verification.get("ok"):
                errors.extend(f"atlas verification: {message}" for message in verification.get("errors", []))
        except Exception as error:
            verification = {"status": "FAIL", "ok": False, "errors": [str(error)]}
            errors.append(f"atlas verification failed: {error}")

    spatial = _validate_spatial(root, errors)

    creatures: dict[str, Any] = {"status": "UNKNOWN"}
    spawns_path = root / "data/spawns.json"
    missing_creature_assets: set[str] = set()
    invalid_descriptors: list[str] = []
    if spawns_path.is_file():
        try:
            spawns = _read_json(spawns_path)
            sprites, animations, static_records, animated_records = _referenced_creature_paths(spawns)
            for relative in sorted(sprites):
                if not (root / relative).is_file():
                    missing_creature_assets.add(relative)
            for relative in sorted(animations):
                descriptor_path = root / relative
                if not descriptor_path.is_file():
                    missing_creature_assets.add(relative)
                    continue
                try:
                    descriptor = _read_json(descriptor_path)
                    for frame in _image_paths(descriptor):
                        if not (root / frame).is_file():
                            missing_creature_assets.add(frame)
                except (OSError, TypeError, json.JSONDecodeError):
                    invalid_descriptors.append(relative)
            creature_ready = not missing_creature_assets and not invalid_descriptors
            creatures = {
                "status": "READY" if creature_ready else "INCOMPLETE",
                "recordsWithStaticSprite": static_records,
                "recordsWithAnimationDescriptor": animated_records,
                "uniqueStaticSpritePaths": len(sprites),
                "uniqueAnimationDescriptorPaths": len(animations),
                "missingReferencedAssets": sorted(missing_creature_assets),
                "invalidAnimationDescriptors": invalid_descriptors,
            }
            if missing_creature_assets:
                errors.append(f"{len(missing_creature_assets)} referenced creature assets are missing")
            if invalid_descriptors:
                errors.append(f"{len(invalid_descriptors)} creature animation descriptors are invalid")
        except (OSError, TypeError, json.JSONDecodeError) as error:
            errors.append(f"data/spawns.json cannot be validated: {error}")

    environment, environment_errors = _validate_environment(root)
    if environment["status"] != "READY":
        warnings.append("final environment-animation artifact is missing or invalid; core preview may be served but full browser acceptance remains partial")
        warnings.extend(environment_errors)
        if require_environment_animations:
            requirement_errors.append("environment-animation final artifact required but missing or invalid")
            requirement_errors.extend(environment_errors)

    core_ready = not errors
    full_runtime_ready = core_ready and creatures.get("status") == "READY" and environment["status"] == "READY"
    status = "FULL_RUNTIME_READY" if full_runtime_ready else "CORE_PREVIEW_READY" if core_ready else "NOT_READY"
    return {
        "status": status,
        "corePreviewReady": core_ready,
        "fullRuntimeReady": full_runtime_ready,
        "root": str(root),
        "identity": identity,
        "viewer": viewer,
        "spatial": spatial,
        "creatures": creatures,
        "environmentAnimations": environment,
        "verification": verification,
        "warnings": warnings,
        "errors": errors,
        "requirementErrors": requirement_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("atlas", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--skip-chunk-verification", action="store_true", help="plumbing-only check; never use this to certify a deployment corpus")
    parser.add_argument("--require-environment-animations", action="store_true")
    args = parser.parse_args()
    report = deployment_preflight(
        args.atlas,
        verify_chunks=not args.skip_chunk_verification,
        require_environment_animations=args.require_environment_animations,
    )
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if report["corePreviewReady"] and not report["requirementErrors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
