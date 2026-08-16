from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.otbm_atlas.assets import Appearance, SpriteInfo, SpriteSheet
from tools.otbm_atlas.atlas import encode_tile
from tools.otbm_atlas.environment_animation_resume import enrich_environment_animations_resumable
from tools.otbm_atlas.semantic import Item, Position, Tile


class _FakeRenderer:
    def __init__(self, _asset_dir: Path) -> None:
        frame = SpriteInfo(
            pattern_width=1,
            pattern_height=1,
            pattern_depth=1,
            layers=1,
            sprite_ids=(10, 11),
            animation_phases=2,
            default_start_phase=0,
            phase_durations=((100, 100), (100, 100)),
            synchronized=False,
            random_start_phase=False,
            loop_type=0,
            loop_count=0,
        )
        appearance = Appearance(
            appearance_id=100,
            name="resumable animated fixture",
            is_ground=True,
            clip=False,
            bottom=False,
            top=False,
            stackable=False,
            splash=False,
            fluid_container=False,
            hangable=False,
            hook_direction=None,
            shift=(0, 0),
            height=0,
            frames=(frame,),
        )
        self.appearances = {100: appearance}
        self.sheets = [SpriteSheet(Path("fixture"), 10, 11, 3)]

    def sprite(self, sprite_id: int):
        value = 80 if sprite_id == 10 else 160
        return 64, 64, bytes((value, value, value, 255)) * 64 * 64

    def item_sprites(self, *_args, **_kwargs):
        return []


class EnvironmentAnimationResumeTests(unittest.TestCase):
    def make_fixture(self) -> tuple[Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        output = root / "atlas"
        spool = output / ".spool" / "z7"
        spool.mkdir(parents=True)
        (output / ".spool" / "spool.json").write_text('{"version":1}\n', encoding="utf-8")
        chunk = {
            "z": 7,
            "chunkX": 1,
            "chunkY": 1,
            "logicalBounds": [128, 255, 128, 255, 7],
        }
        manifest = {
            "schemaVersion": 3,
            "chunkSize": 128,
            "sources": {"mapSha256": "map", "assetsSha256": "assets", "atlasVersion": 3},
            "chunks": [chunk],
        }
        (output / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        tile = Tile(Position(150, 150, 7), None, 0, Item(100), ())
        (spool / "1_1.bin").write_bytes(encode_tile(tile))
        assets = root / "assets"
        assets.mkdir()
        return output, assets

    @staticmethod
    def snapshot(root: Path) -> dict[str, bytes]:
        environment = root / "data/environment-animations"
        return {
            path.relative_to(environment).as_posix(): path.read_bytes()
            for path in environment.rglob("*")
            if path.is_file()
        }

    @staticmethod
    def reusable_payload_snapshot(root: Path) -> dict[str, bytes]:
        return {
            relative: payload
            for relative, payload in EnvironmentAnimationResumeTests.snapshot(root).items()
            if relative not in {"index.json", "export-state.json"}
        }

    def test_clean_build_and_identical_restart_reuse_checkpoint(self) -> None:
        output, assets = self.make_fixture()
        with patch("tools.otbm_atlas.environment_animation_resume.AssetRenderer", _FakeRenderer):
            first = enrich_environment_animations_resumable(assets, output)
            before = self.reusable_payload_snapshot(output)
            second = enrich_environment_animations_resumable(assets, output)
            after = self.reusable_payload_snapshot(output)
        self.assertEqual(first["instances"], 1)
        self.assertEqual(first["reusedChunks"], 0)
        self.assertEqual(second["instances"], 1)
        self.assertEqual(second["reusedChunks"], 1)
        self.assertEqual(before, after)
        index = json.loads((output / "data/environment-animations/index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["schemaVersion"], 2)
        self.assertEqual(index["statistics"]["completedChunks"], 1)
        self.assertEqual(index["statistics"]["reusedChunks"], 1)
        shard = json.loads((output / "data/environment-animations/chunks/z7/1_1.json").read_text(encoding="utf-8"))
        record = shard["records"][0]
        self.assertIn("/underlays/", record["underlay"])
        self.assertTrue((output / record["underlay"]).is_file())

    def test_interrupted_finalization_reuses_completed_chunk(self) -> None:
        output, assets = self.make_fixture()
        with patch("tools.otbm_atlas.environment_animation_resume.AssetRenderer", _FakeRenderer):
            enrich_environment_animations_resumable(assets, output)
            environment = output / "data/environment-animations"
            shard = environment / "chunks/z7/1_1.json"
            shard_before = shard.read_bytes()
            (environment / "index.json").unlink()
            report = enrich_environment_animations_resumable(assets, output)
        self.assertEqual(report["reusedChunks"], 1)
        self.assertEqual(shard_before, shard.read_bytes())
        self.assertTrue((environment / "index.json").is_file())

    def test_changed_spool_invalidates_only_affected_checkpoint(self) -> None:
        output, assets = self.make_fixture()
        spool_path = output / ".spool/z7/1_1.bin"
        checkpoint = output / "data/environment-animations/checkpoints/z7/1_1.json"
        with patch("tools.otbm_atlas.environment_animation_resume.AssetRenderer", _FakeRenderer):
            enrich_environment_animations_resumable(assets, output)
            old = json.loads(checkpoint.read_text(encoding="utf-8"))["fingerprint"]
            distant_static = Tile(Position(250, 250, 7), None, 0, Item(999), ())
            spool_path.write_bytes(spool_path.read_bytes() + encode_tile(distant_static))
            report = enrich_environment_animations_resumable(assets, output)
            new = json.loads(checkpoint.read_text(encoding="utf-8"))["fingerprint"]
        self.assertEqual(report["reusedChunks"], 0)
        self.assertNotEqual(old, new)
        self.assertEqual(report["instances"], 1)

    def test_changed_chunk_removes_stale_shard_and_orphan_payloads(self) -> None:
        output, assets = self.make_fixture()
        spool_path = output / ".spool/z7/1_1.bin"
        with patch("tools.otbm_atlas.environment_animation_resume.AssetRenderer", _FakeRenderer):
            enrich_environment_animations_resumable(assets, output)
            environment = output / "data/environment-animations"
            shard = environment / "chunks/z7/1_1.json"
            old_payloads = {path for path in environment.rglob("*.png")}
            self.assertTrue(shard.is_file())
            self.assertTrue(old_payloads)
            spool_path.write_bytes(encode_tile(Tile(Position(150, 150, 7), None, 0, Item(999), ())))
            report = enrich_environment_animations_resumable(assets, output)
        self.assertEqual(report["instances"], 0)
        self.assertEqual(report["chunks"], 0)
        self.assertFalse(shard.exists())
        self.assertFalse(any(path.exists() for path in old_payloads))

    def test_clean_rebuild_is_byte_deterministic(self) -> None:
        output, assets = self.make_fixture()
        with patch("tools.otbm_atlas.environment_animation_resume.AssetRenderer", _FakeRenderer):
            enrich_environment_animations_resumable(assets, output)
            first = self.snapshot(output)
            environment = output / "data/environment-animations"
            for path in sorted(environment.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            enrich_environment_animations_resumable(assets, output)
            second = self.snapshot(output)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
