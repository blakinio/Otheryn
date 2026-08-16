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


def deployment_preflight(root: Path, *, verify_chunks: bool = True, require_environment_animations: bool = False) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    requirement_errors: list[str] = []
    warnings: list[str] = []

    missing_runtime = [relative for relative in REQUIRED_VIEWER_FILES if not (root / relative).is_file()]
    if missing_runtime:
        errors.extend(f"missing runtime file: {relative}" for relative in missing_runtime)

    viewer_contract: dict[str, Any] = {"status": "UNKNOWN", "files": {}}
    expected_viewer = _expected_viewer_bytes()
    viewer_mismatches: list[str] = []
    for relative, expected in expected_viewer.items():
        path = root / relative
        if not path.is_file():
            viewer_contract["files"][relative] = "MISSING"
            continue
        matches = path.read_bytes() == expected
        viewer_contract["files"][relative] = "CURRENT" if matches else "STALE_OR_MODIFIED"
        if not matches:
            viewer_mismatches.append(relative)
    if viewer_mismatches:
        errors.extend(f"generated viewer differs from current repository runtime: {relative}" for relative in viewer_mismatches)
    viewer_contract["status"] = "CURRENT" if not missing_runtime and not viewer_mismatches else "NOT_CURRENT"

    manifest: dict[str, Any] = {}
    identity: dict[str, Any] = {"status": "UNKNOWN"}
    manifest_path = root / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = _read_json(manifest_path)
            chunks = manifest.get("chunks", [])
            floors = sorted({int(chunk["z"]) for chunk in chunks if isinstance(chunk, dict) and "z" in chunk})
            sources = manifest.get("sources", {}) if isinstance(manifest.get("sources"), dict) else {}
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
        except Exception as error:  # verifier errors are deployment blockers, not guesses
            verification = {"status": "FAIL", "ok": False, "errors": [str(error)]}
            errors.append(f"atlas verification failed: {error}")

    creatures: dict[str, Any] = {"status": "UNKNOWN"}
    spawns_path = root / "data/spawns.json"
    missing_creature_assets: list[str] = []
    if spawns_path.is_file():
        try:
            spawns = _read_json(spawns_path)
            sprites, animations, static_records, animated_records = _referenced_creature_paths(spawns)
            for relative in sorted(sprites | animations):
                if not (root / relative).is_file():
                    missing_creature_assets.append(relative)
            creatures = {
                "status": "READY" if not missing_creature_assets else "INCOMPLETE",
                "recordsWithStaticSprite": static_records,
                "recordsWithAnimationDescriptor": animated_records,
                "uniqueStaticSpritePaths": len(sprites),
                "uniqueAnimationDescriptorPaths": len(animations),
                "missingReferencedAssets": missing_creature_assets,
            }
            if missing_creature_assets:
                errors.append(f"{len(missing_creature_assets)} referenced creature assets are missing")
        except (OSError, TypeError, json.JSONDecodeError) as error:
            errors.append(f"data/spawns.json cannot be validated: {error}")

    environment: dict[str, Any] = {"status": "MISSING", "path": "data/environment-animations/index.json"}
    environment_index = root / "data/environment-animations/index.json"
    if environment_index.is_file():
        try:
            index = _read_json(environment_index)
            schema = index.get("schemaVersion")
            if schema not in (1, 2):
                environment = {"status": "INVALID", "path": environment["path"], "schemaVersion": schema}
            else:
                environment = {
                    "status": "READY",
                    "path": environment["path"],
                    "schemaVersion": schema,
                    "statistics": index.get("statistics", {}),
                }
        except (OSError, TypeError, json.JSONDecodeError) as error:
            environment = {"status": "INVALID", "path": environment["path"], "error": str(error)}
    if environment["status"] != "READY":
        warnings.append("final environment-animation index is missing or invalid; core preview may be served but full browser acceptance remains partial")
        if require_environment_animations:
            requirement_errors.append("environment-animation final artifact required but missing or invalid")

    core_ready = not errors
    full_runtime_ready = core_ready and environment["status"] == "READY" and not missing_creature_assets
    status = "FULL_RUNTIME_READY" if full_runtime_ready else "CORE_PREVIEW_READY" if core_ready else "NOT_READY"
    return {
        "status": status,
        "corePreviewReady": core_ready,
        "fullRuntimeReady": full_runtime_ready,
        "root": str(root),
        "identity": identity,
        "viewer": viewer_contract,
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
