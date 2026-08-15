"""Parse canonical NPC definitions and enrich atlas spawns with shared creature sprites."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from .creature_sprites import (
	CreatureDefinitionIndex,
	CreatureOutfit,
	CreatureSpriteRenderer,
	_enabled_y_patterns,
	_recolor_outfit_mask,
	build_definition_index,
	enrich_creature_spawns,
	outfit_color,
)

_NAME = re.compile(r'local\s+internalNpcName\s*=\s*["\']([^"\']+)["\']')
_OUTFIT = re.compile(r'npcConfig\.outfit\s*=\s*\{(.*?)\}', re.DOTALL)
_VALUE = re.compile(r'\b(lookType|lookHead|lookBody|lookLegs|lookFeet|lookAddons)\s*=\s*(\d+)')

# Compatibility names retained for callers/tests introduced with PR #378.
NpcOutfit = CreatureOutfit
NpcSpriteRenderer = CreatureSpriteRenderer


def _source(path: Path, source_root: Path) -> str:
	try:
		return path.relative_to(source_root).as_posix()
	except ValueError as error:
		raise ValueError(f"{path} is outside declared source root {source_root}") from error


def parse_npc_definition_index(npc_root: Path, source_root: Path | None = None) -> CreatureDefinitionIndex:
	root = source_root or npc_root.parent
	outfits: list[CreatureOutfit] = []
	invalid: list[tuple[str, str]] = []
	for path in sorted(npc_root.rglob("*.lua"), key=lambda value: value.relative_to(npc_root).as_posix()):
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
	return build_definition_index(outfits, invalid)


def parse_npc_outfits(npc_root: Path, source_root: Path | None = None) -> dict[str, CreatureOutfit]:
	"""Compatibility view containing only unambiguous, renderable NPC definitions."""
	return parse_npc_definition_index(npc_root, source_root).resolved


def enrich_npc_spawns(
	asset_dir: Path,
	npc_root: Path,
	output: Path,
	records: list[dict[str, object]],
	source_root: Path | None = None,
) -> dict[str, int]:
	# PR #378 accepted a Crystal data root and appended /npc; keep that call shape without restoring a datapack fallback.
	definition_root = npc_root / "npc" if (npc_root / "npc").is_dir() else npc_root
	root = source_root or definition_root.parent
	definitions = parse_npc_definition_index(definition_root, root)
	return enrich_creature_spawns(
		asset_dir,
		output,
		records,
		definitions,
		"npc",
		_source(definition_root, root),
		_source(asset_dir, root) if asset_dir.is_relative_to(root) else asset_dir.as_posix(),
	)


def enrich_existing_atlas(asset_dir: Path, npc_root: Path, output: Path, source_root: Path | None = None) -> dict[str, int]:
	spawns_path = output / "data" / "spawns.json"
	report = json.loads(spawns_path.read_text(encoding="utf-8"))
	statistics = enrich_npc_spawns(asset_dir, npc_root, output, report["npcSpawns"], source_root)
	spawns_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	by_name = {str(record["name"]).casefold(): record for record in report["npcSpawns"]}
	for path in (output / "data" / "chunks").glob("z*/*.json"):
		content = json.loads(path.read_text(encoding="utf-8"))
		for record in content.get("npcSpawns", []):
			updated = by_name.get(str(record.get("name", "")).casefold())
			if updated:
				record.update({key: value for key, value in updated.items() if key.startswith("look") or key in {"outfitSource", "sprite", "spriteStatus"}})
		path.write_text(json.dumps(content, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
	return statistics


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("assets", type=Path)
	parser.add_argument("npc_root", type=Path)
	parser.add_argument("output", type=Path)
	parser.add_argument("--source-root", type=Path)
	args = parser.parse_args()
	print(json.dumps(enrich_existing_atlas(args.assets, args.npc_root, args.output, args.source_root), sort_keys=True))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
