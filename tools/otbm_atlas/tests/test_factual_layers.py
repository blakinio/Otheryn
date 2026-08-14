from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.otbm_atlas.factual_layers import CANONICAL_WORLD_SHA256, build_factual_layers, enrich_existing_atlas

ROOT = Path(__file__).resolve().parents[3]


class FactualLayerPolicyTests(unittest.TestCase):
    def test_only_proven_mechanics_and_explicit_bosses_are_promoted(self) -> None:
        mechanics = {
            "actionIds": [
                {"actionId": 1, "position": {"x": 100, "y": 100, "z": 7}},
                {"actionId": 2, "position": {"x": 101, "y": 100, "z": 7}},
            ],
            "uniqueIds": [],
        }
        resolutions = {
            "resolutions": [
                {
                    "kind": "ActionID",
                    "value": 1,
                    "status": "RESOLVED",
                    "candidates": [{
                        "script": "actions/one.lua",
                        "basis": "literal-registration",
                        "transitions": [{
                            "destination": {"x": 200, "y": 200, "z": 8},
                            "basis": "table-field:newPosition",
                            "behavior": "scripted-teleport",
                            "conditional": True,
                            "proofStatus": "PROVEN_STATIC",
                        }],
                    }],
                },
                {"kind": "ActionID", "value": 2, "status": "AMBIGUOUS", "candidates": [{}, {}]},
            ],
            "dynamicRegistrations": [{"status": "UNKNOWN"}],
            "statistics": {"RESOLVED": 1, "AMBIGUOUS": 1, "UNRESOLVED": 0},
        }
        spawns = {
            "npcSpawns": [
                {"name": "Guide", "origin": "base-map", "position": {"x": 105, "y": 105, "z": 7}},
                {"name": "Guide", "origin": "supplemental", "position": {"x": 106, "y": 105, "z": 7}},
            ],
            "monsterSpawns": [
                {"name": "True Boss", "origin": "base-map", "position": {"x": 110, "y": 110, "z": 7}},
                {"name": "Path Only Boss", "origin": "base-map", "position": {"x": 111, "y": 110, "z": 7}},
            ],
        }
        npc = {"npcs": {"guide": {"status": "RESOLVED", "services": ["travel"], "travel": {"routes": []}}}}
        monsters = {"definitions": {
            "true boss": {"status": "RESOLVED", "rewardBoss": True, "verifiedBoss": True, "candidates": [{"source": "monster/bosses/true.lua"}]},
            "path only boss": {"status": "UNKNOWN", "candidates": [{"definitionCategory": "bosses", "rewardBoss": None}]},
        }}
        raids = {
            "pointSpawns": [{
                "name": "True Boss", "event": "test", "position": {"x": 120, "y": 120, "z": 7},
                "monster": {"name": "True Boss", "classification": monsters["definitions"]["true boss"]},
            }],
            "areaSpawns": [{
                "name": "test-area", "event": "test", "position": {"x": 130, "y": 130, "z": 7},
                "positionRole": "derived-navigation-center", "bounds": {"x1": 125, "x2": 135, "y1": 125, "y2": 135, "z": 7},
                "monsters": [{"name": "True Boss", "classification": monsters["definitions"]["true boss"]}],
            }],
            "dynamicEvents": [{"spatialStatus": "UNKNOWN"}],
        }

        factual = build_factual_layers(mechanics, resolutions, spawns, npc, raids, monsters)
        self.assertEqual([record["actionId"] for record in factual["groups"]["scriptedTeleports"]], [1])
        self.assertTrue(factual["groups"]["scriptedTeleports"][0]["conditional"])
        self.assertEqual(len(factual["groups"]["npcServices"]), 1)
        self.assertEqual(
            {(record["name"], record.get("event")) for record in factual["groups"]["verifiedBossSpawns"]},
            {("True Boss", None), ("True Boss", "test")},
        )
        self.assertEqual(factual["groups"]["raidAreas"][0]["verifiedBossParticipants"], ["True Boss"])
        self.assertEqual(factual["statistics"]["dynamicMechanicsUnknown"], 1)
        self.assertEqual(factual["statistics"]["dynamicEventsUnknown"], 1)

    def test_canonical_enrichment_uses_pinned_crystal_and_preserves_existing_shard_data(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "data/chunks/z7").mkdir(parents=True)
            manifest = {
                "schemaVersion": 3,
                "chunkSize": 128,
                "sources": {"mapSha256": CANONICAL_WORLD_SHA256},
                "chunks": [],
            }
            (output / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            mechanics = {
                "actionIds": [{"actionId": 50011, "position": {"x": 32360, "y": 32230, "z": 7}, "origin": "base-map"}],
                "uniqueIds": [],
                "teleports": [{"position": {"x": 32361, "y": 32230, "z": 7}, "destination": {"x": 1, "y": 2, "z": 3}}],
                "houseTiles": [], "houseDoors": [], "towns": [], "waypoints": [],
            }
            spawns = {
                "npcSpawns": [{"name": "Captain Bluebear", "origin": "base-map", "position": {"x": 32362, "y": 32230, "z": 7}}],
                "monsterSpawns": [{"name": "Pythius The Rotten", "origin": "base-map", "position": {"x": 32363, "y": 32230, "z": 7}}],
                "statistics": {},
            }
            (output / "data/mechanics.json").write_text(json.dumps(mechanics), encoding="utf-8")
            (output / "data/spawns.json").write_text(json.dumps(spawns), encoding="utf-8")
            (output / "data/statistics.json").write_text(json.dumps({"mechanicsResolution": {}}), encoding="utf-8")
            shard = {"schemaVersion": 1, "teleports": [{"kind": "teleports", **mechanics["teleports"][0]}]}
            (output / "data/chunks/z7/252_251.json").write_text(json.dumps(shard), encoding="utf-8")
            (output / "data/search-index.json").write_text(json.dumps({"schemaVersion": 1, "records": []}), encoding="utf-8")

            report = enrich_existing_atlas(output, ROOT)
            self.assertEqual(report["status"], "RESOLVED")
            self.assertEqual(report["source"]["commit"], "5e89bf8329ea406cb4ea8f4a18f32954f13e5418")
            resolution = json.loads((output / "data/mechanics-resolution.json").read_text(encoding="utf-8"))
            aid = next(entry for entry in resolution["resolutions"] if entry["kind"] == "ActionID" and entry["value"] == 50011)
            self.assertEqual(aid["status"], "RESOLVED")
            self.assertTrue(aid["candidates"][0]["script"].endswith("kazordoon/elevator_lever.lua"))
            shard = json.loads((output / "data/chunks/z7/252_251.json").read_text(encoding="utf-8"))
            self.assertEqual(len(shard["teleports"]), 1, "direct OTBM teleport must remain separate")
            self.assertEqual(shard["scriptedTeleports"][0]["destination"], {"x": 32636, "y": 31881, "z": 2})
            self.assertIn("npcServices", shard)
            self.assertIn("verifiedBossSpawns", shard)
            self.assertEqual(shard["verifiedBossSpawns"][0]["evidenceBasis"], "explicit-rewardBoss=true")
            search = json.loads((output / "data/search-index.json").read_text(encoding="utf-8"))["records"]
            kinds = {record["kind"] for record in search}
            self.assertTrue({"scriptedTeleports", "raidAreas", "npcServices", "verifiedBossSpawns"} <= kinds)


if __name__ == "__main__":
    unittest.main()
