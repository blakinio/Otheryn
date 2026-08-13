from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.mechanics import index_scripts, resolve_mechanics


class MechanicsTests(unittest.TestCase):
	def test_literal_registrations_and_uid_dispatch_are_resolved(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			(root / "move.lua").write_text("local e=MoveEvent()\ne:aid(5555)\ne:register()\n", encoding="utf-8")
			(root / "quest.lua").write_text("local config={[65207]={}}\nlocal x=config[item.uid]\nlocal a=Action()\na:aid(2001)\na:register()\n", encoding="utf-8")
			report = resolve_mechanics({"actionIds": [{"actionId": 5555}], "uniqueIds": [{"uniqueId": 65207}]}, root)
			self.assertEqual([entry["status"] for entry in report["resolutions"]], ["RESOLVED", "RESOLVED"])
			self.assertEqual(report["resolutions"][1]["candidates"][0]["basis"], "literal-uid-dispatch-key")

	def test_multiple_candidates_are_ambiguous_and_dynamic_is_unknown(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			(root / "one.lua").write_text("a:aid(42)\n", encoding="utf-8")
			(root / "two.lua").write_text("b:aid(42)\nc:uid(index)\n", encoding="utf-8")
			index = index_scripts(root)
			report = resolve_mechanics({"actionIds": [{"actionId": 42}], "uniqueIds": [{"uniqueId": 99}]}, root)
			self.assertEqual([entry["status"] for entry in report["resolutions"]], ["AMBIGUOUS", "UNRESOLVED"])
			self.assertEqual(index["dynamicRegistrations"], [{"script": "two.lua", "kind": "uid", "expression": "index", "status": "UNKNOWN"}])


if __name__ == "__main__": unittest.main()
