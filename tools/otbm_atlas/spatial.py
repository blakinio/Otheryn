"""Build bounded viewport overlay shards and a compact factual search index."""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

from .incremental_core import write_bytes_atomic

POSITION_KEYS = {"towns": "temple", "houses": "entry"}
SUPPLEMENTAL_SPAWN_KINDS = {
    "monsterSpawns": "supplementalMonsterSpawns",
    "npcSpawns": "supplementalNpcSpawns",
}


def _position(kind: str, record: dict) -> dict | None:
    return record.get(POSITION_KEYS.get(kind, "position"))


def _viewer_kind(kind: str, record: dict) -> str:
    if kind in SUPPLEMENTAL_SPAWN_KINDS and record.get("origin") != "base-map":
        return SUPPLEMENTAL_SPAWN_KINDS[kind]
    return kind


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")


def _write_if_changed(path: Path, payload: bytes) -> bool:
    if path.is_file() and path.read_bytes() == payload:
        return False
    write_bytes_atomic(path, payload)
    return True


def write_spatial_data(output: Path, chunk_size: int, groups: dict[str, list[dict]]) -> dict[str, int | bool]:
    """Write only changed spatial shards and remove only stale spatial shards.

    The caller supplies the complete desired logical dataset. Identical shard bytes
    retain their inode/mtime, a local record change rewrites only its owning chunk,
    and removed records delete only chunks that no longer have any content.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    shards: dict[tuple[int, int, int], dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    search: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for kind, records in groups.items():
        for record in records:
            position = _position(kind, record)
            if not position:
                continue
            viewer_kind = _viewer_kind(kind, record)
            key = (
                int(position["z"]),
                int(position["x"]) // chunk_size,
                int(position["y"]) // chunk_size,
            )
            shards[key][viewer_kind].append({**record, "kind": viewer_kind})
            label = record.get("name") or record.get("actionId") or record.get("uniqueId") or record.get("houseId")
            if label is not None:
                search_key = (viewer_kind, str(label).casefold())
                if search_key not in seen:
                    seen.add(search_key)
                    search.append({"kind": viewer_kind, "label": str(label), "position": position})

    root = output / "data" / "chunks"
    desired_paths: set[Path] = set()
    changed = reused = 0
    for (z, x, y), content in sorted(shards.items(), key=lambda value: (value[0][0], value[0][2], value[0][1])):
        path = root / f"z{z}" / f"{x}_{y}.json"
        desired_paths.add(path)
        payload = _json_bytes({"schemaVersion": 1, **content})
        if _write_if_changed(path, payload):
            changed += 1
        else:
            reused += 1

    deleted = 0
    if root.exists():
        for path in sorted(candidate for candidate in root.glob("z*/*.json") if candidate.is_file()):
            if path not in desired_paths:
                path.unlink()
                deleted += 1
        for directory in sorted((candidate for candidate in root.glob("z*") if candidate.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass

    search_payload = _json_bytes(
        {
            "schemaVersion": 1,
            "records": sorted(search, key=lambda value: (value["label"].casefold(), value["kind"])),
        }
    )
    search_index_changed = _write_if_changed(output / "data" / "search-index.json", search_payload)

    return {
        "chunks": len(shards),
        "shards": len(shards),
        "searchRecords": len(search),
        "changedChunks": changed,
        "reusedChunks": reused,
        "deletedChunks": deleted,
        "searchIndexChanged": search_index_changed,
    }
