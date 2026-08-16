"""Deterministic in-job sharding for incremental Atlas chunk rendering.

The spatial spool and dependency plan are produced once. This module only divides
already-dirty chunks into balanced render shards and executes those shards in
parallel processes on the same trusted runner/filesystem. Generated imagery is
never transported between GitHub jobs or uploaded as an artifact by this module.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
from typing import Iterable, Mapping

from .incremental_core import ChunkKey, chunk_sort_key, render_selected_chunks, write_json_atomic

SHARD_PLAN_VERSION = 1


@dataclass(frozen=True)
class RenderShard:
    index: int
    chunks: tuple[str, ...]
    spool_bytes: int

    def as_dict(self) -> dict[str, object]:
        return {
            "index": self.index,
            "chunks": list(self.chunks),
            "chunkCount": len(self.chunks),
            "spoolBytes": self.spool_bytes,
        }


def _ordered_chunks(values: Iterable[str]) -> list[str]:
    return sorted(set(values), key=lambda value: chunk_sort_key(ChunkKey.parse(value)))


def build_shard_plan(spool_dir: Path, chunk_keys: Iterable[str], shard_count: int) -> dict[str, object]:
    """Partition chunks with deterministic largest-processing-time balancing.

    Exact spool bytes are a stable, cheap proxy for render work. Ties are broken
    by canonical chunk order and shard index, so repeated planning is identical.
    """
    if shard_count <= 0:
        raise ValueError("shard count must be positive")
    chunks = _ordered_chunks(chunk_keys)
    if not chunks:
        return {"schemaVersion": SHARD_PLAN_VERSION, "requestedShards": shard_count, "shards": [], "chunks": 0, "spoolBytes": 0}

    weighted: list[tuple[str, int]] = []
    for text in chunks:
        path = ChunkKey.parse(text).spool_path(spool_dir)
        if not path.is_file():
            raise FileNotFoundError(path)
        weighted.append((text, path.stat().st_size))

    actual_count = min(shard_count, len(weighted))
    assignments: list[list[str]] = [[] for _ in range(actual_count)]
    totals = [0] * actual_count
    weighted.sort(key=lambda item: (-item[1], chunk_sort_key(ChunkKey.parse(item[0]))))
    for text, size in weighted:
        target = min(range(actual_count), key=lambda index: (totals[index], index))
        assignments[target].append(text)
        totals[target] += size

    shards = [
        RenderShard(index, tuple(_ordered_chunks(assignments[index])), totals[index])
        for index in range(actual_count)
    ]
    return {
        "schemaVersion": SHARD_PLAN_VERSION,
        "requestedShards": shard_count,
        "shards": [shard.as_dict() for shard in shards],
        "chunks": len(chunks),
        "spoolBytes": sum(totals),
        "maxShardBytes": max(totals),
        "minShardBytes": min(totals),
    }


def _render_shard(
    spool_dir: str,
    asset_dir: str,
    output: str,
    chunks: tuple[str, ...],
    dependency_index_path: str,
    asset_state_path: str,
    render_digest: str,
) -> dict[str, object]:
    dependencies = json.loads(Path(dependency_index_path).read_text(encoding="utf-8"))
    assets = json.loads(Path(asset_state_path).read_text(encoding="utf-8"))
    return render_selected_chunks(
        Path(spool_dir),
        Path(asset_dir),
        Path(output),
        chunks,
        dependencies,
        assets,
        render_digest,
        include_overviews=True,
    )


def _merge_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if source.read_bytes() != target.read_bytes():
            raise RuntimeError(f"non-identical incremental shard collision: {target}")
        source.unlink()
        return
    os.replace(source, target)


def _merge_shard_output(source: Path, target: Path) -> None:
    for path in sorted(candidate for candidate in source.rglob("*") if candidate.is_file()):
        relative = path.relative_to(source)
        if relative.as_posix() == "incremental-render.json":
            continue
        _merge_file(path, target / relative)


def render_selected_chunks_sharded(
    spool_dir: Path,
    asset_dir: Path,
    output: Path,
    chunk_keys: Iterable[str],
    dependency_index: Mapping[str, object],
    asset_state: Mapping[str, object],
    render_digest: str,
    *,
    workers: int,
    shards: int,
) -> dict[str, object]:
    """Render dirty chunks in balanced process shards after one preprocessing pass."""
    if workers <= 0:
        raise ValueError("worker count must be positive")
    if shards <= 0:
        raise ValueError("shard count must be positive")

    output.mkdir(parents=True, exist_ok=True)
    final_manifest = output / "incremental-render.json"
    shard_plan_path = output / "incremental-shard-plan.json"
    final_manifest.unlink(missing_ok=True)
    shard_plan_path.unlink(missing_ok=True)

    chunks = _ordered_chunks(chunk_keys)
    plan = build_shard_plan(spool_dir, chunks, shards)
    write_json_atomic(shard_plan_path, plan)
    if not chunks:
        manifest = {"schemaVersion": 1, "chunks": []}
        write_json_atomic(final_manifest, manifest)
        return manifest

    scratch = output / ".shards"
    shutil.rmtree(scratch, ignore_errors=True)
    scratch.mkdir(parents=True, exist_ok=True)
    dependency_path = scratch / "dependency-index.json"
    asset_path = scratch / "asset-state.json"
    write_json_atomic(dependency_path, dependency_index)
    write_json_atomic(asset_path, asset_state)

    shard_records = plan["shards"]
    if not isinstance(shard_records, list):
        raise ValueError("invalid shard plan")
    process_count = min(workers, len(shard_records))
    results: list[dict[str, object]] = []
    try:
        with ProcessPoolExecutor(max_workers=process_count) as pool:
            futures = []
            for record in shard_records:
                if not isinstance(record, Mapping):
                    raise ValueError("invalid shard record")
                index = int(record["index"])
                shard_chunks = tuple(str(value) for value in record["chunks"])
                shard_output = scratch / f"render-{index:04d}"
                futures.append(
                    (
                        index,
                        shard_output,
                        pool.submit(
                            _render_shard,
                            str(spool_dir),
                            str(asset_dir),
                            str(shard_output),
                            shard_chunks,
                            str(dependency_path),
                            str(asset_path),
                            render_digest,
                        ),
                    )
                )
            for index, shard_output, future in futures:
                result = future.result()
                results.append({"index": index, "output": shard_output, "manifest": result})

        combined: list[dict[str, object]] = []
        for result in sorted(results, key=lambda value: int(value["index"])):
            shard_output = result["output"]
            if not isinstance(shard_output, Path):
                raise TypeError("invalid shard output")
            manifest = result["manifest"]
            if not isinstance(manifest, Mapping) or not isinstance(manifest.get("chunks"), list):
                raise ValueError("invalid shard render manifest")
            combined.extend(dict(row) for row in manifest["chunks"] if isinstance(row, Mapping))
            _merge_shard_output(shard_output, output)

        combined.sort(key=lambda row: chunk_sort_key(ChunkKey.parse(str(row["chunk"]))))
        actual = [str(row["chunk"]) for row in combined]
        if actual != chunks:
            raise RuntimeError(f"sharded render coverage mismatch: expected={chunks}, actual={actual}")
        manifest = {
            "schemaVersion": 1,
            "chunks": combined,
            "sharding": {
                "workers": process_count,
                "requestedWorkers": workers,
                "requestedShards": shards,
                "executedShards": len(shard_records),
            },
        }
        write_json_atomic(final_manifest, manifest)
        return manifest
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
