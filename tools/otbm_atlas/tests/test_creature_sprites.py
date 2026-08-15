from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.assets import Appearance, FRAME_GROUP_OUTFIT_IDLE, FRAME_GROUP_OUTFIT_MOVING, SpriteInfo
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


class FakeAnimatedRenderer(FakeRenderer):
	def render_animation_with_status(self, value: CreatureOutfit) -> tuple[dict[str, object] | None, str]:
		return {
			"schemaVersion": 1,
			"presentationGroup": "moving",
			"presentationDirection": "south",
			"groups": {
				"moving": {
					"frameGroupType": FRAME_GROUP_OUTFIT_MOVING,
					"frameGroupId": 1,
					"animationPhases": 2,
					"phaseDurationsMs": [100, 100],
					"durationRangesMs": [[100, 100], [100, 100]],
					"defaultStartPhase": 0,
					"synchronized": False,
					"randomStartPhase": False,
					"loopType": 0,
					"loopCount": 0,
					"directions": ["south"],
					"directionFrames": {"south": [b"phase-0", b"phase-1"]},
				},
			},
			"policy": "canonical-frame-groups-no-spatial-movement",
		}, "resolved"


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

	def test_animation_renderer_preserves_idle_and_moving_groups_and_cardinal_directions(self) -> None:
		idle = SpriteInfo(4, 1, 1, 1, (1, 2, 3, 4), 1, 0, ((250, 250),), False, False, 0, 0, FRAME_GROUP_OUTFIT_IDLE, 0)
		moving = SpriteInfo(4, 1, 1, 1, tuple(range(10, 18)), 2, 0, ((100, 100), (200, 200)), False, False, 0, 0, FRAME_GROUP_OUTFIT_MOVING, 1)
		appearance = Appearance(35, "", False, False, False, False, False, False, False, False, None, None, None, (idle, moving))
		renderer = CreatureSpriteRenderer.__new__(CreatureSpriteRenderer)
		renderer.appearances = {35: appearance}
		renderer.sprite = lambda sprite_id: (1, 1, bytes((sprite_id % 255, 0, 0, 255)))
		animation, status = renderer.render_animation_with_status(outfit())
		self.assertEqual(status, "resolved")
		self.assertIsNotNone(animation)
		assert animation is not None
		self.assertEqual(animation["presentationGroup"], "moving")
		groups = animation["groups"]
		assert isinstance(groups, dict)
		self.assertEqual(set(groups), {"idle", "moving"})
		moving_group = groups["moving"]
		assert isinstance(moving_group, dict)
		self.assertEqual(moving_group["directions"], ["north", "east", "south", "west"])
		self.assertEqual(moving_group["phaseDurationsMs"], [100, 200])
		frames = moving_group["directionFrames"]
		assert isinstance(frames, dict)
		self.assertEqual(len(frames["south"]), 2)
		self.assertNotEqual(frames["south"][0], frames["south"][1])

	def test_animation_renderer_does_not_invent_partial_direction_sets(self) -> None:
		frame = SpriteInfo(2, 1, 1, 1, (1, 2, 3, 4), 2, 0, ((100, 100), (100, 100)), False, False, 0, 0, FRAME_GROUP_OUTFIT_MOVING, 1)
		appearance = Appearance(35, "", False, False, False, False, False, False, False, False, None, None, None, (frame,))
		renderer = CreatureSpriteRenderer.__new__(CreatureSpriteRenderer)
		renderer.appearances = {35: appearance}
		renderer.sprite = lambda sprite_id: (1, 1, bytes((sprite_id, 0, 0, 255)))
		self.assertEqual(renderer.render_animation_with_status(outfit()), (None, "no-renderable-frame-group"))

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
		self.assertEqual(stats, {"uniqueSprites": 1, "uniqueAnimations": 0, "resolvedSpawns": 250, "animatedSpawns": 0, "unresolvedSpawns": 1, "ambiguousDefinitions": 0})
		self.assertEqual({record["sprite"] for record in records[:250]}, {"data/monster-sprites/35-0-0-0-0-0.png"})
		self.assertEqual({record["spriteAnimationStatus"] for record in records[:250]}, {"static-only-renderer"})
		self.assertEqual(records[-1]["spriteStatus"], "missing-definition")

	def test_animated_spawns_share_one_animation_manifest(self) -> None:
		definitions = build_definition_index([outfit()])
		records = [{"name": "Demon"} for _ in range(3)]
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			stats = enrich_creature_spawns(Path("assets"), root, records, definitions, "monster", "vendor/monster", "vendor/assets", FakeAnimatedRenderer())  # type: ignore[arg-type]
			manifest = root / "data/monster-sprites/35-0-0-0-0-0/animation.json"
			phase0 = root / "data/monster-sprites/35-0-0-0-0-0/moving/south/0.png"
		self.assertTrue(manifest.is_file())
		self.assertTrue(phase0.is_file())
		self.assertEqual(stats["uniqueAnimations"], 1)
		self.assertEqual(stats["animatedSpawns"], 3)
		self.assertEqual({record["spriteAnimation"] for record in records}, {"data/monster-sprites/35-0-0-0-0-0/animation.json"})


if __name__ == "__main__":
	unittest.main()
