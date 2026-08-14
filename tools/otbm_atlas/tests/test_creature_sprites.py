from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.assets import Appearance, SpriteInfo
from tools.otbm_atlas.creature_sprites import CreatureOutfit, CreatureSpriteRenderer, build_definition_index, enrich_creature_spawns


def outfit(name: str = "Demon", look_type: int = 35, source: str = "vendor/monster/demon.lua") -> CreatureOutfit:
	return CreatureOutfit(name, look_type, 0, 0, 0, 0, 0, source)


class FakeRenderer:
	def __init__(self, payload: bytes | None = b"png", status: str = "resolved") -> None:
		self.payload = payload
		self.status = status
		self.calls = 0

	def render_with_status(self, value: CreatureOutfit) -> tuple[bytes | None, str]:
		self.calls += 1
		return self.payload, self.status


class CreatureSpriteTests(unittest.TestCase):
	def test_duplicate_canonical_name_with_identical_outfit_deduplicates(self) -> None:
		first = outfit(source="vendor/monster/a.lua")
		second = outfit(source="vendor/monster/b.lua")
		index = build_definition_index([first, second])
		resolved, status = index.resolve("DEMON")
		self.assertEqual(status, "resolved")
		self.assertEqual(resolved, first)

	def test_duplicate_canonical_name_with_different_outfit_is_ambiguous(self) -> None:
		index = build_definition_index([outfit(look_type=35), outfit(look_type=40)])
		self.assertEqual(index.resolve("demon"), (None, "ambiguous-definition"))
		self.assertIn("demon", index.ambiguous)

	def test_explicit_alias_is_case_insensitive_and_never_guessed(self) -> None:
		index = build_definition_index([outfit()], aliases=(("The Demon", "Demon"),))
		resolved, status = index.resolve("THE DEMON")
		self.assertEqual(status, "resolved")
		self.assertEqual(resolved.look_type, 35)
		self.assertEqual(index.resolve("Demon Boss"), (None, "missing-definition"))

	def test_alias_to_missing_definition_is_ignored_without_crashing(self) -> None:
		index = build_definition_index([outfit(name="Alias")], aliases=(("Alias", "Missing"),))
		resolved, status = index.resolve("Alias")
		self.assertEqual(status, "resolved")
		self.assertEqual(resolved.name, "Alias")

	def test_missing_definition_and_missing_look_type_remain_unresolved(self) -> None:
		index = build_definition_index([], invalid=(("Broken", "missing-look-type"),))
		self.assertEqual(index.resolve("Broken"), (None, "missing-look-type"))
		self.assertEqual(index.resolve("Unknown"), (None, "missing-definition"))

	def test_renderer_reports_missing_creature_appearance(self) -> None:
		renderer = CreatureSpriteRenderer.__new__(CreatureSpriteRenderer)
		renderer.appearances = {}
		self.assertEqual(renderer.render_with_status(outfit()), (None, "missing-creature-appearance"))

	def test_renderer_reports_missing_sprite(self) -> None:
		frame = SpriteInfo(1, 1, 1, 1, (999,), 1, 0, ((100, 100),), False, False, 0, 0)
		appearance = Appearance(35, "", False, False, False, False, False, False, False, False, None, None, None, (frame,))
		renderer = CreatureSpriteRenderer.__new__(CreatureSpriteRenderer)
		renderer.appearances = {35: appearance}
		renderer.sprite = lambda _sprite_id: None
		self.assertEqual(renderer.render_with_status(outfit()), (None, "missing-sprite"))

	def test_hundreds_of_identical_spawns_share_one_png(self) -> None:
		definitions = build_definition_index([outfit()])
		records = [{"name": "Demon"} for _ in range(250)] + [{"name": "Missing"}]
		fake = FakeRenderer()
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			stats = enrich_creature_spawns(Path("assets"), root, records, definitions, "monster", "vendor/monster", "vendor/assets", fake)  # type: ignore[arg-type]
			files = list((root / "data/monster-sprites").glob("*.png"))
		self.assertEqual(fake.calls, 1)
		self.assertEqual(len(files), 1)
		self.assertEqual(stats, {"uniqueSprites": 1, "resolvedSpawns": 250, "unresolvedSpawns": 1, "ambiguousDefinitions": 0})
		self.assertEqual({record["sprite"] for record in records[:250]}, {"data/monster-sprites/35-0-0-0-0-0.png"})
		self.assertEqual(records[-1]["spriteStatus"], "missing-definition")


if __name__ == "__main__":
	unittest.main()
