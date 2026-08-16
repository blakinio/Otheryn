from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.spatial import write_spatial_data


class SpatialIncrementalTests(unittest.TestCase):
    def _groups(self, second_label: str = "B"):
        return {"npcSpawns": [
            {"name": "A", "position": {"x": 10, "y": 10, "z": 7}},
            {"name": second_label, "position": {"x": 150, "y": 10, "z": 7}},
        ]}

    def test_identical_second_write_reuses_all_shards(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            first = write_spatial_data(output, 128, self._groups()); second = write_spatial_data(output, 128, self._groups())
            self.assertEqual(first["changedChunks"], 2)
            self.assertEqual(second["changedChunks"], 0)
            self.assertEqual(second["reusedChunks"], 2)
            self.assertFalse(second["searchIndexChanged"])

    def test_one_record_change_writes_one_spatial_shard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary); write_spatial_data(output, 128, self._groups())
            first_path = output / "data/chunks/z7/0_0.json"; first_mtime = first_path.stat().st_mtime_ns
            result = write_spatial_data(output, 128, self._groups("Changed"))
            self.assertEqual(result["changedChunks"], 1); self.assertEqual(result["reusedChunks"], 1)
            self.assertEqual(first_path.stat().st_mtime_ns, first_mtime)

    def test_removed_record_deletes_only_stale_shard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary); write_spatial_data(output, 128, self._groups())
            result = write_spatial_data(output, 128, {"npcSpawns": [{"name": "A", "position": {"x": 10, "y": 10, "z": 7}}]})
            self.assertEqual(result["deletedChunks"], 1); self.assertTrue((output / "data/chunks/z7/0_0.json").is_file()); self.assertFalse((output / "data/chunks/z7/1_0.json").exists())


if __name__ == "__main__": unittest.main()
