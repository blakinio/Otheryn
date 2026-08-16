"""Deterministic spatial invalidation primitives for the OTBM Atlas.

The canonical Game -> Atlas contract remains snapshot based. This module is an
Atlas-side build cache: it turns a monolithic source snapshot into stable spatial
chunks, tracks only the render dependencies of each chunk and publishes changed
objects without making a whole-file source hash part of every chunk fingerprint.
"""
from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
from typing import BinaryIO

from .assets import Appearance, SpriteSheet, load_object_appearances, load_sprite_catalog
from .overview import LOW_OVERVIEW_FACTOR, OVERVIEW_FACTOR, OVERVIEW_VERSION, make_overview
from .render import AssetRenderer, _item_patterns, render_tiles
from .semantic import Item, Position, Tile, iter_map_records

STATE_VERSION = 1
DEPENDENCY_INDEX_VERSION = 1
SPOOL_VERSION = 1
PUBLICATION_MANIFEST_VERSION = 1
RENDER_CORE_VERSION = 1
TILE_PIXELS = 32


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def write_bytes_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def write_json_atomic(path: Path, value: object) -> None:
    write_bytes_atomic(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"))


class ChunkKey(tuple):
    __slots__ = ()

    def __new__(cls, z: int, x: int, y: int) -> "ChunkKey":
        return tuple.__new__(cls, (int(z), int(x), int(y)))

    @property
    def z(self) -> int:
        return int(self[0])

    @property
    def x(self) -> int:
        return int(self[1])

    @property
    def y(self) -> int:
        return int(self[2])

    @property
    def text(self) -> str:
        return f"z{self.z}/{self.x}_{self.y}"

    @classmethod
    def parse(cls, value: str) -> "ChunkKey":
        floor, name = value.split("/", 1)
        if not floor.startswith("z"):
            raise ValueError(f"invalid chunk key {value!r}")
        x_text, y_text = name.split("_", 1)
        return cls(int(floor[1:]), int(x_text), int(y_text))

    @classmethod
    def from_spool_path(cls, path: Path) -> "ChunkKey":
        x_text, y_text = path.stem.split("_", 1)
        return cls(int(path.parent.name[1:]), int(x_text), int(y_text))

    def spool_path(self, root: Path) -> Path:
        return root / f"z{self.z}" / f"{self.x}_{self.y}.bin"


def chunk_sort_key(key: ChunkKey) -> tuple[int, int, int]:
    return key.z, key.y, key.x


def _encode_item(item: Item) -> bytes:
    subtype = 0xFFFF if item.subtype is None else int(item.subtype)
    children = b"".join(_encode_item(child) for child in item.children)
    return struct.pack("<HHH", int(item.server_id), subtype, len(item.children)) + children


def _decode_item(handle: BinaryIO) -> Item:
    payload = handle.read(6)
    if len(payload) != 6:
        raise ValueError("truncated incremental spool item")
    server_id, subtype, child_count = struct.unpack("<HHH", payload)
    children = tuple(_decode_item(handle) for _ in range(child_count))
    return Item(server_id, None if subtype == 0xFFFF else subtype, children=children)


def encode_tile(tile: Tile) -> bytes:
    house_id = 0xFFFFFFFF if tile.house_id is None else int(tile.house_id)
    items = (() if tile.ground is None else (tile.ground,)) + tile.items
    payload = struct.pack(
        "<HHBIIHH",
        tile.position.x,
        tile.position.y,
        tile.position.z,
        house_id,
        tile.flags,
        len(tile.zones),
        len(items),
    )
    payload += b"".join(struct.pack("<H", zone) for zone in tile.zones)
    payload += b"".join(_encode_item(item) for item in items)
    return struct.pack("<I", len(payload)) + payload


def decode_tiles(path: Path) -> Iterator[Tile]:
    with path.open("rb") as handle:
        while size_data := handle.read(4):
            if len(size_data) != 4:
                raise ValueError("truncated incremental spool record size")
            size = struct.unpack("<I", size_data)[0]
            payload = handle.read(size)
            if len(payload) != size:
                raise ValueError("truncated incremental spool record")
            from io import BytesIO

            record = BytesIO(payload)
            header = record.read(17)
            if len(header) != 17:
                raise ValueError("truncated incremental spool tile header")
            x, y, z, house_id, flags, zone_count, item_count = struct.unpack("<HHBIIHH", header)
            zones = tuple(struct.unpack("<H", record.read(2))[0] for _ in range(zone_count))
            items = tuple(_decode_item(record) for _ in range(item_count))
            if record.read(1):
                raise ValueError("unconsumed incremental spool payload")
            yield Tile(
                Position(x, y, z),
                None if house_id == 0xFFFFFFFF else house_id,
                flags,
                items[0] if items else None,
                items[1:] if items else (),
                zones,
            )


class _WriterPool:
    def __init__(self, directory: Path, limit: int = 64) -> None:
        self.directory = directory
        self.limit = limit
        self.handles: OrderedDict[ChunkKey, BinaryIO] = OrderedDict()

    def write(self, key: ChunkKey, payload: bytes) -> None:
        handle = self.handles.pop(key, None)
        if handle is None:
            path = key.spool_path(self.directory)
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


def iter_spool_files(root: Path) -> Iterator[tuple[ChunkKey, Path]]:
    paths = sorted(
        root.glob("z*/*.bin"),
        key=lambda value: chunk_sort_key(ChunkKey.from_spool_path(value)),
    )
    for path in paths:
        yield ChunkKey.from_spool_path(path), path


def spool_map(map_path: Path, output: Path, chunk_size: int) -> dict[str, object]:
    """Parse once and produce deterministic spatial render-source chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk size must be positive")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    pool = _WriterPool(output)
    tiles = 0
    try:
        for record in iter_map_records(map_path, strict=True):
            if not isinstance(record, Tile):
                continue
            key = ChunkKey(record.position.z, record.position.x // chunk_size, record.position.y // chunk_size)
            pool.write(key, encode_tile(record))
            tiles += 1
    finally:
        pool.close()
    metadata = {
        "schemaVersion": SPOOL_VERSION,
        "chunkSize": chunk_size,
        "tiles": tiles,
        "sourceSha256": sha256_file(map_path),
    }
    write_json_atomic(output / "spool.json", metadata)
    return metadata


def spool_hashes(root: Path) -> dict[str, str]:
    return {key.text: sha256_file(path) for key, path in iter_spool_files(root)}


def reconcile_spool(candidate: Path, stable: Path) -> dict[str, object]:
    """Promote only changed chunk bytes from a freshly parsed candidate spool."""
    candidate_meta = json.loads((candidate / "spool.json").read_text(encoding="utf-8"))
    old_meta = None
    if (stable / "spool.json").is_file():
        old_meta = json.loads((stable / "spool.json").read_text(encoding="utf-8"))
    if old_meta and int(old_meta.get("chunkSize", -1)) != int(candidate_meta["chunkSize"]):
        raise ValueError("chunk size changed; stable spool requires an explicit clean rebuild")

    old = spool_hashes(stable) if stable.exists() else {}
    new = spool_hashes(candidate)
    changed = sorted((key for key in new if old.get(key) != new[key]), key=lambda text: chunk_sort_key(ChunkKey.parse(text)))
    reused = sorted((key for key in new if old.get(key) == new[key]), key=lambda text: chunk_sort_key(ChunkKey.parse(text)))
    deleted = sorted((key for key in old if key not in new), key=lambda text: chunk_sort_key(ChunkKey.parse(text)))

    for text in changed:
        key = ChunkKey.parse(text)
        write_bytes_atomic(key.spool_path(stable), key.spool_path(candidate).read_bytes())
    for text in deleted:
        path = ChunkKey.parse(text).spool_path(stable)
        if path.exists():
            path.unlink()
    write_json_atomic(stable / "spool.json", candidate_meta)
    return {"changed": changed, "reused": reused, "deleted": deleted}


def _dependency_ids_for_tile(tile: Tile, appearances: Mapping[int, Appearance]) -> tuple[set[int], set[int]]:
    items = (() if tile.ground is None else (tile.ground,)) + tile.items
    hook_south = False
    hook_east = False
    for item in items:
        appearance = appearances.get(item.server_id)
        if appearance is not None:
            hook_south = hook_south or appearance.hook_direction == 1
            hook_east = hook_east or appearance.hook_direction == 2

    appearance_ids: set[int] = set()
    sprite_ids: set[int] = set()
    for item in items:
        appearance_ids.add(int(item.server_id))
        appearance = appearances.get(item.server_id)
        if appearance is None or not appearance.frames:
            continue
        frame = appearance.frames[0]
        px, py, pz = _item_patterns(
            appearance,
            frame,
            item,
            tile.position.x,
            tile.position.y,
            tile.position.z,
            hook_south,
            hook_east,
        )
        phase = frame.default_start_phase % frame.animation_phases
        for layer in range(frame.layers):
            index = (((((phase * frame.pattern_depth + pz) * frame.pattern_height + py) * frame.pattern_width + px) * frame.layers) + layer)
            if index < len(frame.sprite_ids):
                sprite_ids.add(int(frame.sprite_ids[index]))
    return appearance_ids, sprite_ids


def build_dependency_index(spool_dir: Path, asset_dir: Path) -> dict[str, object]:
    metadata = json.loads((spool_dir / "spool.json").read_text(encoding="utf-8"))
    chunk_size = int(metadata["chunkSize"])
    appearance_path = next(asset_dir.glob("appearances-*.dat"))
    appearances = load_object_appearances(appearance_path)
    chunks: dict[str, dict[str, object]] = {}
    appearance_to_chunks: dict[str, list[str]] = {}
    sprite_to_chunks: dict[str, list[str]] = {}
    for key, path in iter_spool_files(spool_dir):
        appearance_ids: set[int] = set()
        sprite_ids: set[int] = set()
        for tile in decode_tiles(path):
            tile_appearances, tile_sprites = _dependency_ids_for_tile(tile, appearances)
            appearance_ids.update(tile_appearances)
            sprite_ids.update(tile_sprites)
        text = key.text
        chunks[text] = {
            "chunkSize": chunk_size,
            "spoolSha256": sha256_file(path),
            "appearanceIds": sorted(appearance_ids),
            "spriteIds": sorted(sprite_ids),
        }
        for appearance_id in appearance_ids:
            appearance_to_chunks.setdefault(str(appearance_id), []).append(text)
        for sprite_id in sprite_ids:
            sprite_to_chunks.setdefault(str(sprite_id), []).append(text)
    for reverse in (appearance_to_chunks, sprite_to_chunks):
        for values in reverse.values():
            values.sort(key=lambda text: chunk_sort_key(ChunkKey.parse(text)))
    return {
        "schemaVersion": DEPENDENCY_INDEX_VERSION,
        "chunkSize": chunk_size,
        "chunks": chunks,
        "appearanceToChunks": dict(sorted(appearance_to_chunks.items(), key=lambda item: int(item[0]))),
        "spriteToChunks": dict(sorted(sprite_to_chunks.items(), key=lambda item: int(item[0]))),
    }


def _appearance_digest(appearance: Appearance) -> str:
    return sha256_bytes(canonical_json(asdict(appearance)))


def _sheet_record(sheet: SpriteSheet, asset_dir: Path) -> dict[str, object]:
    return {
        "path": sheet.path.relative_to(asset_dir).as_posix(),
        "firstId": int(sheet.first_id),
        "lastId": int(sheet.last_id),
        "layout": int(sheet.layout),
        "sha256": sha256_file(sheet.path),
    }


def collect_asset_state(asset_dir: Path) -> dict[str, object]:
    appearance_path = next(asset_dir.glob("appearances-*.dat"))
    appearances = load_object_appearances(appearance_path)
    sheets = load_sprite_catalog(asset_dir)
    shifts = [appearance.shift or (0, 0) for appearance in appearances.values()]
    gutter_profile = {
        "maxSpriteWidth": max(sheet.sprite_size[0] for sheet in sheets),
        "maxSpriteHeight": max(sheet.sprite_size[1] for sheet in sheets),
        "minShiftX": min(value[0] for value in shifts),
        "maxShiftX": max(value[0] for value in shifts),
        "minShiftY": min(value[1] for value in shifts),
        "maxShiftY": max(value[1] for value in shifts),
    }
    state: dict[str, object] = {
        "schemaVersion": STATE_VERSION,
        "appearanceDigests": {str(key): _appearance_digest(value) for key, value in sorted(appearances.items())},
        "sheets": [_sheet_record(sheet, asset_dir) for sheet in sheets],
        "gutterProfile": gutter_profile,
    }
    state["stateDigest"] = sha256_bytes(canonical_json(state))
    return state


def _sheet_map(state: Mapping[str, object]) -> dict[str, dict[str, object]]:
    records = state.get("sheets", [])
    if not isinstance(records, list):
        return {}
    return {str(record["path"]): dict(record) for record in records if isinstance(record, Mapping)}


def _sheet_for_sprite_state(state: Mapping[str, object], sprite_id: int) -> Mapping[str, object] | None:
    records = state.get("sheets", [])
    if not isinstance(records, list):
        return None
    for record in records:
        if isinstance(record, Mapping) and int(record["firstId"]) <= sprite_id <= int(record["lastId"]):
            return record
    return None


def asset_impact(old_state: Mapping[str, object] | None, new_state: Mapping[str, object], dependency_index: Mapping[str, object]) -> dict[str, object]:
    chunks_value = dependency_index.get("chunks", {})
    all_chunks = {str(key) for key in chunks_value.keys()} if isinstance(chunks_value, Mapping) else set()
    if old_state is None:
        return {"affectedChunks": sorted(all_chunks), "changedAppearanceIds": [], "changedSheetPaths": [], "globalReasons": ["INITIAL_ASSET_STATE"]}

    global_reasons: list[str] = []
    if old_state.get("gutterProfile") != new_state.get("gutterProfile"):
        global_reasons.append("GLOBAL_GUTTER_PROFILE_CHANGED")
    old_appearances = old_state.get("appearanceDigests", {})
    new_appearances = new_state.get("appearanceDigests", {})
    if not isinstance(old_appearances, Mapping) or not isinstance(new_appearances, Mapping):
        global_reasons.append("INVALID_APPEARANCE_STATE")
        changed_appearance_ids: set[str] = set()
    else:
        changed_appearance_ids = {str(key) for key in set(old_appearances) | set(new_appearances) if old_appearances.get(key) != new_appearances.get(key)}
    old_sheets = _sheet_map(old_state)
    new_sheets = _sheet_map(new_state)
    changed_sheet_paths = {path for path in set(old_sheets) | set(new_sheets) if old_sheets.get(path) != new_sheets.get(path)}

    if global_reasons:
        affected = set(all_chunks)
    else:
        affected: set[str] = set()
        reverse_appearances = dependency_index.get("appearanceToChunks", {})
        if isinstance(reverse_appearances, Mapping):
            for appearance_id in changed_appearance_ids:
                values = reverse_appearances.get(appearance_id, [])
                if isinstance(values, list):
                    affected.update(str(value) for value in values)
        ranges: list[tuple[int, int]] = []
        for path in changed_sheet_paths:
            for sheet in (old_sheets.get(path), new_sheets.get(path)):
                if sheet is not None:
                    ranges.append((int(sheet["firstId"]), int(sheet["lastId"])))
        reverse_sprites = dependency_index.get("spriteToChunks", {})
        if isinstance(reverse_sprites, Mapping):
            for sprite_text, values in reverse_sprites.items():
                sprite_id = int(sprite_text)
                if any(first <= sprite_id <= last for first, last in ranges) and isinstance(values, list):
                    affected.update(str(value) for value in values)
    return {
        "affectedChunks": sorted(affected, key=lambda text: chunk_sort_key(ChunkKey.parse(text))),
        "changedAppearanceIds": sorted((int(value) for value in changed_appearance_ids)),
        "changedSheetPaths": sorted(changed_sheet_paths),
        "globalReasons": global_reasons,
    }


def detail_fingerprint(chunk_record: Mapping[str, object], asset_state: Mapping[str, object], render_digest: str) -> str:
    appearance_digests = asset_state.get("appearanceDigests", {})
    if not isinstance(appearance_digests, Mapping):
        raise ValueError("invalid appearance digest state")
    local_appearances = {str(value): appearance_digests.get(str(value), "MISSING") for value in chunk_record.get("appearanceIds", [])}
    local_sheets: dict[str, dict[str, object]] = {}
    for sprite_id in chunk_record.get("spriteIds", []):
        sheet = _sheet_for_sprite_state(asset_state, int(sprite_id))
        if sheet is None:
            local_sheets[f"missing:{sprite_id}"] = {"spriteId": int(sprite_id)}
        else:
            local_sheets[str(sheet["path"])] = {
                "firstId": int(sheet["firstId"]),
                "lastId": int(sheet["lastId"]),
                "layout": int(sheet["layout"]),
                "sha256": str(sheet["sha256"]),
            }
    payload = {
        "chunkSize": int(chunk_record["chunkSize"]),
        "spoolSha256": str(chunk_record["spoolSha256"]),
        "appearanceDigests": local_appearances,
        "spriteSheets": dict(sorted(local_sheets.items())),
        "gutterProfile": asset_state.get("gutterProfile"),
        "renderContractDigest": render_digest,
    }
    return sha256_bytes(canonical_json(payload))


def render_contract_digest(repository_root: Path) -> str:
    """Hash pixel semantics; planner-only edits do not globally invalidate render."""
    paths = [
        repository_root / "tools/otbm_atlas/render.py",
        repository_root / "tools/otbm_atlas/assets.py",
        repository_root / "tools/otbm_atlas/semantic.py",
    ]
    digest = hashlib.sha256()
    digest.update(f"incremental-render-core:{RENDER_CORE_VERSION}\n".encode("utf-8"))
    for path in paths:
        relative = path.relative_to(repository_root).as_posix().encode("utf-8")
        digest.update(struct.pack("<I", len(relative)))
        digest.update(relative)
        digest.update(path.read_bytes())
    return digest.hexdigest()


def overview_contract_digest(repository_root: Path) -> str:
    return sha256_file(repository_root / "tools/otbm_atlas/overview.py")


def chunk_render_bounds(tiles: Sequence[Tile], renderer: AssetRenderer) -> tuple[int, int, int, int, int]:
    if not tiles:
        raise ValueError("cannot render an empty chunk")
    floors = {tile.position.z for tile in tiles}
    if len(floors) != 1:
        raise ValueError("a chunk must contain exactly one floor")
    max_width = max(sheet.sprite_size[0] for sheet in renderer.sheets)
    max_height = max(sheet.sprite_size[1] for sheet in renderer.sheets)
    shifts = [appearance.shift or (0, 0) for appearance in renderer.appearances.values()]
    min_shift_x, max_shift_x = min(v[0] for v in shifts), max(v[0] for v in shifts)
    min_shift_y, max_shift_y = min(v[1] for v in shifts), max(v[1] for v in shifts)
    left = (max_width - TILE_PIXELS + max_shift_x + TILE_PIXELS - 1) // TILE_PIXELS
    top = (max_height - TILE_PIXELS + max_shift_y + TILE_PIXELS - 1) // TILE_PIXELS
    right = max(0, (-min_shift_x + TILE_PIXELS - 1) // TILE_PIXELS)
    bottom = max(0, (-min_shift_y + TILE_PIXELS - 1) // TILE_PIXELS)
    return (
        min(tile.position.x for tile in tiles) - left,
        max(tile.position.x for tile in tiles) + right,
        min(tile.position.y for tile in tiles) - top,
        max(tile.position.y for tile in tiles) + bottom,
        next(iter(floors)),
    )


def render_selected_chunks(spool_dir: Path, asset_dir: Path, output: Path, chunk_keys: Iterable[str], dependency_index: Mapping[str, object], asset_state: Mapping[str, object], render_digest: str, *, include_overviews: bool = True) -> dict[str, object]:
    renderer = AssetRenderer(asset_dir)
    chunk_records = dependency_index.get("chunks", {})
    if not isinstance(chunk_records, Mapping):
        raise ValueError("invalid dependency index")
    rendered: list[dict[str, object]] = []
    for text in sorted(set(chunk_keys), key=lambda value: chunk_sort_key(ChunkKey.parse(value))):
        key = ChunkKey.parse(text)
        record = chunk_records.get(text)
        if not isinstance(record, Mapping):
            raise KeyError(f"chunk {text} is absent from dependency index")
        spool_path = key.spool_path(spool_dir)
        tiles = list(decode_tiles(spool_path))
        png, report = render_tiles(iter(tiles), renderer, chunk_render_bounds(tiles, renderer))
        fingerprint = detail_fingerprint(record, asset_state, render_digest)
        tile_path = output / "tiles" / f"z{key.z}" / f"{key.x}_{key.y}.png"
        write_bytes_atomic(tile_path, png)
        checksum = sha256_bytes(png)
        detail_report = {**report, "fingerprint": fingerprint, "checksum": checksum}
        write_json_atomic(tile_path.with_suffix(".json"), detail_report)
        result: dict[str, object] = {"chunk": text, "z": key.z, "chunkX": key.x, "chunkY": key.y, "path": tile_path.relative_to(output).as_posix(), **detail_report}
        if include_overviews:
            for prefix, directory, factor in (("overview", "overview", OVERVIEW_FACTOR), ("lowOverview", "overview-low", LOW_OVERVIEW_FACTOR)):
                payload = make_overview(png, factor)
                overview_path = output / directory / f"z{key.z}" / f"{key.x}_{key.y}.png"
                write_bytes_atomic(overview_path, payload)
                overview_checksum = sha256_bytes(payload)
                overview_report = {
                    "fingerprint": sha256_bytes(f"{OVERVIEW_VERSION}:{factor}:{checksum}".encode("utf-8")),
                    "checksum": overview_checksum,
                    "imageWidth": int(report["imageWidth"]) // factor,
                    "imageHeight": int(report["imageHeight"]) // factor,
                }
                write_json_atomic(overview_path.with_suffix(".json"), overview_report)
                result[f"{prefix}Path"] = overview_path.relative_to(output).as_posix()
                result[f"{prefix}Checksum"] = overview_checksum
        rendered.append(result)
    manifest = {"schemaVersion": 1, "chunks": rendered}
    write_json_atomic(output / "incremental-render.json", manifest)
    return manifest


def build_content_addressed_manifest(source_root: Path, logical_paths: Iterable[str], object_root: Path) -> dict[str, object]:
    entries: dict[str, dict[str, object]] = {}
    for logical in sorted(set(logical_paths)):
        source = source_root / logical
        if not source.is_file():
            raise FileNotFoundError(source)
        payload = source.read_bytes()
        digest = sha256_bytes(payload)
        object_path = object_root / "sha256" / digest[:2] / digest
        if object_path.exists():
            if sha256_file(object_path) != digest:
                raise ValueError(f"content-address collision/corruption at {object_path}")
        else:
            write_bytes_atomic(object_path, payload)
        entries[logical] = {"sha256": digest, "bytes": len(payload), "object": object_path.relative_to(object_root).as_posix()}
    manifest: dict[str, object] = {"schemaVersion": PUBLICATION_MANIFEST_VERSION, "entries": entries}
    manifest["manifestDigest"] = sha256_bytes(canonical_json(manifest))
    return manifest


def diff_publication_manifests(base: Mapping[str, object] | None, target: Mapping[str, object]) -> dict[str, object]:
    base_entries = base.get("entries", {}) if base else {}
    target_entries = target.get("entries", {})
    if not isinstance(base_entries, Mapping) or not isinstance(target_entries, Mapping):
        raise ValueError("invalid publication manifest")
    changed = sorted(path for path, record in target_entries.items() if base_entries.get(path) != record)
    deleted = sorted(set(base_entries) - set(target_entries))
    unchanged = sorted(path for path, record in target_entries.items() if base_entries.get(path) == record)
    return {
        "schemaVersion": PUBLICATION_MANIFEST_VERSION,
        "baseManifestDigest": None if base is None else base.get("manifestDigest"),
        "targetManifestDigest": target.get("manifestDigest"),
        "changed": changed,
        "deleted": deleted,
        "unchanged": unchanged,
    }
