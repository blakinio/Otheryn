"""Export conservative cyclic object animations for the browser atlas.

The detailed chunk PNG remains the canonical static fallback. Eligible cyclic
appearances are reconstructed at runtime from the same pinned Tibia object
appearance phases without generating GIFs. Per-instance underlay/overlay patches
erase the baked default phase and preserve canonical draw ordering while the
phase images themselves stay deduplicated across identical appearances.
"""
from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from .assets import encode_png, sheet_for_sprite
from .environment_spool import decode_spool_tiles
from .render import AssetRenderer, _blend, _item_patterns

ANIMATION_ZOOM = 1.5


def _items(tile):
	return ([] if tile.ground is None else [tile.ground]) + list(tile.items)


def _hooks(items, renderer):
	south = east = False
	for item in items:
		appearance = renderer.appearances.get(item.server_id)
		if appearance:
			south = south or appearance.hook_direction == 1
			east = east or appearance.hook_direction == 2
	return south, east


def _idx(frame, layer, pattern_x, pattern_y, pattern_z, phase):
	return ((((phase * frame.pattern_depth + pattern_z) * frame.pattern_height + pattern_y) * frame.pattern_width + pattern_x) * frame.layers + layer)


def _draw_offset(appearance, width: int, height: int) -> tuple[int, int]:
	shift_x, shift_y = appearance.shift or (0, 0)
	elevation = appearance.height or 0
	return -(width - 32) - shift_x - elevation, -(height - 32) - shift_y - elevation


def _candidate_geometry(renderer, item, x: int, y: int, z: int, hook_south: bool, hook_east: bool):
	appearance = renderer.appearances.get(item.server_id)
	if not appearance or not appearance.frames:
		return None
	frame = appearance.frames[0]
	if frame.animation_phases <= 1:
		return None
	pattern_x, pattern_y, pattern_z = _item_patterns(appearance, frame, item, x, y, z, hook_south, hook_east)
	size = None
	for phase in range(frame.animation_phases):
		for layer in range(frame.layers):
			index = _idx(frame, layer, pattern_x, pattern_y, pattern_z, phase)
			if index >= len(frame.sprite_ids):
				return None
			sheet = sheet_for_sprite(renderer.sheets, frame.sprite_ids[index])
			if not sheet:
				return None
			if size is None:
				size = sheet.sprite_size
			elif sheet.sprite_size != size:
				return None
	if size is None:
		return None
	width, height = size
	offset_x, offset_y = _draw_offset(appearance, width, height)
	return appearance, frame, pattern_x, pattern_y, pattern_z, width, height, offset_x, offset_y


def _candidate(renderer, item, x: int, y: int, z: int, hook_south: bool, hook_east: bool):
	"""Compatibility probe used by the repository E2E harness."""
	candidate = _candidate_geometry(renderer, item, x, y, z, hook_south, hook_east)
	return None if candidate is None else candidate[:5]


def _dangerous(renderer, item) -> bool:
	"""Return whether a static item can draw outside its owning 32px tile."""
	appearance = renderer.appearances.get(item.server_id)
	if not appearance or not appearance.frames:
		return False
	if appearance.shift not in (None, (0, 0)) or appearance.height not in (None, 0):
		return True
	for sprite_id in appearance.frames[0].sprite_ids:
		sheet = sheet_for_sprite(renderer.sheets, sprite_id)
		if sheet and sheet.sprite_size != (32, 32):
			return True
	return False


def _phase_pixels(renderer, frame, pattern_x: int, pattern_y: int, pattern_z: int, phase: int, width: int, height: int) -> bytes:
	out = bytearray(width * height * 4)
	for layer in range(frame.layers):
		decoded = renderer.sprite(frame.sprite_ids[_idx(frame, layer, pattern_x, pattern_y, pattern_z, phase)])
		if not decoded or decoded[:2] != (width, height):
			raise ValueError("invalid eligible animation sprite")
		_blend(out, width, height, decoded[2], width, height, 0, 0)
	return bytes(out)


def _phase(renderer, frame, pattern_x: int, pattern_y: int, pattern_z: int, phase: int) -> bytes:
	"""Compatibility PNG helper used by the repository browser E2E harness."""
	index = _idx(frame, 0, pattern_x, pattern_y, pattern_z, phase)
	if index >= len(frame.sprite_ids):
		raise ValueError("invalid eligible animation phase")
	sheet = sheet_for_sprite(renderer.sheets, frame.sprite_ids[index])
	if not sheet:
		raise ValueError("missing eligible animation sprite sheet")
	width, height = sheet.sprite_size
	return encode_png(width, height, _phase_pixels(renderer, frame, pattern_x, pattern_y, pattern_z, phase, width, height))


def _partition_pixels(tiles, renderer, candidate_tile, candidate_item, width: int, height: int, offset_x: int, offset_y: int, *, after: bool) -> bytes:
	"""Render all canonical operations before or after one candidate into its patch."""
	out = bytearray(width * height * 4)
	seen_candidate = False
	candidate_x = candidate_tile.position.x
	candidate_y = candidate_tile.position.y
	for tile in tiles:
		items = _items(tile)
		hook_south, hook_east = _hooks(items, renderer)
		for item in items:
			if tile is candidate_tile and item is candidate_item:
				seen_candidate = True
				continue
			if seen_candidate != after:
				continue
			for appearance, _sprite_id, (sprite_width, sprite_height, pixels) in renderer.item_sprites(
				item, tile.position.x, tile.position.y, tile.position.z, hook_south, hook_east
			):
				draw_x, draw_y = _draw_offset(appearance, sprite_width, sprite_height)
				draw_x += (tile.position.x - candidate_x) * 32 - offset_x
				draw_y += (tile.position.y - candidate_y) * 32 - offset_y
				_blend(out, width, height, pixels, sprite_width, sprite_height, draw_x, draw_y)
	if not seen_candidate:
		raise ValueError("candidate item is not present in its decoded chunk")
	return bytes(out)


def _composite(width: int, height: int, *layers: bytes) -> bytes:
	out = bytearray(width * height * 4)
	for pixels in layers:
		_blend(out, width, height, pixels, width, height, 0, 0)
	return bytes(out)


def _runtime_replacement_safe(width: int, height: int, underlay: bytes, phases: list[bytes], overlay: bytes, default_phase: int) -> bool:
	"""Prove that drawing the runtime patch over the baked static patch cannot leak it."""
	if not phases:
		return False
	default_phase %= len(phases)
	static_patch = _composite(width, height, underlay, phases[default_phase], overlay)
	for phase in phases:
		desired = _composite(width, height, underlay, phase, overlay)
		runtime = bytearray(static_patch)
		for layer in (underlay, phase, overlay):
			_blend(runtime, width, height, layer, width, height, 0, 0)
		if bytes(runtime) != desired:
			return False
	return True


def _overlap_radius(renderer) -> int:
	"""Bound how far another item can reach into a candidate replacement patch."""
	reach = 64
	for appearance in renderer.appearances.values():
		shift_x, shift_y = appearance.shift or (0, 0)
		elevation = appearance.height or 0
		local_reach = 32 + max(abs(shift_x), abs(shift_y)) + elevation
		if appearance.frames:
			for sprite_id in appearance.frames[0].sprite_ids:
				sheet = sheet_for_sprite(renderer.sheets, sprite_id)
				if sheet:
					local_reach = max(local_reach, max(sheet.sprite_size) + max(abs(shift_x), abs(shift_y)) + elevation)
		reach = max(reach, local_reach)
	return max(1, math.ceil(reach / 32))


def _durations(frame):
	# assets.py currently maps protobuf 0/0 to 1/1. The pinned object assets contain
	# no genuine 1ms phases, so restore OTClient's first-nonzero fallback semantics.
	ranges = list(frame.phase_durations)
	fallback = next((value for value in ranges if value != (1, 1)), (1, 1))
	return [fallback if value == (1, 1) else value for value in ranges]


def _write_png(path: Path, width: int, height: int, pixels: bytes) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_bytes(encode_png(width, height, pixels))


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
		by_position = {(tile.position.x, tile.position.y): tile for tile in tiles}
		danger = {position for position, tile in by_position.items() if any(_dangerous(renderer, item) for item in _items(tile))}
		records = []
		x1, x2, y1, y2, _ = map(int, chunk["logicalBounds"])

		for tile in tiles:
			items = _items(tile)
			if not items:
				continue
			hook_south, hook_east = _hooks(items, renderer)
			animated = []
			for item in items:
				appearance = renderer.appearances.get(item.server_id)
				if appearance and appearance.frames and appearance.frames[0].animation_phases > 1:
					animated.append(item)
			if not animated:
				continue
			# One replacement patch per tile. The highest animated member allows
			# static items above it to be reconstructed in the overlay.
			item = animated[-1]
			candidate = _candidate_geometry(renderer, item, tile.position.x, tile.position.y, tile.position.z, hook_south, hook_east)
			if not candidate:
				fallbacks += 1
				continue
			x, y = tile.position.x, tile.position.y
			if (
				x - x1 < radius or x2 - x < radius or y - y1 < radius or y2 - y < radius
				or any(
					(nx, ny) in danger
					for nx in range(x - radius, x + radius + 1)
					for ny in range(y - radius, y + radius + 1)
					if (nx, ny) != (x, y)
				)
			):
				fallbacks += 1
				continue

			appearance, frame, pattern_x, pattern_y, pattern_z, width, height, offset_x, offset_y = candidate
			phase_pixels = [
				_phase_pixels(renderer, frame, pattern_x, pattern_y, pattern_z, phase, width, height)
				for phase in range(frame.animation_phases)
			]
			underlay_pixels = _partition_pixels(tiles, renderer, tile, item, width, height, offset_x, offset_y, after=False)
			overlay_pixels = _partition_pixels(tiles, renderer, tile, item, width, height, offset_x, offset_y, after=True)
			if not _runtime_replacement_safe(width, height, underlay_pixels, phase_pixels, overlay_pixels, frame.default_start_phase):
				fallbacks += 1
				continue

			subtype = -1 if item.subtype is None else int(item.subtype)
			key = (
				f"{item.server_id}-{subtype}-{pattern_x}-{pattern_y}-{pattern_z}-"
				f"{int(hook_south)}-{int(hook_east)}-{width}x{height}-{offset_x}-{offset_y}"
			)
			frames = [f"data/environment-animations/frames/{key}/{phase}.png" for phase in range(frame.animation_phases)]
			if key not in made:
				for phase, relative in enumerate(frames):
					_write_png(output / relative, width, height, phase_pixels[phase])
				made.add(key)

			underlay = f"data/environment-animations/underlays/z{z}/{chunk_x}_{chunk_y}/{x}_{y}.png"
			_write_png(output / underlay, width, height, underlay_pixels)
			overlay = None
			if any(overlay_pixels[index] for index in range(3, len(overlay_pixels), 4)):
				overlay = f"data/environment-animations/overlays/z{z}/{chunk_x}_{chunk_y}/{x}_{y}.png"
				_write_png(output / overlay, width, height, overlay_pixels)

			ranges = _durations(frame)
			loop = -1 if frame.loop_type > 1 else frame.loop_type
			record = {
				"position": {"x": x, "y": y, "z": tile.position.z}, "serverId": item.server_id,
				"animationKey": key, "frames": frames, "underlay": underlay,
				"frameSizePx": [width, height], "drawOffsetPx": [offset_x, offset_y],
				"phaseDurationsMs": [max(1, (low + high) // 2) for low, high in ranges],
				"durationRangesMs": [[low, high] for low, high in ranges],
				"defaultStartPhase": frame.default_start_phase, "synchronized": frame.synchronized,
				"randomStartPhase": frame.random_start_phase, "loopType": loop, "loopCount": frame.loop_count,
				"policy": "cyclic-appearance",
			}
			if overlay:
				record["overlay"] = overlay
			if item.subtype is not None:
				record["subtype"] = item.subtype
			records.append(record)
			instances += 1

		if records:
			path = root / "chunks" / f"z{z}" / f"{chunk_x}_{chunk_y}.json"
			path.parent.mkdir(parents=True, exist_ok=True)
			path.write_text(json.dumps({"schemaVersion": 1, "records": records}, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
			chunks += 1

	stats = {"instances": instances, "uniqueAnimations": len(made), "chunks": chunks, "staticFallbacks": fallbacks}
	index = {
		"schemaVersion": 1, "animationZoom": ANIMATION_ZOOM, "overlapSafetyRadiusTiles": radius, "statistics": stats,
		"policy": {
			"cyclicAppearance": "browser animated from pinned object appearance phases; no GIF generation",
			"statefulAppearance": "not inferred; server-driven variants remain canonical static state",
			"eligibility": "one highest cyclic item per tile when exact underlay/phase/overlay replacement is proven safe",
			"geometry": "native 32x32, 32x64, 64x32 or 64x64 sprite-sheet geometry plus canonical shift/height displacement",
			"fallback": "unsupported, edge-risk, overlapping cross-tile risk or non-exact replacement remains deterministic static pixels",
		},
	}
	(root / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	return stats
