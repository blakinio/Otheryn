from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.npc_sprites import NpcOutfit, _enabled_y_patterns, _recolor_outfit_mask, outfit_color, parse_npc_outfits


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

	def test_identical_visual_duplicate_keeps_deterministic_first_provenance(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); npc = root / "npc"; npc.mkdir()
			body = 'local internalNpcName = "Guide"\nnpcConfig.outfit = { lookType = 128, lookHead = 1 }'
			(npc / "a.lua").write_text(body, encoding="utf-8")
			(npc / "b.lua").write_text(body, encoding="utf-8")
			outfit = parse_npc_outfits(npc, root)["guide"]
			self.assertEqual(outfit.source, "npc/a.lua")

	def test_addon_bits_select_otclient_y_patterns(self) -> None:
		self.assertEqual(_enabled_y_patterns(3, 0), (0,))
		self.assertEqual(_enabled_y_patterns(3, 1), (0, 1))
		self.assertEqual(_enabled_y_patterns(3, 2), (0, 2))
		self.assertEqual(_enabled_y_patterns(3, 3), (0, 1, 2))

	def test_mask_primary_colors_map_to_head_body_legs_feet(self) -> None:
		outfit = NpcOutfit("Guide", 128, 1, 2, 3, 4, 0, "npc/guide.lua")
		pixels = b"\xff\xff\x00\xff" + b"\xff\x00\x00\xff" + b"\x00\xff\x00\xff" + b"\x00\x00\xff\xff"
		recolored = _recolor_outfit_mask(pixels, outfit)
		self.assertEqual(recolored[0:3], bytes(outfit_color(outfit.head)))
		self.assertEqual(recolored[4:7], bytes(outfit_color(outfit.body)))
		self.assertEqual(recolored[8:11], bytes(outfit_color(outfit.legs)))
		self.assertEqual(recolored[12:15], bytes(outfit_color(outfit.feet)))

	def test_conflicting_same_name_is_left_unresolved(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); npc = root / "npc"; npc.mkdir()
			(npc / "a.lua").write_text('local internalNpcName = "Guide"\nnpcConfig.outfit = { lookType = 128 }', encoding="utf-8")
			(npc / "b.lua").write_text('local internalNpcName = "Guide"\nnpcConfig.outfit = { lookType = 129 }', encoding="utf-8")
			self.assertNotIn("guide", parse_npc_outfits(npc, root))


if __name__ == "__main__":
	unittest.main()
