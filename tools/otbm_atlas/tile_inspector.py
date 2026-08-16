"""Write viewport-bounded factual OTBM tile-inspector shards.

The inspector exposes raw OTBM positions, ground server IDs, visible top-level
stack server IDs and only ActionID/UniqueID attributes that can be associated
unambiguously with the exact canonical OTBM item. It never derives identity
from rendered pixels.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any

from .environment_spool import decode_spool_tiles
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
            identity = (
                int(position["x"]),
                int(position["y"]),
                int(position["z"]),
                int(entry["serverId"]),
            )
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

    # The stable spool preserves item hierarchy and server IDs, while AID/UID
    # facts are stored separately by position + serverId. Associate an
    # attribute only when exactly one occurrence of that serverId exists in the
    # complete tile hierarchy and the canonical fact value is unique. Otherwise
    # omit it rather than guessing which stack/container item owns it.
    if counts[server_id] == 1:
        aids = action_ids.get(identity, set())
        uids = unique_ids.get(identity, set())
        if len(aids) == 1:
            record["actionId"] = next(iter(aids))
            resolved += 1
        elif len(aids) > 1:
            ambiguous += 1
        if len(uids) == 1:
            record["uniqueId"] = next(iter(uids))
            resolved += 1
        elif len(uids) > 1:
            ambiguous += 1
    else:
        ambiguous += int(bool(action_ids.get(identity))) + int(bool(unique_ids.get(identity)))
    return record, resolved, ambiguous


def tile_record(
    tile: Tile,
    action_ids: dict[tuple[int, int, int, int], set[int]] | None = None,
    unique_ids: dict[tuple[int, int, int, int], set[int]] | None = None,
) -> tuple[dict[str, Any], int, int]:
    action_ids = action_ids or {}
    unique_ids = unique_ids or {}
    counts = _all_item_counts(tile)
    resolved = ambiguous = 0

    ground: dict[str, int] | None = None
    if tile.ground is not None:
        ground, value_resolved, value_ambiguous = _item_record(tile.ground, tile, counts, action_ids, unique_ids)
        resolved += value_resolved
        ambiguous += value_ambiguous

    items: list[dict[str, int]] = []
    for item in tile.items:
        value, value_resolved, value_ambiguous = _item_record(item, tile, counts, action_ids, unique_ids)
        items.append(value)
        resolved += value_resolved
        ambiguous += value_ambiguous

    record: dict[str, Any] = {
        "x": int(tile.position.x),
        "y": int(tile.position.y),
        "z": int(tile.position.z),
        "ground": ground,
        "items": items,
    }
    return record, resolved, ambiguous


def write_tile_inspector_data(output: Path) -> dict[str, int]:
    spool = output / ".spool"
    root = output / "data" / "tile-inspector"
    root.mkdir(parents=True, exist_ok=True)
    facts_path = spool / "facts.json"
    facts = json.loads(facts_path.read_text(encoding="utf-8")) if facts_path.is_file() else {}
    action_ids = _fact_index(facts, "actionIds", "actionId")
    unique_ids = _fact_index(facts, "uniqueIds", "uniqueId")

    shards = tiles = stack_items = bytes_written = attributes_resolved = attributes_ambiguous = 0
    seen_paths: set[str] = set()

    for spool_path in sorted(
        spool.glob("z*/*.bin"),
        key=lambda path: (
            int(path.parent.name[1:]),
            int(path.stem.split("_")[1]),
            int(path.stem.split("_")[0]),
        ),
    ):
        z = int(spool_path.parent.name[1:])
        chunk_x, chunk_y = map(int, spool_path.stem.split("_"))
        records: list[dict[str, Any]] = []
        for tile in decode_spool_tiles(spool_path):
            record, resolved, ambiguous = tile_record(tile, action_ids, unique_ids)
            records.append(record)
            attributes_resolved += resolved
            attributes_ambiguous += ambiguous
        if not records:
            continue
        relative = f"data/tile-inspector/z{z}/{chunk_x}_{chunk_y}.json"
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {"schemaVersion": SCHEMA_VERSION, "records": records},
            separators=(",", ":"),
            sort_keys=True,
        ) + "\n"
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(payload, encoding="utf-8")
        temporary.replace(path)
        seen_paths.add(relative)
        shards += 1
        tiles += len(records)
        stack_items += sum(len(record["items"]) for record in records)
        bytes_written += len(payload.encode("utf-8"))

    for path in root.glob("z*/*.json"):
        relative = path.relative_to(output).as_posix()
        if relative not in seen_paths:
            path.unlink()

    statistics = {
        "shards": shards,
        "tiles": tiles,
        "topLevelStackItems": stack_items,
        "attributesResolved": attributes_resolved,
        "attributesAmbiguousOmitted": attributes_ambiguous,
        "bytes": bytes_written,
    }
    index = {
        "schemaVersion": SCHEMA_VERSION,
        "chunkSize": 128,
        "statistics": statistics,
        "policy": {
            "identity": "raw OTBM server IDs only; never inferred from rendered pixels",
            "scope": "ground plus visible top-level stack items at the exact X/Y/Z position",
            "attributes": "ActionID/UniqueID from canonical OTBM facts only when position+serverId ownership is unambiguous; ambiguous attributes are omitted",
            "loading": "viewport chunk bounded; no full-world browser preload",
        },
    }
    (root / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return statistics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("atlas", type=Path, help="generated Atlas root containing .spool")
    args = parser.parse_args()
    statistics = write_tile_inspector_data(args.atlas)
    print(json.dumps(statistics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
