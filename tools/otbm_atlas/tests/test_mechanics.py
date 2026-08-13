from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.mechanics import index_scripts, resolve_mechanics


class MechanicsTests(unittest.TestCase):
	def test_literal_registrations_are_resolved(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			(root / "move.lua").write_text("local e=MoveEvent()\ne:aid(5555)\ne:register()\n", encoding="utf-8")
			(root / "quest.lua").write_text("local a=Action()\na:uid(65207)\na:register()\n", encoding="utf-8")
			report = resolve_mechanics({"actionIds": [{"actionId": 5555}], "uniqueIds": [{"uniqueId": 65207}]}, root)
			self.assertEqual([entry["status"] for entry in report["resolutions"]], ["RESOLVED", "RESOLVED"])
			self.assertEqual(report["resolutions"][1]["candidates"][0]["basis"], "literal-registration")

	def test_dynamic_uid_registration_does_not_promote_numeric_table_keys(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			(root / "walls.lua").write_text(
				"local config = { [2246] = { [1] = {}, [2] = {} } }\nlocal action=Action()\naction:uid(index)\naction:register()\n",
				encoding="utf-8",
			)
			index = index_scripts(root)
			report = resolve_mechanics({"uniqueIds": [{"uniqueId": 2246}, {"uniqueId": 1}]}, root)
			self.assertEqual([entry["status"] for entry in report["resolutions"]], ["UNRESOLVED", "UNRESOLVED"])
			self.assertNotIn(2246, index["registrations"]["uid"])
			self.assertNotIn(1, index["registrations"]["uid"])
			self.assertEqual(index["dynamicRegistrations"], [{"script": "walls.lua", "kind": "uid", "expression": "index", "status": "UNKNOWN"}])

	def test_multiple_candidates_are_ambiguous_and_dynamic_is_unknown(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); (root / "one.lua").write_text("a:aid(42)\n", encoding="utf-8")
			(root / "two.lua").write_text("b:aid(42)\nc:uid(index)\n", encoding="utf-8")
			index = index_scripts(root)
			report = resolve_mechanics({"actionIds": [{"actionId": 42}], "uniqueIds": [{"uniqueId": 99}]}, root)
			self.assertEqual([entry["status"] for entry in report["resolutions"]], ["AMBIGUOUS", "UNRESOLVED"])
			self.assertEqual(index["dynamicRegistrations"], [{"script": "two.lua", "kind": "uid", "expression": "index", "status": "UNKNOWN"}])


if __name__ == "__main__": unittest.main()
