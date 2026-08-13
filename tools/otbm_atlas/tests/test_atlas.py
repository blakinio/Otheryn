from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from types import SimpleNamespace

from tools.otbm_atlas import _atlas_core
from tools.otbm_atlas.atlas import chunk_render_bounds, decode_tiles, encode_tile
from tools.otbm_atlas.semantic import Item, Position, Tile


class AtlasTests(unittest.TestCase):
	def test_authoritative_core_uses_v3_cache_schema(self) -> None:
		self.assertEqual(_atlas_core.ATLAS_VERSION, 3)

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


if __name__ == "__main__": unittest.main()
