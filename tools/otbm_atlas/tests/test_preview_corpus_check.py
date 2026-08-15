from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.preview_corpus_check import (
    CANONICAL_ASSETS_SHA256,
    CANONICAL_MAP_SHA256,
    CURRENT_V3_DESKTOP_ASSETS_SHA256,
    REQUIRED_FACTUAL_FILES,
    REQUIRED_VIEWER_FILES,
    inspect_corpus,
)


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class PreviewCorpusCheckTests(unittest.TestCase):
    def _fixture(self, root: Path, *, environment: bool = True, assets_sha: str = CANONICAL_ASSETS_SHA256) -> None:
        detailed = b"detail"
        overview = b"overview"
        low = b"low-overview"
        files = {
            "tiles/z7/1_2.png": detailed,
            "overview/z7/1_2.png": overview,
            "overview-low/z7/1_2.png": low,
        }
        for relative, payload in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        manifest = {
            "schemaVersion": 3,
            "chunkSize": 128,
            "chunks": [
                {
                    "z": 7,
                    "chunkX": 1,
                    "chunkY": 2,
                    "path": "tiles/z7/1_2.png",
                    "checksum": _sha(detailed),
                    "overviewPath": "overview/z7/1_2.png",
                    "overviewChecksum": _sha(overview),
                    "lowOverviewPath": "overview-low/z7/1_2.png",
                    "lowOverviewChecksum": _sha(low),
                }
            ],
            "sources": {
                "mapSha256": CANONICAL_MAP_SHA256,
                "assetsSha256": assets_sha,
                "chunkSize": 128,
                "atlasVersion": 3,
            },
        }
        (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        for relative in REQUIRED_VIEWER_FILES:
            (root / relative).write_text("fixture", encoding="utf-8")
        for relative in REQUIRED_FACTUAL_FILES:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}", encoding="utf-8")
        shard = root / "data/chunks/z7/1_2.json"
        shard.parent.mkdir(parents=True, exist_ok=True)
        shard.write_text('{"schemaVersion":1}', encoding="utf-8")
        for kind in ("npc", "monster"):
            path = root / f"data/{kind}-sprites/index.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"schemaVersion":2,"sprites":[],"animations":[]}', encoding="utf-8")
        if environment:
            path = root / "data/environment-animations/index.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"schemaVersion":2,"statistics":{"chunks":0}}', encoding="utf-8")

    def test_complete_fixture_is_full_browser_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            report = inspect_corpus(root, expected_chunks=1)
            self.assertTrue(report["browserCoreReady"])
            self.assertTrue(report["fullBrowserReady"])
            self.assertTrue(report["detailCorpus"]["checksumsVerified"])

    def test_missing_environment_is_explicit_without_invalidating_browser_core(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root, environment=False)
            report = inspect_corpus(root, expected_chunks=1)
            self.assertTrue(report["browserCoreReady"])
            self.assertFalse(report["environmentAnimations"]["ready"])
            self.assertFalse(report["fullBrowserReady"])
            self.assertIn("OTH-20260815-atlas-environment-animation-export-performance.md", report["environmentAnimations"]["dependencyTask"])

    def test_checksum_mismatch_blocks_detail_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root)
            (root / "tiles/z7/1_2.png").write_bytes(b"corrupt")
            report = inspect_corpus(root, expected_chunks=1)
            self.assertFalse(report["detailCorpus"]["ready"])
            self.assertTrue(any("checksum mismatch" in issue for issue in report["detailCorpus"]["issues"]))

    def test_verified_current_v3_desktop_asset_fingerprint_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._fixture(root, assets_sha=CURRENT_V3_DESKTOP_ASSETS_SHA256)
            report = inspect_corpus(root, expected_chunks=1)
            self.assertTrue(report["detailCorpus"]["ready"])
            self.assertEqual(report["detailCorpus"]["assetsProvenance"], "verified-current-v3-desktop-worktree-bytes")


if __name__ == "__main__":
    unittest.main()
