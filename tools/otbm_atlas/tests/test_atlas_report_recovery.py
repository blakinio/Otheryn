from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.atlas import _read_report, _write_text_atomic


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


if __name__ == "__main__":
    unittest.main()
