"""Deterministic region renderer using only canonical OTBM and Tibia assets."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterator

from .assets import Appearance, SpriteInfo, SpriteSheet, decode_sheet, encode_png, extract_sprite, load_object_appearances, load_sprite_catalog, sheet_for_sprite
from .semantic import Item, Tile, iter_map_records, walk_items


@dataclass(slots=True)
class RenderStats:
	tiles: int = 0
	ground_items: int = 0
	child_items: int = 0
	render_operations: int = 0


_MODERN_FLUID_COLORS=(0,1,7,3,3,2,4,3,5,6,7,2,5,3,5,6,3,3,8,10,9)

def _item_patterns(appearance:Appearance,frame:SpriteInfo,item:Item,x:int,y:int,z:int,hook_south:bool=False,hook_east:bool=False)->tuple[int,int,int]:
	px=x%frame.pattern_width;py=y%frame.pattern_height;pz=z%frame.pattern_depth
	if appearance.stackable and frame.pattern_width==4 and frame.pattern_height==2:
		count=item.subtype or 0
		if count<=0:px,py=0,0
		elif count<5:px,py=count-1,0
		elif count<10:px,py=0,1
		elif count<25:px,py=1,1
		elif count<50:px,py=2,1
		else:px,py=3,1
		pz=0
	elif appearance.hangable:
		px=1 if hook_south and frame.pattern_width>=2 else 2 if hook_east and frame.pattern_width>=3 else 0
		py=pz=0
	elif appearance.splash or appearance.fluid_container:
		subtype=item.subtype or 0;color=_MODERN_FLUID_COLORS[subtype] if 0<=subtype<len(_MODERN_FLUID_COLORS) else 0
		px=(color%4)%frame.pattern_width;py=(color//4)%frame.pattern_height;pz=0
	return px,py,pz


def _blend(canvas: bytearray, canvas_width: int, canvas_height: int, source: bytes, width: int, height: int, x: int, y: int) -> None:
	for source_y in range(height):
		destination_y = y + source_y
		if not 0 <= destination_y < canvas_height: continue
		for source_x in range(width):
			destination_x = x + source_x
			if not 0 <= destination_x < canvas_width: continue
			source_index = (source_y * width + source_x) * 4
			alpha = source[source_index + 3]
			if alpha == 0: continue
			destination_index = (destination_y * canvas_width + destination_x) * 4
			if alpha == 255:
				canvas[destination_index : destination_index + 4] = source[source_index : source_index + 4]
				continue
			inverse = 255 - alpha
			for channel in range(3):
				canvas[destination_index + channel] = (source[source_index + channel] * alpha + canvas[destination_index + channel] * inverse + 127) // 255
			canvas[destination_index + 3] = alpha + (canvas[destination_index + 3] * inverse + 127) // 255


class AssetRenderer:
	def __init__(self, asset_dir: Path) -> None:
		appearance_path = next(asset_dir.glob("appearances-*.dat"))
		self.appearances = load_object_appearances(appearance_path)
		self.sheets = load_sprite_catalog(asset_dir)
		self.sheet_cache: dict[Path, bytes] = {}
		self.sprite_cache: dict[int, tuple[int, int, bytes]] = {}
		self.missing_appearances: Counter[int] = Counter()
		self.missing_sprites: Counter[int] = Counter()
		self.appearance_ids: set[int] = set()
		self.sprite_ids: set[int] = set()

	def sprite(self, sprite_id: int) -> tuple[int, int, bytes] | None:
		if sprite_id in self.sprite_cache: return self.sprite_cache[sprite_id]
		sheet = sheet_for_sprite(self.sheets, sprite_id)
		if sheet is None:
			self.missing_sprites[sprite_id] += 1; return None
		if sheet.path not in self.sheet_cache:
			_width, _height, pixels = decode_sheet(sheet.path)
			self.sheet_cache[sheet.path] = pixels
		result = extract_sprite(sheet, self.sheet_cache[sheet.path], sprite_id)
		self.sprite_cache[sprite_id] = result
		return result

	def item_sprites(self,item:Item,position_x:int,position_y:int,position_z:int,hook_south:bool=False,hook_east:bool=False)->Iterator[tuple[Appearance,int,tuple[int,int,bytes]]]:
		appearance=self.appearances.get(item.server_id);self.appearance_ids.add(item.server_id)
		if appearance is None or not appearance.frames:
			self.missing_appearances[item.server_id]+=1;return
		frame=appearance.frames[0];px,py,pz=_item_patterns(appearance,frame,item,position_x,position_y,position_z,hook_south,hook_east);phase=frame.default_start_phase%frame.animation_phases
		for layer in range(frame.layers):
			index=((((phase*frame.pattern_depth+pz)*frame.pattern_height+py)*frame.pattern_width+px)*frame.layers+layer)
			if index>=len(frame.sprite_ids):self.missing_sprites[-item.server_id]+=1;continue
			sprite_id=frame.sprite_ids[index];self.sprite_ids.add(sprite_id);decoded=self.sprite(sprite_id)
			if decoded is not None:yield appearance,sprite_id,decoded


def render_tiles(tiles: Iterator[Tile], renderer: AssetRenderer, bounds: tuple[int, int, int, int, int]) -> tuple[bytes, dict[str, object]]:
	x1, x2, y1, y2, z = bounds
	width, height = (x2 - x1 + 1) * 32, (y2 - y1 + 1) * 32
	canvas = bytearray(width * height * 4)
	stats = RenderStats()
	start_missing_appearances = renderer.missing_appearances.copy()
	start_missing_sprites = renderer.missing_sprites.copy()
	appearance_ids: set[int] = set()
	sprite_ids: set[int] = set()
	for tile in tiles:
		if tile.position.z != z or not (x1 <= tile.position.x <= x2 and y1 <= tile.position.y <= y2): continue
		stats.tiles += 1
		items: list[Item] = []
		if tile.ground is not None:
			stats.ground_items += 1; items.append(tile.ground)
		stats.child_items += sum(1 for _item in walk_items(tile.items))
		# Item child nodes below top-level tile items are container contents, not visible map stack entries.
		items.extend(tile.items)
		hook_south=hook_east=False
		for visible_item in items:
			visible_appearance=renderer.appearances.get(visible_item.server_id)
			if visible_appearance is not None:
				hook_south=hook_south or visible_appearance.hook_direction==1
				hook_east=hook_east or visible_appearance.hook_direction==2
		for item in items:
			appearance_ids.add(item.server_id)
			for appearance, _sprite_id, (sprite_width, sprite_height, pixels) in renderer.item_sprites(item, tile.position.x, tile.position.y, tile.position.z, hook_south, hook_east):
				sprite_ids.add(_sprite_id)
				shift_x, shift_y = appearance.shift or (0, 0)
				draw_x = (tile.position.x - x1) * 32 - (sprite_width - 32) - shift_x
				draw_y = (tile.position.y - y1) * 32 - (sprite_height - 32) - shift_y
				if appearance.height: draw_x -= appearance.height; draw_y -= appearance.height
				_blend(canvas, width, height, pixels, sprite_width, sprite_height, draw_x, draw_y)
				stats.render_operations += 1
	report: dict[str, object] = {
		"bounds": list(bounds), "imageWidth": width, "imageHeight": height,
		"tiles": stats.tiles, "groundItems": stats.ground_items, "childItems": stats.child_items,
		"renderOperations": stats.render_operations,
		"uniqueAppearanceIds": len(appearance_ids), "uniqueSpriteIds": len(sprite_ids),
		"missingAppearances": dict(sorted((renderer.missing_appearances - start_missing_appearances).items())),
		"missingSprites": dict(sorted((renderer.missing_sprites - start_missing_sprites).items())),
		"animationPolicy": "first frame group, declared default_start_phase, no elapsed-time advancement",
		"itemPatternPolicy": "OTClient-compatible position, stack-count, hangable-hook and modern-fluid subtype patterns",
	}
	return encode_png(width, height, bytes(canvas)), report


def render_region(map_path: Path, asset_dir: Path, bounds: tuple[int, int, int, int, int]) -> tuple[bytes, dict[str, object]]:
	renderer = AssetRenderer(asset_dir)
	tiles = (record for record in iter_map_records(map_path, strict=True) if isinstance(record, Tile))
	return render_tiles(tiles, renderer, bounds)


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("map", type=Path); parser.add_argument("assets", type=Path)
	parser.add_argument("--bounds", nargs=5, type=int, required=True, metavar=("X1", "X2", "Y1", "Y2", "Z"))
	parser.add_argument("--output", type=Path, required=True); parser.add_argument("--report", type=Path)
	args = parser.parse_args()
	png, report = render_region(args.map, args.assets, tuple(args.bounds))
	args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_bytes(png)
	if args.report:
		args.report.parent.mkdir(parents=True, exist_ok=True)
		args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
	return 1 if report["missingAppearances"] or report["missingSprites"] else 0


if __name__ == "__main__": raise SystemExit(main())
