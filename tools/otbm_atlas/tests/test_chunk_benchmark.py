from __future__ import annotations

import unittest

from tools.otbm_atlas.chunk_benchmark import partition_tiles
from tools.otbm_atlas.semantic import Position, Tile


class ChunkBenchmarkTests(unittest.TestCase):
    def test_partition_uses_floor_and_spatial_chunk(self) -> None:
        tiles = [
            Tile(Position(0, 0, 7), None, 0, None, ()),
            Tile(Position(31, 31, 7), None, 0, None, ()),
            Tile(Position(32, 0, 7), None, 0, None, ()),
            Tile(Position(0, 0, 8), None, 0, None, ()),
        ]
        groups = partition_tiles(tiles, 32)
        self.assertEqual(sorted(groups), [(7, 0, 0), (7, 1, 0), (8, 0, 0)])
        self.assertEqual(len(groups[(7, 0, 0)]), 2)

    def test_smaller_chunk_size_reduces_nominal_invalidation_area(self) -> None:
        self.assertEqual(32 * 32, 1024)
        self.assertEqual(64 * 64, 4096)
        self.assertEqual(128 * 128, 16384)
        self.assertLess(32 * 32, 64 * 64)
        self.assertLess(64 * 64, 128 * 128)

    def test_invalid_chunk_size_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            partition_tiles([], 0)


if __name__ == "__main__":
    unittest.main()
