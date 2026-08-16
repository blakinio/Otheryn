from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.deploy_preflight import (
    EXPECTED_MAP_SHA256,
    KNOWN_ASSET_SHA256,
    deployment_preflight,
)
from tools.otbm_atlas.viewer import write_viewer


class DeployPreflightTests(unittest.TestCase):
    def make_fixture(self, *, environment: bool = True, assets_sha: str | None = None) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        write_viewer(root)
        (root / "data").mkdir(exist_ok=True)
        chunks = [
            {"z": z, "chunkX": index, "chunkY": z, "path": f"tiles/z{z}/{index}_{z}.png"}
            for z in range(16)
            for index in range(218)
        ]
        chunks.extend(
            {"z": z, "chunkX": 1000 + z, "chunkY": z, "path": f"tiles/z{z}/{1000 + z}_{z}.png"}
            for z in range(6)
        )
        self.assertEqual(3494, len(chunks))
        if assets_sha is None:
            assets_sha = next(iter(KNOWN_ASSET_SHA256))
        manifest = {
            "schemaVersion": 3,
            "chunkSize": 128,
            "chunks": chunks,
            "sources": {
                "mapSha256": EXPECTED_MAP_SHA256,
                "assetsSha256": assets_sha,
                "chunkSize": 128,
                "atlasVersion": 3,
            },
        }
        (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (root / "data/search-index.json").write_text(json.dumps({"records": []}), encoding="utf-8")
        (root / "data/statistics.json").write_text(json.dumps({"chunks": 3494}), encoding="utf-8")
        (root / "data/spawns.json").write_text(
            json.dumps({"npcSpawns": [], "monsterSpawns": [], "statistics": {}}),
            encoding="utf-8",
        )
        if environment:
            directory = root / "data/environment-animations"
            directory.mkdir(parents=True)
            (directory / "index.json").write_text(
                json.dumps({"schemaVersion": 2, "statistics": {"instances": 1, "uniqueAnimations": 1, "chunks": 1, "staticFallbacks": 0}}),
                encoding="utf-8",
            )
        return root

    def test_full_runtime_fixture_is_ready(self) -> None:
        report = deployment_preflight(self.make_fixture(), verify_chunks=False, require_environment_animations=True)
        self.assertEqual("FULL_RUNTIME_READY", report["status"])
        self.assertTrue(report["corePreviewReady"])
        self.assertTrue(report["fullRuntimeReady"])
        self.assertEqual([], report["errors"])
        self.assertEqual([], report["requirementErrors"])
        self.assertEqual("CURRENT", report["viewer"]["status"])

    def test_missing_environment_is_explicit_partial_state(self) -> None:
        root = self.make_fixture(environment=False)
        report = deployment_preflight(root, verify_chunks=False)
        self.assertEqual("CORE_PREVIEW_READY", report["status"])
        self.assertTrue(report["corePreviewReady"])
        self.assertFalse(report["fullRuntimeReady"])
        self.assertEqual("MISSING", report["environmentAnimations"]["status"])
        self.assertEqual([], report["requirementErrors"])
        required = deployment_preflight(root, verify_chunks=False, require_environment_animations=True)
        self.assertEqual(
            ["environment-animation final artifact required but missing or invalid"],
            required["requirementErrors"],
        )

    def test_unknown_asset_provenance_is_rejected(self) -> None:
        report = deployment_preflight(
            self.make_fixture(assets_sha="0" * 64),
            verify_chunks=False,
        )
        self.assertEqual("NOT_READY", report["status"])
        self.assertFalse(report["corePreviewReady"])
        self.assertTrue(any("asset SHA-256" in error for error in report["errors"]))

    def test_stale_viewer_is_rejected(self) -> None:
        root = self.make_fixture()
        (root / "viewer-app.js").write_text("// stale\n", encoding="utf-8")
        report = deployment_preflight(root, verify_chunks=False)
        self.assertEqual("NOT_READY", report["status"])
        self.assertEqual("NOT_CURRENT", report["viewer"]["status"])
        self.assertTrue(any("viewer-app.js" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
