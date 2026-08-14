from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from types import SimpleNamespace

from tools.otbm_atlas.atlas import canonical_source_paths, chunk_render_bounds, decode_tiles, encode_tile
from tools.otbm_atlas.semantic import Item, Position, Tile


class AtlasTests(unittest.TestCase):
	def test_spool_codec_round_trip_preserves_render_structure(self) -> None:
		tile = Tile(Position(123, 456, 7), 42, 3, Item(100), (Item(200, 5, children=(Item(201),)),), (8, 9))
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory, "chunk.bin"); path.write_bytes(encode_tile(tile))
			decoded = list(decode_tiles(path))
		self.assertEqual(decoded, [tile])

	def test_spool_codec_rejects_truncated_tile_header(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory, "chunk.bin"); path.write_bytes(b"\x01\x00\x00\x00\x00")
			with self.assertRaisesRegex(ValueError, "tile header"):
				list(decode_tiles(path))

	def test_chunk_bounds_crop_empty_space_and_keep_sprite_gutter(self) -> None:
		tiles = [Tile(Position(100, 200, 7), None, 0, Item(100), (), ()), Tile(Position(102, 203, 7), None, 0, Item(100), (), ())]
		renderer = SimpleNamespace(
			sheets=[SimpleNamespace(sprite_size=(64, 64))],
			appearances={100: SimpleNamespace(shift=(25, 24))},
		)
		self.assertEqual(chunk_render_bounds(tiles, renderer), (98, 102, 198, 203, 7))

	def test_canonical_source_contract_is_vendor_map_analysis_only(self) -> None:
		root = Path("/repo")
		sources = canonical_source_paths(root)
		for value in sources.values():
			self.assertTrue(value.as_posix().startswith("/repo/vendor/map-analysis/"), value)
		code_root = Path(__file__).parents[1]
		for name in ("atlas.py", "composition.py", "render.py", "environment_animation.py", "creature_sprites.py", "npc_sprites.py", "monster_sprites.py"):
			text = (code_root / name).read_text(encoding="utf-8")
			self.assertNotIn("data-otservbr-global", text, name)


if __name__ == "__main__": unittest.main()
