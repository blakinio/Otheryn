"""Shared deterministic creature outfit rendering and spawn enrichment."""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from .assets import (
	Appearance,
	FRAME_GROUP_OUTFIT_IDLE,
	FRAME_GROUP_OUTFIT_MOVING,
	SpriteInfo,
	decode_sheet,
	encode_png,
	extract_sprite,
	load_creature_appearances,
	load_sprite_catalog,
	sheet_for_sprite,
)

HSI_H_STEPS = 19
HSI_SI_VALUES = 7
_MASK_FIELDS = {(255, 255, 0, 255): "head", (255, 0, 0, 255): "body", (0, 255, 0, 255): "legs", (0, 0, 255, 255): "feet"}
_DIRECTION_PATTERNS = {"north": 0, "east": 1, "south": 2, "west": 3}
_FRAME_GROUP_NAMES = {FRAME_GROUP_OUTFIT_IDLE: "idle", FRAME_GROUP_OUTFIT_MOVING: "moving"}


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


def _sprite_index(frame: SpriteInfo, layer: int, x_pattern: int, y_pattern: int, z_pattern: int, phase: int) -> int:
	return ((((phase * frame.pattern_depth + z_pattern) * frame.pattern_height + y_pattern) * frame.pattern_width + x_pattern) * frame.layers + layer)


def _supported_directions(frame: SpriteInfo) -> tuple[str, ...]:
	if frame.pattern_width == 1:
		return ("south",)
	if frame.pattern_width >= 4:
		return ("north", "east", "south", "west")
	return ()


def _direction_pattern(frame: SpriteInfo, direction: str) -> int | None:
	if direction not in _DIRECTION_PATTERNS:
		return None
	if frame.pattern_width == 1:
		return 0
	if frame.pattern_width >= 4:
		return _DIRECTION_PATTERNS[direction]
	return None


def _duration_ranges(frame: SpriteInfo) -> list[tuple[int, int]]:
	# assets.py maps protobuf zero durations to 1/1. Match the existing object-animation
	# safety rule by substituting the first non-1ms range when the canonical file used 0/0.
	ranges = list(frame.phase_durations)
	fallback = next((value for value in ranges if value != (1, 1)), (1, 1))
	return [fallback if value == (1, 1) else value for value in ranges]


class CreatureSpriteRenderer:
	"""Render canonical creature outfits and animation phases with bounded sprite caches."""

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

	def _render_frame_with_status(self, outfit: CreatureOutfit, frame: SpriteInfo, x_pattern: int, phase: int) -> tuple[bytes | None, str]:
		if not frame.sprite_ids:
			return None, "missing-sprite"
		if not 0 <= x_pattern < frame.pattern_width:
			return None, "unsupported-direction-pattern"
		z_pattern = 0
		phase %= max(1, frame.animation_phases)
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

	def render_with_status(self, outfit: CreatureOutfit) -> tuple[bytes | None, str]:
		appearance: Appearance | None = self.appearances.get(outfit.look_type)
		if appearance is None or not appearance.frames:
			return None, "missing-creature-appearance"
		frame = appearance.frames[0]
		# Preserve the established canonical static marker: south-facing default phase.
		return self._render_frame_with_status(outfit, frame, 2 % frame.pattern_width, frame.default_start_phase)

	def render_animation_with_status(self, outfit: CreatureOutfit) -> tuple[dict[str, object] | None, str]:
		appearance: Appearance | None = self.appearances.get(outfit.look_type)
		if appearance is None or not appearance.frames:
			return None, "missing-creature-appearance"
		groups: dict[str, dict[str, object]] = {}
		for frame in appearance.frames:
			group_name = _FRAME_GROUP_NAMES.get(frame.frame_group_type)
			if group_name is None:
				continue
			if group_name in groups:
				return None, "ambiguous-frame-group"
			directions = _supported_directions(frame)
			if not directions:
				continue
			direction_frames: dict[str, list[bytes]] = {}
			group_failed = False
			for direction in directions:
				x_pattern = _direction_pattern(frame, direction)
				if x_pattern is None:
					group_failed = True
					break
				payloads: list[bytes] = []
				for phase in range(frame.animation_phases):
					payload, status = self._render_frame_with_status(outfit, frame, x_pattern, phase)
					if payload is None:
						group_failed = True
						break
					payloads.append(payload)
				if group_failed:
					break
				direction_frames[direction] = payloads
			if group_failed:
				continue
			ranges = _duration_ranges(frame)
			loop = -1 if frame.loop_type > 1 else frame.loop_type
			groups[group_name] = {
				"frameGroupType": frame.frame_group_type,
				"frameGroupId": frame.frame_group_id,
				"animationPhases": frame.animation_phases,
				"phaseDurationsMs": [max(1, (low + high) // 2) for low, high in ranges],
				"durationRangesMs": [[low, high] for low, high in ranges],
				"defaultStartPhase": frame.default_start_phase % max(1, frame.animation_phases),
				"synchronized": frame.synchronized,
				"randomStartPhase": frame.random_start_phase,
				"loopType": loop,
				"loopCount": frame.loop_count,
				"directions": list(directions),
				"directionFrames": direction_frames,
			}
		if not groups:
			return None, "no-renderable-frame-group"
		presentation_group = next((name for name in ("idle", "moving") if name in groups and int(groups[name]["animationPhases"]) > 1), None)
		if presentation_group is None:
			return None, "static-only-appearance"
		return {
			"schemaVersion": 1,
			"presentationGroup": presentation_group,
			"presentationDirection": "south",
			"groups": groups,
			"policy": "canonical-frame-groups-no-spatial-movement",
		}, "resolved"

	def render(self, outfit: CreatureOutfit) -> bytes | None:
		return self.render_with_status(outfit)[0]


def _write_animation(sprite_root: Path, kind: str, outfit: CreatureOutfit, animation: dict[str, object]) -> str:
	root = sprite_root / outfit.key
	public_groups: dict[str, object] = {}
	groups = animation["groups"]
	assert isinstance(groups, dict)
	for group_name, raw_group in groups.items():
		assert isinstance(raw_group, dict)
		group = {key: value for key, value in raw_group.items() if key != "directionFrames"}
		direction_frames = raw_group["directionFrames"]
		assert isinstance(direction_frames, dict)
		frames: dict[str, list[str]] = {}
		for direction, payloads in direction_frames.items():
			assert isinstance(payloads, list)
			paths: list[str] = []
			for phase, payload in enumerate(payloads):
				relative = f"data/{kind}-sprites/{outfit.key}/{group_name}/{direction}/{phase}.png"
				path = sprite_root.parents[1] / relative
				path.parent.mkdir(parents=True, exist_ok=True)
				path.write_bytes(payload)
				paths.append(relative)
			frames[str(direction)] = paths
		group["frames"] = frames
		group["animationKey"] = f"{kind}-{outfit.key}-{group_name}"
		public_groups[str(group_name)] = group
	manifest = {key: value for key, value in animation.items() if key != "groups"}
	manifest["outfitKey"] = outfit.key
	manifest["groups"] = public_groups
	root.mkdir(parents=True, exist_ok=True)
	(root / "animation.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	return f"data/{kind}-sprites/{outfit.key}/animation.json"


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
	animations: dict[str, str] = {}
	failures: dict[str, str] = {}
	animation_failures: dict[str, str] = {}
	resolved = unresolved = animated_spawns = 0
	status_counts: dict[str, int] = {}
	animation_status_counts: dict[str, int] = {}
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
				animation_method = getattr(renderer, "render_animation_with_status", None)
				if animation_method is not None:
					animation, animation_status = animation_method(outfit)
					if animation is None:
						animation_failures[outfit.key] = animation_status
					else:
						animations[outfit.key] = _write_animation(sprite_root, kind, outfit, animation)
		if path is None:
			status = failures[outfit.key]
			record["spriteStatus"] = status
			status_counts[status] = status_counts.get(status, 0) + 1
			unresolved += 1
			continue
		record["sprite"] = path
		record["spriteStatus"] = "resolved"
		status_counts["resolved"] = status_counts.get("resolved", 0) + 1
		animation_path = animations.get(outfit.key)
		if animation_path is not None:
			record["spriteAnimation"] = animation_path
			record["spriteAnimationStatus"] = "resolved"
			animation_status_counts["resolved"] = animation_status_counts.get("resolved", 0) + 1
			animated_spawns += 1
		else:
			animation_status = animation_failures.get(outfit.key, "static-only-renderer")
			record["spriteAnimationStatus"] = animation_status
			animation_status_counts[animation_status] = animation_status_counts.get(animation_status, 0) + 1
		resolved += 1
	statistics = {
		"uniqueSprites": len(generated),
		"uniqueAnimations": len(animations),
		"resolvedSpawns": resolved,
		"animatedSpawns": animated_spawns,
		"unresolvedSpawns": unresolved,
		"ambiguousDefinitions": len(definitions.ambiguous),
	}
	index = {
		"schemaVersion": 2,
		"sprites": sorted(generated.values()),
		"animations": sorted(animations.values()),
		"statistics": statistics,
		"statusCounts": dict(sorted(status_counts.items())),
		"animationStatusCounts": dict(sorted(animation_status_counts.items())),
		"provenance": {"definitionRoot": definition_root, "appearanceAssetRoot": asset_root},
		"policy": {"movement": "spawn positions remain factual; animation never simulates pathing", "fallback": "unsupported animation retains canonical static sprite"},
	}
	(sprite_root / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	return statistics