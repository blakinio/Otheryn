"""Parse vendored CrystalServer monster definitions and enrich atlas monster spawns."""
from __future__ import annotations

from pathlib import Path
import re

from .creature_sprites import CreatureDefinitionIndex, CreatureOutfit, build_definition_index, enrich_creature_spawns

_NAME = re.compile(r'Game\.createMonsterType\(\s*["\']([^"\']+)["\']\s*\)')
_OUTFIT = re.compile(r'\bmonster\.outfit\s*=\s*\{(.*?)\}', re.DOTALL)
_VALUE = re.compile(r'\b(lookType|lookHead|lookBody|lookLegs|lookFeet|lookAddons)\s*=\s*(\d+)')


def _source(path: Path, source_root: Path) -> str:
	try:
		return path.relative_to(source_root).as_posix()
	except ValueError as error:
		raise ValueError(f"{path} is outside declared source root {source_root}") from error


def parse_monster_definition_index(
	monster_root: Path,
	source_root: Path | None = None,
	aliases: tuple[tuple[str, str], ...] = (),
) -> CreatureDefinitionIndex:
	"""Index literal `Game.createMonsterType` + `monster.outfit` definitions.

	Aliases are accepted only as explicit evidence supplied by the caller. The canonical atlas does
	not derive aliases from filenames, descriptions, folders, or other heuristics.
	"""
	root = source_root or monster_root.parent
	outfits: list[CreatureOutfit] = []
	invalid: list[tuple[str, str]] = []
	for path in sorted(monster_root.rglob("*.lua"), key=lambda value: value.relative_to(monster_root).as_posix()):
		text = path.read_text(encoding="utf-8")
		name_match = _NAME.search(text)
		if name_match is None:
			continue
		name = name_match.group(1)
		block = _OUTFIT.search(text)
		if block is None:
			invalid.append((name, "missing-outfit"))
			continue
		values = {key: int(value) for key, value in _VALUE.findall(block.group(1))}
		look_type = values.get("lookType", 0)
		if look_type <= 0:
			invalid.append((name, "missing-look-type"))
			continue
		outfits.append(CreatureOutfit(
			name=name,
			look_type=look_type,
			head=values.get("lookHead", 0),
			body=values.get("lookBody", 0),
			legs=values.get("lookLegs", 0),
			feet=values.get("lookFeet", 0),
			addons=values.get("lookAddons", 0),
			source=_source(path, root),
		))
	return build_definition_index(outfits, invalid, aliases)


def parse_monster_outfits(monster_root: Path, source_root: Path | None = None) -> dict[str, CreatureOutfit]:
	return parse_monster_definition_index(monster_root, source_root).resolved


def enrich_monster_spawns(
	asset_dir: Path,
	monster_root: Path,
	output: Path,
	records: list[dict[str, object]],
	source_root: Path | None = None,
) -> dict[str, int]:
	root = source_root or monster_root.parent
	definitions = parse_monster_definition_index(monster_root, root)
	return enrich_creature_spawns(
		asset_dir,
		output,
		records,
		definitions,
		"monster",
		_source(monster_root, root),
		_source(asset_dir, root) if asset_dir.is_relative_to(root) else asset_dir.as_posix(),
	)
