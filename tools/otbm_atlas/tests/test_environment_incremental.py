from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.assets import Appearance, SpriteInfo
from tools.otbm_atlas.environment_incremental import EnvironmentAssetFingerprinter, environment_contract_fingerprint
from tools.otbm_atlas.incremental_core import encode_tile
from tools.otbm_atlas.semantic import Item, Position, Tile


def _appearance(appearance_id: int, sprite_id: int) -> Appearance:
    frame = SpriteInfo(pattern_width=1, pattern_height=1, pattern_depth=1, layers=1, sprite_ids=(sprite_id,), animation_phases=1, default_start_phase=0, phase_durations=((100, 100),), synchronized=False, random_start_phase=False, loop_type=0, loop_count=0)
    return Appearance(appearance_id=appearance_id, name=f"appearance-{appearance_id}", is_ground=True, clip=False, bottom=False, top=False, stackable=False, splash=False, fluid_container=False, hangable=False, hook_direction=None, shift=(0, 0), height=0, frames=(frame,))


class _Renderer:
    def __init__(self, sprite_10: int = 10, sprite_20: int = 20) -> None:
        self.appearances = {100: _appearance(100, 10), 200: _appearance(200, 20)}; self._pixels = {10: sprite_10, 20: sprite_20}

    def sprite(self, sprite_id: int):
        value = self._pixels[sprite_id]; return 32, 32, bytes((value, value, value, 255)) * 32 * 32


class EnvironmentIncrementalFingerprintTests(unittest.TestCase):
    def _spool(self, root: Path, name: str, appearance_id: int) -> Path:
        path = root / name; path.write_bytes(encode_tile(Tile(Position(150, 150, 7), None, 0, Item(appearance_id), ()))); return path

    def test_global_contract_ignores_monolithic_source_sha_and_chunk_inventory(self) -> None:
        first = {"schemaVersion": 3, "chunkSize": 128, "sources": {"mapSha256": "old", "assetsSha256": "old"}, "chunks": [{"z": 7, "chunkX": 1, "chunkY": 1}]}
        second = {"schemaVersion": 3, "chunkSize": 128, "sources": {"mapSha256": "new", "assetsSha256": "new"}, "chunks": [{"z": 7, "chunkX": 1, "chunkY": 1}, {"z": 7, "chunkX": 2, "chunkY": 1}]}
        self.assertEqual(
            environment_contract_fingerprint(first, export_version=3, overlap_radius=2, semantics_digest="same-code"),
            environment_contract_fingerprint(second, export_version=3, overlap_radius=2, semantics_digest="same-code"),
        )
        self.assertNotEqual(
            environment_contract_fingerprint(first, export_version=3, overlap_radius=2, semantics_digest="same-code"),
            environment_contract_fingerprint(first, export_version=3, overlap_radius=3, semantics_digest="same-code"),
        )

    def test_semantic_code_digest_is_global_contract_input(self) -> None:
        manifest = {"schemaVersion": 3, "chunkSize": 128}
        self.assertNotEqual(
            environment_contract_fingerprint(manifest, export_version=3, overlap_radius=2, semantics_digest="code-v1"),
            environment_contract_fingerprint(manifest, export_version=3, overlap_radius=2, semantics_digest="code-v2"),
        )

    def test_unrelated_sprite_change_invalidates_only_dependent_chunk(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); chunk_a = self._spool(root, "a.bin", 100); chunk_b = self._spool(root, "b.bin", 200)
            contract = environment_contract_fingerprint({"schemaVersion": 3, "chunkSize": 128}, export_version=3, overlap_radius=2, semantics_digest="same-code")
            before = EnvironmentAssetFingerprinter(_Renderer(sprite_10=10, sprite_20=20)); a1 = before.chunk_fingerprint(contract, chunk_a, [128, 255, 128, 255, 7]); b1 = before.chunk_fingerprint(contract, chunk_b, [256, 383, 128, 255, 7])
            after = EnvironmentAssetFingerprinter(_Renderer(sprite_10=10, sprite_20=99)); a2 = after.chunk_fingerprint(contract, chunk_a, [128, 255, 128, 255, 7]); b2 = after.chunk_fingerprint(contract, chunk_b, [256, 383, 128, 255, 7])
            self.assertEqual(a1, a2); self.assertNotEqual(b1, b2)

    def test_logical_bounds_are_part_of_local_checkpoint_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            chunk = self._spool(Path(temporary), "chunk.bin", 100)
            contract = environment_contract_fingerprint({"schemaVersion": 3, "chunkSize": 128}, export_version=3, overlap_radius=2, semantics_digest="same-code")
            fingerprinter = EnvironmentAssetFingerprinter(_Renderer())
            first = fingerprinter.chunk_fingerprint(contract, chunk, [128, 255, 128, 255, 7]); second = fingerprinter.chunk_fingerprint(contract, chunk, [129, 256, 128, 255, 7])
            self.assertNotEqual(first, second)


if __name__ == "__main__": unittest.main()
