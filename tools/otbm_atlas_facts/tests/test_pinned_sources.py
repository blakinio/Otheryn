from __future__ import annotations
from pathlib import Path
import unittest

from tools.otbm_atlas_facts.mechanics import index_scripts, resolve_values
from tools.otbm_atlas_facts.monster_metadata import classification_for, scan_monster_definitions
from tools.otbm_atlas_facts.npc_services import parse_npc_services
from tools.otbm_atlas_facts.npclib_semantics import verify_npc_system
from tools.otbm_atlas_facts.raids import parse_raids

ROOT = Path(__file__).resolve().parents[3]
CRYSTAL = ROOT / "vendor/map-analysis/crystalserver"
GLOBAL = CRYSTAL / "data-global"


class PinnedSourceFactsTests(unittest.TestCase):
    def test_literal_elevator_and_table_loop_fibula_destinations(self) -> None:
        elevator = index_scripts(GLOBAL / "scripts/actions/kazordoon")
        values = resolve_values([50011, 50012], "aid", elevator)
        self.assertEqual([entry["status"] for entry in values], ["RESOLVED", "RESOLVED"])
        destinations = [entry["candidates"][0]["transitions"][0]["destination"] for entry in values]
        self.assertEqual(destinations, [{"x": 32636, "y": 31881, "z": 2}, {"x": 32636, "y": 31881, "z": 7}])

        fibula = index_scripts(GLOBAL / "scripts/movements/teleport")
        values = resolve_values([50390, 50391], "aid", fibula)
        self.assertEqual([entry["status"] for entry in values], ["RESOLVED", "RESOLVED"])
        destinations = [entry["candidates"][0]["transitions"][0]["destination"] for entry in values]
        self.assertEqual(destinations, [{"x": 33651, "y": 31942, "z": 7}, {"x": 32172, "y": 32439, "z": 8}])
        self.assertTrue(all(entry["candidates"][0]["transitions"][0]["conditional"] for entry in values))

    def test_explicit_reward_boss_is_separate_from_definition_path(self) -> None:
        report = scan_monster_definitions(GLOBAL / "monster", GLOBAL)
        pythius = classification_for("Pythius the Rotten", report)
        self.assertEqual(pythius["status"], "RESOLVED")
        self.assertTrue(pythius["rewardBoss"])
        self.assertTrue(pythius["verifiedBoss"])
        rat = classification_for("Rat", report)
        self.assertEqual(rat["status"], "RESOLVED")
        self.assertFalse(rat["verifiedBoss"])

    def test_xml_raids_static_script_raids_and_dynamic_events_stay_distinct(self) -> None:
        monsters = scan_monster_definitions(GLOBAL / "monster", GLOBAL)
        report = parse_raids(GLOBAL / "raids", monsters, GLOBAL / "scripts/raids")
        self.assertGreater(report["statistics"]["raids"], 0)
        self.assertGreater(report["statistics"]["areaSpawns"], 0)
        thais = [record for record in report["areaSpawns"] if record["event"] == "thais.orcs"]
        self.assertTrue(thais)
        self.assertTrue(all(record["origin"] == "raid-event" for record in thais))
        self.assertGreater(report["statistics"]["scriptRaids"], 0)
        self.assertTrue(any(event["spatialStatus"] == "UNKNOWN" for event in report["dynamicEvents"]))
        self.assertGreater(report["statistics"]["verifiedAreaBossParticipants"] + report["statistics"]["verifiedPointBossSpawns"], 0)

    def test_npc_services_and_shared_helper_semantics(self) -> None:
        semantics = verify_npc_system(CRYSTAL / "data/npclib/npc_system")
        self.assertEqual(semantics["travel"]["status"], "RESOLVED")
        self.assertTrue(semantics["travel"]["teleportsToDestination"])
        self.assertEqual(semantics["bank"]["status"], "RESOLVED")

        report = parse_npc_services(GLOBAL / "npc")
        ray = report["npcs"]["ray"]
        self.assertEqual(ray["status"], "RESOLVED")
        self.assertIn("shop", ray["services"])
        self.assertGreater(len(ray["shop"]["items"]), 0)
        naji = report["npcs"]["naji"]
        self.assertIn("bank", naji["services"])
        self.assertIn("guildBank", naji["services"])
        bluebear = report["npcs"]["captain bluebear"]
        self.assertIn("travel", bluebear["services"])
        carlin = next(route for route in bluebear["travel"]["routes"] if route["keyword"] == "carlin")
        self.assertEqual(carlin["cost"], 110)
        self.assertEqual(carlin["destination"], {"x": 32387, "y": 31820, "z": 6})
        self.assertEqual(carlin["proofStatus"], "PROVEN_STATIC")


if __name__ == "__main__":
    unittest.main()
