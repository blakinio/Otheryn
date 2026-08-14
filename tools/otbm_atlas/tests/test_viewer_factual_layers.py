from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.otbm_atlas.factual_layers import _merge_spatial
from tools.otbm_atlas.viewer import VIEWER_HTML, write_viewer


class FactualViewerContractTests(unittest.TestCase):
    def test_raid_area_is_replicated_to_every_intersecting_chunk(self) -> None:
        factual = {
            "groups": {
                "scriptedTeleports": [],
                "raidPointSpawns": [],
                "raidAreas": [{
                    "name": "cross-chunk raid",
                    "position": {"x": 128, "y": 128, "z": 7},
                    "positionRole": "derived-navigation-center",
                    "bounds": {"x1": 120, "x2": 135, "y1": 120, "y2": 135, "z": 7},
                }],
                "npcServices": [],
                "verifiedBossSpawns": [],
            },
            "actionIds": [],
            "uniqueIds": [],
        }
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "data").mkdir(parents=True)
            (output / "data/search-index.json").write_text(json.dumps({"schemaVersion": 1, "records": []}), encoding="utf-8")
            report = _merge_spatial(output, 128, factual)
            self.assertEqual(report["touchedShards"], 4)
            for chunk_x, chunk_y in ((0, 0), (0, 1), (1, 0), (1, 1)):
                path = output / f"data/chunks/z7/{chunk_x}_{chunk_y}.json"
                content = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(content["raidAreas"][0]["bounds"]["x1"], 120)

    def test_viewer_exposes_factual_layers_without_hidden_enrichment_side_effect(self) -> None:
        for kind in ("scriptedTeleports", "raidAreas", "raidPointSpawns", "npcServices", "verifiedBossSpawns"):
            self.assertIn(f'data-overlay="{kind}"', VIEWER_HTML)
        self.assertNotIn("Bosses (UNKNOWN)", VIEWER_HTML)
        with TemporaryDirectory() as directory:
            output = Path(directory)
            path = write_viewer(output)
            self.assertTrue(path.is_file())
            self.assertTrue((output / "viewer-app.js").is_file())
            self.assertFalse((output / "data/factual-layers.json").exists())


if __name__ == "__main__":
    unittest.main()
