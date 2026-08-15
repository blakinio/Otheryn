from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).parents[3]
CONTRACT = ROOT / "docs/agents/GOVERNANCE_CONTRACT.json"
ACTIVE = ROOT / "docs/agents/tasks/active/OTH-20260815-otbm-atlas-creature-sprites.md"
ARCHIVE = ROOT / "docs/agents/tasks/archive/OTH-20260815-otbm-atlas-creature-sprites.md"
EXPECTED_PR = "395"
EXPECTED_MERGE_SHA = "ea1810ed0a878230d1e68ad45e455c01ef7fc99d"


class CheckpointContractTests(unittest.TestCase):
	def test_completed_creature_task_is_archived_and_not_resumable(self) -> None:
		contract = json.loads(CONTRACT.read_text(encoding="utf-8"))["shared_checkpoint_contract"]
		self.assertIn("completed", contract["allowed_statuses"])
		self.assertFalse(ACTIVE.exists(), "completed task must not remain resumable under tasks/active")
		self.assertTrue(ARCHIVE.is_file(), "completed task must have a durable archive record")

		text = ARCHIVE.read_text(encoding="utf-8")
		frontmatter = text.split("---", 2)[1]
		status = re.search(r"(?m)^status:\s*([a-z_]+)\s*$", frontmatter)
		self.assertIsNotNone(status)
		self.assertEqual(status.group(1), "completed")
		self.assertRegex(frontmatter, rf'(?m)^related_pr:\s*["\']?{EXPECTED_PR}["\']?\s*$')
		self.assertRegex(frontmatter, rf"(?m)^merge_sha:\s*{EXPECTED_MERGE_SHA}\s*$")
		self.assertIn(f"PR #{EXPECTED_PR} was squash-merged into `main` as `{EXPECTED_MERGE_SHA}`.", text)
		self.assertIn("Final exact-head PR validation passed before merge", text)
		self.assertIn("This archive replaces the former `tasks/active` checkpoint", text)


if __name__ == "__main__":
	unittest.main()
