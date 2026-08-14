"""Export bounded cyclic object animations for the browser atlas."""
from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path

from .assets import Appearance, SpriteInfo, encode_png, sheet_for_sprite
from .environment_spool import decode_spool_tiles
from .render import AssetRenderer, _blend, _item_patterns
from .semantic import Item, Tile

ANIMATION_ZOOM = 1.5


@dataclass(frozen=True, slots=True)
class AnimationCandidate:
	appearance: Appearance
	frame: SpriteInfo
	px: int
	py: int
	pz: int
	width: int
	height: int
	offset_x: int
	offset_y: int


def _items(tile: Tile) -> list[Item]:
	return ([] if tile.ground is None else [tile.ground]) + list(tile.items)


def _hooks(items: list[Item], renderer: AssetRenderer) -> tuple[bool, bool]:
	south = east = False
	for item in items:
		appearance = renderer.appearances.get(item.server_id)
		if appearance:
			south = south or appearance.hook_direction == 1
			east = east or appearance.hook_direction == 2
	return south, east


def _idx(frame: SpriteInfo, layer: int, x: int, y: int, z: int, phase: int) -> int:
	return ((((phase * frame.pattern_depth + z) * frame.pattern_height + y) * frame.pattern_width + x) * frame.layers + layer)


def _frame_size(renderer: AssetRenderer, frame: SpriteInfo, px: int, py: int, pz: int) -> tuple[int, int] | None:
	size: tuple[int, int] | None = None
	for phase in range(frame.animation_phases):
		for layer in range(frame.layers):
			index = _idx(frame, layer, px, py, pz, phase)
			if index >= len(frame.sprite_ids):
				return None
			sheet = sheet_for_sprite(renderer.sheets, frame.sprite_ids[index])
			if sheet is None:
				return None
			if size is None:
				size = sheet.sprite_size
			elif sheet.sprite_size != size:
				return None
	return size


def _geometry(appearance: Appearance, width: int, height: int) -> tuple[int, int, int, int]:
	shift_x, shift_y = appearance.shift or (0, 0)
	height_offset = appearance.height or 0
	return width, height, -(width - 32) - shift_x - height_offset, -(height - 32) - shift_y - height_offset


def _candidate(renderer: AssetRenderer, item: Item, x: int, y: int, z: int, south: bool, east: bool):
	"""Return the selected cyclic appearance frame group when all phases are decodable.

	The tuple return shape is retained for existing integration probes. Geometry is
	resolved separately through ``_candidate_details`` so 32x32 callers remain valid.
	"""
	appearance = renderer.appearances.get(item.server_id)
	if not appearance or not appearance.frames:
		return None
	frame = appearance.frames[0]
	if frame.animation_phases <= 1:
		return None
	px, py, pz = _item_patterns(appearance, frame, item, x, y, z, south, east)
	if _frame_size(renderer, frame, px, py, pz) is None:
		return None
	return appearance, frame, px, py, pz


def _candidate_details(renderer: AssetRenderer, item: Item, x: int, y: int, z: int, south: bool, east: bool) -> AnimationCandidate | None:
	candidate = _candidate(renderer, item, x, y, z, south, east)
	if candidate is None:
		return None
	appearance, frame, px, py, pz = candidate
	size = _frame_size(renderer, frame, px, py, pz)
	if size is None:
		return None
	width, height, offset_x, offset_y = _geometry(appearance, *size)
	return AnimationCandidate(appearance, frame, px, py, pz, width, height, offset_x, offset_y)


def _dangerous(renderer: AssetRenderer, item: Item) -> bool:
	"""Compatibility helper: identify appearances that can paint outside one tile."""
	appearance = renderer.appearances.get(item.server_id)
	if not appearance or not appearance.frames:
		return False
	if appearance.shift not in (None, (0, 0)) or appearance.height not in (None, 0):
		return True
	frame = appearance.frames[0]
	for sprite_id in frame.sprite_ids:
		sheet = sheet_for_sprite(renderer.sheets, sprite_id)
		if sheet and sheet.sprite_size != (32, 32):
			return True
	return False


def _phase_rgba(renderer: AssetRenderer, frame: SpriteInfo, px: int, py: int, pz: int, phase: int) -> tuple[int, int, bytes]:
	size = _frame_size(renderer, frame, px, py, pz)
	if size is None:
		raise ValueError("inconsistent or missing eligible animation sprite geometry")
	width, height = size
	out = bytearray(width * height * 4)
	for layer in range(frame.layers):
		decoded = renderer.sprite(frame.sprite_ids[_idx(frame, layer, px, py, pz, phase)])
		if not decoded or decoded[:2] != size:
			raise ValueError("invalid eligible animation sprite")
		_blend(out, width, height, decoded[2], width, height, 0, 0)
	return width, height, bytes(out)


def _phase(renderer: AssetRenderer, frame: SpriteInfo, px: int, py: int, pz: int, phase: int) -> bytes:
	width, height, pixels = _phase_rgba(renderer, frame, px, py, pz, phase)
	return encode_png(width, height, pixels)


def _overlap_radius(renderer: AssetRenderer) -> int:
	max_width = max((sheet.sprite_size[0] for sheet in renderer.sheets), default=32)
	max_height = max((sheet.sprite_size[1] for sheet in renderer.sheets), default=32)
	max_shift_x = max((abs((appearance.shift or (0, 0))[0]) for appearance in renderer.appearances.values()), default=0)
	max_shift_y = max((abs((appearance.shift or (0, 0))[1]) for appearance in renderer.appearances.values()), default=0)
	max_height_offset = max((abs(appearance.height or 0) for appearance in renderer.appearances.values()), default=0)
	reach = max(max_width - 32 + max_shift_x + max_height_offset, max_height - 32 + max_shift_y + max_height_offset)
	return max(1, math.ceil(reach / 32) + 1)


def _durations(frame: SpriteInfo) -> list[tuple[int, int]]:
	# assets.py currently maps protobuf 0/0 to 1/1. The pinned object assets contain
	# no genuine 1ms phases, so restore OTClient's first-nonzero fallback semantics.
	ranges = list(frame.phase_durations)
	fallback = next((value for value in ranges if value != (1, 1)), (1, 1))
	return [fallback if value == (1, 1) else value for value in ranges]


def _rect(candidate: AnimationCandidate, x: int, y: int) -> tuple[int, int, int, int]:
	left = x * 32 + candidate.offset_x
	top = y * 32 + candidate.offset_y
	return left, top, left + candidate.width, top + candidate.height


def _intersects(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
	return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def _rect_cells(rect: tuple[int, int, int, int], cell_size: int = 32):
	"""Yield bounded spatial buckets touched by a half-open pixel rectangle."""
	left, top, right, bottom = rect
	if right <= left or bottom <= top:
		return
	for cell_y in range(top // cell_size, (bottom - 1) // cell_size + 1):
		for cell_x in range(left // cell_size, (right - 1) // cell_size + 1):
			yield cell_x, cell_y


def _overlap_conflicts(rects: list[tuple[int, int, int, int]]) -> set[int]:
	"""Find intersecting animation rectangles without an all-pairs chunk scan.

	A 32-pixel spatial hash keeps dense non-overlapping animated grounds effectively
	linear in candidate count. Candidates spanning multiple cells are compared only
	with earlier rectangles that touched one of the same cells; a small per-candidate
	set prevents duplicate comparisons when two rectangles share multiple buckets.
	"""
	buckets: dict[tuple[int, int], list[int]] = {}
	conflicts: set[int] = set()
	for index, rect in enumerate(rects):
		cells = tuple(_rect_cells(rect))
		nearby: set[int] = set()
		for cell in cells:
			nearby.update(buckets.get(cell, ()))
		for other in nearby:
			if _intersects(rect, rects[other]):
				conflicts.add(other)
				conflicts.add(index)
		for cell in cells:
			buckets.setdefault(cell, []).append(index)
	return conflicts


def _paint_item(canvas: bytearray, patch_left: int, patch_top: int, width: int, height: int, renderer: AssetRenderer, tile: Tile, item: Item, south: bool, east: bool) -> None:
	for appearance, _sprite_id, (sprite_width, sprite_height, pixels) in renderer.item_sprites(item, tile.position.x, tile.position.y, tile.position.z, south, east):
		shift_x, shift_y = appearance.shift or (0, 0)
		height_offset = appearance.height or 0
		draw_x = tile.position.x * 32 - patch_left - (sprite_width - 32) - shift_x - height_offset
		draw_y = tile.position.y * 32 - patch_top - (sprite_height - 32) - shift_y - height_offset
		_blend(canvas, width, height, pixels, sprite_width, sprite_height, draw_x, draw_y)


def _compose_context(
	renderer: AssetRenderer,
	by_pos: dict[tuple[int, int], Tile],
	order_by_pos: dict[tuple[int, int], int],
	target_tile: Tile,
	target_stack_index: int,
	candidate: AnimationCandidate,
	radius: int,
) -> tuple[bytes, bytes]:
	patch_left, patch_top, _patch_right, _patch_bottom = _rect(candidate, target_tile.position.x, target_tile.position.y)
	width, height = candidate.width, candidate.height
	underlay = bytearray(width * height * 4)
	overdraw = bytearray(width * height * 4)
	target_key = (order_by_pos[(target_tile.position.x, target_tile.position.y)], target_stack_index)
	nearby: list[tuple[int, Tile]] = []
	for nx in range(target_tile.position.x - radius, target_tile.position.x + radius + 1):
		for ny in range(target_tile.position.y - radius, target_tile.position.y + radius + 1):
			tile = by_pos.get((nx, ny))
			if tile is not None:
				nearby.append((order_by_pos[(nx, ny)], tile))
	for tile_order, tile in sorted(nearby, key=lambda pair: pair[0]):
		items = _items(tile)
		south, east = _hooks(items, renderer)
		for stack_index, item in enumerate(items):
			key = (tile_order, stack_index)
			if key == target_key:
				continue
			canvas = underlay if key < target_key else overdraw
			_paint_item(canvas, patch_left, patch_top, width, height, renderer, tile, item, south, east)
	return bytes(underlay), bytes(overdraw)


def _opaque_composite(underlay: bytes, overdraw: bytes, phases: list[bytes], width: int, height: int) -> bool:
	for phase in phases:
		canvas = bytearray(underlay)
		_blend(canvas, width, height, phase, width, height, 0, 0)
		_blend(canvas, width, height, overdraw, width, height, 0, 0)
		if any(canvas[index] != 255 for index in range(3, len(canvas), 4)):
			return False
	return True


def _has_alpha(pixels: bytes) -> bool:
	return any(pixels[index] for index in range(3, len(pixels), 4))


def enrich_environment_animations(asset_dir: Path, output: Path) -> dict[str, int]:
	manifest_path = output / "manifest.json"
	spool = output / ".spool"
	zero = {"instances": 0, "uniqueAnimations": 0, "chunks": 0, "staticFallbacks": 0}
	if not manifest_path.exists() or not (spool / "spool.json").exists():
		return zero
	root = output / "data" / "environment-animations"
	shutil.rmtree(root, ignore_errors=True)
	root.mkdir(parents=True)
	renderer = AssetRenderer(asset_dir)
	radius = _overlap_radius(renderer)
	manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
	made: set[str] = set()
	instances = chunks = fallbacks = 0
	for chunk in manifest.get("chunks", []):
		z, chunk_x, chunk_y = int(chunk["z"]), int(chunk["chunkX"]), int(chunk["chunkY"])
		spool_path = spool / f"z{z}" / f"{chunk_x}_{chunk_y}.bin"
		if not spool_path.exists():
			continue
		tiles = list(decode_spool_tiles(spool_path))
		by_pos = {(tile.position.x, tile.position.y): tile for tile in tiles}
		order_by_pos = {(tile.position.x, tile.position.y): index for index, tile in enumerate(tiles)}
		x1, x2, y1, y2, _ = map(int, chunk["logicalBounds"])
		candidates: list[tuple[Tile, int, Item, AnimationCandidate, tuple[int, int, int, int], bool, bool]] = []
		for tile in tiles:
			items = _items(tile)
			if not items:
				continue
			south, east = _hooks(items, renderer)
			for stack_index, item in enumerate(items):
				appearance = renderer.appearances.get(item.server_id)
				if not appearance or not appearance.frames or appearance.frames[0].animation_phases <= 1:
					continue
				details = _candidate_details(renderer, item, tile.position.x, tile.position.y, tile.position.z, south, east)
				if details is None:
					fallbacks += 1
					continue
				candidates.append((tile, stack_index, item, details, _rect(details, tile.position.x, tile.position.y), south, east))
		conflicts = _overlap_conflicts([candidate[4] for candidate in candidates])
		records: list[dict[str, object]] = []
		for index, (tile, stack_index, item, details, _visual_rect, south, east) in enumerate(candidates):
			x, y = tile.position.x, tile.position.y
			if index in conflicts:
				fallbacks += 1
				continue
			if x - x1 < radius or x2 - x < radius or y - y1 < radius or y2 - y < radius:
				fallbacks += 1
				continue
			underlay_pixels, overdraw_pixels = _compose_context(renderer, by_pos, order_by_pos, tile, stack_index, details, radius)
			phase_pixels: list[bytes] = []
			for phase in range(details.frame.animation_phases):
				phase_width, phase_height, pixels = _phase_rgba(renderer, details.frame, details.px, details.py, details.pz, phase)
				if (phase_width, phase_height) != (details.width, details.height):
					raise ValueError("animation phase geometry changed after candidate validation")
				phase_pixels.append(pixels)
			if not _opaque_composite(underlay_pixels, overdraw_pixels, phase_pixels, details.width, details.height):
				fallbacks += 1
				continue
			subtype = -1 if item.subtype is None else int(item.subtype)
			key = f"{item.server_id}-{subtype}-{details.px}-{details.py}-{details.pz}-{int(south)}-{int(east)}"
			frames = [f"data/environment-animations/frames/{key}/{phase}.png" for phase in range(details.frame.animation_phases)]
			if key not in made:
				for phase, relative in enumerate(frames):
					path = output / relative
					path.parent.mkdir(parents=True, exist_ok=True)
					path.write_bytes(encode_png(details.width, details.height, phase_pixels[phase]))
				made.add(key)
			underlay = f"data/environment-animations/underlays/z{z}/{chunk_x}_{chunk_y}/{x}_{y}_{stack_index}.png"
			path = output / underlay
			path.parent.mkdir(parents=True, exist_ok=True)
			path.write_bytes(encode_png(details.width, details.height, underlay_pixels))
			overdraw: str | None = None
			if _has_alpha(overdraw_pixels):
				overdraw = f"data/environment-animations/overdraws/z{z}/{chunk_x}_{chunk_y}/{x}_{y}_{stack_index}.png"
				path = output / overdraw
				path.parent.mkdir(parents=True, exist_ok=True)
				path.write_bytes(encode_png(details.width, details.height, overdraw_pixels))
			ranges = _durations(details.frame)
			loop = -1 if details.frame.loop_type > 1 else details.frame.loop_type
			record: dict[str, object] = {
				"position": {"x": x, "y": y, "z": tile.position.z},
				"serverId": item.server_id,
				"animationKey": key,
				"frames": frames,
				"underlay": underlay,
				"spriteSize": [details.width, details.height],
				"drawOffsetPixels": [details.offset_x, details.offset_y],
				"stackIndex": stack_index,
				"stackSize": len(_items(tile)),
				"phaseDurationsMs": [max(1, (low + high) // 2) for low, high in ranges],
				"durationRangesMs": [[low, high] for low, high in ranges],
				"defaultStartPhase": details.frame.default_start_phase,
				"synchronized": details.frame.synchronized,
				"randomStartPhase": details.frame.random_start_phase,
				"loopType": loop,
				"loopCount": details.frame.loop_count,
				"policy": "cyclic-appearance-composited",
			}
			if overdraw is not None:
				record["overdraw"] = overdraw
			if item.subtype is not None:
				record["subtype"] = item.subtype
			records.append(record)
			instances += 1
		if records:
			path = root / "chunks" / f"z{z}" / f"{chunk_x}_{chunk_y}.json"
			path.parent.mkdir(parents=True, exist_ok=True)
			path.write_text(json.dumps({"schemaVersion": 2, "records": records}, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
			chunks += 1
	stats = {"instances": instances, "uniqueAnimations": len(made), "chunks": chunks, "staticFallbacks": fallbacks}
	index = {
		"schemaVersion": 2,
		"animationZoom": ANIMATION_ZOOM,
		"overlapSafetyRadiusTiles": radius,
		"statistics": stats,
		"policy": {
			"cyclicAppearance": "browser animated from pinned object appearance phases without GIF/WebP animation assets",
			"geometry": "32x32, 32x64, 64x32 and 64x64 sprite sheets with canonical shift/height offsets",
			"stacking": "safe ground and non-topmost entries use canonical per-instance underlay/overdraw composition",
			"statefulAppearance": "not inferred; server-driven variants remain canonical static state",
			"eligibility": "decodable cyclic object whose replacement patch is opaque and does not overlap another animated instance or a chunk edge safety zone",
			"fallback": "unsupported, conflicting, edge-risk or non-replaceable animations remain deterministic static pixels",
		},
	}
	(root / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	return stats
