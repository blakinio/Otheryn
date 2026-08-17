from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.atlas import _overview_report, _read_report, _write_text_atomic


class AtlasReportRecoveryTests(unittest.TestCase):
    def test_malformed_cached_report_is_treated_as_non_reusable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "chunk.json"
            path.write_text("{broken", encoding="utf-8")
            self.assertIsNone(_read_report(path))

    def test_atomic_report_replacement_leaves_complete_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "chunk.json"
            path.write_text("old\n", encoding="utf-8")
            _write_text_atomic(path, '{"checksum":"new"}\n')
            self.assertEqual(path.read_text(encoding="utf-8"), '{"checksum":"new"}\n')
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_overview_report_scales_both_dimensions(self) -> None:
        report = _overview_report({"imageWidth": 1024, "imageHeight": 768}, b"png", 4, "fp")
        self.assertEqual(report["imageWidth"], 256)
        self.assertEqual(report["imageHeight"], 192)
        self.assertEqual(report["fingerprint"], "fp")


if __name__ == "__main__":
    unittest.main()
