from __future__ import annotations

from pathlib import Path
import unittest

from tools.otbm_atlas_facts.mechanics import index_scripts, resolve_values
from tools.otbm_atlas_facts.monster_metadata import classification_for, scan_monster_definitions

ROOT = Path(__file__).resolve().parents[3]
GLOBAL = ROOT / "vendor/map-analysis/crystalserver/data-global"


class StatusContractTests(unittest.TestCase):
    def test_unresolved_and_unknown_are_not_promoted_to_resolved(self) -> None:
        index = index_scripts(GLOBAL / "scripts")
        missing = resolve_values([999999], "aid", index)[0]
        self.assertEqual(missing["status"], "UNRESOLVED")

        monsters = scan_monster_definitions(GLOBAL / "monster", GLOBAL)
        absent = classification_for("Definitely Not A Crystal Monster", monsters)
        self.assertEqual(absent["status"], "UNRESOLVED")
        self.assertEqual(absent["candidates"], [])


if __name__ == "__main__":
    unittest.main()
