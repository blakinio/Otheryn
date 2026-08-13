from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.atlas import decode_tiles, encode_tile
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


if __name__ == "__main__": unittest.main()
