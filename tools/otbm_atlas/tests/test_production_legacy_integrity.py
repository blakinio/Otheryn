from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.incremental_core import sha256_file
from tools.otbm_atlas.production_incremental import _detail_output_reusable, overview_output_reusable


class ProductionLegacyIntegrityTests(unittest.TestCase):
    @staticmethod
    def _write_report_bound_output(root: Path, directory: str, payload: bytes, fingerprint: str = "fp") -> Path:
        image = root / directory / "z7/1_2.png"
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(payload)
        image.with_suffix(".json").write_text(
            json.dumps({"checksum": sha256_file(image), "fingerprint": fingerprint}) + "\n",
            encoding="utf-8",
        )
        return image

    def test_legacy_detail_reuse_requires_actual_png_checksum_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            image = self._write_report_bound_output(output, "tiles", b"detail-v1")
            self.assertTrue(_detail_output_reusable(output, "z7/1_2", None))

            image.write_bytes(b"detail-v2")
            self.assertFalse(_detail_output_reusable(output, "z7/1_2", None))

    def test_legacy_overview_reuse_requires_actual_png_checksum_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            image = self._write_report_bound_output(output, "overview", b"overview-v1", fingerprint="derived-fp")
            self.assertTrue(overview_output_reusable(output, "overview", "z7/1_2", "derived-fp", None))

            image.write_bytes(b"overview-v2")
            self.assertFalse(overview_output_reusable(output, "overview", "z7/1_2", "derived-fp", None))


if __name__ == "__main__":
    unittest.main()
