from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.spawns import parse_spawn_file, scan_spawns


class SpawnTests(unittest.TestCase):
	def test_coordinates_use_relative_xy_and_absolute_z(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); path = root / "world-monster.xml"
			path.write_text('<monsters><monster centerx="100" centery="200" centerz="7" radius="3"><monster name="Rat" x="-2" y="4" z="8" spawntime="60" direction="2"/></monster></monsters>', encoding="utf-8")
			spawn = parse_spawn_file(path, root, "monster")[0]
			self.assertEqual(spawn.position, {"x": 98, "y": 204, "z": 8})
			self.assertEqual(spawn.center, {"x": 100, "y": 200, "z": 7})
			self.assertEqual(spawn.origin, "base-map")

	def test_scanner_keeps_sources_and_spawn_kinds_separate(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); (root / "custom").mkdir()
			(root / "world-monster.xml").write_text('<monsters><monster centerx="1" centery="2" centerz="3" radius="1"><monster name="Rat" x="0" y="0" z="3" spawntime="60"/></monster></monsters>', encoding="utf-8")
			(root / "custom" / "extra-npc.xml").write_text('<npcs><npc centerx="4" centery="5" centerz="6" radius="1"><npc name="Guide" x="0" y="0" z="6" spawntime="60"/></npc></npcs>', encoding="utf-8")
			report = scan_spawns(root)
			self.assertEqual(report["statistics"], {"monsterSpawns": 1, "npcSpawns": 1, "files": 2})
			self.assertEqual(report["npcSpawns"][0]["origin"], "conditional-custom-map")


if __name__ == "__main__": unittest.main()
