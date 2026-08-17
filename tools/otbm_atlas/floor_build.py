"""Build one canonical Atlas floor for distributed full-world certification.

This is a validation/recovery primitive, not the ordinary production entry point.
Each invocation parses the canonical snapshot into a private runner-local spool,
keeps exactly one Z floor, renders that floor with bounded process sharding, then
runs the current production data/environment/viewer producers against the same
partial manifest. No generated map corpus leaves the runner.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
from typing import Mapping

from .atlas import (
    ATLAS_VERSION,
    CANONICAL_ASSET_ROOT,
    CANONICAL_MONSTER_ROOT,
    CANONICAL_NPC_ROOT,
    CANONICAL_WORLD_ROOT,
    TILE_FACTS_VERSION,
    _sha256,
    _tree_sha256,
    canonical_source_paths,
    spool_map,
)
from .incremental_core import (
    ChunkKey,
    build_dependency_index,
    collect_asset_state,
    render_contract_digest,
)
from .incremental_shards import render_selected_chunks_sharded
from .overview import LOW_OVERVIEW_FACTOR, OVERVIEW_FACTOR, OVERVIEW_VERSION
from .production_data import build_incremental_production_data


def _chunk_key_for_path(path: Path) -> str:
    x, y = map(int, path.stem.split("_"))
    return ChunkKey(int(path.parent.name[1:]), x, y).text


def _keep_floor_spool(spool: Path, floor: int) -> tuple[list[str], list[str]]:
    chunk_keys: list[str] = []
    for path in sorted(spool.glob("z*/*.bin")):
        z = int(path.parent.name[1:])
        if z != floor:
            path.unlink()
            continue
        chunk_keys.append(_chunk_key_for_path(path))

    tile_fact_root = spool / "tile-facts"
    sidecars: list[str] = []
    if tile_fact_root.exists():
        for path in sorted(tile_fact_root.glob("z*/*.jsonl")):
            z = int(path.parent.name[1:])
            if z != floor:
                path.unlink()
                continue
            sidecars.append(path.relative_to(tile_fact_root).as_posix())
        for directory in sorted((candidate for candidate in tile_fact_root.glob("z*") if candidate.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass

    if not chunk_keys:
        raise RuntimeError(f"canonical floor Z{floor} contains no populated Atlas chunks")
    return chunk_keys, sidecars


def _manifest_rows(rendered: Mapping[str, object], chunk_size: int) -> list[dict[str, object]]:
    rows = rendered.get("chunks", [])
    if not isinstance(rows, list):
        raise ValueError("sharded floor render returned no chunks list")
    result: list[dict[str, object]] = []
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("invalid rendered floor chunk")
        row = dict(raw)
        z = int(row["z"])
        x = int(row["chunkX"])
        y = int(row["chunkY"])
        row["logicalBounds"] = [
            x * chunk_size,
            x * chunk_size + chunk_size - 1,
            y * chunk_size,
            y * chunk_size + chunk_size - 1,
            z,
        ]
        row["overviewImageWidth"] = int(row["imageWidth"]) // OVERVIEW_FACTOR
        row["overviewImageHeight"] = int(row["imageHeight"]) // OVERVIEW_FACTOR
        row["lowOverviewImageWidth"] = int(row["imageWidth"]) // LOW_OVERVIEW_FACTOR
        row["lowOverviewImageHeight"] = int(row["imageHeight"]) // LOW_OVERVIEW_FACTOR
        result.append(row)
    return result


def build_floor(
    map_path: Path,
    asset_dir: Path,
    output: Path,
    *,
    floor: int,
    workers: int = 4,
    repository_root: Path = Path("."),
    chunk_size: int = 128,
) -> dict[str, object]:
    if not 0 <= floor <= 15:
        raise ValueError("floor must be in Z0..Z15")
    if workers <= 0:
        raise ValueError("workers must be positive")
    cpu_count = max(1, os.cpu_count() or 1)
    worker_count = min(workers, cpu_count, 4)

    canonical = canonical_source_paths(repository_root)
    if map_path.resolve() != canonical["map"].resolve():
        raise ValueError("distributed floor certification requires the canonical map")
    if asset_dir.resolve() != canonical["appearanceAssetRoot"].resolve():
        raise ValueError("distributed floor certification requires canonical appearance assets")

    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True)
    spool = output / ".spool"
    spool_map(map_path, spool, chunk_size)
    chunk_keys, sidecars = _keep_floor_spool(spool, floor)

    dependency_index = build_dependency_index(spool, asset_dir)
    asset_state = collect_asset_state(asset_dir)
    render_digest = render_contract_digest(repository_root)
    rendered = render_selected_chunks_sharded(
        spool,
        asset_dir,
        output,
        chunk_keys,
        dependency_index,
        asset_state,
        render_digest,
        workers=worker_count,
        shards=worker_count,
    )
    chunks = _manifest_rows(rendered, chunk_size)

    map_sha = _sha256(map_path)
    assets_sha = _tree_sha256(asset_dir)
    sources = {
        "mapSha256": map_sha,
        "assetsSha256": assets_sha,
        "chunkSize": chunk_size,
        "atlasVersion": ATLAS_VERSION,
        "tileFactsVersion": TILE_FACTS_VERSION,
    }
    provenance = {
        "map": CANONICAL_WORLD_ROOT.joinpath("world.otbm").as_posix(),
        "worldRoot": CANONICAL_WORLD_ROOT.as_posix(),
        "npcDefinitionRoot": CANONICAL_NPC_ROOT.as_posix(),
        "monsterDefinitionRoot": CANONICAL_MONSTER_ROOT.as_posix(),
        "appearanceAssetRoot": CANONICAL_ASSET_ROOT.as_posix(),
    }
    manifest = {
        "schemaVersion": ATLAS_VERSION,
        "chunkSize": chunk_size,
        "tilePixels": 32,
        "overviewFactor": OVERVIEW_FACTOR,
        "lowOverviewFactor": LOW_OVERVIEW_FACTOR,
        "overviewVersion": OVERVIEW_VERSION,
        "chunks": chunks,
        "sources": sources,
        "provenance": provenance,
        "certification": {
            "scope": "single-floor",
            "floor": floor,
            "workers": worker_count,
        },
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (spool / "source.json").write_text(json.dumps(sources, sort_keys=True) + "\n", encoding="utf-8")

    render_plan = {
        "dirtyDetailChunks": chunk_keys,
        "reusedDetailChunks": [],
        "deletedDetailChunks": [],
        "fullBuildRequired": False,
        "fullBuildReasons": [],
        "legacyPublicationAdopted": False,
        "spool": {
            "parsed": True,
            "integrity": "canonical-single-floor-certification",
            "renderShards": {"changed": chunk_keys, "reused": [], "deleted": []},
            "tileFacts": {"changed": sidecars, "reused": [], "deleted": []},
            "factsChanged": True,
        },
    }
    build_incremental_production_data(
        map_path=map_path,
        asset_dir=asset_dir,
        output=output,
        repository_root=repository_root,
        canonical=canonical,
        chunk_size=chunk_size,
        chunks=chunks,
        render_plan=render_plan,
        provenance=provenance,
        assets_sha=assets_sha,
    )
    print(
        json.dumps(
            {
                "floor": floor,
                "chunks": len(chunks),
                "workers": worker_count,
                "mapSha256": map_sha,
                "assetsSha256": assets_sha,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", type=Path)
    parser.add_argument("assets", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--floor", type=int, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--chunk-size", type=int, default=128)
    parser.add_argument("--repository", type=Path, default=Path("."))
    args = parser.parse_args()
    build_floor(
        args.map,
        args.assets,
        args.output,
        floor=args.floor,
        workers=args.workers,
        repository_root=args.repository,
        chunk_size=args.chunk_size,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
