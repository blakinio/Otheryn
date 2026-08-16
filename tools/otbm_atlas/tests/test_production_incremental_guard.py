from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.otbm_atlas.incremental_core import sha256_file
from tools.otbm_atlas.production_incremental import prepare_production_render_plan


class ProductionIncrementalGuardTests(unittest.TestCase):
    def test_existing_unbound_publication_with_source_mismatch_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            map_path = root / "world.otbm"
            map_path.write_bytes(b"current-map")
            asset_dir = root / "assets"
            asset_dir.mkdir()
            output = root / "atlas"
            output.mkdir()
            (output / "manifest.json").write_text(json.dumps({
                "schemaVersion": 3,
                "chunkSize": 128,
                "sources": {
                    "mapSha256": "older-map-sha",
                    "assetsSha256": "same-assets",
                    "chunkSize": 128,
                    "atlasVersion": 3,
                },
                "chunks": [],
            }), encoding="utf-8")
            expected = {
                "mapSha256": sha256_file(map_path),
                "assetsSha256": "same-assets",
                "chunkSize": 128,
                "atlasVersion": 3,
            }
            with (
                patch("tools.otbm_atlas.production_incremental.collect_asset_state", return_value={"stateDigest": "assets", "gutterProfile": "g1"}),
                patch("tools.otbm_atlas.production_incremental.render_contract_digest", return_value="render-v1"),
            ):
                with self.assertRaisesRegex(RuntimeError, "UNBOUND_PUBLICATION_SOURCE_MISMATCH"):
                    prepare_production_render_plan(
                        map_path,
                        asset_dir,
                        output,
                        root,
                        128,
                        expected,
                        {"version": 1, "tileFactsVersion": 1},
                        lambda *_: self.fail("source mismatch must fail before spooling"),
                    )


if __name__ == "__main__":
    unittest.main()
