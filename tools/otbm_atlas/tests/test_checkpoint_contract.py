from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).parents[3]
CONTRACT = ROOT / "docs/agents/GOVERNANCE_CONTRACT.json"
TASK = ROOT / "docs/agents/tasks/active/OTH-20260815-otbm-atlas-creature-sprites.md"


class CheckpointContractTests(unittest.TestCase):
	def test_active_creature_task_checkpoint_matches_governance_contract(self) -> None:
		contract = json.loads(CONTRACT.read_text(encoding="utf-8"))["shared_checkpoint_contract"]
		text = TASK.read_text(encoding="utf-8")
		match = re.search(r"## Context checkpoint\s*\n\s*```yaml\n(.*?)\n```", text, re.DOTALL)
		self.assertIsNotNone(match, "task must contain a machine-readable Context checkpoint YAML fence")
		checkpoint = match.group(1)
		keys = set(re.findall(r"(?m)^([a-z_][a-z0-9_]*):(?:\s|$)", checkpoint))
		self.assertEqual(set(contract["required_fields"]) - keys, set())
		status = re.search(r"(?m)^status:\s*([a-z_]+)\s*$", checkpoint)
		self.assertIsNotNone(status)
		self.assertIn(status.group(1), contract["allowed_statuses"])
		for result in re.findall(r"(?m)^\s+result:\s*([A-Z_]+)\s*$", checkpoint):
			self.assertIn(result, contract["allowed_validation_results"])

		frontmatter = text.split("---", 2)[1]
		front_status = re.search(r"(?m)^status:\s*([a-z_]+)\s*$", frontmatter)
		self.assertIsNotNone(front_status)
		self.assertIn(front_status.group(1), contract["allowed_statuses"])
		self.assertRegex(frontmatter, r'(?m)^related_pr:\s*["\']?395["\']?\s*$')
		self.assertNotIn("PR #392 remains open", text)
		self.assertIn("PR #392 is closed unmerged", text)


if __name__ == "__main__":
	unittest.main()
