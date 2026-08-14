from __future__ import annotations
from pathlib import Path
import tempfile,unittest
from tools.otbm_atlas.viewer import write_viewer
class ViewerTests(unittest.TestCase):
	def test_static_viewer_exposes_navigation_and_required_overlays(self)->None:
		with tempfile.TemporaryDirectory() as directory:
			text=write_viewer(directory).read_text(encoding="utf-8");self.assertTrue((Path(directory)/"viewer-runtime.js").is_file());self.assertTrue((Path(directory)/"viewer-app.js").is_file())
		for marker in ("actionIds","uniqueIds","teleports","houseDoors","monsterSpawns","npcSpawns","Jump","Search world","details","tooltip","X,Y,Z"):self.assertIn(marker,text)
		for marker in ("Render mode","Auto","Detailed","Performance","Diagnostics"):self.assertIn(marker,text)
		self.assertIn('min="0" max="15"',text);app=(Path(__file__).parents[1]/"viewer_app.js").read_text(encoding="utf-8");runtime=(Path(__file__).parents[1]/"viewer_runtime.js").read_text(encoding="utf-8");self.assertIn("Number.isInteger(requestedZ)",app);self.assertIn("displayFloor=z=>z",app);self.assertIn("state.overlays=[...state.overlays,item.kind]",app);self.assertIn("if(target)showDetails(item.kind,target)",app);self.assertIn("parseCoordinateSearch",app);self.assertIn("showTooltip",app);self.assertIn("drawNpcSprite",app);self.assertIn("record.sprite",app);self.assertIn("supplementalNpcSpawns",runtime);self.assertIn("supplementalMonsterSpawns",runtime);self.assertIn("p.has('z')&&Number.isFinite(+p.get('z'))?+p.get('z'):7",runtime)
if __name__=="__main__":unittest.main()
