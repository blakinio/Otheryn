from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.creature_sprites import CreatureSpriteRenderer
from tools.otbm_atlas.monster_sprites import enrich_monster_spawns, parse_monster_definition_index
from tools.otbm_atlas.npc_sprites import enrich_npc_spawns, parse_npc_definition_index
from tools.otbm_atlas.render import render_region
from tools.otbm_atlas.spawns import scan_spawns
from tools.otbm_atlas.spatial import write_spatial_data


ROOT = Path(__file__).parents[3]
WORLD = ROOT / "vendor/map-analysis/crystalserver/data-global/world"
NPC_ROOT = ROOT / "vendor/map-analysis/crystalserver/data-global/npc"
MONSTER_ROOT = ROOT / "vendor/map-analysis/crystalserver/data-global/monster"
ASSETS = ROOT / "vendor/map-analysis/tibia-client/15.25.bd5a04/assets"
RUN = os.environ.get("OTBM_ATLAS_CANONICAL_INTEGRATION") == "1"


@unittest.skipUnless(RUN, "set OTBM_ATLAS_CANONICAL_INTEGRATION=1 for pinned-data integration")
class CanonicalCreatureIntegrationTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.spawns = scan_spawns(WORLD)
		cls.npc_index = parse_npc_definition_index(NPC_ROOT, ROOT)
		cls.monster_index = parse_monster_definition_index(MONSTER_ROOT, ROOT)
		cls.renderer = CreatureSpriteRenderer(ASSETS)

	@classmethod
	def _real_spawn(cls, kind: str, preferred: str | None = None) -> tuple[dict[str, object], object]:
		key = "npcSpawns" if kind == "npc" else "monsterSpawns"
		index = cls.npc_index if kind == "npc" else cls.monster_index
		candidates = [record for record in cls.spawns[key] if record.get("origin") == "base-map"]
		if preferred:
			candidates.sort(key=lambda record: str(record["name"]).casefold() != preferred.casefold())
		for record in candidates:
			outfit, status = index.resolve(str(record["name"]))
			if status != "resolved" or outfit is None:
				continue
			payload, sprite_status = cls.renderer.render_with_status(outfit)
			if payload is not None and sprite_status == "resolved":
				return dict(record), outfit
		raise AssertionError(f"no renderable canonical {kind} base-map spawn")

	@classmethod
	def _real_animated_spawn(cls, kind: str) -> tuple[dict[str, object], object, dict[str, object]]:
		key = "npcSpawns" if kind == "npc" else "monsterSpawns"
		index = cls.npc_index if kind == "npc" else cls.monster_index
		for source in cls.spawns[key]:
			if source.get("origin") != "base-map":
				continue
			outfit, status = index.resolve(str(source["name"]))
			if status != "resolved" or outfit is None:
				continue
			animation, animation_status = cls.renderer.render_animation_with_status(outfit)
			if animation is not None and animation_status == "resolved":
				return dict(source), outfit, animation
		raise AssertionError(f"no animated canonical {kind} base-map spawn")

	def test_real_vendored_npc_spawn_resolves_and_generates_sprite(self) -> None:
		record, outfit = self._real_spawn("npc", "Benjamin")
		with tempfile.TemporaryDirectory() as directory:
			stats = enrich_npc_spawns(ASSETS, NPC_ROOT, Path(directory), [record], ROOT)
			self.assertTrue((Path(directory) / str(record["sprite"])).is_file())
		self.assertEqual(stats["resolvedSpawns"], 1)
		self.assertTrue(str(record["outfitSource"]).startswith("vendor/map-analysis/crystalserver/data-global/npc/"))
		self.assertEqual(record["lookType"], outfit.look_type)

	def test_real_vendored_monster_spawn_resolves_generates_sprite_and_survives_sharding(self) -> None:
		record, outfit = self._real_spawn("monster", "Demon")
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory)
			stats = enrich_monster_spawns(ASSETS, MONSTER_ROOT, output, [record], ROOT)
			self.assertTrue((output / str(record["sprite"])).is_file())
			write_spatial_data(output, 128, {"monsterSpawns": [record]})
			position = record["position"]
			shard = output / "data/chunks" / f"z{position['z']}" / f"{position['x'] // 128}_{position['y'] // 128}.json"
			payload = json.loads(shard.read_text(encoding="utf-8"))
			self.assertEqual(payload["monsterSpawns"][0]["sprite"], record["sprite"])
		self.assertEqual(stats["resolvedSpawns"], 1)
		self.assertTrue(str(record["outfitSource"]).startswith("vendor/map-analysis/crystalserver/data-global/monster/"))
		self.assertEqual(record["lookType"], outfit.look_type)

	def test_real_pinned_npc_and_monster_have_time_based_animation_export(self) -> None:
		for kind, enrich, definition_root in (("npc", enrich_npc_spawns, NPC_ROOT), ("monster", enrich_monster_spawns, MONSTER_ROOT)):
			record, _outfit, animation = self._real_animated_spawn(kind)
			self.assertIn(animation["presentationGroup"], {"idle", "moving"})
			with tempfile.TemporaryDirectory() as directory:
				output = Path(directory)
				stats = enrich(ASSETS, definition_root, output, [record], ROOT)
				self.assertEqual(stats["animatedSpawns"], 1)
				self.assertEqual(record["spriteAnimationStatus"], "resolved")
				manifest_path = output / str(record["spriteAnimation"])
				self.assertTrue(manifest_path.is_file())
				manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
				group = manifest["groups"][manifest["presentationGroup"]]
				self.assertGreater(len(group["phaseDurationsMs"]), 1)
				self.assertIn(manifest["presentationDirection"], group["frames"])
				self.assertEqual(len(group["frames"][manifest["presentationDirection"]]), len(group["phaseDurationsMs"]))

	def test_real_vendored_apostrophe_monster_definition_resolves(self) -> None:
		outfit, status = self.monster_index.resolve("Mooh'Tah Warrior")
		self.assertEqual(status, "resolved")
		self.assertIsNotNone(outfit)
		self.assertGreater(outfit.look_type, 0)
		self.assertTrue(str(outfit.source).startswith("vendor/map-analysis/crystalserver/data-global/monster/"))

	def test_real_canonical_item_fragment_renders_from_vendored_world_and_assets(self) -> None:
		record, _outfit = self._real_spawn("npc", "Benjamin")
		position = record["position"]
		bounds = (position["x"] - 1, position["x"] + 1, position["y"] - 1, position["y"] + 1, position["z"])
		png, report = render_region(WORLD / "world.otbm", ASSETS, bounds)
		self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
		self.assertGreater(report["renderOperations"], 0)


if __name__ == "__main__":
	unittest.main()
