from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.composition import classify_maps


class CompositionTests(unittest.TestCase):
	def test_only_evidenced_maps_are_runtime_overlays(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			repo = Path(directory); world = repo / "vendor" / "world"; additions = world / "quest" / "demo"; additions.mkdir(parents=True)
			(world / "world.otbm").write_bytes(b"base"); (additions / "loaded.otbm").write_bytes(b"loaded"); (additions / "unknown.otbm").write_bytes(b"unknown")
			custom = world / "custom"; custom.mkdir(); (custom / "extra.otbm").write_bytes(b"extra")
			scripts = repo / "vendor/map-analysis/crystalserver/data-global/scripts"; scripts.mkdir(parents=True)
			(scripts / "load.lua").write_text('Game.loadMap(DATA_DIRECTORY .. "/world/quest/demo/loaded.otbm")', encoding="utf-8")
			result = {entry["source"]: entry for entry in classify_maps(world, repo)["maps"]}
			self.assertEqual(result["world.otbm"]["classification"], "base-map")
			self.assertEqual(result["quest/demo/loaded.otbm"]["classification"], "runtime-loaded-overlay")
			self.assertEqual(result["quest/demo/loaded.otbm"]["runtimeEvidence"], ["vendor/map-analysis/crystalserver/data-global/scripts/load.lua"])
			self.assertEqual(result["quest/demo/unknown.otbm"]["classification"], "UNKNOWN")
			self.assertEqual(result["custom/extra.otbm"]["classification"], "conditional-runtime-overlay")
			self.assertTrue(all(not entry["mergedIntoBaseAtlas"] for entry in result.values()))

	def test_dynamic_directory_and_normalized_map_name_are_evidence(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			repo = Path(directory); world = repo / "world"; maps = world / "world_changes" / "trader"; maps.mkdir(parents=True)
			(maps / "libertybay.otbm").write_bytes(b"map")
			scripts = repo / "vendor/map-analysis/crystalserver/data-global/scripts"; scripts.mkdir(parents=True)
			(scripts / "load.lua").write_text('local mapName="Liberty Bay"\nGame.loadMap("/world/world_changes/trader/" .. string.removeAllSpaces(mapName):lower() .. ".otbm")', encoding="utf-8")
			entry = classify_maps(world, repo)["maps"][0]
			self.assertEqual(entry["classification"], "runtime-loaded-overlay")


if __name__ == "__main__": unittest.main()
