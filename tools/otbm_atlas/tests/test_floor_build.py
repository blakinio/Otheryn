from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.floor_build import _keep_floor_spool


class FloorBuildTests(unittest.TestCase):
    def test_keep_floor_spool_removes_other_floor_render_and_tile_fact_shards(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            spool = Path(temporary)
            for z in (6, 7, 8):
                render = spool / f"z{z}" / "1_2.bin"
                render.parent.mkdir(parents=True, exist_ok=True)
                render.write_bytes(f"z{z}".encode())
                fact = spool / "tile-facts" / f"z{z}" / "1_2.jsonl"
                fact.parent.mkdir(parents=True, exist_ok=True)
                fact.write_text('{"x":1}\n', encoding="utf-8")

            chunks, sidecars = _keep_floor_spool(spool, 7)

            self.assertEqual(chunks, ["z7/1_2"])
            self.assertEqual(sidecars, ["z7/1_2.jsonl"])
            self.assertTrue((spool / "z7/1_2.bin").is_file())
            self.assertTrue((spool / "tile-facts/z7/1_2.jsonl").is_file())
            self.assertFalse((spool / "z6/1_2.bin").exists())
            self.assertFalse((spool / "z8/1_2.bin").exists())
            self.assertFalse((spool / "tile-facts/z6/1_2.jsonl").exists())
            self.assertFalse((spool / "tile-facts/z8/1_2.jsonl").exists())

    def test_keep_floor_spool_rejects_empty_floor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            spool = Path(temporary)
            (spool / "z6").mkdir(parents=True)
            (spool / "z6/1_2.bin").write_bytes(b"z6")
            with self.assertRaisesRegex(RuntimeError, "Z7"):
                _keep_floor_spool(spool, 7)


if __name__ == "__main__":
    unittest.main()
