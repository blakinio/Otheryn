from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.environment_animation_resume import enrich_environment_animations_resumable


class EnvironmentSpoolGuardTests(unittest.TestCase):
    def test_manifest_chunk_without_spool_fails_closed_before_export(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "atlas"
            spool = output / ".spool"
            spool.mkdir(parents=True)
            (spool / "spool.json").write_text('{"chunkSize":128}\n', encoding="utf-8")
            (output / "manifest.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 3,
                        "chunkSize": 128,
                        "chunks": [
                            {
                                "z": 7,
                                "chunkX": 1,
                                "chunkY": 1,
                                "logicalBounds": [128, 255, 128, 255, 7],
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, r"missing spool shards: z7/1_1"):
                enrich_environment_animations_resumable(root / "unused-assets", output)

            self.assertFalse((output / "data/environment-animations").exists())


if __name__ == "__main__":
    unittest.main()
