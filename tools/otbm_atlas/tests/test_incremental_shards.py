from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.otbm_atlas.incremental_shards import build_shard_plan, render_selected_chunks_sharded


class IncrementalShardPlanTests(unittest.TestCase):
    def _spool(self, root: Path, records: dict[str, int]) -> Path:
        spool = root / "spool"
        for key, size in records.items():
            floor, stem = key.split("/", 1)
            path = spool / floor / f"{stem}.bin"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bytes([size % 251]) * size)
        return spool

    def test_every_chunk_is_assigned_once_and_deterministically(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            sizes = {
                "z7/1_1": 90,
                "z7/2_1": 80,
                "z7/3_1": 70,
                "z8/1_1": 60,
                "z8/2_1": 50,
                "z8/3_1": 40,
            }
            spool = self._spool(root, sizes)
            first = build_shard_plan(spool, sizes, 3)
            second = build_shard_plan(spool, reversed(list(sizes)), 3)
            self.assertEqual(first, second)
            assigned = [chunk for shard in first["shards"] for chunk in shard["chunks"]]
            self.assertEqual(sorted(assigned), sorted(sizes))
            self.assertEqual(len(assigned), len(set(assigned)))
            self.assertEqual(first["spoolBytes"], sum(sizes.values()))

    def test_lpt_balances_weighted_chunks(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            sizes = {
                "z7/1_1": 100,
                "z7/2_1": 90,
                "z7/3_1": 80,
                "z7/4_1": 70,
                "z7/5_1": 60,
                "z7/6_1": 50,
            }
            plan = build_shard_plan(self._spool(root, sizes), sizes, 3)
            totals = [int(shard["spoolBytes"]) for shard in plan["shards"]]
            self.assertEqual(totals, [150, 150, 150])

    def test_shard_count_is_capped_to_chunk_count(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            sizes = {"z7/1_1": 10, "z7/2_1": 20}
            plan = build_shard_plan(self._spool(root, sizes), sizes, 32)
            self.assertEqual(len(plan["shards"]), 2)
            self.assertEqual(plan["requestedShards"], 32)

    def test_empty_plan_is_valid(self) -> None:
        with TemporaryDirectory() as directory:
            plan = build_shard_plan(Path(directory), [], 8)
            self.assertEqual(plan["chunks"], 0)
            self.assertEqual(plan["shards"], [])

    def test_invalid_shard_count_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "shard count"):
                build_shard_plan(Path(directory), [], 0)

    def test_invalid_worker_count_is_rejected_before_render(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "worker count"):
                render_selected_chunks_sharded(
                    root / "spool",
                    root / "assets",
                    root / "output",
                    [],
                    {},
                    {},
                    "digest",
                    workers=0,
                    shards=1,
                )


if __name__ == "__main__":
    unittest.main()
