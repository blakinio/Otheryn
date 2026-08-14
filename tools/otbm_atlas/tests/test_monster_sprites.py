from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.monster_sprites import parse_monster_definition_index, parse_monster_outfits


class MonsterSpriteTests(unittest.TestCase):
	def test_parser_reads_demon_style_outfit_and_provenance(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); monsters = root / "monster"; monsters.mkdir()
			(monsters / "demon.lua").write_text(
				'local mType = Game.createMonsterType("Demon")\nmonster.outfit = { lookType = 35, lookHead = 1, lookBody = 2, lookLegs = 3, lookFeet = 4, lookAddons = 2, lookMount = 0 }',
				encoding="utf-8",
			)
			outfit = parse_monster_outfits(monsters, root)["demon"]
		self.assertEqual(outfit.key, "35-1-2-3-4-2")
		self.assertEqual(outfit.source, "monster/demon.lua")

	def test_missing_look_type_is_explicitly_unresolved(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); monsters = root / "monster"; monsters.mkdir()
			(monsters / "broken.lua").write_text('local mType = Game.createMonsterType("Broken")\nmonster.outfit = { lookHead = 1 }', encoding="utf-8")
			index = parse_monster_definition_index(monsters, root)
		self.assertEqual(index.resolve("broken"), (None, "missing-look-type"))

	def test_missing_outfit_is_explicitly_unresolved(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); monsters = root / "monster"; monsters.mkdir()
			(monsters / "broken.lua").write_text('local mType = Game.createMonsterType("Broken")', encoding="utf-8")
			index = parse_monster_definition_index(monsters, root)
		self.assertEqual(index.resolve("broken"), (None, "missing-outfit"))

	def test_identical_duplicate_keeps_first_sorted_source(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); monsters = root / "monster"; monsters.mkdir()
			body = 'local mType = Game.createMonsterType("Demon")\nmonster.outfit = { lookType = 35 }'
			(monsters / "b.lua").write_text(body, encoding="utf-8")
			(monsters / "a.lua").write_text(body, encoding="utf-8")
			outfit = parse_monster_outfits(monsters, root)["demon"]
		self.assertEqual(outfit.source, "monster/a.lua")

	def test_conflicting_duplicate_is_ambiguous(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); monsters = root / "monster"; monsters.mkdir()
			(monsters / "a.lua").write_text('local mType = Game.createMonsterType("Demon")\nmonster.outfit = { lookType = 35 }', encoding="utf-8")
			(monsters / "b.lua").write_text('local mType = Game.createMonsterType("demon")\nmonster.outfit = { lookType = 40 }', encoding="utf-8")
			index = parse_monster_definition_index(monsters, root)
		self.assertEqual(index.resolve("DEMON"), (None, "ambiguous-definition"))
		self.assertEqual(len(index.ambiguous), 1)


if __name__ == "__main__":
	unittest.main()
