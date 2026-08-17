from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.tile_inspector import write_tile_inspector_data


class TileInspectorIncrementalTests(unittest.TestCase):
    def _fixture(self, root: Path) -> Path:
        output = root / "atlas"; sidecars = output / ".spool/tile-facts/z7"; sidecars.mkdir(parents=True)
        (output / ".spool/spool.json").write_text(json.dumps({"schemaVersion": 1, "chunkSize": 128}), encoding="utf-8")
        (sidecars / "0_0.jsonl").write_text(json.dumps({"x": 10, "y": 10, "z": 7, "ground": {"serverId": 100}, "items": []}) + "\n", encoding="utf-8")
        (sidecars / "1_0.jsonl").write_text(json.dumps({"x": 150, "y": 10, "z": 7, "ground": {"serverId": 200}, "items": []}) + "\n", encoding="utf-8")
        return output

    def test_changed_sidecar_updates_only_matching_browser_shard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self._fixture(Path(temporary)); first = write_tile_inspector_data(output); self.assertEqual(first["shards"], 2)
            untouched = output / "data/tile-inspector/z7/0_0.json"; changed = output / "data/tile-inspector/z7/1_0.json"; untouched_mtime = untouched.stat().st_mtime_ns; changed_before = changed.read_bytes()
            source = output / ".spool/tile-facts/z7/1_0.jsonl"; source.write_text(json.dumps({"x": 150, "y": 10, "z": 7, "ground": {"serverId": 201}, "items": []}) + "\n", encoding="utf-8")
            result = write_tile_inspector_data(output, changed_sidecars=["z7/1_0.jsonl"], deleted_sidecars=[])
            self.assertEqual(result["shards"], 2); self.assertEqual(untouched.stat().st_mtime_ns, untouched_mtime); self.assertNotEqual(changed.read_bytes(), changed_before)

    def test_deleted_sidecar_removes_only_matching_browser_shard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self._fixture(Path(temporary)); write_tile_inspector_data(output)
            (output / ".spool/tile-facts/z7/1_0.jsonl").unlink()
            result = write_tile_inspector_data(output, changed_sidecars=[], deleted_sidecars=["z7/1_0.jsonl"])
            self.assertEqual(result["shards"], 1); self.assertTrue((output / "data/tile-inspector/z7/0_0.json").is_file()); self.assertFalse((output / "data/tile-inspector/z7/1_0.json").exists())
            index = json.loads((output / "data/tile-inspector/index.json").read_text(encoding="utf-8")); self.assertEqual(len(index["shardStatistics"]), 1)


if __name__ == "__main__": unittest.main()
