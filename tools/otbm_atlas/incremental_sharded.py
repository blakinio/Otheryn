"""Execute an existing incremental Atlas plan with deterministic process shards."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from collections.abc import Mapping

from .incremental import ASSET_REL, render_overview_chunks, require_full_build_authorization
from .incremental_core import render_contract_digest
from .incremental_shards import render_selected_chunks_sharded


def execute(
    plan_path: Path,
    work: Path,
    target_root: Path,
    output: Path,
    *,
    detail_source: Path | None = None,
    allow_full_build: bool = False,
    workers: int | None = None,
    shards: int | None = None,
) -> dict[str, object]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    require_full_build_authorization(plan, allow_full_build=allow_full_build)
    dependencies = json.loads((work / "dependency-index.json").read_text(encoding="utf-8"))
    assets = json.loads((work / "asset-state.json").read_text(encoding="utf-8"))
    detail = plan.get("detail", {})
    overview = plan.get("overview", {})
    dirty_detail = {str(value) for value in detail.get("dirtyChunks", [])} if isinstance(detail, Mapping) else set()
    dirty_overview = {str(value) for value in overview.get("dirtyChunks", [])} if isinstance(overview, Mapping) else set()

    resolved_workers = workers if workers is not None else max(1, os.cpu_count() or 1)
    # One weighted shard per process is the normal default because each shard
    # initializes an AssetRenderer. Extra shards remain an explicit tuning knob.
    resolved_shards = shards if shards is not None else resolved_workers
    if resolved_workers <= 0:
        raise ValueError("worker count must be positive")
    if resolved_shards <= 0:
        raise ValueError("shard count must be positive")

    manifest: dict[str, object] = {"schemaVersion": 1, "chunks": []}
    if dirty_detail:
        manifest = render_selected_chunks_sharded(
            work / "target-spool",
            target_root / ASSET_REL,
            output,
            dirty_detail,
            dependencies,
            assets,
            render_contract_digest(target_root),
            workers=resolved_workers,
            shards=resolved_shards,
        )

    overview_only = dirty_overview - dirty_detail
    if overview_only:
        if detail_source is None:
            raise RuntimeError("overview-only invalidation requires --detail-source pointing at the prior detail publication")
        render_overview_chunks(detail_source, output, overview_only)

    return {
        "schemaVersion": 1,
        "dirtyDetailChunks": len(dirty_detail),
        "overviewOnlyChunks": len(overview_only),
        "workers": resolved_workers,
        "requestedShards": resolved_shards,
        "renderedChunks": len(manifest.get("chunks", [])) if isinstance(manifest.get("chunks"), list) else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--detail-source", type=Path)
    parser.add_argument("--allow-full-build", action="store_true")
    parser.add_argument("--workers", type=int)
    parser.add_argument("--shards", type=int)
    args = parser.parse_args()
    result = execute(
        args.plan,
        args.work,
        args.target_root,
        args.output,
        detail_source=args.detail_source,
        allow_full_build=args.allow_full_build,
        workers=args.workers,
        shards=args.shards,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
