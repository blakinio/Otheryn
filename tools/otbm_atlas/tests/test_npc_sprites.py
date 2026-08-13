from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.npc_sprites import outfit_color, parse_npc_outfits


class NpcSpriteTests(unittest.TestCase):
	def test_parser_reads_explicit_npc_outfit_and_keeps_provenance(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); npc = root / "npc"; npc.mkdir()
			(npc / "guide.lua").write_text('local internalNpcName = "Guide"\nnpcConfig.outfit = { lookType = 138, lookHead = 96, lookBody = 95, lookLegs = 0, lookFeet = 95, lookAddons = 0 }', encoding="utf-8")
			outfit = parse_npc_outfits(npc, root)["guide"]
			self.assertEqual(outfit.key, "138-96-95-0-95-0")
			self.assertEqual(outfit.source, "npc/guide.lua")

	def test_tibia_hsi_palette_is_bounded_and_deterministic(self) -> None:
		self.assertEqual(outfit_color(0), (255, 255, 255))
		self.assertEqual(outfit_color(132), (128, 0, 0))
		self.assertEqual(outfit_color(95), outfit_color(95))
		self.assertEqual(outfit_color(133), (0, 0, 0))

	def test_conflicting_same_name_is_left_unresolved(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); npc = root / "npc"; npc.mkdir()
			(npc / "a.lua").write_text('local internalNpcName = "Guide"\nnpcConfig.outfit = { lookType = 128 }', encoding="utf-8")
			(npc / "b.lua").write_text('local internalNpcName = "Guide"\nnpcConfig.outfit = { lookType = 129 }', encoding="utf-8")
			self.assertNotIn("guide", parse_npc_outfits(npc, root))


if __name__ == "__main__":
	unittest.main()
