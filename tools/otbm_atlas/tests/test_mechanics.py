from __future__ import annotations
from pathlib import Path
import tempfile,unittest
from tools.otbm_atlas.mechanics import index_scripts,resolve_mechanics
class MechanicsTests(unittest.TestCase):
	def test_literal_registrations_resolve_but_dynamic_uid_table_does_not_guess(self):
		with tempfile.TemporaryDirectory() as directory:
			root=Path(directory);(root/"move.lua").write_text("local e=MoveEvent()\ne:aid(5555)\ne:register()\n",encoding="utf-8");(root/"quest.lua").write_text("local config={[65207]={}}\nlocal x=config[item.uid]\nlocal a=Action()\na:uid(65208)\na:register()\n",encoding="utf-8")
			report=resolve_mechanics({"actionIds":[{"actionId":5555}],"uniqueIds":[{"uniqueId":65207},{"uniqueId":65208}]},root)
			self.assertEqual([entry["status"] for entry in report["resolutions"]],["RESOLVED","UNRESOLVED","RESOLVED"]);self.assertEqual(report["resolutions"][2]["candidates"][0]["basis"],"literal-registration")
	def test_multiple_candidates_are_ambiguous_and_dynamic_is_unknown(self):
		with tempfile.TemporaryDirectory() as directory:
			root=Path(directory);(root/"one.lua").write_text("a:aid(42)\n",encoding="utf-8");(root/"two.lua").write_text("b:aid(42)\nc:uid(index)\n",encoding="utf-8");index=index_scripts(root);report=resolve_mechanics({"actionIds":[{"actionId":42}],"uniqueIds":[{"uniqueId":99}]},root)
			self.assertEqual([entry["status"] for entry in report["resolutions"]],["AMBIGUOUS","UNRESOLVED"]);self.assertEqual(index["dynamicRegistrations"],[{"script":"two.lua","kind":"uid","expression":"index","status":"UNKNOWN"}])
if __name__=="__main__":unittest.main()
