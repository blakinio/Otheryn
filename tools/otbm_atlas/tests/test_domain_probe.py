from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools.otbm_atlas.domain_probe import run_domain_probe


class DomainProbeTests(unittest.TestCase):
    def test_only_selected_non_render_domains_are_executed(self) -> None:
        plan = {"classification": {"domains": ["spawns", "houses", "npcDefinitions", "monsterDefinitions", "mechanics", "factualData", "frontend"]}}
        definitions = SimpleNamespace(resolved={"a": object()}, ambiguous=frozenset(), invalid={}, aliases={})
        with (
            patch("tools.otbm_atlas.domain_probe.scan_spawns", return_value={"statistics": {"files": 1}}) as spawns,
            patch("tools.otbm_atlas.domain_probe.parse_houses", return_value={"statistics": {"houses": 2}}) as houses,
            patch("tools.otbm_atlas.domain_probe.parse_npc_definition_index", return_value=definitions) as npc,
            patch("tools.otbm_atlas.domain_probe.parse_monster_definition_index", return_value=definitions) as monster,
            patch("tools.otbm_atlas.domain_probe.index_scripts", return_value={"registrations": {"aid": {1: []}, "uid": {}}, "dynamicRegistrations": []}) as mechanics,
        ):
            report = run_domain_probe(plan, Path("."))
        spawns.assert_called_once()
        houses.assert_called_once()
        npc.assert_called_once()
        monster.assert_called_once()
        mechanics.assert_called_once()
        self.assertEqual(report["validated"]["spawns"], {"files": 1})
        self.assertEqual(report["validated"]["houses"], {"houses": 2})
        self.assertEqual(report["validated"]["npcDefinitions"]["resolved"], 1)
        self.assertEqual(report["validated"]["monsterDefinitions"]["resolved"], 1)
        self.assertEqual(report["validated"]["mechanics"]["aidValues"], 1)
        self.assertEqual(report["validated"]["factualData"]["delegatedWorkflow"], "OTBM Atlas Factual Layers")
        self.assertEqual(report["validated"]["frontend"]["delegatedWorkflow"], "OTBM Atlas Tests")

    def test_documentation_only_plan_executes_no_data_generator(self) -> None:
        plan = {"classification": {"domains": ["documentation"]}}
        with patch("tools.otbm_atlas.domain_probe.scan_spawns") as spawns:
            report = run_domain_probe(plan, Path("."))
        spawns.assert_not_called()
        self.assertEqual(report["validated"], {})


if __name__ == "__main__":
    unittest.main()
