"""Bounded benchmark for Atlas spatial invalidation sizes.

This command never changes the canonical chunk size. It renders one explicitly
bounded representative region at 32, 64 and 128 map-tile chunk sizes and records
measured chunk count, encoded detail bytes and render time so a future default
change is evidence-based.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import time
from typing import Iterable

from .incremental_core import chunk_render_bounds
from .render import AssetRenderer, render_tiles
from .semantic import Tile, iter_map_records

CANONICAL_MAP = Path("vendor/map-analysis/crystalserver/data-global/world/world.otbm")
CANONICAL_ASSETS = Path("vendor/map-analysis/tibia-client/15.25.bd5a04/assets")


def partition_tiles(tiles: Iterable[Tile], chunk_size: int) -> dict[tuple[int, int, int], list[Tile]]:
    if chunk_size <= 0:
        raise ValueError("chunk size must be positive")
    groups: dict[tuple[int, int, int], list[Tile]] = defaultdict(list)
    for tile in tiles:
        groups[(tile.position.z, tile.position.x // chunk_size, tile.position.y // chunk_size)].append(tile)
    return dict(groups)


def load_region(map_path: Path, bounds: tuple[int, int, int, int, int]) -> list[Tile]:
    x1, x2, y1, y2, z = bounds
    if x1 > x2 or y1 > y2:
        raise ValueError("invalid bounds")
    return [
        record
        for record in iter_map_records(map_path, strict=True)
        if isinstance(record, Tile)
        and record.position.z == z
        and x1 <= record.position.x <= x2
        and y1 <= record.position.y <= y2
    ]


def benchmark(map_path: Path, asset_dir: Path, bounds: tuple[int, int, int, int, int], sizes: Iterable[int]) -> dict[str, object]:
    tiles = load_region(map_path, bounds)
    if not tiles:
        raise ValueError("benchmark region has no populated tiles")
    rows: list[dict[str, object]] = []
    for chunk_size in sizes:
        renderer = AssetRenderer(asset_dir)
        groups = partition_tiles(tiles, chunk_size)
        started = time.perf_counter()
        encoded_bytes = 0
        render_operations = 0
        for key in sorted(groups):
            chunk = groups[key]
            png, report = render_tiles(iter(chunk), renderer, chunk_render_bounds(chunk, renderer))
            encoded_bytes += len(png)
            render_operations += int(report["renderOperations"])
        elapsed = time.perf_counter() - started
        rows.append(
            {
                "chunkSize": chunk_size,
                "chunks": len(groups),
                "populatedTiles": len(tiles),
                "nominalInvalidationAreaTiles": chunk_size * chunk_size,
                "detailBytes": encoded_bytes,
                "renderOperations": render_operations,
                "renderSeconds": elapsed,
            }
        )
    return {"schemaVersion": 1, "bounds": list(bounds), "results": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path("."))
    parser.add_argument("--bounds", nargs=5, type=int, required=True, metavar=("X1", "X2", "Y1", "Y2", "Z"))
    parser.add_argument("--sizes", nargs="+", type=int, default=[32, 64, 128])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = benchmark(args.repository / CANONICAL_MAP, args.repository / CANONICAL_ASSETS, tuple(args.bounds), args.sizes)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
