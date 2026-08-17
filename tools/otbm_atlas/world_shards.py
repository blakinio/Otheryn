"""Chunk-centric full-world certification planner and shard builder.

The canonical clean/recovery gate plans the complete OTBM world once, partitions
all populated chunks into deterministic weighted shards, then lets each GitHub
runner parse and render only its assignment. Generated map/animation corpora
remain runner-local; only the compact plan and verification evidence may cross
job boundaries.
"""
from __future__ import annotations

import argparse
from collections import Counter, OrderedDict
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import BinaryIO, Iterable, Mapping

from .atlas import (
    ATLAS_VERSION,
    CANONICAL_ASSET_ROOT,
    CANONICAL_MONSTER_ROOT,
    CANONICAL_NPC_ROOT,
    CANONICAL_WORLD_ROOT,
    SPOOL_VERSION,
    TILE_FACTS_VERSION,
    _sha256,
    _tree_sha256,
    canonical_source_paths,
    encode_tile,
    spool_map,
)
from .environment_animation_resume import enrich_environment_animations_resumable
from .incremental_core import (
    ChunkKey,
    build_dependency_index,
    chunk_sort_key,
    collect_asset_state,
    render_contract_digest,
)
from .incremental_shards import build_shard_plan, render_selected_chunks_sharded
from .overview import LOW_OVERVIEW_FACTOR, OVERVIEW_FACTOR, OVERVIEW_VERSION
from .semantic import Tile, iter_map_records

WORLD_SHARD_PLAN_VERSION = 1
WORLD_SHARD_COUNT = 32
WORLD_SHARD_ALGORITHM = "deterministic-lpt-spool-bytes-v1"
WORLD_WORKER_CAP = 4


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _json_digest(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _ordered_chunk_keys(values: Iterable[str]) -> list[str]:
    return sorted(set(values), key=lambda value: chunk_sort_key(ChunkKey.parse(value)))


def _chunk_keys_from_spool(spool: Path) -> list[str]:
    values: list[str] = []
    for path in sorted(spool.glob("z*/*.bin")):
        z = int(path.parent.name[1:])
        x, y = map(int, path.stem.split("_"))
        values.append(ChunkKey(z, x, y).text)
    if not values:
        raise RuntimeError("canonical world spool contains no populated Atlas chunks")
    return _ordered_chunk_keys(values)


def _assignment_digest(chunk_keys: Iterable[str]) -> str:
    return _json_digest(_ordered_chunk_keys(chunk_keys))


def _coverage_digest(chunk_keys: Iterable[str]) -> str:
    return hashlib.sha256(("\n".join(_ordered_chunk_keys(chunk_keys)) + "\n").encode("utf-8")).hexdigest()


def build_world_shard_plan(
    spool: Path,
    sources: Mapping[str, object],
    shard_count: int = WORLD_SHARD_COUNT,
) -> dict[str, object]:
    """Build one deterministic LPT partition over every populated world chunk."""
    if shard_count <= 0:
        raise ValueError("shard count must be positive")
    chunk_keys = _chunk_keys_from_spool(spool)
    weighted = build_shard_plan(spool, chunk_keys, shard_count)
    raw_shards = weighted.get("shards", [])
    if not isinstance(raw_shards, list):
        raise ValueError("invalid weighted shard plan")

    assignments: list[dict[str, object]] = []
    assigned: list[str] = []
    for raw in raw_shards:
        if not isinstance(raw, Mapping):
            raise ValueError("invalid weighted shard record")
        index = int(raw["index"])
        chunks = _ordered_chunk_keys(str(value) for value in raw.get("chunks", []))
        assigned.extend(chunks)
        assignments.append(
            {
                "index": index,
                "chunks": chunks,
                "chunkCount": len(chunks),
                "spoolBytes": int(raw.get("spoolBytes", 0)),
                "assignmentDigest": _assignment_digest(chunks),
            }
        )

    assignments.sort(key=lambda value: int(value["index"]))
    if [int(value["index"]) for value in assignments] != list(range(len(assignments))):
        raise RuntimeError("world shard indices are not contiguous")
    if len(assignments) != min(shard_count, len(chunk_keys)):
        raise RuntimeError("world shard count differs from deterministic planner output")
    if _ordered_chunk_keys(assigned) != chunk_keys or len(assigned) != len(set(assigned)):
        raise RuntimeError("world shard partition does not cover canonical chunks exactly once")

    floor_counts = Counter(ChunkKey.parse(value).z for value in chunk_keys)
    core = {
        "schemaVersion": WORLD_SHARD_PLAN_VERSION,
        "algorithm": WORLD_SHARD_ALGORITHM,
        "shardCount": shard_count,
        "chunks": len(chunk_keys),
        "floorCounts": {str(key): int(value) for key, value in sorted(floor_counts.items())},
        "coverageDigest": _coverage_digest(chunk_keys),
        "sources": dict(sources),
        "assignments": assignments,
        "spoolBytes": int(weighted.get("spoolBytes", 0)),
        "maxShardBytes": int(weighted.get("maxShardBytes", 0)),
        "minShardBytes": int(weighted.get("minShardBytes", 0)),
    }
    return {**core, "worldPlanDigest": _json_digest(core)}


def write_canonical_world_plan(
    map_path: Path,
    asset_dir: Path,
    plan_path: Path,
    *,
    shard_count: int = WORLD_SHARD_COUNT,
    repository_root: Path = Path("."),
    chunk_size: int = 128,
) -> dict[str, object]:
    canonical = canonical_source_paths(repository_root)
    if map_path.resolve() != canonical["map"].resolve():
        raise ValueError("world shard certification requires the canonical map")
    if asset_dir.resolve() != canonical["appearanceAssetRoot"].resolve():
        raise ValueError("world shard certification requires canonical appearance assets")

    sources = {
        "mapSha256": _sha256(map_path),
        "assetsSha256": _tree_sha256(asset_dir),
        "chunkSize": chunk_size,
        "atlasVersion": ATLAS_VERSION,
        "tileFactsVersion": TILE_FACTS_VERSION,
    }
    scratch = plan_path.parent / ".full-world-plan-spool"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        spool_map(map_path, scratch, chunk_size)
        plan = build_world_shard_plan(scratch, sources, shard_count)
        plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(
            json.dumps(
                {
                    "worldPlanDigest": plan["worldPlanDigest"],
                    "coverageDigest": plan["coverageDigest"],
                    "chunks": plan["chunks"],
                    "shards": plan["shardCount"],
                    "floorCounts": plan["floorCounts"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return plan
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


class _SelectedWriterPool:
    def __init__(self, directory: Path, limit: int = 64) -> None:
        self.directory = directory
        self.limit = limit
        self.handles: OrderedDict[tuple[int, int, int], BinaryIO] = OrderedDict()

    def write(self, key: tuple[int, int, int], payload: bytes) -> None:
        handle = self.handles.pop(key, None)
        if handle is None:
            path = self.directory / f"z{key[0]}" / f"{key[1]}_{key[2]}.bin"
            path.parent.mkdir(parents=True, exist_ok=True)
            handle = path.open("ab")
        self.handles[key] = handle
        handle.write(payload)
        if len(self.handles) > self.limit:
            _unused, old = self.handles.popitem(last=False)
            old.close()

    def close(self) -> None:
        for handle in self.handles.values():
            handle.close()
        self.handles.clear()


def spool_selected_chunks(
    map_path: Path,
    spool_dir: Path,
    chunk_size: int,
    chunk_keys: Iterable[str],
) -> dict[str, object]:
    """Parse the canonical OTBM once but materialize only one runner assignment."""
    selected = _ordered_chunk_keys(chunk_keys)
    if not selected:
        raise ValueError("world shard assignment is empty")
    selected_set = set(selected)
    selected_tuples = {
        (ChunkKey.parse(text).z, ChunkKey.parse(text).x, ChunkKey.parse(text).y)
        for text in selected
    }

    shutil.rmtree(spool_dir, ignore_errors=True)
    spool_dir.mkdir(parents=True, exist_ok=True)
    pool = _SelectedWriterPool(spool_dir)
    found: set[tuple[int, int, int]] = set()
    tiles = 0
    try:
        for record in iter_map_records(map_path, strict=True):
            if not isinstance(record, Tile):
                continue
            key = (
                int(record.position.z),
                int(record.position.x) // chunk_size,
                int(record.position.y) // chunk_size,
            )
            if key not in selected_tuples:
                continue
            pool.write(key, encode_tile(record))
            found.add(key)
            tiles += 1
    finally:
        pool.close()

    missing = selected_tuples - found
    if missing:
        values = ", ".join(
            ChunkKey(z, x, y).text for z, x, y in sorted(missing)
        )
        raise RuntimeError(f"selected canonical chunks were not materialized: {values}")

    metadata: dict[str, object] = {
        "schemaVersion": 1,
        "version": SPOOL_VERSION,
        "tileFactsVersion": TILE_FACTS_VERSION,
        "chunkSize": chunk_size,
        "tiles": tiles,
        "sourceSha256": _sha256(map_path),
        "scope": "world-chunk-shard",
        "selectedChunks": len(selected_set),
        "assignmentDigest": _assignment_digest(selected),
    }
    (spool_dir / "spool.json").write_text(
        json.dumps(metadata, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def _manifest_rows(rendered: Mapping[str, object], chunk_size: int) -> list[dict[str, object]]:
    rows = rendered.get("chunks", [])
    if not isinstance(rows, list):
        raise ValueError("sharded world render returned no chunks list")
    result: list[dict[str, object]] = []
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("invalid rendered world chunk")
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


def _load_plan(plan_path: Path) -> dict[str, object]:
    value = json.loads(plan_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("world shard plan must be a JSON object")
    if int(value.get("schemaVersion", -1)) != WORLD_SHARD_PLAN_VERSION:
        raise ValueError("unsupported world shard plan schema")
    core = dict(value)
    digest = str(core.pop("worldPlanDigest", ""))
    if not digest or _json_digest(core) != digest:
        raise ValueError("world shard plan digest mismatch")
    return value


def _assignment(plan: Mapping[str, object], shard_index: int) -> dict[str, object]:
    assignments = plan.get("assignments", [])
    if not isinstance(assignments, list):
        raise ValueError("world shard plan has no assignments")
    matches = [
        dict(value)
        for value in assignments
        if isinstance(value, Mapping) and int(value.get("index", -1)) == shard_index
    ]
    if len(matches) != 1:
        raise ValueError(f"world shard plan does not contain exactly one assignment for {shard_index}")
    assignment = matches[0]
    chunks = _ordered_chunk_keys(str(value) for value in assignment.get("chunks", []))
    if int(assignment.get("chunkCount", -1)) != len(chunks):
        raise ValueError("world shard assignment chunk count mismatch")
    if str(assignment.get("assignmentDigest", "")) != _assignment_digest(chunks):
        raise ValueError("world shard assignment digest mismatch")
    assignment["chunks"] = chunks
    return assignment


def build_world_shard(
    map_path: Path,
    asset_dir: Path,
    plan_path: Path,
    output: Path,
    *,
    shard_index: int,
    workers: int = WORLD_WORKER_CAP,
    repository_root: Path = Path("."),
) -> dict[str, object]:
    """Render one deterministic full-world chunk assignment plus its animations."""
    if workers <= 0:
        raise ValueError("workers must be positive")
    cpu_count = max(1, os.cpu_count() or 1)
    worker_count = min(workers, cpu_count, WORLD_WORKER_CAP)

    canonical = canonical_source_paths(repository_root)
    if map_path.resolve() != canonical["map"].resolve():
        raise ValueError("world shard certification requires the canonical map")
    if asset_dir.resolve() != canonical["appearanceAssetRoot"].resolve():
        raise ValueError("world shard certification requires canonical appearance assets")

    plan = _load_plan(plan_path)
    shard_count = int(plan["shardCount"])
    if not 0 <= shard_index < shard_count:
        raise ValueError(f"shard index must be in 0..{shard_count - 1}")
    assignment = _assignment(plan, shard_index)
    chunk_keys = list(assignment["chunks"])

    sources = dict(plan.get("sources", {}))
    chunk_size = int(sources.get("chunkSize", 0))
    if chunk_size <= 0:
        raise ValueError("world shard plan has invalid chunk size")
    local_sources = {
        "mapSha256": _sha256(map_path),
        "assetsSha256": _tree_sha256(asset_dir),
        "chunkSize": chunk_size,
        "atlasVersion": ATLAS_VERSION,
        "tileFactsVersion": TILE_FACTS_VERSION,
    }
    if local_sources != sources:
        raise RuntimeError(
            "world shard source identity mismatch: "
            f"plan={json.dumps(sources, sort_keys=True)} "
            f"local={json.dumps(local_sources, sort_keys=True)}"
        )

    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True, exist_ok=True)
    spool = output / ".spool"
    spool_selected_chunks(map_path, spool, chunk_size, chunk_keys)

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
    actual_keys = _ordered_chunk_keys(
        ChunkKey(int(row["z"]), int(row["chunkX"]), int(row["chunkY"])).text
        for row in chunks
    )
    if actual_keys != chunk_keys:
        raise RuntimeError("rendered world shard coverage differs from its assignment")

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
            "scope": "world-chunk-shard",
            "shardIndex": shard_index,
            "shardCount": shard_count,
            "workers": worker_count,
            "algorithm": plan["algorithm"],
            "worldPlanDigest": plan["worldPlanDigest"],
            "coverageDigest": plan["coverageDigest"],
            "assignmentDigest": assignment["assignmentDigest"],
        },
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (spool / "source.json").write_text(
        json.dumps(sources, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    environment = enrich_environment_animations_resumable(
        asset_dir,
        output,
        workers=worker_count,
    )
    if int(environment.get("completedChunks", -1)) != len(chunks):
        raise RuntimeError("environment exporter did not complete every assigned chunk")

    floor_counts = Counter(int(row["z"]) for row in chunks)
    statistics = {
        "schemaVersion": 1,
        "scope": "world-chunk-shard",
        "shardIndex": shard_index,
        "shardCount": shard_count,
        "chunks": len(chunks),
        "floorCounts": {str(key): int(value) for key, value in sorted(floor_counts.items())},
        "tiles": sum(int(row["tiles"]) for row in chunks),
        "groundItems": sum(int(row["groundItems"]) for row in chunks),
        "childItems": sum(int(row["childItems"]) for row in chunks),
        "renderOperations": sum(int(row["renderOperations"]) for row in chunks),
        "environmentAnimations": environment,
    }
    data_dir = output / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "shard-statistics.json").write_text(
        json.dumps(statistics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "shardIndex": shard_index,
                "shardCount": shard_count,
                "chunks": len(chunks),
                "workers": worker_count,
                "worldPlanDigest": plan["worldPlanDigest"],
                "assignmentDigest": assignment["assignmentDigest"],
                "environmentCompletedChunks": environment["completedChunks"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="plan all canonical chunks into weighted runner shards")
    plan.add_argument("map", type=Path)
    plan.add_argument("assets", type=Path)
    plan.add_argument("output", type=Path)
    plan.add_argument("--shards", type=int, default=WORLD_SHARD_COUNT)
    plan.add_argument("--chunk-size", type=int, default=128)
    plan.add_argument("--repository", type=Path, default=Path("."))

    build = subparsers.add_parser("build", help="build exactly one planned world chunk shard")
    build.add_argument("map", type=Path)
    build.add_argument("assets", type=Path)
    build.add_argument("plan", type=Path)
    build.add_argument("output", type=Path)
    build.add_argument("--shard", type=int, required=True)
    build.add_argument("--workers", type=int, default=WORLD_WORKER_CAP)
    build.add_argument("--repository", type=Path, default=Path("."))
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "plan":
        write_canonical_world_plan(
            args.map,
            args.assets,
            args.output,
            shard_count=args.shards,
            repository_root=args.repository,
            chunk_size=args.chunk_size,
        )
        return 0
    build_world_shard(
        args.map,
        args.assets,
        args.plan,
        args.output,
        shard_index=args.shard,
        workers=args.workers,
        repository_root=args.repository,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
