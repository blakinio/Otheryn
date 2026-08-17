from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


def _load_module():
    path = Path(__file__).with_name("transfer_state.py")
    spec = importlib.util.spec_from_file_location("atlas_transfer_state", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


transfer_state = _load_module()
PRODUCER = "a" * 40


class TransferStateTests(unittest.TestCase):
    def test_export_resume_reuses_only_complete_durable_marker(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "generation"
            output = Path(temporary) / "out"
            marker_root = root / "control" / "transferred-verified"
            evidence_root = marker_root / "evidence"
            evidence_root.mkdir(parents=True)
            (root / "receipts").mkdir(parents=True)
            (root / "bundles" / "shard-00").mkdir(parents=True)
            (root / "receipts" / "shard-00.json").write_text("{}\n", encoding="utf-8")
            marker = {
                "schemaVersion": 1,
                "status": "TRANSFERRED_VERIFIED",
                "producerSha": PRODUCER,
                "bundleId": "shard-00",
                "shardIndex": 0,
                "archiveBytes": 123,
                "archiveSha256": "b" * 64,
                "chunks": 109,
            }
            (marker_root / "shard-00.json").write_text(json.dumps(marker) + "\n", encoding="utf-8")
            (evidence_root / "full-world-shard-00.json").write_text('{"shardIndex":0}\n', encoding="utf-8")
            (evidence_root / "shard-manifest-00.json").write_text('{"schemaVersion":3}\n', encoding="utf-8")

            summary = transfer_state.export_resume(root, PRODUCER, output)

            self.assertEqual(summary["transferredVerifiedShards"], [0])
            self.assertEqual(summary["transferredCsv"], "0")
            self.assertTrue((output / "full-world-shard-00.json").is_file())
            self.assertTrue((output / "shard-manifest-00.json").is_file())

    def test_export_resume_ignores_marker_for_other_producer(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "generation"
            output = Path(temporary) / "out"
            marker_root = root / "control" / "transferred-verified"
            evidence_root = marker_root / "evidence"
            evidence_root.mkdir(parents=True)
            (root / "receipts").mkdir(parents=True)
            (root / "bundles" / "shard-00").mkdir(parents=True)
            (root / "receipts" / "shard-00.json").write_text("{}\n", encoding="utf-8")
            (marker_root / "shard-00.json").write_text(json.dumps({"status": "TRANSFERRED_VERIFIED", "producerSha": "c" * 40, "shardIndex": 0}) + "\n", encoding="utf-8")
            (evidence_root / "full-world-shard-00.json").write_text("{}\n", encoding="utf-8")
            (evidence_root / "shard-manifest-00.json").write_text("{}\n", encoding="utf-8")

            summary = transfer_state.export_resume(root, PRODUCER, output)

            self.assertEqual(summary["transferredVerifiedShards"], [])
            self.assertEqual(summary["transferredCsv"], "")

    def test_verify_existing_reports_missing_without_touching_uploader(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "generation"
            root.mkdir(parents=True)
            summary = transfer_state.verify_existing(root, PRODUCER, Path("does-not-need-to-exist.py"), False)
            self.assertEqual(summary["verifiedShards"], [])
            self.assertEqual(summary["missingShards"], list(range(32)))
            self.assertEqual(summary["status"], "PARTIAL_TRANSFERRED_VERIFIED")

    def test_verify_existing_require_all_fails_on_missing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "generation"
            root.mkdir(parents=True)
            with self.assertRaises(RuntimeError):
                transfer_state.verify_existing(root, PRODUCER, Path("unused.py"), True)


if __name__ == "__main__":
    unittest.main()
