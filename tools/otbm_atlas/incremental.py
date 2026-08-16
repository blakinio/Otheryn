"""Plan and execute bounded incremental OTBM Atlas work.

Normal CI calls ``plan`` first. A plan that truly requires every detail chunk is
marked ``fullBuildRequired`` and is rejected by ``guard`` unless an operator
explicitly supplies ``--allow-full-build``. The command never silently falls
back to a canonical full-world render.
"""
from __future__ import annotations

import argparse
from collections.abc import Iterable, Mapping
import json
from pathlib import Path

from .incremental_core import (
    ChunkKey,
    asset_impact,
    build_content_addressed_manifest,
    build_dependency_index,
    canonical_json,
    collect_asset_state,
    diff_publication_manifests,
    overview_contract_digest,
    render_contract_digest,
    render_selected_chunks,
    sha256_bytes,
    sha256_file,
    spool_hashes,
    spool_map,
    write_bytes_atomic,
    write_json_atomic,
)
from .overview import LOW_OVERVIEW_FACTOR, OVERVIEW_FACTOR, OVERVIEW_VERSION, make_overview

WORLD_REL = Path("vendor/map-analysis/crystalserver/data-global/world/world.otbm")
ASSET_REL = Path("vendor/map-analysis/tibia-client/15.25.bd5a04/assets")
PLAN_VERSION = 1
DEFAULT_CHUNK_SIZE = 128


def _sorted_chunks(values: Iterable[str]) -> list[str]:
    return sorted(set(values), key=lambda text: (ChunkKey.parse(text).z, ChunkKey.parse(text).y, ChunkKey.parse(text).x))


def classify_changed_paths(paths: Iterable[str]) -> dict[str, object]:
    domains: set[str] = set()
    normalized = sorted({path.replace("\\", "/") for path in paths})
    for path in normalized:
        if path.endswith("world.otbm"):
            domains.add("mapGeometry")
        if path.startswith("vendor/map-analysis/tibia-client/"):
            domains.add("renderAssets")
        if path.startswith("vendor/map-analysis/crystalserver/data-global/world/") and (path.endswith("-monster.xml") or path.endswith("-npc.xml")):
            domains.add("spawns")
        if path.startswith("vendor/map-analysis/crystalserver/data-global/npc/"):
            domains.add("npcDefinitions")
        if path.startswith("vendor/map-analysis/crystalserver/data-global/monster/"):
            domains.add("monsterDefinitions")
        if path.startswith("vendor/map-analysis/crystalserver/data-global/scripts/") or "mechanics" in path:
            domains.add("mechanics")
        if "factual" in path or "/facts" in path:
            domains.add("factualData")
        if path.startswith("tools/otbm_atlas/") and ("viewer" in path or path.endswith("_runtime.js") or path.endswith(".css")):
            domains.add("frontend")
        if path.startswith(".github/workflows/"):
            domains.add("ci")
        if path.startswith("docs/") or path.endswith(".md"):
            domains.add("documentation")
    if not domains:
        domains.add("unclassified")
    return {"changedPaths": normalized, "domains": sorted(domains)}


def plan_from_states(
    base_spool: Mapping[str, str],
    target_spool: Mapping[str, str],
    dependency_index: Mapping[str, object],
    base_assets: Mapping[str, object],
    target_assets: Mapping[str, object],
    base_render_digest: str,
    target_render_digest: str,
    base_overview_digest: str,
    target_overview_digest: str,
    *,
    changed_paths: Iterable[str] = (),
) -> dict[str, object]:
    added = set(target_spool) - set(base_spool)
    deleted = set(base_spool) - set(target_spool)
    map_changed = {key for key in set(base_spool) & set(target_spool) if base_spool[key] != target_spool[key]}
    assets = asset_impact(base_assets, target_assets, dependency_index)
    all_target = set(target_spool)
    full_reasons = list(assets.get("globalReasons", []))
    if base_render_digest != target_render_digest:
        full_reasons.append("RENDER_CONTRACT_CHANGED")

    if full_reasons:
        detail = all_target
    else:
        detail = added | map_changed | set(str(value) for value in assets.get("affectedChunks", []))
    overview = set(detail)
    if base_overview_digest != target_overview_digest:
        overview = all_target

    classification = classify_changed_paths(changed_paths)
    result: dict[str, object] = {
        "schemaVersion": PLAN_VERSION,
        "classification": classification,
        "fullBuildRequired": bool(full_reasons),
        "fullBuildReasons": sorted(set(full_reasons)),
        "map": {
            "addedChunks": _sorted_chunks(added),
            "changedChunks": _sorted_chunks(map_changed),
            "deletedChunks": _sorted_chunks(deleted),
        },
        "assets": assets,
        "detail": {
            "dirtyChunks": _sorted_chunks(detail),
            "deletedChunks": _sorted_chunks(deleted),
            "totalTargetChunks": len(all_target),
        },
        "overview": {
            "dirtyChunks": _sorted_chunks(overview),
            "contractChanged": base_overview_digest != target_overview_digest,
        },
        "dataDomains": {
            "spawns": any(value in classification["domains"] for value in ("spawns", "npcDefinitions", "monsterDefinitions")),
            "mechanics": "mechanics" in classification["domains"],
            "factualData": "factualData" in classification["domains"],
            "frontend": "frontend" in classification["domains"],
        },
    }
    result["planDigest"] = sha256_bytes(canonical_json(result))
    return result


def _prepare_spools(base_root: Path, target_root: Path, work: Path, chunk_size: int) -> tuple[dict[str, str], dict[str, str], Path]:
    target_spool_dir = work / "target-spool"
    spool_map(target_root / WORLD_REL, target_spool_dir, chunk_size)
    target_hashes = spool_hashes(target_spool_dir)
    if sha256_file(base_root / WORLD_REL) == sha256_file(target_root / WORLD_REL):
        base_hashes = dict(target_hashes)
    else:
        base_spool_dir = work / "base-spool"
        spool_map(base_root / WORLD_REL, base_spool_dir, chunk_size)
        base_hashes = spool_hashes(base_spool_dir)
    return base_hashes, target_hashes, target_spool_dir


def build_plan(base_root: Path, target_root: Path, work: Path, *, chunk_size: int = DEFAULT_CHUNK_SIZE, changed_paths: Iterable[str] = ()) -> tuple[dict[str, object], dict[str, object], dict[str, object], Path]:
    base_root = base_root.resolve()
    target_root = target_root.resolve()
    work.mkdir(parents=True, exist_ok=True)
    base_hashes, target_hashes, target_spool_dir = _prepare_spools(base_root, target_root, work, chunk_size)
    dependency_index = build_dependency_index(target_spool_dir, target_root / ASSET_REL)
    base_assets = collect_asset_state(base_root / ASSET_REL)
    target_assets = collect_asset_state(target_root / ASSET_REL)
    plan = plan_from_states(
        base_hashes,
        target_hashes,
        dependency_index,
        base_assets,
        target_assets,
        render_contract_digest(base_root),
        render_contract_digest(target_root),
        overview_contract_digest(base_root),
        overview_contract_digest(target_root),
        changed_paths=changed_paths,
    )
    write_json_atomic(work / "dependency-index.json", dependency_index)
    write_json_atomic(work / "asset-state.json", target_assets)
    write_json_atomic(work / "impact-plan.json", plan)
    return plan, dependency_index, target_assets, target_spool_dir


def require_full_build_authorization(plan: Mapping[str, object], *, allow_full_build: bool) -> None:
    if bool(plan.get("fullBuildRequired")) and not allow_full_build:
        reasons = ", ".join(str(value) for value in plan.get("fullBuildReasons", [])) or "UNKNOWN"
        raise RuntimeError(f"full Atlas build is required but not authorized: {reasons}; rerun explicitly with --allow-full-build")


def _detail_paths_for_chunk(text: str) -> list[str]:
    key = ChunkKey.parse(text)
    stem = f"z{key.z}/{key.x}_{key.y}"
    return [f"tiles/{stem}.png", f"tiles/{stem}.json"]


def _overview_paths_for_chunk(text: str) -> list[str]:
    key = ChunkKey.parse(text)
    stem = f"z{key.z}/{key.x}_{key.y}"
    return [
        f"overview/{stem}.png",
        f"overview/{stem}.json",
        f"overview-low/{stem}.png",
        f"overview-low/{stem}.json",
    ]


def _logical_paths_for_chunk(text: str) -> list[str]:
    return _detail_paths_for_chunk(text) + _overview_paths_for_chunk(text)


def render_overview_chunks(detail_source: Path, output: Path, chunk_keys: Iterable[str]) -> dict[str, object]:
    rendered: list[dict[str, object]] = []
    for text in _sorted_chunks(chunk_keys):
        key = ChunkKey.parse(text)
        detail_path = detail_source / "tiles" / f"z{key.z}" / f"{key.x}_{key.y}.png"
        if not detail_path.is_file():
            raise FileNotFoundError(f"overview-only rebuild requires existing detail PNG: {detail_path}")
        detail = detail_path.read_bytes()
        detail_checksum = sha256_bytes(detail)
        result: dict[str, object] = {"chunk": text, "detailChecksum": detail_checksum}
        for prefix, directory, factor in (("overview", "overview", OVERVIEW_FACTOR), ("lowOverview", "overview-low", LOW_OVERVIEW_FACTOR)):
            payload = make_overview(detail, factor)
            target = output / directory / f"z{key.z}" / f"{key.x}_{key.y}.png"
            write_bytes_atomic(target, payload)
            checksum = sha256_bytes(payload)
            report = {
                "fingerprint": sha256_bytes(f"{OVERVIEW_VERSION}:{factor}:{detail_checksum}".encode("utf-8")),
                "checksum": checksum,
            }
            write_json_atomic(target.with_suffix(".json"), report)
            result[f"{prefix}Path"] = target.relative_to(output).as_posix()
            result[f"{prefix}Checksum"] = checksum
        rendered.append(result)
    manifest = {"schemaVersion": 1, "chunks": rendered}
    write_json_atomic(output / "incremental-overview.json", manifest)
    return manifest


def compose_publication(base: Mapping[str, object] | None, changed_manifest: Mapping[str, object], deleted_chunks: Iterable[str]) -> dict[str, object]:
    base_entries = dict(base.get("entries", {})) if base and isinstance(base.get("entries"), Mapping) else {}
    changed_entries = changed_manifest.get("entries", {})
    if not isinstance(changed_entries, Mapping):
        raise ValueError("invalid changed publication manifest")
    for text in deleted_chunks:
        for logical in _logical_paths_for_chunk(text):
            base_entries.pop(logical, None)
    base_entries.update({str(path): dict(record) for path, record in changed_entries.items() if isinstance(record, Mapping)})
    target: dict[str, object] = {"schemaVersion": 1, "entries": dict(sorted(base_entries.items()))}
    target["manifestDigest"] = sha256_bytes(canonical_json(target))
    return target


def publish_incremental(render_root: Path, object_root: Path, plan: Mapping[str, object], base_manifest_path: Path | None, target_manifest_path: Path) -> dict[str, object]:
    detail = plan.get("detail", {})
    overview = plan.get("overview", {})
    dirty_detail = {str(value) for value in detail.get("dirtyChunks", [])} if isinstance(detail, Mapping) else set()
    dirty_overview = {str(value) for value in overview.get("dirtyChunks", [])} if isinstance(overview, Mapping) else set()
    logical_paths: set[str] = set()
    for text in dirty_detail:
        logical_paths.update(_detail_paths_for_chunk(text))
    for text in dirty_overview:
        logical_paths.update(_overview_paths_for_chunk(text))
    existing = [path for path in sorted(logical_paths) if (render_root / path).is_file()]
    changed_manifest = build_content_addressed_manifest(render_root, existing, object_root)
    base = json.loads(base_manifest_path.read_text(encoding="utf-8")) if base_manifest_path and base_manifest_path.is_file() else None
    deleted = detail.get("deletedChunks", []) if isinstance(detail, Mapping) else []
    target = compose_publication(base, changed_manifest, (str(value) for value in deleted))
    patch = diff_publication_manifests(base, target)
    # Immutable objects are durable first; one atomic manifest replacement promotes the candidate.
    write_json_atomic(target_manifest_path, target)
    write_json_atomic(target_manifest_path.with_name("publication-patch.json"), patch)
    return patch


def _read_changed_paths(path: Path | None) -> list[str]:
    if path is None:
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    classify = sub.add_parser("classify")
    classify.add_argument("paths", nargs="*")

    plan_parser = sub.add_parser("plan")
    plan_parser.add_argument("--base-root", type=Path, required=True)
    plan_parser.add_argument("--target-root", type=Path, required=True)
    plan_parser.add_argument("--work", type=Path, required=True)
    plan_parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    plan_parser.add_argument("--changed-paths", type=Path)
    plan_parser.add_argument("--output", type=Path)

    guard = sub.add_parser("guard")
    guard.add_argument("plan", type=Path)
    guard.add_argument("--allow-full-build", action="store_true")

    render = sub.add_parser("render")
    render.add_argument("plan", type=Path)
    render.add_argument("--work", type=Path, required=True)
    render.add_argument("--target-root", type=Path, required=True)
    render.add_argument("--output", type=Path, required=True)
    render.add_argument("--detail-source", type=Path, help="existing detail publication used only for overview-only invalidation")
    render.add_argument("--allow-full-build", action="store_true")

    publish = sub.add_parser("publish")
    publish.add_argument("plan", type=Path)
    publish.add_argument("--render-root", type=Path, required=True)
    publish.add_argument("--object-root", type=Path, required=True)
    publish.add_argument("--base-manifest", type=Path)
    publish.add_argument("--target-manifest", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "classify":
        print(json.dumps(classify_changed_paths(args.paths), indent=2, sort_keys=True))
        return 0
    if args.command == "plan":
        changed = _read_changed_paths(args.changed_paths)
        result, _deps, _assets, _spool = build_plan(args.base_root, args.target_root, args.work, chunk_size=args.chunk_size, changed_paths=changed)
        if args.output:
            write_json_atomic(args.output, result)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "guard":
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        require_full_build_authorization(plan, allow_full_build=args.allow_full_build)
        return 0
    if args.command == "render":
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        require_full_build_authorization(plan, allow_full_build=args.allow_full_build)
        deps = json.loads((args.work / "dependency-index.json").read_text(encoding="utf-8"))
        assets = json.loads((args.work / "asset-state.json").read_text(encoding="utf-8"))
        detail = plan.get("detail", {})
        overview = plan.get("overview", {})
        dirty_detail = {str(value) for value in detail.get("dirtyChunks", [])} if isinstance(detail, Mapping) else set()
        dirty_overview = {str(value) for value in overview.get("dirtyChunks", [])} if isinstance(overview, Mapping) else set()
        render_selected_chunks(args.work / "target-spool", args.target_root / ASSET_REL, args.output, dirty_detail, deps, assets, render_contract_digest(args.target_root))
        overview_only = dirty_overview - dirty_detail
        if overview_only:
            if args.detail_source is None:
                raise RuntimeError("overview-only invalidation requires --detail-source pointing at the prior detail publication")
            render_overview_chunks(args.detail_source, args.output, overview_only)
        return 0
    if args.command == "publish":
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        patch = publish_incremental(args.render_root, args.object_root, plan, args.base_manifest, args.target_manifest)
        print(json.dumps(patch, indent=2, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
