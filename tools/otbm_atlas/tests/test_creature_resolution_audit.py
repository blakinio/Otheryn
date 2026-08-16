from __future__ import annotations

import unittest

from tools.otbm_atlas.creature_resolution_audit import audit_spawns


class CreatureResolutionAuditTests(unittest.TestCase):
    def test_audit_preserves_every_unresolved_record_and_explicit_classification(self) -> None:
        spawns = {
            "npcSpawns": [
                {"name": "Good", "position": {"x": 1, "y": 2, "z": 7}, "source": "a.xml", "origin": "base-map", "spriteStatus": "resolved", "spriteAnimationStatus": "static-only-appearance", "sprite": "good.png"},
                {"name": "Missing", "position": {"x": 3, "y": 4, "z": 7}, "source": "b.xml", "origin": "base-map", "spriteStatus": "missing-definition"},
            ],
            "monsterSpawns": [
                {"name": "Ambiguous", "position": {"x": 5, "y": 6, "z": 8}, "source": "c.xml", "origin": "quest-map", "spriteStatus": "ambiguous-definition"},
            ],
        }
        report = audit_spawns(spawns)
        self.assertEqual(report["statistics"]["npcSpawns"], 2)
        self.assertEqual(report["statistics"]["monsterSpawns"], 1)
        self.assertEqual(report["statistics"]["unresolvedSpriteRecords"], 2)
        self.assertEqual(
            [value["classification"] for value in report["unresolvedSpriteRecords"]],
            ["AMBIGUOUS_CANONICAL_DEFINITION", "MISSING_CANONICAL_DEFINITION"],
        )
        self.assertEqual(report["statistics"]["nonResolvedAnimationRecordsWithStaticFallback"], 1)
        self.assertEqual(
            report["nonResolvedAnimationRecordsWithStaticFallback"][0]["classification"],
            "EXPECTED_STATIC_CANONICAL",
        )

    def test_unknown_status_remains_explicit_other_not_guessed(self) -> None:
        report = audit_spawns({"npcSpawns": [{"name": "X", "spriteStatus": "future-status"}], "monsterSpawns": []})
        self.assertEqual(report["unresolvedSpriteRecords"][0]["classification"], "UNRESOLVED_OTHER")
        self.assertIn("no fuzzy-name", report["policy"]["noGuessing"])


if __name__ == "__main__":
    unittest.main()
