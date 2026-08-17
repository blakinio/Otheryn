from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.otbm_atlas.environment_animation_resume import _chunk_weight, _effective_worker_count


class EnvironmentParallelTests(unittest.TestCase):
    def test_worker_count_never_oversubscribes_cpu_or_work(self) -> None:
        with patch("tools.otbm_atlas.environment_animation_resume.os.cpu_count", return_value=4):
            self.assertEqual(_effective_worker_count(8, 100), 4)
            self.assertEqual(_effective_worker_count(4, 100), 4)
            self.assertEqual(_effective_worker_count(4, 2), 2)
            self.assertEqual(_effective_worker_count(None, 100), 4)
            self.assertEqual(_effective_worker_count(None, 1), 1)

    def test_default_worker_cap_is_four_even_on_larger_host(self) -> None:
        with patch("tools.otbm_atlas.environment_animation_resume.os.cpu_count", return_value=32):
            with patch.dict("tools.otbm_atlas.environment_animation_resume.os.environ", {}, clear=True):
                self.assertEqual(_effective_worker_count(None, 100), 4)
            with patch.dict("tools.otbm_atlas.environment_animation_resume.os.environ", {"OTBM_ATLAS_ENV_WORKERS": "12"}, clear=True):
                self.assertEqual(_effective_worker_count(None, 100), 12)

    def test_historical_work_outweighs_cold_spool_size_for_scheduling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "atlas"
            spool = output / ".spool"
            (spool / "z7").mkdir(parents=True)
            (spool / "z7/1_1.bin").write_bytes(b"a" * 1024)
            (spool / "z7/2_2.bin").write_bytes(b"b" * 8192)
            checkpoint = output / "data/environment-animations/checkpoints/z7/1_1.json"
            checkpoint.parent.mkdir(parents=True)
            checkpoint.write_text(json.dumps({"instances": 14000, "staticFallbacks": 2000}), encoding="utf-8")
            heavy = {"z": 7, "chunkX": 1, "chunkY": 1}
            unknown = {"z": 7, "chunkX": 2, "chunkY": 2}
            self.assertGreater(_chunk_weight(output, spool, heavy), _chunk_weight(output, spool, unknown))

    def test_non_positive_requested_worker_count_is_rejected(self) -> None:
        with patch("tools.otbm_atlas.environment_animation_resume.os.cpu_count", return_value=4):
            with self.assertRaises(ValueError):
                _effective_worker_count(0, 3)


if __name__ == "__main__":
    unittest.main()
