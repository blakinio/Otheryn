from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.otbm_atlas.assets import encode_png
from tools.otbm_atlas.resume_partial_local import load_verified_detail_chunks


def _write_detail(output: Path, fingerprint: str = "fingerprint") -> Path:
    pixels = bytes((23, 47, 89, 255)) * 16
    payload = encode_png(4, 4, pixels)
    path = output / "tiles" / "z7" / "1_2.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    report = {
        "fingerprint": fingerprint,
        "checksum": hashlib.sha256(payload).hexdigest(),
        "imageWidth": 4,
        "imageHeight": 4,
        "tiles": 1,
        "groundItems": 1,
        "childItems": 0,
        "renderOperations": 1,
        "missingAppearances": {},
        "missingSprites": {},
    }
    path.with_suffix(".json").write_text(json.dumps(report), encoding="utf-8")
    return path


class PartialResumeTests(unittest.TestCase):
    def test_verified_detail_is_adopted_without_render(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            _write_detail(output)
            chunks = load_verified_detail_chunks(output, {"z7/1_2": "fingerprint"}, 128)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["path"], "tiles/z7/1_2.png")
        self.assertEqual(chunks[0]["logicalBounds"], [128, 255, 256, 383, 7])

    def test_tampered_detail_png_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            path = _write_detail(output)
            path.write_bytes(path.read_bytes() + b"tamper")
            with self.assertRaisesRegex(RuntimeError, "PNG checksum mismatch"):
                load_verified_detail_chunks(output, {"z7/1_2": "fingerprint"}, 128)

    def test_wrong_detail_fingerprint_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            _write_detail(output)
            with self.assertRaisesRegex(RuntimeError, "fingerprint mismatch"):
                load_verified_detail_chunks(output, {"z7/1_2": "different"}, 128)

    def test_local_launchers_are_valid_bash(self) -> None:
        repository = Path(__file__).parents[3]
        for relative in (
            "tools/otbm_atlas/build_latest_local.sh",
            "tools/otbm_atlas/resume_latest_local.sh",
        ):
            subprocess.run(["bash", "-n", relative], cwd=repository, check=True)


if __name__ == "__main__":
    unittest.main()
