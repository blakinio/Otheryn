from __future__ import annotations

from io import BytesIO
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest import mock

from tools.otbm_atlas import world_publish


def _load_deploy_module(name: str, filename: str):
    path = Path(__file__).resolve().parents[3] / "deploy" / "otbm-atlas-ci-ingest" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


receiver = _load_deploy_module("atlas_ci_receiver", "receiver.py")
uploader = _load_deploy_module("atlas_ci_uploader", "upload_bundle.py")


class CIIngestTests(unittest.TestCase):
    def test_receiver_requires_exact_bearer_capability(self):
        with tempfile.TemporaryDirectory() as text:
            token = "a" * 64
            target = receiver.Receiver(Path(text), token)
            self.assertFalse(target.authorized(None))
            self.assertFalse(target.authorized("Bearer " + "b" * 64))
            self.assertFalse(target.authorized(token))
            self.assertTrue(target.authorized("Bearer " + token))

    def test_oversized_part_is_rejected_before_body_read(self):
        class ShouldNotRead:
            def read(self, _size):
                raise AssertionError("oversized part must fail before reading request body")

        with tempfile.TemporaryDirectory() as text:
            target = receiver.Receiver(Path(text), "x" * 64, max_part_bytes=8)
            with self.assertRaisesRegex(ValueError, "part size"):
                target.store_part("fixture", "part-0000", ShouldNotRead(), 9, "0" * 64)

    def test_safe_extract_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as text:
            root = Path(text)
            archive = root / "bad.tar"
            with tarfile.open(archive, "w") as package:
                info = tarfile.TarInfo("../escape.txt")
                payload = b"nope"
                info.size = len(payload)
                package.addfile(info, BytesIO(payload))
            with self.assertRaisesRegex(ValueError, "unsafe archive member"):
                receiver.safe_extract_tar(archive, root / "out")
            self.assertFalse((root / "escape.txt").exists())

    def test_safe_extract_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as text:
            root = Path(text)
            archive = root / "bad.tar"
            with tarfile.open(archive, "w") as package:
                info = tarfile.TarInfo("link")
                info.type = tarfile.SYMTYPE
                info.linkname = "/etc/passwd"
                package.addfile(info)
            with self.assertRaisesRegex(ValueError, "unsupported archive member type"):
                receiver.safe_extract_tar(archive, root / "out")

    def test_part_store_and_completion_are_sha_bound(self):
        with tempfile.TemporaryDirectory() as text:
            root = Path(text)
            source = root / "source"
            source.mkdir()
            (source / "hello.txt").write_text("hello atlas\n", encoding="utf-8")
            archive = root / "bundle.tar"
            info = uploader.build_archive(source, archive)
            parts = uploader.split_archive(archive, root / "split", 4096)
            target = receiver.Receiver(root / "receiver", "x" * 64, max_part_bytes=4096)
            manifest_parts = []
            for part in parts:
                payload = Path(part["path"]).read_bytes()
                stored = target.store_part("fixture", part["name"], BytesIO(payload), len(payload), part["sha256"])
                self.assertIn(stored["status"], {"stored", "reused"})
                manifest_parts.append({"name": part["name"], "bytes": part["bytes"], "sha256": part["sha256"]})
            receipt = target.complete("fixture", {
                "schemaVersion": 1,
                "bundleId": "fixture",
                "kind": "fixture",
                "producerSha": "a" * 40,
                "archiveSha256": info["sha256"],
                "parts": manifest_parts,
            })
            self.assertEqual(receipt["status"], "COMPLETE")
            self.assertEqual((root / "receiver/bundles/fixture/hello.txt").read_text(encoding="utf-8"), "hello atlas\n")
            self.assertFalse((root / "receiver/parts/fixture").exists())

    def test_existing_part_with_different_bytes_is_rejected(self):
        with tempfile.TemporaryDirectory() as text:
            target = receiver.Receiver(Path(text), "x" * 64, max_part_bytes=64)
            payload = b"first"
            sha = hashlib.sha256(payload).hexdigest()
            target.store_part("fixture", "part-0000", BytesIO(payload), len(payload), sha)
            other = b"other"
            other_sha = hashlib.sha256(other).hexdigest()
            with self.assertRaises(FileExistsError):
                target.store_part("fixture", "part-0000", BytesIO(other), len(other), other_sha)

    def test_completion_rejects_total_bundle_size_bound(self):
        with tempfile.TemporaryDirectory() as text:
            root = Path(text)
            target = receiver.Receiver(root, "x" * 64, max_part_bytes=64)
            payload = b"0123456789"
            sha = hashlib.sha256(payload).hexdigest()
            target.store_part("fixture", "part-0000", BytesIO(payload), len(payload), sha)
            with mock.patch.object(receiver, "MAX_BUNDLE_BYTES", 9):
                with self.assertRaisesRegex(ValueError, "bundle archive exceeds"):
                    target.complete("fixture", {
                        "schemaVersion": 1,
                        "bundleId": "fixture",
                        "kind": "fixture",
                        "producerSha": "a" * 40,
                        "archiveSha256": sha,
                        "parts": [{"name": "part-0000", "bytes": len(payload), "sha256": sha}],
                    })


class WorldPublishTests(unittest.TestCase):
    def _write_complete_manifest_set(self, root: Path) -> None:
        chunks = []
        for z, count in world_publish.EXPECTED_FLOORS.items():
            for index in range(count):
                chunks.append({
                    "z": z,
                    "chunkX": index % 64,
                    "chunkY": index // 64,
                    "path": f"tiles/z{z}/{index % 64}_{index // 64}.png",
                    "overviewPath": f"overview/z{z}/{index % 64}_{index // 64}.png",
                    "lowOverviewPath": f"overview-low/z{z}/{index % 64}_{index // 64}.png",
                })
        keys = [world_publish._chunk_key(chunk) for chunk in chunks]
        coverage = world_publish._coverage_digest(keys)
        assignments = [[] for _ in range(world_publish.EXPECTED_SHARDS)]
        for index, chunk in enumerate(chunks):
            assignments[index % world_publish.EXPECTED_SHARDS].append(chunk)
        for shard, values in enumerate(assignments):
            manifest = {
                "schemaVersion": world_publish.EXPECTED_ATLAS_VERSION,
                "chunkSize": world_publish.EXPECTED_CHUNK_SIZE,
                "tilePixels": 32,
                "overviewFactor": 4,
                "lowOverviewFactor": 8,
                "overviewVersion": 1,
                "sources": {
                    "mapSha256": world_publish.EXPECTED_MAP_SHA256,
                    "assetsSha256": "a",
                    "chunkSize": world_publish.EXPECTED_CHUNK_SIZE,
                    "atlasVersion": world_publish.EXPECTED_ATLAS_VERSION,
                    "tileFactsVersion": 1,
                },
                "provenance": {"map": "world.otbm", "appearanceAssetRoot": "assets"},
                "chunks": values,
                "certification": {
                    "scope": "world-chunk-shard",
                    "shardIndex": shard,
                    "shardCount": world_publish.EXPECTED_SHARDS,
                    "worldPlanDigest": "plan",
                    "coverageDigest": coverage,
                },
            }
            (root / f"shard-manifest-{shard:02d}.json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_merge_shard_manifests_requires_exact_world(self):
        with tempfile.TemporaryDirectory() as text:
            root = Path(text)
            self._write_complete_manifest_set(root)
            merged = world_publish.merge_shard_manifests(root, "a" * 40)
            self.assertEqual(len(merged["chunks"]), 3494)
            self.assertEqual(merged["certification"]["scope"], "full-world-assembled-publication")
            self.assertEqual(merged["certification"]["producerSha"], "a" * 40)

    def test_current_capture_promotion_and_rollback_are_manifest_bound(self):
        with tempfile.TemporaryDirectory() as text:
            root = Path(text) / "atlas"
            current = root / "current"
            current.mkdir(parents=True)
            (current / "manifest.json").write_text('{"generation":"old"}\n', encoding="utf-8")
            state_path = root / "state.json"
            captured = world_publish.capture_current(root, state_path)
            self.assertTrue(captured["exists"])

            assembled = root / "incoming/assembled"
            (assembled / "data").mkdir(parents=True)
            (assembled / "manifest.json").write_text('{"generation":"new"}\n', encoding="utf-8")
            (assembled / "data/deployment-source.json").write_text(json.dumps({"producerSha": "b" * 40}), encoding="utf-8")
            receipt_path = root / "deployments/test.json"
            receipt = world_publish.promote(assembled, root, state_path, "test", receipt_path)
            self.assertEqual(receipt["status"], "PROMOTED_PENDING_RUNTIME")
            self.assertEqual(json.loads((root / "current/manifest.json").read_text())["generation"], "new")
            self.assertEqual(json.loads((root / "previous-test/manifest.json").read_text())["generation"], "old")

            rolled = world_publish.rollback(root, receipt_path)
            self.assertEqual(rolled["status"], "ROLLED_BACK_RUNTIME_FAILURE")
            self.assertEqual(json.loads((root / "current/manifest.json").read_text())["generation"], "old")
            self.assertEqual(json.loads((root / "failed-test/manifest.json").read_text())["generation"], "new")

    def test_promotion_refuses_current_drift(self):
        with tempfile.TemporaryDirectory() as text:
            root = Path(text) / "atlas"
            current = root / "current"
            current.mkdir(parents=True)
            (current / "manifest.json").write_text('{"generation":1}\n', encoding="utf-8")
            state_path = root / "state.json"
            world_publish.capture_current(root, state_path)
            (current / "manifest.json").write_text('{"generation":2}\n', encoding="utf-8")
            assembled = root / "incoming/assembled"
            (assembled / "data").mkdir(parents=True)
            (assembled / "manifest.json").write_text('{"generation":3}\n', encoding="utf-8")
            (assembled / "data/deployment-source.json").write_text(json.dumps({"producerSha": "c" * 40}), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "current changed"):
                world_publish.promote(assembled, root, state_path, "test", root / "receipt.json")
            self.assertEqual(json.loads((current / "manifest.json").read_text())["generation"], 2)


if __name__ == "__main__":
    unittest.main()
