"""Single-pass, disk-spooled, resumable full-map atlas builder."""

from __future__ import annotations

import argparse
from collections import OrderedDict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import shutil
import struct
from typing import BinaryIO, Iterator

from .render import AssetRenderer, render_tiles
from .mechanics import resolve_mechanics
from .composition import classify_maps
from .houses import parse_houses
from .semantic import Item, Position, Tile, Town, Waypoint, iter_map_records, walk_items
from .spawns import scan_spawns
from .viewer import write_viewer

SPOOL_VERSION = 1
ATLAS_VERSION = 2
_WORKER_RENDERER: AssetRenderer | None = None


def _encode_item(item: Item) -> bytes:
	subtype = 0xFFFF if item.subtype is None else item.subtype
	children = b"".join(_encode_item(child) for child in item.children)
	return struct.pack("<HHH", item.server_id, subtype, len(item.children)) + children


def _decode_item(handle: BinaryIO) -> Item:
	payload = handle.read(6)
	if len(payload) != 6: raise ValueError("truncated spool item")
	server_id, subtype, child_count = struct.unpack("<HHH", payload)
	children = tuple(_decode_item(handle) for _ in range(child_count))
	return Item(server_id, None if subtype == 0xFFFF else subtype, children=children)


def encode_tile(tile: Tile) -> bytes:
	house_id = 0xFFFFFFFF if tile.house_id is None else tile.house_id
	items = (() if tile.ground is None else (tile.ground,)) + tile.items
	payload = struct.pack("<HHBIIHH", tile.position.x, tile.position.y, tile.position.z, house_id, tile.flags, len(tile.zones), len(items))
	payload += b"".join(struct.pack("<H", zone) for zone in tile.zones)
	payload += b"".join(_encode_item(item) for item in items)
	return struct.pack("<I", len(payload)) + payload


def decode_tiles(path: Path) -> Iterator[Tile]:
	with path.open("rb") as handle:
		while size_data := handle.read(4):
			if len(size_data) != 4: raise ValueError("truncated spool record size")
			size = struct.unpack("<I", size_data)[0]
			payload = handle.read(size)
			if len(payload) != size: raise ValueError("truncated spool record")
			from io import BytesIO
			record = BytesIO(payload)
			header = record.read(17)
			if len(header) != 17: raise ValueError("truncated spool tile header")
			x, y, z, house_id, flags, zone_count, item_count = struct.unpack("<HHBIIHH", header)
			zones = []
			for _ in range(zone_count):
				zone_data = record.read(2)
				if len(zone_data) != 2: raise ValueError("truncated spool tile zone")
				zones.append(struct.unpack("<H", zone_data)[0])
			items = tuple(_decode_item(record) for _ in range(item_count))
			if record.read(1): raise ValueError("unconsumed spool payload")
			yield Tile(Position(x, y, z), None if house_id == 0xFFFFFFFF else house_id, flags, items[0] if items else None, items[1:] if items else (), tuple(zones))


class _WriterPool:
	def __init__(self, directory: Path, limit: int = 64) -> None:
		self.directory, self.limit = directory, limit
		self.handles: OrderedDict[tuple[int, int, int], BinaryIO] = OrderedDict()

	def write(self, key: tuple[int, int, int], payload: bytes) -> None:
		handle = self.handles.pop(key, None)
		if handle is None:
			path = self.directory / f"z{key[0]}" / f"{key[1]}_{key[2]}.bin"
			path.parent.mkdir(parents=True, exist_ok=True); handle = path.open("ab")
		self.handles[key] = handle; handle.write(payload)
		if len(self.handles) > self.limit:
			_unused, old = self.handles.popitem(last=False); old.close()

	def close(self) -> None:
		for handle in self.handles.values(): handle.close()
		self.handles.clear()


def _sha256(path: Path) -> str:
	digest = hashlib.sha256()
	with path.open("rb") as handle:
		while block := handle.read(1024 * 1024): digest.update(block)
	return digest.hexdigest()


def _tree_sha256(directory: Path) -> str:
	"""Fingerprint asset names and bytes, independent of filesystem ordering."""
	digest = hashlib.sha256()
	for path in sorted((path for path in directory.rglob("*") if path.is_file()), key=lambda value: value.relative_to(directory).as_posix()):
		relative = path.relative_to(directory).as_posix().encode("utf-8")
		digest.update(struct.pack("<I", len(relative))); digest.update(relative)
		with path.open("rb") as handle:
			while block := handle.read(1024 * 1024): digest.update(block)
	return digest.hexdigest()


def chunk_render_bounds(tiles: list[Tile], renderer: AssetRenderer) -> tuple[int, int, int, int, int]:
	"""Crop empty chunk margins while retaining a conservative sprite gutter."""
	if not tiles: raise ValueError("cannot render an empty chunk")
	floors = {tile.position.z for tile in tiles}
	if len(floors) != 1: raise ValueError("a chunk must contain exactly one floor")
	max_width = max(sheet.sprite_size[0] for sheet in renderer.sheets)
	max_height = max(sheet.sprite_size[1] for sheet in renderer.sheets)
	shifts = [appearance.shift or (0, 0) for appearance in renderer.appearances.values()]
	min_shift_x, max_shift_x = min(value[0] for value in shifts), max(value[0] for value in shifts)
	min_shift_y, max_shift_y = min(value[1] for value in shifts), max(value[1] for value in shifts)
	left = (max_width - 32 + max_shift_x + 31) // 32; top = (max_height - 32 + max_shift_y + 31) // 32
	right = max(0, (-min_shift_x + 31) // 32); bottom = max(0, (-min_shift_y + 31) // 32)
	return (
		min(tile.position.x for tile in tiles) - left, max(tile.position.x for tile in tiles) + right,
		min(tile.position.y for tile in tiles) - top, max(tile.position.y for tile in tiles) + bottom,
		next(iter(floors)),
	)


def _write_rendered_chunk(path: Path, report_path: Path, spool_path: Path, fingerprint: str, renderer: AssetRenderer) -> dict[str, object]:
	tiles = list(decode_tiles(spool_path)); bounds = chunk_render_bounds(tiles, renderer)
	png, report = render_tiles(iter(tiles), renderer, bounds); path.parent.mkdir(parents=True, exist_ok=True)
	temporary_png = path.with_suffix(path.suffix + ".tmp"); temporary_png.write_bytes(png); temporary_png.replace(path)
	report["fingerprint"] = fingerprint; report["checksum"] = hashlib.sha256(png).hexdigest()
	temporary_report = report_path.with_suffix(report_path.suffix + ".tmp")
	temporary_report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"); temporary_report.replace(report_path)
	return report


def _init_render_worker(asset_dir: str) -> None:
	global _WORKER_RENDERER
	_WORKER_RENDERER = AssetRenderer(Path(asset_dir))


def _render_worker(job: tuple[str, str, str, str]) -> dict[str, object]:
	if _WORKER_RENDERER is None: raise RuntimeError("render worker was not initialized")
	return _write_rendered_chunk(Path(job[1]), Path(job[2]), Path(job[0]), job[3], _WORKER_RENDERER)


def spool_map(map_path: Path, spool_dir: Path, chunk_size: int) -> dict[str, int]:
	if spool_dir.exists(): shutil.rmtree(spool_dir)
	spool_dir.mkdir(parents=True)
	pool = _WriterPool(spool_dir); tiles = 0
	facts: dict[str, list[dict[str, object]]] = {key: [] for key in ("actionIds", "uniqueIds", "teleports", "houseTiles", "houseDoors", "towns", "waypoints")}
	source = map_path.as_posix()
	try:
		for record in iter_map_records(map_path, strict=True):
			if isinstance(record, Town):
				facts["towns"].append({"id": record.town_id, "name": record.name, "temple": asdict(record.temple), "source": source, "origin": "base-map"}); continue
			if isinstance(record, Waypoint):
				facts["waypoints"].append({"name": record.name, "position": asdict(record.position), "source": source, "origin": "base-map"}); continue
			if not isinstance(record, Tile): continue
			pool.write((record.position.z, record.position.x // chunk_size, record.position.y // chunk_size), encode_tile(record)); tiles += 1
			position = asdict(record.position)
			if record.house_id is not None:
				facts["houseTiles"].append({"position": position, "houseId": record.house_id, "source": source, "origin": "base-map"})
			items = (() if record.ground is None else (record.ground,)) + tuple(walk_items(record.items))
			for item in items:
				base = {"position": position, "serverId": item.server_id, "source": source, "origin": "base-map"}
				if item.action_id is not None: facts["actionIds"].append({**base, "actionId": item.action_id})
				if item.unique_id is not None: facts["uniqueIds"].append({**base, "uniqueId": item.unique_id})
				if item.teleport_destination is not None: facts["teleports"].append({**base, "destination": asdict(item.teleport_destination)})
				if item.house_door_id is not None: facts["houseDoors"].append({**base, "doorId": item.house_door_id, "houseId": record.house_id})
	finally: pool.close()
	metadata = {"version": SPOOL_VERSION, "chunkSize": chunk_size, "tiles": tiles}
	(spool_dir / "spool.json").write_text(json.dumps(metadata, sort_keys=True) + "\n", encoding="utf-8")
	(spool_dir / "facts.json").write_text(json.dumps({"schemaVersion": 1, **facts}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	return metadata


def build_atlas(map_path: Path, asset_dir: Path, output: Path, chunk_size: int = 128, scripts_dir: Path = Path("data-otservbr-global"), repository_root: Path = Path("."), workers: int = 1) -> dict[str, object]:
	if chunk_size <= 0: raise ValueError("chunk size must be positive")
	if workers <= 0: raise ValueError("workers must be positive")
	spool_dir = output / ".spool"
	map_sha, assets_sha = _sha256(map_path), _tree_sha256(asset_dir)
	state_path = spool_dir / "source.json"
	expected = {"mapSha256": map_sha, "assetsSha256": assets_sha, "chunkSize": chunk_size, "atlasVersion": ATLAS_VERSION}
	if not state_path.exists() or json.loads(state_path.read_text()) != expected:
		spool_map(map_path, spool_dir, chunk_size)
		state_path.write_text(json.dumps(expected, sort_keys=True) + "\n", encoding="utf-8")
	renderer = AssetRenderer(asset_dir) if workers == 1 else None; chunks = []
	entries: list[tuple[dict[str, object], tuple[str, str, str, str] | None]] = []
	def chunk_order(value: Path) -> tuple[int, int, int]:
		chunk_x, chunk_y = map(int, value.stem.split("_")); return int(value.parent.name[1:]), chunk_y, chunk_x
	for path in sorted(spool_dir.glob("z*/*.bin"), key=chunk_order):
		z = int(path.parent.name[1:]); chunk_x, chunk_y = map(int, path.stem.split("_"))
		logical_bounds = (chunk_x * chunk_size, chunk_x * chunk_size + chunk_size - 1, chunk_y * chunk_size, chunk_y * chunk_size + chunk_size - 1, z)
		tile_path = output / "tiles" / f"z{z}" / f"{chunk_x}_{chunk_y}.png"
		report_path = tile_path.with_suffix(".json")
		fingerprint = hashlib.sha256((expected["mapSha256"] + expected["assetsSha256"] + str(ATLAS_VERSION) + _sha256(path)).encode()).hexdigest()
		cached_report = json.loads(report_path.read_text()) if report_path.exists() else {}
		cache_valid = (
			tile_path.exists()
			and cached_report.get("fingerprint") == fingerprint
			and cached_report.get("checksum") == _sha256(tile_path)
		)
		if cache_valid:
			report = cached_report
			entries.append(({"z": z, "chunkX": chunk_x, "chunkY": chunk_y, "logicalBounds": list(logical_bounds), "path": tile_path.relative_to(output).as_posix(), **report}, None))
		else:
			metadata = {"z": z, "chunkX": chunk_x, "chunkY": chunk_y, "logicalBounds": list(logical_bounds), "path": tile_path.relative_to(output).as_posix()}
			entries.append((metadata, (str(path), str(tile_path), str(report_path), fingerprint)))
	if workers == 1:
		assert renderer is not None
		for metadata, job in entries:
			report = {} if job is None else _write_rendered_chunk(Path(job[1]), Path(job[2]), Path(job[0]), job[3], renderer)
			chunks.append({**metadata, **report})
	else:
		with ProcessPoolExecutor(max_workers=workers, initializer=_init_render_worker, initargs=(str(asset_dir),)) as executor:
			futures = [None if job is None else executor.submit(_render_worker, job) for _metadata, job in entries]
			for (metadata, _job), future in zip(entries, futures): chunks.append({**metadata, **({} if future is None else future.result())})
	manifest = {"schemaVersion": ATLAS_VERSION, "chunkSize": chunk_size, "tilePixels": 32, "sources": expected, "chunks": chunks}
	(output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	data_dir = output / "data"; data_dir.mkdir(parents=True, exist_ok=True)
	unknown_items: dict[int, dict[str, object]] = {}
	for chunk in chunks:
		for server_id, occurrences in chunk.get("missingAppearances", {}).items():
			value = unknown_items.setdefault(int(server_id), {"serverId": int(server_id), "occurrences": 0, "chunks": []})
			value["occurrences"] = int(value["occurrences"]) + int(occurrences)
			value["chunks"].append({"z": chunk["z"], "chunkX": chunk["chunkX"], "chunkY": chunk["chunkY"], "logicalBounds": chunk["logicalBounds"]})
	unknown_report = {"schemaVersion": 1, "items": list(unknown_items.values()), "statistics": {"uniqueServerIds": len(unknown_items), "occurrences": sum(int(value["occurrences"]) for value in unknown_items.values())}}
	(data_dir / "unknown-items.json").write_text(json.dumps(unknown_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	shutil.copyfile(spool_dir / "facts.json", data_dir / "mechanics.json")
	(data_dir / "spawns.json").write_text(json.dumps(scan_spawns(map_path.parent), indent=2, sort_keys=True) + "\n", encoding="utf-8")
	(data_dir / "houses.json").write_text(json.dumps(parse_houses(map_path.parent / "world-house.xml"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
	mechanics = json.loads((spool_dir / "facts.json").read_text(encoding="utf-8"))
	(data_dir / "mechanics-resolution.json").write_text(json.dumps(resolve_mechanics(mechanics, scripts_dir), indent=2, sort_keys=True) + "\n", encoding="utf-8")
	(data_dir / "composition.json").write_text(json.dumps(classify_maps(map_path.parent, repository_root), indent=2, sort_keys=True) + "\n", encoding="utf-8")
	spawns = json.loads((data_dir / "spawns.json").read_text(encoding="utf-8")); resolutions = json.loads((data_dir / "mechanics-resolution.json").read_text(encoding="utf-8")); houses = json.loads((data_dir / "houses.json").read_text(encoding="utf-8"))
	statistics = {
		"schemaVersion": 1, "chunks": len(chunks), "populatedFloors": sorted({int(chunk["z"]) for chunk in chunks}),
		"tiles": sum(int(chunk["tiles"]) for chunk in chunks), "groundItems": sum(int(chunk["groundItems"]) for chunk in chunks),
		"childItems": sum(int(chunk["childItems"]) for chunk in chunks), "renderOperations": sum(int(chunk["renderOperations"]) for chunk in chunks),
		"actionIdRecords": len(mechanics["actionIds"]), "uniqueActionIds": len({entry["actionId"] for entry in mechanics["actionIds"]}),
		"uniqueIdRecords": len(mechanics["uniqueIds"]), "uniqueUniqueIds": len({entry["uniqueId"] for entry in mechanics["uniqueIds"]}),
		"teleports": len(mechanics["teleports"]), "houseTiles": len(mechanics["houseTiles"]), "houseDoors": len(mechanics["houseDoors"]),
		"houses": houses["statistics"]["houses"], "towns": len(mechanics["towns"]), "waypoints": len(mechanics["waypoints"]),
		**spawns["statistics"], "mechanicsResolution": resolutions["statistics"], "unknownItems": unknown_report["statistics"],
	}
	(data_dir / "statistics.json").write_text(json.dumps(statistics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	write_viewer(output)
	return manifest


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("map", type=Path); parser.add_argument("assets", type=Path); parser.add_argument("output", type=Path); parser.add_argument("--chunk-size", type=int, default=128); parser.add_argument("--scripts", type=Path, default=Path("data-otservbr-global")); parser.add_argument("--repository", type=Path, default=Path(".")); parser.add_argument("--workers", type=int, default=1)
	args = parser.parse_args(); build_atlas(args.map, args.assets, args.output, args.chunk_size, args.scripts, args.repository, args.workers); return 0


if __name__ == "__main__": raise SystemExit(main())
