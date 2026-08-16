"""Persistent-state wrapper for the Atlas incremental planner.

This is the GitHub-hosted/production orchestration entry point. It reuses a
self-validating spatial spool and dependency index between runs, but delegates
all canonical impact semantics to :mod:`tools.otbm_atlas.incremental`.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .incremental import (
    ASSET_REL,
    DEFAULT_CHUNK_SIZE,
    WORLD_REL,
    _paths_require_render_scan,
    build_plan,
    plan_from_states,
)
from .incremental_core import (
    collect_asset_state,
    overview_contract_digest,
    render_contract_digest,
    write_json_atomic,
)
from .incremental_core_guard import strict_render_core_transition_reasons
from .incremental_state import (
    prepare_dependency_index,
    prepare_persistent_spool,
    write_operational_state,
)


def _link_target_spool(work: Path, target_spool: Path) -> Path:
    """Expose persistent spool at the legacy incremental renderer work path."""
    link = work / "target-spool"
    if link.is_symlink() or link.exists():
        if link.is_symlink() or link.is_file():
            link.unlink()
        else:
            import shutil
            shutil.rmtree(link)
    relative = os.path.relpath(target_spool, start=work)
    link.symlink_to(relative, target_is_directory=True)
    return link


def build_cached_plan(
    base_root: Path,
    target_root: Path,
    work: Path,
    state_root: Path,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    changed_paths: list[str] | None = None,
) -> dict[str, object]:
    base_root = base_root.resolve()
    target_root = target_root.resolve()
    work = work.resolve()
    state_root = state_root.resolve()
    changed = list(changed_paths or [])
    work.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)

    core_reasons = strict_render_core_transition_reasons(base_root, target_root)
    if not _paths_require_render_scan(changed, core_reasons):
        plan, _deps, _assets, _spool = build_plan(
            base_root,
            target_root,
            work,
            chunk_size=chunk_size,
            changed_paths=changed,
        )
        write_operational_state(
            work,
            work / "target-spool",
            {"cacheHit": None, "targetSpoolSource": "not-required"},
            {"dependencyIndexCacheHit": None},
        )
        return plan

    base_hashes, target_hashes, persistent_spool, spatial_report = prepare_persistent_spool(
        base_root / WORLD_REL,
        target_root / WORLD_REL,
        work,
        state_root,
        chunk_size,
    )
    target_spool = _link_target_spool(work, persistent_spool)
    dependency_index, dependency_report = prepare_dependency_index(
        persistent_spool,
        target_root / ASSET_REL,
        state_root,
    )
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
        changed_paths=changed,
        additional_full_reasons=core_reasons,
    )
    write_json_atomic(work / "dependency-index.json", dependency_index)
    write_json_atomic(work / "asset-state.json", target_assets)
    write_json_atomic(work / "impact-plan.json", plan)
    write_operational_state(work, target_spool, spatial_report, dependency_report)
    return plan


def _read_changed_paths(path: Path | None) -> list[str]:
    if path is None:
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--changed-paths", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    plan = build_cached_plan(
        args.base_root,
        args.target_root,
        args.work,
        args.state_root,
        chunk_size=args.chunk_size,
        changed_paths=_read_changed_paths(args.changed_paths),
    )
    if args.output:
        write_json_atomic(args.output, plan)
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
