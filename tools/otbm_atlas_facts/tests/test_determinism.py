from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.otbm_atlas_facts.build import compile_facts

ROOT = Path(__file__).resolve().parents[3]
CRYSTAL = ROOT / "vendor/map-analysis/crystalserver"


class DeterministicFactsTests(unittest.TestCase):
    def test_full_source_index_is_byte_deterministic(self) -> None:
        with TemporaryDirectory() as first_dir, TemporaryDirectory() as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            summary_a = compile_facts(CRYSTAL, first)
            summary_b = compile_facts(CRYSTAL, second)
            self.assertEqual(summary_a, summary_b)
            first_files = sorted(path.relative_to(first) for path in first.rglob("*.json"))
            second_files = sorted(path.relative_to(second) for path in second.rglob("*.json"))
            self.assertEqual(first_files, second_files)
            for relative in first_files:
                self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes(), str(relative))

            monsters = json.loads((first / "monster-metadata.json").read_text(encoding="utf-8"))
            pythius = monsters["definitions"]["pythius the rotten"]
            self.assertEqual(pythius["status"], "RESOLVED")
            self.assertTrue(pythius["rewardBoss"])


if __name__ == "__main__":
    unittest.main()
