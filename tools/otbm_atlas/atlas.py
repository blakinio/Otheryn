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
from tools.otbm_atlas_facts.mechanics import resolve_mechanics
from .composition import classify_maps
from .houses import parse_houses
from .semantic import Item, Position, Tile, Town, Waypoint, iter_map_records, walk_items
from .spawns import scan_spawns
from .viewer import write_viewer
from .overview import make_overview, OVERVIEW_FACTOR, LOW_OVERVIEW_FACTOR, OVERVIEW_VERSION
from .spatial import write_spatial_data
from .tile_inspector import write_tile_inspector_data
from .npc_sprites import enrich_npc_spawns
from .monster_sprites import enrich_monster_spawns
from .environment_animation_resume import enrich_environment_animations_resumable as enrich_environment_animations
from .factual_layers import enrich_existing_atlas
from .incremental_core import chunk_render_bounds as incremental_chunk_render_bounds, decode_tiles as incremental_decode_tiles
from .production_incremental import commit_production_render_state, prepare_production_render_plan, remove_deleted_chunk_outputs

SPOOL_VERSION = 1
TILE_FACTS_VERSION = 1
ATLAS_VERSION = 3
_WORKER_RENDERER: AssetRenderer | None = None

CANONICAL_WORLD_ROOT = Path("vendor/map-analysis/crystalserver/data-global/world")
CANONICAL_NPC_ROOT = Path("vendor/map-analysis/crystalserver/data-global/npc")
CANONICAL_MONSTER_ROOT = Path("vendor/map-analysis/crystalserver/data-global/monster")
CANONICAL_CRYSTAL_DATA_ROOT = Path("vendor/map-analysis/crystalserver/data-global")
CANONICAL_ASSET_ROOT = Path("vendor/map-analysis/tibia-client/15.25.bd5a04/assets")


def canonical_source_paths(repository_root: Path) -> dict[str, Path]:
	return {
		"map": repository_root / CANONICAL_WORLD_ROOT / "world.otbm",
		"worldRoot": repository_root / CANONICAL_WORLD_ROOT,
		"npcDefinitionRoot": repository_root / CANONICAL_NPC_ROOT,
		"monsterDefinitionRoot": repository_root / CANONICAL_MONSTER_ROOT,
		"crystalDataRoot": repository_root / CANONICAL_CRYSTAL_DATA_ROOT,
		"appearanceAssetRoot": repository_root / CANONICAL_ASSET_ROOT,
	}


def _require_canonical_source(actual: Path, expected: Path, label: str) -> None:
	if actual.resolve() != expected.resolve():
		raise ValueError(f"canonical OTBM Atlas {label} must be {expected.as_posix()}, got {actual.as_posix()}")


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
		for handle in self.handles.values(): old = handle; old.close()
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


def _tile_fact_item(item: Item) -> dict[str, int]:
	value = {"serverId": int(item.server_id)}
	if item.action_id is not None: value["actionId"] = int(item.action_id)
	if item.unique_id is not None: value["uniqueId"] = int(item.unique_id)
	return value


class _TileFactWriterPool:
	def __init__(self, directory: Path, limit: int = 64) -> None:
		self.directory, self.limit = directory, limit
		self.handles: OrderedDict[tuple[int, int, int], BinaryIO] = OrderedDict()

	def write(self, key: tuple[int, int, int], record: dict[str, object]) -> None:
		handle = self.handles.pop(key, None)
		if handle is None:
			path = self.directory / f"z{key[0]}" / f"{key[1]}_{key[2]}.jsonl"
			path.parent.mkdir(parents=True, exist_ok=True)
			handle = path.open("a", encoding="utf-8", newline="\n")
		self.handles[key] = handle
		handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
		if len(self.handles) > self.limit:
			_unused, old = self.handles.popitem(last=False)
			old.close()

	def close(self) -> None:
		for handle in self.handles.values(): handle.close()
		self.handles.clear()


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
	tiles = list(incremental_decode_tiles(spool_path)); bounds = incremental_chunk_render_bounds(tiles, renderer)
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
	pool = _WriterPool(spool_dir); tile_fact_pool = _TileFactWriterPool(spool_dir / "tile-facts"); tiles = 0
	facts: dict[str, list[dict[str, object]]] = {key: [] for key in ("actionIds", "uniqueIds", "teleports", "houseTiles", "houseDoors", "towns", "waypoints")}
	source = map_path.as_posix()
	try:
		for record in iter_map_records(map_path, strict=True):
			if isinstance(record, Town):
				facts["towns"].append({"id": record.town_id, "name": record.name, "temple": asdict(record.temple), "source": source, "origin": "base-map"}); continue
			if isinstance(record, Waypoint):
				facts["waypoints"].append({"name": record.name, "position": asdict(record.position), "source": source, "origin": "base-map"}); continue
			if not isinstance(record, Tile): continue
			chunk_key = (record.position.z, record.position.x // chunk_size, record.position.y // chunk_size)
			pool.write(chunk_key, encode_tile(record))
			tile_fact_pool.write(chunk_key, {
				"x": int(record.position.x), "y": int(record.position.y), "z": int(record.position.z),
				"ground": None if record.ground is None else _tile_fact_item(record.ground),
				"items": [_tile_fact_item(item) for item in record.items],
			})
			tiles += 1
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
	finally: pool.close(); tile_fact_pool.close()
	metadata = {"schemaVersion": 1, "version": SPOOL_VERSION, "tileFactsVersion": TILE_FACTS_VERSION, "chunkSize": chunk_size, "tiles": tiles, "sourceSha256": _sha256(map_path)}
	(spool_dir / "spool.json").write_text(json.dumps(metadata, sort_keys=True) + "\n", encoding="utf-8")
	(spool_dir / "facts.json").write_text(json.dumps({"schemaVersion": 1, **facts}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	return metadata


def build_atlas(map_path: Path, asset_dir: Path, output: Path, chunk_size: int = 128, scripts_dir: Path | None = None, repository_root: Path = Path("."), workers: int = 1, allow_full_build: bool = False) -> dict[str, object]:
	if chunk_size <= 0: raise ValueError("chunk size must be positive")
	if workers <= 0: raise ValueError("workers must be positive")
	canonical = canonical_source_paths(repository_root)
	_require_canonical_source(map_path, canonical["map"], "map")
	_require_canonical_source(asset_dir, canonical["appearanceAssetRoot"], "appearance assets")
	if scripts_dir is not None:
		_require_canonical_source(scripts_dir, canonical["crystalDataRoot"], "CrystalServer data root")
	map_sha, assets_sha = _sha256(map_path), _tree_sha256(asset_dir)
	expected = {"mapSha256": map_sha, "assetsSha256": assets_sha, "chunkSize": chunk_size, "atlasVersion": ATLAS_VERSION, "tileFactsVersion": TILE_FACTS_VERSION}
	render_plan = prepare_production_render_plan(
		map_path, asset_dir, output, repository_root, chunk_size, expected,
		{"version": SPOOL_VERSION, "tileFactsVersion": TILE_FACTS_VERSION}, spool_map,
		allow_full_build=allow_full_build,
	)
	spool_dir = Path(str(render_plan["spoolDir"]))
	dirty_chunks = {str(value) for value in render_plan["dirtyDetailChunks"]}
	fingerprints = {str(key): str(value) for key, value in dict(render_plan["chunkFingerprints"]).items()}
	remove_deleted_chunk_outputs(output, [str(value) for value in render_plan["deletedDetailChunks"]])
	renderer = AssetRenderer(asset_dir) if workers == 1 else None; chunks = []
	entries: list[tuple[dict[str, object], tuple[str, str, str, str] | None]] = []
	def chunk_order(value: Path) -> tuple[int, int, int]:
		chunk_x, chunk_y = map(int, value.stem.split("_")); return int(value.parent.name[1:]), chunk_y, chunk_x
	for path in sorted(spool_dir.glob("z*/*.bin"), key=chunk_order):
		z = int(path.parent.name[1:]); chunk_x, chunk_y = map(int, path.stem.split("_")); chunk_text = f"z{z}/{chunk_x}_{chunk_y}"
		logical_bounds = (chunk_x * chunk_size, chunk_x * chunk_size + chunk_size - 1, chunk_y * chunk_size, chunk_y * chunk_size + chunk_size - 1, z)
		tile_path = output / "tiles" / f"z{z}" / f"{chunk_x}_{chunk_y}.png"
		report_path = tile_path.with_suffix(".json")
		fingerprint = fingerprints[chunk_text]
		cached_report = json.loads(report_path.read_text()) if report_path.exists() else {}
		cache_valid = chunk_text not in dirty_chunks and tile_path.exists() and report_path.exists()
		if cache_valid:
			report = {**cached_report, "fingerprint": fingerprint}
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
	for chunk in chunks:
		detailed_path = output / str(chunk["path"])
		for prefix, directory, factor in (("overview", "overview", OVERVIEW_FACTOR), ("lowOverview", "overview-low", LOW_OVERVIEW_FACTOR)):
			overview_path = output / directory / f"z{chunk['z']}" / f"{chunk['chunkX']}_{chunk['chunkY']}.png"; fingerprint = hashlib.sha256(f"{OVERVIEW_VERSION}:{factor}:{chunk['checksum']}".encode()).hexdigest(); report_path = overview_path.with_suffix(".json")
			report = json.loads(report_path.read_text()) if report_path.exists() else {}
			if not (overview_path.exists() and report.get("fingerprint") == fingerprint and isinstance(report.get("checksum"), str)):
				payload = make_overview(detailed_path.read_bytes(), factor); overview_path.parent.mkdir(parents=True, exist_ok=True); temporary = overview_path.with_suffix(".png.tmp"); temporary.write_bytes(payload); temporary.replace(overview_path)
				report = {"fingerprint": fingerprint, "checksum": hashlib.sha256(payload).hexdigest(), "imageWidth": int(chunk["imageWidth"]) // factor, "imageHeight": int(chunk["imageHeight"]) // factor}; report_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
			chunk.update({f"{prefix}Path": overview_path.relative_to(output).as_posix(), f"{prefix}Checksum": report["checksum"], f"{prefix}ImageWidth": report["imageWidth"], f"{prefix}ImageHeight": report["imageHeight"]})
	provenance = {
		"map": CANONICAL_WORLD_ROOT.joinpath("world.otbm").as_posix(),
		"worldRoot": CANONICAL_WORLD_ROOT.as_posix(),
		"npcDefinitionRoot": CANONICAL_NPC_ROOT.as_posix(),
		"monsterDefinitionRoot": CANONICAL_MONSTER_ROOT.as_posix(),
		"appearanceAssetRoot": CANONICAL_ASSET_ROOT.as_posix(),
	}
	manifest = {"schemaVersion": ATLAS_VERSION, "chunkSize": chunk_size, "tilePixels": 32, "overviewFactor": OVERVIEW_FACTOR, "lowOverviewFactor": LOW_OVERVIEW_FACTOR, "overviewVersion": OVERVIEW_VERSION, "chunks": chunks, "sources": expected, "provenance": provenance}
	(output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	commit_production_render_state(output, render_plan)
	(spool_dir / "source.json").write_text(json.dumps(expected, sort_keys=True) + "\n", encoding="utf-8")
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
	spawns_report = scan_spawns(canonical["worldRoot"])
	npc_sprite_statistics = enrich_npc_spawns(asset_dir, canonical["npcDefinitionRoot"], output, spawns_report["npcSpawns"], repository_root)
	monster_sprite_statistics = enrich_monster_spawns(asset_dir, canonical["monsterDefinitionRoot"], output, spawns_report["monsterSpawns"], repository_root)
	spawns_report["provenance"] = {"worldRoot": provenance["worldRoot"], "npcDefinitionRoot": provenance["npcDefinitionRoot"], "monsterDefinitionRoot": provenance["monsterDefinitionRoot"], "appearanceAssetRoot": provenance["appearanceAssetRoot"]}
	(data_dir / "spawns.json").write_text(json.dumps(spawns_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	(data_dir / "houses.json").write_text(json.dumps(parse_houses(map_path.parent / "world-house.xml"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
	mechanics = json.loads((spool_dir / "facts.json").read_text(encoding="utf-8"))
	(data_dir / "mechanics-resolution.json").write_text(json.dumps(resolve_mechanics(mechanics, canonical["crystalDataRoot"] / "scripts"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
		**spawns["statistics"], "npcSprites": npc_sprite_statistics, "monsterSprites": monster_sprite_statistics, "mechanicsResolution": resolutions["statistics"], "unknownItems": unknown_report["statistics"], "provenance": provenance,
	}
	statistics["incrementalBuild"] = {
		"dirtyDetailChunks": len(render_plan["dirtyDetailChunks"]),
		"reusedDetailChunks": len(render_plan["reusedDetailChunks"]),
		"deletedDetailChunks": len(render_plan["deletedDetailChunks"]),
		"fullBuildRequired": render_plan["fullBuildRequired"],
		"fullBuildReasons": render_plan["fullBuildReasons"],
		"legacyPublicationAdopted": render_plan["legacyPublicationAdopted"],
		"spool": render_plan["spool"],
	}
	(data_dir / "statistics.json").write_text(json.dumps(statistics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	resolution_by_key = {(entry["kind"], int(entry["value"])): entry for entry in resolutions["resolutions"]}
	action_records = [{**entry, "mechanics": resolution_by_key.get(("ActionID", int(entry["actionId"])), {"status": "UNKNOWN", "candidates": []})} for entry in mechanics["actionIds"]]
	unique_records = [{**entry, "mechanics": resolution_by_key.get(("UniqueID", int(entry["uniqueId"])), {"status": "UNKNOWN", "candidates": []})} for entry in mechanics["uniqueIds"]]
	spatial_statistics = write_spatial_data(output, chunk_size, {
		**{key: mechanics[key] for key in ("teleports", "houseTiles", "houseDoors", "towns", "waypoints")}, "actionIds": action_records, "uniqueIds": unique_records,
		"mechanics": action_records + unique_records,
		"monsterSpawns": spawns["monsterSpawns"], "npcSpawns": spawns["npcSpawns"], "houses": houses["houses"],
	})
	statistics["spatialData"] = spatial_statistics
	statistics["tileInspector"] = write_tile_inspector_data(output)
	statistics["environmentAnimations"] = enrich_environment_animations(asset_dir, output)
	factual_report = enrich_existing_atlas(output, repository_root)
	if factual_report.get("status") == "RESOLVED":
		statistics["mechanicsResolution"] = factual_report["statistics"].get("mechanicsResolution", {})
		statistics["factualLayers"] = factual_report["statistics"]
		statistics["factualSpatial"] = factual_report["spatial"]
	else:
		statistics["factualLayers"] = {"status": factual_report.get("status", "UNKNOWN"), "reason": factual_report.get("reason")}
	(data_dir / "statistics.json").write_text(json.dumps(statistics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	write_viewer(output)
	return manifest


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("map", type=Path)
	parser.add_argument("assets", type=Path)
	parser.add_argument("output", type=Path)
	parser.add_argument("--chunk-size", type=int, default=128)
	parser.add_argument("--scripts", type=Path, default=None, help=argparse.SUPPRESS)
	parser.add_argument("--repository", type=Path, default=Path("."))
	parser.add_argument("--workers", type=int, default=1)
	parser.add_argument("--allow-full-build", action="store_true", help="explicitly authorize a detail-wide rebuild when the incremental planner reports a global render transition")
	args = parser.parse_args()
	build_atlas(args.map, args.assets, args.output, args.chunk_size, args.scripts, args.repository, args.workers, args.allow_full_build)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
