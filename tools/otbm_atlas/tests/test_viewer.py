from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.viewer import write_viewer


class ViewerTests(unittest.TestCase):
	def test_static_viewer_exposes_navigation_and_required_overlays(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			text = write_viewer(directory).read_text(encoding="utf-8")
		for marker in ("manifest.json", "data/mechanics.json", "actionIds", "uniqueIds", "teleports", "houseDoors", "monsterSpawns", "npcSpawns", "Jump"):
			self.assertIn(marker, text)
		self.assertIn('min="-8" max="7"', text)
		self.assertIn("function displayFloor(rawZ){return 7-rawZ}", text)
		self.assertIn("sort((a,b)=>displayFloor(a)-displayFloor(b))", text)


if __name__ == "__main__": unittest.main()
