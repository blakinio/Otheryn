from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.viewer import write_viewer


class ViewerTests(unittest.TestCase):
	def test_static_viewer_exposes_navigation_and_required_overlays(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			text = write_viewer(directory).read_text(encoding="utf-8")
			self.assertTrue((Path(directory) / "viewer-runtime.js").is_file())
			self.assertTrue((Path(directory) / "viewer-app.js").is_file())
		for marker in ("actionIds", "uniqueIds", "teleports", "houseDoors", "monsterSpawns", "npcSpawns", "supplementalMonsterSpawns", "supplementalNpcSpawns", "Jump", "Search world", "details", "tooltip", "X,Y,Z"):
			self.assertIn(marker, text)
		for marker in ("Render mode", "Auto", "Detailed", "Performance", "Diagnostics"):
			self.assertIn(marker, text)
		self.assertIn('min="-8" max="7"', text)
		app=(Path(__file__).parents[1]/"viewer_app.js").read_text(encoding="utf-8")
		self.assertIn("Number.isInteger(requestedFloor)",app)
		self.assertIn("parseCoordinateSearch",app)
		self.assertIn("showTooltip",app)
		self.assertIn("ctx.imageSmoothingEnabled=false",app)
		self.assertIn("for(const chunk of visible)",app)
		self.assertIn("supplementalMonsterSpawns",app)


if __name__ == "__main__": unittest.main()
