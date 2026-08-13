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
		for marker in ("actionIds", "uniqueIds", "teleports", "houseDoors", "monsterSpawns", "npcSpawns", "Jump", "Search world", "details"):
			self.assertIn(marker, text)
		for marker in ("Render mode", "Auto", "Detailed", "Performance", "Diagnostics"):
			self.assertIn(marker, text)
		self.assertIn('min="-8" max="7"', text)


if __name__ == "__main__": unittest.main()
