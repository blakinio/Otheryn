"""Shared deterministic creature outfit rendering and spawn enrichment."""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from .assets import Appearance, decode_sheet, encode_png, extract_sprite, load_creature_appearances, load_sprite_catalog, sheet_for_sprite

HSI_H_STEPS = 19
HSI_SI_VALUES = 7
_MASK_FIELDS = {(255, 255, 0, 255): "head", (255, 0, 0, 255): "body", (0, 255, 0, 255): "legs", (0, 0, 255, 255): "feet"}


@dataclass(frozen=True)
class CreatureOutfit:
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

	def public(self) -> dict[str, object]:
		return {
			"lookType": self.look_type,
			"lookHead": self.head,
			"lookBody": self.body,
			"lookLegs": self.legs,
			"lookFeet": self.feet,
			"lookAddons": self.addons,
			"outfitSource": self.source,
		}


@dataclass(frozen=True)
class CreatureDefinitionIndex:
	resolved: dict[str, CreatureOutfit]
	ambiguous: frozenset[str]
	invalid: dict[str, str]
	aliases: dict[str, str]

	def resolve(self, name: str) -> tuple[CreatureOutfit | None, str]:
		key = name.casefold()
		canonical = self.aliases.get(key, key)
		if canonical in self.ambiguous or key in self.ambiguous:
			return None, "ambiguous-definition"
		if canonical in self.invalid:
			return None, self.invalid[canonical]
		outfit = self.resolved.get(canonical)
		return (outfit, "resolved") if outfit is not None else (None, "missing-definition")


def build_definition_index(
	outfits: Iterable[CreatureOutfit],
	invalid: Iterable[tuple[str, str]] = (),
	aliases: Iterable[tuple[str, str]] = (),
) -> CreatureDefinitionIndex:
	resolved: dict[str, CreatureOutfit] = {}
	ambiguous: set[str] = set()
	invalid_map: dict[str, str] = {}
	for name, reason in invalid:
		key = name.casefold()
		if key not in invalid_map:
			invalid_map[key] = reason
	for outfit in outfits:
		key = outfit.name.casefold()
		if key in ambiguous:
			continue
		previous = resolved.get(key)
		if previous is not None and previous.key != outfit.key:
			resolved.pop(key, None)
			ambiguous.add(key)
			continue
		if previous is None:
			resolved[key] = outfit
	if ambiguous:
		for key in ambiguous:
			invalid_map.pop(key, None)
	for key in tuple(invalid_map):
		if key in resolved:
			# A duplicate canonical definition that is both concrete and incomplete is not safe to choose.
			resolved.pop(key, None)
			invalid_map.pop(key, None)
			ambiguous.add(key)
	alias_map: dict[str, str] = {}
	for alias, canonical_name in aliases:
		alias_key, canonical_key = alias.casefold(), canonical_name.casefold()
		if alias_key == canonical_key:
			continue
		previous = alias_map.get(alias_key)
		if previous is not None and previous != canonical_key:
			ambiguous.add(alias_key)
			alias_map.pop(alias_key, None)
			continue
		alias_map[alias_key] = canonical_key
	for alias_key, canonical_key in tuple(alias_map.items()):
		target = resolved.get(canonical_key)
		alias_outfit = resolved.get(alias_key)
		if target is None or alias_key in invalid_map or alias_key in ambiguous:
			alias_map.pop(alias_key, None)
			continue
		if alias_outfit is not None:
			alias_map.pop(alias_key, None)
			if alias_outfit.key != target.key:
				ambiguous.add(alias_key)
	return CreatureDefinitionIndex(resolved, frozenset(ambiguous), invalid_map, alias_map)


def outfit_color(value: int) -> tuple[int, int, int]:
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


def _blend(canvas: bytearray, source: bytes, width: int, height: int) -> None:
	for index in range(0, width * height * 4, 4):
		alpha = source[index + 3]
		if not alpha:
			continue
		inverse = 255 - alpha
		for channel in range(3):
			canvas[index + channel] = (source[index + channel] * alpha + canvas[index + channel] * inverse + 127) // 255
		canvas[index + 3] = alpha + (canvas[index + 3] * inverse + 127) // 255


def _recolor_outfit_mask(pixels: bytes, outfit: CreatureOutfit) -> bytes:
	result = bytearray(len(pixels))
	for index in range(0, len(pixels), 4):
		field = _MASK_FIELDS.get(tuple(pixels[index:index + 4]))
		if field is None:
			continue
		result[index:index + 3] = bytes(outfit_color(getattr(outfit, field)))
		result[index + 3] = 255
	return bytes(result)


def _apply_outfit_mask(canvas: bytearray, mask: bytes, width: int, height: int, outfit: CreatureOutfit) -> None:
	for index in range(0, width * height * 4, 4):
		field = _MASK_FIELDS.get(tuple(mask[index:index + 4]))
		if field is None:
			continue
		color = outfit_color(getattr(outfit, field))
		for channel in range(3):
			canvas[index + channel] = (canvas[index + channel] * color[channel] + 127) // 255


def _enabled_y_patterns(pattern_height: int, addons: int) -> tuple[int, ...]:
	return tuple([0] + [value for value in range(1, pattern_height) if addons & (1 << (value - 1))])


def _sprite_index(frame, layer: int, x_pattern: int, y_pattern: int, z_pattern: int, phase: int) -> int:
	return ((((phase * frame.pattern_depth + z_pattern) * frame.pattern_height + y_pattern) * frame.pattern_width + x_pattern) * frame.layers + layer)


class CreatureSpriteRenderer:
	"""Render one static canonical creature outfit with bounded decoded-sheet caching."""

	def __init__(self, asset_dir: Path, sheet_cache_limit: int = 48, sprite_cache_limit: int = 4096) -> None:
		appearance_paths = sorted(asset_dir.glob("appearances-*.dat"))
		if len(appearance_paths) != 1:
			raise ValueError(f"expected exactly one appearances-*.dat in {asset_dir}, found {len(appearance_paths)}")
		self.appearances = load_creature_appearances(appearance_paths[0])
		self.sheets = load_sprite_catalog(asset_dir)
		self.sheet_cache: OrderedDict[Path, bytes] = OrderedDict()
		self.sprite_cache: OrderedDict[int, tuple[int, int, bytes]] = OrderedDict()
		self.sheet_cache_limit = max(1, sheet_cache_limit)
		self.sprite_cache_limit = max(1, sprite_cache_limit)

	def sprite(self, sprite_id: int) -> tuple[int, int, bytes] | None:
		cached = self.sprite_cache.pop(sprite_id, None)
		if cached is not None:
			self.sprite_cache[sprite_id] = cached
			return cached
		sheet = sheet_for_sprite(self.sheets, sprite_id)
		if sheet is None:
			return None
		pixels = self.sheet_cache.pop(sheet.path, None)
		if pixels is None:
			pixels = decode_sheet(sheet.path)[2]
		self.sheet_cache[sheet.path] = pixels
		while len(self.sheet_cache) > self.sheet_cache_limit:
			self.sheet_cache.popitem(last=False)
		result = extract_sprite(sheet, pixels, sprite_id)
		self.sprite_cache[sprite_id] = result
		while len(self.sprite_cache) > self.sprite_cache_limit:
			self.sprite_cache.popitem(last=False)
		return result

	def render_with_status(self, outfit: CreatureOutfit) -> tuple[bytes | None, str]:
		appearance: Appearance | None = self.appearances.get(outfit.look_type)
		if appearance is None or not appearance.frames:
			return None, "missing-creature-appearance"
		frame = appearance.frames[0]
		if not frame.sprite_ids:
			return None, "missing-sprite"
		x_pattern = 2 % frame.pattern_width
		z_pattern = 0
		phase = frame.default_start_phase % frame.animation_phases
		canvas: bytearray | None = None
		width = height = 0
		for y_pattern in _enabled_y_patterns(frame.pattern_height, outfit.addons):
			base_index = _sprite_index(frame, 0, x_pattern, y_pattern, z_pattern, phase)
			if base_index >= len(frame.sprite_ids):
				return None, "missing-sprite"
			base = self.sprite(frame.sprite_ids[base_index])
			if base is None:
				return None, "missing-sprite"
			if canvas is None:
				width, height = base[0], base[1]
				canvas = bytearray(width * height * 4)
			elif (base[0], base[1]) != (width, height):
				return None, "inconsistent-sprite-geometry"
			_blend(canvas, base[2], width, height)
			if frame.layers > 1:
				mask_index = _sprite_index(frame, 1, x_pattern, y_pattern, z_pattern, phase)
				if mask_index >= len(frame.sprite_ids):
					return None, "missing-sprite"
				mask = self.sprite(frame.sprite_ids[mask_index])
				if mask is None:
					return None, "missing-sprite"
				if (mask[0], mask[1]) != (width, height):
					return None, "inconsistent-sprite-geometry"
				_apply_outfit_mask(canvas, mask[2], width, height, outfit)
		if canvas is None:
			return None, "missing-sprite"
		return encode_png(width, height, bytes(canvas)), "resolved"

	def render(self, outfit: CreatureOutfit) -> bytes | None:
		return self.render_with_status(outfit)[0]


def enrich_creature_spawns(
	asset_dir: Path,
	output: Path,
	records: list[dict[str, object]],
	definitions: CreatureDefinitionIndex,
	kind: str,
	definition_root: str,
	asset_root: str,
	renderer: CreatureSpriteRenderer | None = None,
) -> dict[str, int]:
	if kind not in {"npc", "monster"}:
		raise ValueError(f"unsupported creature kind {kind!r}")
	renderer = renderer or CreatureSpriteRenderer(asset_dir)
	sprite_root = output / "data" / f"{kind}-sprites"
	sprite_root.mkdir(parents=True, exist_ok=True)
	generated: dict[str, str] = {}
	failures: dict[str, str] = {}
	resolved = unresolved = 0
	status_counts: dict[str, int] = {}
	for record in records:
		outfit, definition_status = definitions.resolve(str(record.get("name", "")))
		if outfit is None:
			record["spriteStatus"] = definition_status
			status_counts[definition_status] = status_counts.get(definition_status, 0) + 1
			unresolved += 1
			continue
		record.update(outfit.public())
		path = generated.get(outfit.key)
		if path is None and outfit.key not in failures:
			payload, render_status = renderer.render_with_status(outfit)
			if payload is None:
				failures[outfit.key] = render_status
			else:
				path = f"data/{kind}-sprites/{outfit.key}.png"
				(sprite_root / f"{outfit.key}.png").write_bytes(payload)
				generated[outfit.key] = path
		if path is None:
			status = failures[outfit.key]
			record["spriteStatus"] = status
			status_counts[status] = status_counts.get(status, 0) + 1
			unresolved += 1
			continue
		record["sprite"] = path
		record["spriteStatus"] = "resolved"
		status_counts["resolved"] = status_counts.get("resolved", 0) + 1
		resolved += 1
	statistics = {
		"uniqueSprites": len(generated),
		"resolvedSpawns": resolved,
		"unresolvedSpawns": unresolved,
		"ambiguousDefinitions": len(definitions.ambiguous),
	}
	index = {
		"schemaVersion": 1,
		"sprites": sorted(generated.values()),
		"statistics": statistics,
		"statusCounts": dict(sorted(status_counts.items())),
		"provenance": {"definitionRoot": definition_root, "appearanceAssetRoot": asset_root},
	}
	(sprite_root / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	return statistics
