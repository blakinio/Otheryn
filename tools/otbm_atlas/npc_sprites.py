"""Generate deterministic, canonical Tibia NPC outfit sprites for the atlas."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re

from .assets import Appearance, encode_png, load_creature_appearances, load_sprite_catalog, decode_sheet, extract_sprite, sheet_for_sprite


HSI_H_STEPS = 19
HSI_SI_VALUES = 7
_NAME = re.compile(r'local\s+internalNpcName\s*=\s*["\']([^"\']+)["\']')
_OUTFIT = re.compile(r'npcConfig\.outfit\s*=\s*\{(.*?)\}', re.DOTALL)
_VALUE = re.compile(r'\b(lookType|lookHead|lookBody|lookLegs|lookFeet|lookAddons)\s*=\s*(\d+)')


@dataclass(frozen=True)
class NpcOutfit:
	name: str
	look_type: int
	head: int
	body: int
	legs: int
	feet: int
	addons: int
	source: str

	@property
	def key(self) -> str:
		return f"{self.look_type}-{self.head}-{self.body}-{self.legs}-{self.feet}-{self.addons}"

	def public(self, path: str) -> dict[str, object]:
		return {"lookType": self.look_type, "lookHead": self.head, "lookBody": self.body, "lookLegs": self.legs, "lookFeet": self.feet, "lookAddons": self.addons, "outfitSource": self.source, "sprite": path}


def outfit_color(value: int) -> tuple[int, int, int]:
	"""Decode Tibia's 0..132 HSI outfit colour value to an RGB triplet."""
	if not 0 <= value < HSI_H_STEPS * HSI_SI_VALUES:
		return (0, 0, 0)
	if value % HSI_H_STEPS == 0:
		gray = round((1 - value / (HSI_H_STEPS * HSI_SI_VALUES)) * 255)
		return (gray, gray, gray)
	hue = (value % HSI_H_STEPS) / 18
	saturation, intensity = ((.25, 1), (.25, .75), (.5, .75), (.667, .75), (1, 1), (1, .75), (1, .5))[value // HSI_H_STEPS]
	minimum = intensity * (1 - saturation)
	if hue < 1 / 6:
		channels = (intensity, minimum + (intensity - minimum) * 6 * hue, minimum)
	elif hue < 2 / 6:
		channels = (intensity - (intensity - minimum) * (6 * hue - 1), intensity, minimum)
	elif hue < 3 / 6:
		channels = (minimum, intensity, minimum + (intensity - minimum) * (6 * hue - 2))
	elif hue < 4 / 6:
		channels = (minimum, intensity - (intensity - minimum) * (6 * hue - 3), intensity)
	elif hue < 5 / 6:
		channels = (minimum + (intensity - minimum) * (6 * hue - 4), minimum, intensity)
	else:
		channels = (intensity, minimum, intensity - (intensity - minimum) * (6 * hue - 5))
	return tuple(round(channel * 255) for channel in channels)


def parse_npc_outfits(npc_root: Path, source_root: Path | None = None) -> dict[str, NpcOutfit]:
	"""Read explicit npcConfig.outfit records; dynamic definitions stay absent."""
	root = source_root or npc_root.parent
	result: dict[str, NpcOutfit] = {}
	ambiguous: set[str] = set()
	for path in sorted(npc_root.rglob("*.lua"), key=lambda value: value.relative_to(npc_root).as_posix()):
		text = path.read_text(encoding="utf-8")
		name = _NAME.search(text); block = _OUTFIT.search(text)
		if name is None or block is None:
			continue
		values = {key: int(value) for key, value in _VALUE.findall(block.group(1))}
		look_type = values.get("lookType", 0)
		if look_type <= 0:
			continue  # lookTypeEx is an item appearance, not a creature outfit.
		outfit = NpcOutfit(name.group(1), look_type, values.get("lookHead", 0), values.get("lookBody", 0), values.get("lookLegs", 0), values.get("lookFeet", 0), values.get("lookAddons", 0), path.relative_to(root).as_posix())
		key = outfit.name.casefold()
		if key in ambiguous:
			continue
		if key in result and result[key].key != outfit.key:
			# Provenance is not visual state. Only genuinely different visual outfits conflict.
			result.pop(key); ambiguous.add(key); continue
		if key not in result:
			result[key] = outfit
	return result


def _blend(canvas: bytearray, source: bytes, width: int, height: int) -> None:
	for index in range(0, width * height * 4, 4):
		alpha = source[index + 3]
		if not alpha:
			continue
		inverse = 255 - alpha
		for channel in range(3):
			canvas[index + channel] = (source[index + channel] * alpha + canvas[index + channel] * inverse + 127) // 255
		canvas[index + 3] = alpha + (canvas[index + 3] * inverse + 127) // 255


def _enabled_y_patterns(pattern_height: int, addons: int) -> tuple[int, ...]:
	return tuple([0] + [value for value in range(1, pattern_height) if addons & (1 << (value - 1))])


def _sprite_index(frame, layer: int, x_pattern: int, y_pattern: int, z_pattern: int, phase: int) -> int:
	return ((((phase * frame.pattern_depth + z_pattern) * frame.pattern_height + y_pattern) * frame.pattern_width + x_pattern) * frame.layers + layer)


def _recolor_outfit_mask(pixels: bytes, outfit: NpcOutfit) -> bytes:
	# Pinned OTClient: yellow=head, red=body, green=legs, blue=feet.
	fields = {(255, 255, 0): outfit.head, (255, 0, 0): outfit.body, (0, 255, 0): outfit.legs, (0, 0, 255): outfit.feet}
	mask = bytearray(len(pixels))
	for index in range(0, len(pixels), 4):
		red, green, blue, alpha = pixels[index:index + 4]
		if not alpha or (red, green, blue) not in fields:
			continue
		mask[index:index + 3] = bytes(outfit_color(fields[(red, green, blue)]))
		mask[index + 3] = alpha
	return bytes(mask)


class NpcSpriteRenderer:
	def __init__(self, asset_dir: Path) -> None:
		appearance_path = next(asset_dir.glob("appearances-*.dat"))
		self.appearances = load_creature_appearances(appearance_path)
		self.sheets = load_sprite_catalog(asset_dir)
		self.sheet_cache: dict[Path, bytes] = {}
		self.sprite_cache: dict[int, tuple[int, int, bytes]] = {}

	def sprite(self, sprite_id: int) -> tuple[int, int, bytes] | None:
		if sprite_id in self.sprite_cache:
			return self.sprite_cache[sprite_id]
		sheet = sheet_for_sprite(self.sheets, sprite_id)
		if sheet is None:
			return None
		if sheet.path not in self.sheet_cache:
			self.sheet_cache[sheet.path] = decode_sheet(sheet.path)[2]
		result = extract_sprite(sheet, self.sheet_cache[sheet.path], sprite_id)
		self.sprite_cache[sprite_id] = result
		return result

	def render(self, outfit: NpcOutfit) -> bytes | None:
		appearance: Appearance | None = self.appearances.get(outfit.look_type)
		if appearance is None or not appearance.frames:
			return None
		frame = appearance.frames[0]
		if not frame.sprite_ids:
			return None
		x_pattern = 2 % frame.pattern_width  # deterministic south-facing atlas pose
		z_pattern = 0
		phase = frame.default_start_phase % frame.animation_phases
		canvas = None; width = height = 0
		for y_pattern in _enabled_y_patterns(frame.pattern_height, outfit.addons):
			base_index = _sprite_index(frame, 0, x_pattern, y_pattern, z_pattern, phase)
			if base_index >= len(frame.sprite_ids):
				return None
			base = self.sprite(frame.sprite_ids[base_index])
			if base is None:
				return None
			if canvas is None:
				width, height = base[0], base[1]; canvas = bytearray(width * height * 4)
			elif (base[0], base[1]) != (width, height):
				return None
			_blend(canvas, base[2], width, height)
			if frame.layers > 1:
				mask_index = _sprite_index(frame, 1, x_pattern, y_pattern, z_pattern, phase)
				if mask_index >= len(frame.sprite_ids):
					return None
				mask = self.sprite(frame.sprite_ids[mask_index])
				if mask is None or (mask[0], mask[1]) != (width, height):
					return None
				_blend(canvas, _recolor_outfit_mask(mask[2], outfit), width, height)
		if canvas is None:
			return None
		return encode_png(width, height, bytes(canvas))



def enrich_npc_spawns(asset_dir: Path, scripts_dir: Path, output: Path, records: list[dict[str, object]]) -> dict[str, int]:
	definitions = parse_npc_outfits(scripts_dir / "npc", scripts_dir)
	renderer = NpcSpriteRenderer(asset_dir)
	sprite_root = output / "data" / "npc-sprites"; sprite_root.mkdir(parents=True, exist_ok=True)
	generated: dict[str, str] = {}; resolved = 0; unresolved = 0
	for record in records:
		outfit = definitions.get(str(record["name"]).casefold())
		if outfit is None:
			unresolved += 1; continue
		path = generated.get(outfit.key)
		if path is None:
			payload = renderer.render(outfit)
			if payload is None:
				unresolved += 1; continue
			path = f"data/npc-sprites/{outfit.key}.png"
			(sprite_root / f"{outfit.key}.png").write_bytes(payload)
			generated[outfit.key] = path
		record.update(outfit.public(path)); resolved += 1
	(sprite_root / "index.json").write_text(json.dumps({"schemaVersion": 1, "sprites": sorted(generated.values()), "statistics": {"uniqueSprites": len(generated), "resolvedSpawns": resolved, "unresolvedSpawns": unresolved}}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	return {"uniqueSprites": len(generated), "resolvedSpawns": resolved, "unresolvedSpawns": unresolved}


def enrich_existing_atlas(asset_dir: Path, scripts_dir: Path, output: Path) -> dict[str, int]:
	spawns_path = output / "data" / "spawns.json"; report = json.loads(spawns_path.read_text(encoding="utf-8"))
	statistics = enrich_npc_spawns(asset_dir, scripts_dir, output, report["npcSpawns"])
	spawns_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	by_name = {str(record["name"]).casefold(): record for record in report["npcSpawns"]}
	for path in (output / "data" / "chunks").glob("z*/*.json"):
		content = json.loads(path.read_text(encoding="utf-8"))
		for record in content.get("npcSpawns", []):
			updated = by_name.get(str(record.get("name", "")).casefold())
			if updated:
				record.update({key: value for key, value in updated.items() if key.startswith("look") or key in {"outfitSource", "sprite"}})
		path.write_text(json.dumps(content, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
	return statistics


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("assets", type=Path); parser.add_argument("scripts", type=Path); parser.add_argument("output", type=Path)
	args = parser.parse_args(); print(json.dumps(enrich_existing_atlas(args.assets, args.scripts, args.output), sort_keys=True)); return 0


if __name__ == "__main__":
	raise SystemExit(main())
