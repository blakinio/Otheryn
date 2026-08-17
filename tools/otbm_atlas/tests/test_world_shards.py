from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.world_shards import (
    WORLD_SHARD_ALGORITHM,
    _assignment_digest,
    _coverage_digest,
    _load_plan,
    build_world_shard_plan,
)


class WorldShardPlannerTests(unittest.TestCase):
    def _spool(self, root: Path) -> None:
        values = {
            "z0/10_10.bin": 100,
            "z0/11_10.bin": 90,
            "z1/10_10.bin": 80,
            "z1/11_10.bin": 70,
            "z2/10_10.bin": 60,
            "z2/11_10.bin": 50,
            "z3/10_10.bin": 40,
            "z3/11_10.bin": 30,
        }
        for relative, size in values.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bytes([size % 251]) * size)

    def test_plan_is_deterministic_complete_and_balanced_by_spool_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            spool = Path(temporary)
            self._spool(spool)
            sources = {
                "mapSha256": "map",
                "assetsSha256": "assets",
                "chunkSize": 128,
                "atlasVersion": 3,
                "tileFactsVersion": 1,
            }
            first = build_world_shard_plan(spool, sources, shard_count=4)
            second = build_world_shard_plan(spool, sources, shard_count=4)
            self.assertEqual(first, second)
            self.assertEqual(first["algorithm"], WORLD_SHARD_ALGORITHM)
            self.assertEqual(first["chunks"], 8)
            self.assertEqual(first["shardCount"], 4)
            self.assertEqual(first["floorCounts"], {"0": 2, "1": 2, "2": 2, "3": 2})
            assignments = first["assignments"]
            all_chunks = [chunk for assignment in assignments for chunk in assignment["chunks"]]
            self.assertEqual(len(all_chunks), 8)
            self.assertEqual(len(set(all_chunks)), 8)
            self.assertEqual(first["coverageDigest"], _coverage_digest(all_chunks))
            for assignment in assignments:
                self.assertEqual(assignment["assignmentDigest"], _assignment_digest(assignment["chunks"]))
            weights = [assignment["spoolBytes"] for assignment in assignments]
            self.assertLessEqual(max(weights) - min(weights), 30)

    def test_plan_digest_detects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spool = root / "spool"
            spool.mkdir()
            self._spool(spool)
            plan = build_world_shard_plan(
                spool,
                {
                    "mapSha256": "map",
                    "assetsSha256": "assets",
                    "chunkSize": 128,
                    "atlasVersion": 3,
                    "tileFactsVersion": 1,
                },
                shard_count=4,
            )
            path = root / "plan.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            self.assertEqual(_load_plan(path), plan)
            plan["assignments"][0]["chunks"] = plan["assignments"][0]["chunks"][1:]
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "plan digest mismatch"):
                _load_plan(path)


if __name__ == "__main__":
    unittest.main()
