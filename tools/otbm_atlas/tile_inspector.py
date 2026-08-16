"""Write viewport-bounded factual OTBM tile-inspector shards.

The inspector exposes raw OTBM positions, ground server IDs, visible top-level
stack server IDs and only ActionID/UniqueID attributes present on the exact
canonical OTBM item. It never derives identity from rendered pixels.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any

from .incremental_core import write_bytes_atomic
from .semantic import Item, Tile, walk_items

SCHEMA_VERSION = 1


def _fact_index(facts: dict[str, Any], key: str, value_key: str) -> dict[tuple[int, int, int, int], set[int]]:
    index: dict[tuple[int, int, int, int], set[int]] = defaultdict(set)
    for entry in facts.get(key, []):
        if not isinstance(entry, dict) or value_key not in entry or "serverId" not in entry:
            continue
        position = entry.get("position")
        if not isinstance(position, dict):
            continue
        try:
            identity = (int(position["x"]), int(position["y"]), int(position["z"]), int(entry["serverId"]))
            index[identity].add(int(entry[value_key]))
        except (KeyError, TypeError, ValueError):
            continue
    return index


def _all_item_counts(tile: Tile) -> Counter[int]:
    items = (() if tile.ground is None else (tile.ground,)) + tuple(walk_items(tile.items))
    return Counter(int(item.server_id) for item in items)


def _item_record(
    item: Item,
    tile: Tile,
    counts: Counter[int],
    action_ids: dict[tuple[int, int, int, int], set[int]],
    unique_ids: dict[tuple[int, int, int, int], set[int]],
) -> tuple[dict[str, int], int, int]:
    server_id = int(item.server_id)
    record = {"serverId": server_id}
    position = tile.position
    identity = (int(position.x), int(position.y), int(position.z), server_id)
    resolved = ambiguous = 0
    if counts[server_id] == 1:
        aids = action_ids.get(identity, set())
        uids = unique_ids.get(identity, set())
        if len(aids) == 1:
            record["actionId"] = next(iter(aids)); resolved += 1
        elif len(aids) > 1: ambiguous += 1
        if len(uids) == 1:
            record["uniqueId"] = next(iter(uids)); resolved += 1
        elif len(uids) > 1: ambiguous += 1
    else:
        ambiguous += int(bool(action_ids.get(identity))) + int(bool(unique_ids.get(identity)))
    return record, resolved, ambiguous


def tile_record(
    tile: Tile,
    action_ids: dict[tuple[int, int, int, int], set[int]] | None = None,
    unique_ids: dict[tuple[int, int, int, int], set[int]] | None = None,
) -> tuple[dict[str, Any], int, int]:
    action_ids = action_ids or {}; unique_ids = unique_ids or {}
    counts = _all_item_counts(tile); resolved = ambiguous = 0
    ground: dict[str, int] | None = None
    if tile.ground is not None:
        ground, value_resolved, value_ambiguous = _item_record(tile.ground, tile, counts, action_ids, unique_ids)
        resolved += value_resolved; ambiguous += value_ambiguous
    items: list[dict[str, int]] = []
    for item in tile.items:
        value, value_resolved, value_ambiguous = _item_record(item, tile, counts, action_ids, unique_ids)
        items.append(value); resolved += value_resolved; ambiguous += value_ambiguous
    return {
        "x": int(tile.position.x), "y": int(tile.position.y), "z": int(tile.position.z),
        "ground": ground, "items": items,
    }, resolved, ambiguous


def _validate_exact_record(record: Any, *, z: int, chunk_x: int, chunk_y: int, chunk_size: int) -> dict[str, Any]:
    if not isinstance(record, dict): raise ValueError("tile-inspector sidecar record must be an object")
    try: x, y, record_z = int(record["x"]), int(record["y"]), int(record["z"])
    except (KeyError, TypeError, ValueError) as exc: raise ValueError("tile-inspector sidecar has invalid coordinates") from exc
    if record_z != z or x // chunk_size != chunk_x or y // chunk_size != chunk_y:
        raise ValueError(f"tile-inspector sidecar escaped chunk z{z}/{chunk_x}_{chunk_y}: {(x, y, record_z)}")
    ground = record.get("ground")
    if ground is not None and (not isinstance(ground, dict) or "serverId" not in ground):
        raise ValueError("tile-inspector sidecar ground must be null or an item object")
    items = record.get("items")
    if not isinstance(items, list) or any(not isinstance(item, dict) or "serverId" not in item for item in items):
        raise ValueError("tile-inspector sidecar items must be item objects")
    return record


def _attribute_count(record: dict[str, Any]) -> int:
    items = ([] if record.get("ground") is None else [record["ground"]]) + list(record["items"])
    return sum(int("actionId" in item) + int("uniqueId" in item) for item in items)


def _sidecar_sort_key(path: Path) -> tuple[int, int, int]:
    return int(path.parent.name[1:]), int(path.stem.split("_")[1]), int(path.stem.split("_")[0])


def _target_relative(sidecar_relative: str) -> str:
    path = Path(sidecar_relative)
    return (Path("data/tile-inspector") / path.parent / f"{path.stem}.json").as_posix()


def _write_shard(source: Path, output: Path, chunk_size: int) -> tuple[str | None, dict[str, int]]:
    z = int(source.parent.name[1:]); chunk_x, chunk_y = map(int, source.stem.split("_"))
    records = [
        _validate_exact_record(json.loads(line), z=z, chunk_x=chunk_x, chunk_y=chunk_y, chunk_size=chunk_size)
        for line in source.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    records.sort(key=lambda record: (int(record["y"]), int(record["x"])))
    relative = f"data/tile-inspector/z{z}/{chunk_x}_{chunk_y}.json"
    path = output / relative
    if not records:
        if path.exists(): path.unlink()
        return None, {"tiles": 0, "topLevelStackItems": 0, "attributesResolved": 0, "bytes": 0}
    payload = (json.dumps({"schemaVersion": SCHEMA_VERSION, "records": records}, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")
    if not path.is_file() or path.read_bytes() != payload:
        write_bytes_atomic(path, payload)
    return relative, {
        "tiles": len(records),
        "topLevelStackItems": sum(len(record["items"]) for record in records),
        "attributesResolved": sum(_attribute_count(record) for record in records),
        "bytes": len(payload),
    }


def _aggregate(shards: dict[str, dict[str, int]]) -> dict[str, int]:
    return {
        "shards": len(shards),
        "tiles": sum(value["tiles"] for value in shards.values()),
        "topLevelStackItems": sum(value["topLevelStackItems"] for value in shards.values()),
        "attributesResolved": sum(value["attributesResolved"] for value in shards.values()),
        "attributesAmbiguousOmitted": 0,
        "bytes": sum(value["bytes"] for value in shards.values()),
    }


def write_tile_inspector_data(
    output: Path,
    *,
    changed_sidecars: list[str] | None = None,
    deleted_sidecars: list[str] | None = None,
) -> dict[str, int]:
    spool = output / ".spool"; sidecars = spool / "tile-facts"; root = output / "data" / "tile-inspector"
    root.mkdir(parents=True, exist_ok=True)
    metadata_path = spool / "spool.json"
    if not metadata_path.is_file(): raise FileNotFoundError(metadata_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")); chunk_size = int(metadata.get("chunkSize", 0))
    if chunk_size <= 0: raise ValueError("Atlas spool has invalid chunkSize")
    if not sidecars.is_dir(): raise RuntimeError("exact tile-inspector sidecars are missing; rebuild the Atlas spool before publishing the inspector")

    index_path = root / "index.json"
    prior: dict[str, Any] = {}
    if index_path.is_file():
        try: prior = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): prior = {}
    prior_shards = prior.get("shardStatistics")
    incremental = (changed_sidecars is not None or deleted_sidecars is not None) and isinstance(prior_shards, dict)

    if incremental:
        shard_statistics: dict[str, dict[str, int]] = {
            str(key): {name: int(value[name]) for name in ("tiles", "topLevelStackItems", "attributesResolved", "bytes")}
            for key, value in prior_shards.items() if isinstance(value, dict) and all(name in value for name in ("tiles", "topLevelStackItems", "attributesResolved", "bytes"))
        }
        for relative in deleted_sidecars or []:
            target = _target_relative(relative); shard_statistics.pop(target, None)
            path = output / target
            if path.exists(): path.unlink()
        for relative in changed_sidecars or []:
            source = sidecars / relative
            target = _target_relative(relative); shard_statistics.pop(target, None)
            if not source.is_file():
                path = output / target
                if path.exists(): path.unlink()
                continue
            written, stats = _write_shard(source, output, chunk_size)
            if written is not None: shard_statistics[written] = stats
    else:
        shard_statistics = {}
        seen: set[str] = set()
        for source in sorted(sidecars.glob("z*/*.jsonl"), key=_sidecar_sort_key):
            written, stats = _write_shard(source, output, chunk_size)
            if written is not None:
                shard_statistics[written] = stats; seen.add(written)
        for path in root.glob("z*/*.json"):
            relative = path.relative_to(output).as_posix()
            if relative not in seen: path.unlink()

    statistics = _aggregate(shard_statistics)
    index = {
        "schemaVersion": SCHEMA_VERSION,
        "chunkSize": chunk_size,
        "statistics": statistics,
        "shardStatistics": dict(sorted(shard_statistics.items())),
        "policy": {
            "identity": "raw OTBM server IDs only; never inferred from rendered pixels",
            "scope": "ground plus visible top-level stack items at the exact X/Y/Z position",
            "attributes": "direct canonical OTBM item ActionID/UniqueID only; ambiguous attributes are omitted rather than inferred",
            "loading": "viewport chunk bounded; no full-world browser preload",
        },
    }
    payload = (json.dumps(index, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if not index_path.is_file() or index_path.read_bytes() != payload:
        write_bytes_atomic(index_path, payload)
    return statistics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("atlas", type=Path, help="generated Atlas root containing .spool/tile-facts")
    args = parser.parse_args(); statistics = write_tile_inspector_data(args.atlas)
    print(json.dumps(statistics, indent=2, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
