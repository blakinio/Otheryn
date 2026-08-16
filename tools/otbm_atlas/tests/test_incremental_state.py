from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools.otbm_atlas.incremental_core import canonical_json, sha256_bytes, sha256_file
from tools.otbm_atlas.incremental_state import (
    prepare_dependency_index,
    prepare_persistent_spool,
)


def _chunks_digest(chunks: dict[str, str]) -> str:
    return sha256_bytes(canonical_json(dict(sorted(chunks.items()))))


class PersistentSpoolTests(unittest.TestCase):
    @staticmethod
    def _write_spool(root: Path, source_sha: str, payload: bytes, *, chunk_size: int = 128) -> None:
        path = root / "z7/1_1.bin"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        (root / "spool.json").write_text(
            json.dumps({
                "schemaVersion": 1,
                "chunkSize": chunk_size,
                "tiles": 1,
                "sourceSha256": source_sha,
            }),
            encoding="utf-8",
        )

    @classmethod
    def _write_persistent_spool(cls, state: Path, source_sha: str, payload: bytes, *, chunk_size: int = 128) -> None:
        spool = state / "spool"
        cls._write_spool(spool, source_sha, payload, chunk_size=chunk_size)
        chunks = {"z7/1_1": sha256_file(spool / "z7/1_1.bin")}
        state.mkdir(parents=True, exist_ok=True)
        (state / "spool-index.json").write_text(
            json.dumps({
                "schemaVersion": 1,
                "sourceSha256": source_sha,
                "chunkSize": chunk_size,
                "chunks": chunks,
                "chunksDigest": _chunks_digest(chunks),
            }),
            encoding="utf-8",
        )

    def test_exact_target_cache_hit_skips_otbm_parse(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base_map = root / "base.otbm"
            target_map = root / "target.otbm"
            base_map.write_bytes(b"same-map")
            target_map.write_bytes(b"same-map")
            state = root / "state"
            source_sha = sha256_file(target_map)
            self._write_persistent_spool(state, source_sha, b"cached-chunk")

            with patch("tools.otbm_atlas.incremental_state.spool_map") as spool:
                base, target, stable, report = prepare_persistent_spool(
                    base_map, target_map, root / "work", state, 128
                )

            spool.assert_not_called()
            self.assertEqual(base, target)
            self.assertEqual(stable, state / "spool")
            self.assertTrue(report["cacheHit"])
            self.assertEqual(report["cacheIntegrity"], "VERIFIED")
            self.assertEqual(report["targetSpoolSource"], "persistent-cache")

    def test_exact_base_cache_parses_target_once_and_reconciles_changed_chunk(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base_map = root / "base.otbm"
            target_map = root / "target.otbm"
            base_map.write_bytes(b"base-map")
            target_map.write_bytes(b"target-map")
            state = root / "state"
            self._write_persistent_spool(state, sha256_file(base_map), b"old-chunk")

            def fake_spool(map_path: Path, output: Path, chunk_size: int):
                self.assertEqual(map_path, target_map)
                self.assertEqual(chunk_size, 128)
                self._write_spool(output, sha256_file(target_map), b"new-chunk")
                return {"schemaVersion": 1, "chunkSize": 128, "tiles": 1, "sourceSha256": sha256_file(target_map)}

            with patch("tools.otbm_atlas.incremental_state.spool_map", side_effect=fake_spool) as spool:
                base, target, stable, report = prepare_persistent_spool(
                    base_map, target_map, root / "work", state, 128
                )

            spool.assert_called_once()
            self.assertNotEqual(base, target)
            self.assertEqual((stable / "z7/1_1.bin").read_bytes(), b"new-chunk")
            self.assertEqual(report["baseSpoolSource"], "persistent-cache")
            self.assertEqual(report["reconciliation"]["changed"], ["z7/1_1"])
            refreshed = json.loads((state / "spool-index.json").read_text(encoding="utf-8"))
            self.assertEqual(refreshed["sourceSha256"], sha256_file(target_map))

    def test_corrupted_cached_chunk_is_rejected_and_rebuilt(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base_map = root / "base.otbm"
            target_map = root / "target.otbm"
            base_map.write_bytes(b"same-map")
            target_map.write_bytes(b"same-map")
            state = root / "state"
            source_sha = sha256_file(target_map)
            self._write_persistent_spool(state, source_sha, b"good-cached-chunk")
            (state / "spool/z7/1_1.bin").write_bytes(b"corrupted")

            def fake_spool(_map_path: Path, output: Path, chunk_size: int):
                self._write_spool(output, source_sha, b"rebuilt-good-chunk", chunk_size=chunk_size)
                return {"schemaVersion": 1, "chunkSize": chunk_size, "tiles": 1, "sourceSha256": source_sha}

            with patch("tools.otbm_atlas.incremental_state.spool_map", side_effect=fake_spool) as spool:
                _base, _target, stable, report = prepare_persistent_spool(
                    base_map, target_map, root / "work", state, 128
                )

            spool.assert_called_once()
            self.assertFalse(report["cacheHit"])
            self.assertEqual(report["cacheIntegrity"], "REBUILT")
            self.assertEqual((stable / "z7/1_1.bin").read_bytes(), b"rebuilt-good-chunk")


class DependencyIndexCacheTests(unittest.TestCase):
    @staticmethod
    def _prepare_inputs(root: Path) -> tuple[Path, Path, Path, str]:
        spool = root / "spool"
        spool.mkdir()
        (spool / "spool.json").write_text(
            json.dumps({
                "schemaVersion": 1,
                "chunkSize": 128,
                "tiles": 0,
                "sourceSha256": "map-sha",
            }),
            encoding="utf-8",
        )
        chunks: dict[str, str] = {}
        state = root / "state"
        state.mkdir()
        chunks_digest = _chunks_digest(chunks)
        (state / "spool-index.json").write_text(
            json.dumps({
                "schemaVersion": 1,
                "sourceSha256": "map-sha",
                "chunkSize": 128,
                "chunks": chunks,
                "chunksDigest": chunks_digest,
            }),
            encoding="utf-8",
        )
        assets = root / "assets"
        assets.mkdir()
        (assets / "appearances-test.dat").write_bytes(b"appearance-catalog")
        return spool, assets, state, chunks_digest

    def test_exact_dependency_identity_reuses_cached_index(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            spool, assets, state, chunks_digest = self._prepare_inputs(root)
            identity = {
                "cacheVersion": 2,
                "spoolSourceSha256": "map-sha",
                "spoolChunksDigest": chunks_digest,
                "chunkSize": 128,
                "appearanceCatalogSha256": sha256_file(assets / "appearances-test.dat"),
            }
            cached = {
                "schemaVersion": 1,
                "chunkSize": 128,
                "chunks": {},
                "appearanceToChunks": {},
                "spriteToChunks": {},
                "cacheIdentity": identity,
            }
            (state / "dependency-index.json").write_text(json.dumps(cached), encoding="utf-8")

            with patch("tools.otbm_atlas.incremental_state.build_dependency_index") as build:
                index, report = prepare_dependency_index(spool, assets, state)

            build.assert_not_called()
            self.assertEqual(index, cached)
            self.assertTrue(report["dependencyIndexCacheHit"])

    def test_dependency_identity_mismatch_rebuilds_index(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            spool, assets, state, chunks_digest = self._prepare_inputs(root)
            stale = {
                "schemaVersion": 1,
                "chunkSize": 128,
                "chunks": {},
                "appearanceToChunks": {},
                "spriteToChunks": {},
                "cacheIdentity": {
                    "cacheVersion": 2,
                    "spoolSourceSha256": "map-sha",
                    "spoolChunksDigest": chunks_digest,
                    "chunkSize": 128,
                    "appearanceCatalogSha256": "stale",
                },
            }
            (state / "dependency-index.json").write_text(json.dumps(stale), encoding="utf-8")
            fresh = {
                "schemaVersion": 1,
                "chunkSize": 128,
                "chunks": {},
                "appearanceToChunks": {},
                "spriteToChunks": {},
            }

            with patch("tools.otbm_atlas.incremental_state.build_dependency_index", return_value=fresh) as build:
                index, report = prepare_dependency_index(spool, assets, state)

            build.assert_called_once_with(spool, assets)
            self.assertFalse(report["dependencyIndexCacheHit"])
            self.assertEqual(index["cacheIdentity"]["appearanceCatalogSha256"], sha256_file(assets / "appearances-test.dat"))
            self.assertEqual(index["cacheIdentity"]["spoolChunksDigest"], chunks_digest)
            saved = json.loads((state / "dependency-index.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, index)


if __name__ == "__main__":
    unittest.main()
