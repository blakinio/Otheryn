from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.otbm_atlas.incremental_core import sha256_file, spool_hashes
from tools.otbm_atlas.production_incremental import (
    PRODUCTION_STATE_VERSION,
    commit_production_render_state,
    prepare_production_render_plan,
)


class ProductionIncrementalTests(unittest.TestCase):
    def _fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, Path, dict[str, object], dict[str, object]]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        map_path = root / "world.otbm"
        map_path.write_bytes(b"map-v1")
        asset_dir = root / "assets"
        asset_dir.mkdir()
        output = root / "atlas"
        spool = output / ".spool"
        (spool / "z7").mkdir(parents=True)
        (spool / "z7/0_0.bin").write_bytes(b"chunk-a")
        (spool / "z7/1_0.bin").write_bytes(b"chunk-b")
        (spool / "tile-facts/z7").mkdir(parents=True)
        (spool / "tile-facts/z7/0_0.jsonl").write_text('{"x":1}\n', encoding="utf-8")
        (spool / "tile-facts/z7/1_0.jsonl").write_text('{"x":2}\n', encoding="utf-8")
        (spool / "facts.json").write_text('{"schemaVersion":1}\n', encoding="utf-8")
        spool_contract = {"version": 1, "tileFactsVersion": 1}
        (spool / "spool.json").write_text(
            json.dumps({
                "schemaVersion": 1,
                "version": 1,
                "tileFactsVersion": 1,
                "chunkSize": 128,
                "tiles": 2,
                "sourceSha256": sha256_file(map_path),
            }) + "\n",
            encoding="utf-8",
        )
        expected_sources = {
            "mapSha256": sha256_file(map_path),
            "assetsSha256": "assets-v1",
            "chunkSize": 128,
            "atlasVersion": 3,
            "tileFactsVersion": 1,
        }
        for x in (0, 1):
            tile = output / f"tiles/z7/{x}_0.png"
            tile.parent.mkdir(parents=True, exist_ok=True)
            tile.write_bytes(b"png" + bytes([x]))
            tile.with_suffix(".json").write_text(json.dumps({"checksum": sha256_file(tile)}) + "\n", encoding="utf-8")
        return temporary, root, map_path, asset_dir, expected_sources, spool_contract

    @staticmethod
    def _dependency_index(a: str = "fp-a", b: str = "fp-b") -> dict[str, object]:
        return {
            "chunks": {
                "z7/0_0": {"chunkSize": 128, "spoolSha256": "a", "appearanceIds": [], "spriteIds": [], "testFingerprint": a},
                "z7/1_0": {"chunkSize": 128, "spoolSha256": "b", "appearanceIds": [], "spriteIds": [], "testFingerprint": b},
            }
        }

    def _patches(self, dependency_index: dict[str, object], gutter: str = "g1"):
        return (
            patch("tools.otbm_atlas.production_incremental.collect_asset_state", return_value={"stateDigest": "asset-state", "gutterProfile": gutter}),
            patch("tools.otbm_atlas.production_incremental.render_contract_digest", return_value="render-v1"),
            patch("tools.otbm_atlas.production_incremental.prepare_dependency_index", return_value=(dependency_index, {"dependencyIndexCacheHit": True})),
            patch("tools.otbm_atlas.production_incremental.detail_fingerprint", side_effect=lambda record, _assets, _digest: str(record["testFingerprint"])),
        )

    @staticmethod
    def _detail_identity(output: Path, text: str) -> dict[str, object]:
        z_name, stem = text.split("/", 1)
        tile = output / "tiles" / z_name / f"{stem}.png"
        report_path = tile.with_suffix(".json")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        tile_stat = tile.stat()
        report_stat = report_path.stat()
        return {
            "size": tile_stat.st_size,
            "mtimeNs": tile_stat.st_mtime_ns,
            "checksum": report["checksum"],
            "reportSize": report_stat.st_size,
            "reportMtimeNs": report_stat.st_mtime_ns,
            "reportSha256": sha256_file(report_path),
        }

    @classmethod
    def _write_state(cls, output: Path, fingerprints: dict[str, str], gutter: str = "g1") -> None:
        state_dir = output / ".incremental-state"
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "production-render-state.json").write_text(json.dumps({
            "stateVersion": PRODUCTION_STATE_VERSION,
            "chunkSize": 128,
            "renderCoreVersion": 1,
            "renderContractDigest": "render-v1",
            "gutterProfile": gutter,
            "spoolChunkHashes": spool_hashes(output / ".spool"),
            "chunkFingerprints": fingerprints,
            "detailFiles": {text: cls._detail_identity(output, text) for text in fingerprints},
        }), encoding="utf-8")

    def test_identical_committed_state_renders_zero_chunks(self) -> None:
        temporary, root, map_path, asset_dir, sources, spool_contract = self._fixture()
        self.addCleanup(temporary.cleanup)
        output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"})
        patches = self._patches(self._dependency_index())
        with patches[0], patches[1], patches[2], patches[3]:
            plan = prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, lambda *_: self.fail("spool parser should not run"))
        self.assertEqual(plan["dirtyDetailChunks"], [])
        self.assertEqual(plan["reusedDetailChunks"], ["z7/0_0", "z7/1_0"])
        self.assertFalse(plan["spool"]["parsed"])
        self.assertEqual(plan["spool"]["integrity"], "verified")

    def test_matching_legacy_publication_is_adopted_without_full_render(self) -> None:
        temporary, root, map_path, asset_dir, sources, spool_contract = self._fixture()
        self.addCleanup(temporary.cleanup)
        output = root / "atlas"
        (output / "manifest.json").write_text(json.dumps({
            "schemaVersion": 3,
            "chunkSize": 128,
            "sources": sources,
            "chunks": [
                {"z": 7, "chunkX": 0, "chunkY": 0},
                {"z": 7, "chunkX": 1, "chunkY": 0},
            ],
        }), encoding="utf-8")
        patches = self._patches(self._dependency_index())
        with patches[0], patches[1], patches[2], patches[3]:
            plan = prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, lambda *_: self.fail("spool parser should not run"))
        self.assertTrue(plan["legacyPublicationAdopted"])
        self.assertEqual(plan["dirtyDetailChunks"], [])
        self.assertEqual(plan["spool"]["integrity"], "legacy-adoption-bound-on-commit")
        commit_production_render_state(output, plan)
        state = json.loads((output / ".incremental-state/production-render-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["stateVersion"], PRODUCTION_STATE_VERSION)
        self.assertEqual(state["chunkFingerprints"], {"z7/0_0": "fp-a", "z7/1_0": "fp-b"})
        self.assertEqual(state["spoolChunkHashes"], spool_hashes(output / ".spool"))
        self.assertEqual(set(state["detailFiles"]), {"z7/0_0", "z7/1_0"})
        self.assertIn("reportSha256", state["detailFiles"]["z7/0_0"])

    def test_one_changed_local_fingerprint_renders_only_that_chunk(self) -> None:
        temporary, root, map_path, asset_dir, sources, spool_contract = self._fixture()
        self.addCleanup(temporary.cleanup)
        output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-old"})
        patches = self._patches(self._dependency_index())
        with patches[0], patches[1], patches[2], patches[3]:
            plan = prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, lambda *_: self.fail("spool parser should not run"))
        self.assertEqual(plan["dirtyDetailChunks"], ["z7/1_0"])
        self.assertEqual(plan["reusedDetailChunks"], ["z7/0_0"])

    def test_modified_reused_png_marks_only_that_chunk_dirty(self) -> None:
        temporary, root, map_path, asset_dir, sources, spool_contract = self._fixture()
        self.addCleanup(temporary.cleanup)
        output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"})
        (output / "tiles/z7/1_0.png").write_bytes(b"tampered-detail-output")
        patches = self._patches(self._dependency_index())
        with patches[0], patches[1], patches[2], patches[3]:
            plan = prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, lambda *_: self.fail("spool parser should not run"))
        self.assertEqual(plan["dirtyDetailChunks"], ["z7/1_0"])
        self.assertEqual(plan["reusedDetailChunks"], ["z7/0_0"])

    def test_modified_reused_report_marks_only_that_chunk_dirty(self) -> None:
        temporary, root, map_path, asset_dir, sources, spool_contract = self._fixture()
        self.addCleanup(temporary.cleanup)
        output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"})
        (output / "tiles/z7/1_0.json").write_text('{"checksum":"forged","imageWidth":1}\n', encoding="utf-8")
        patches = self._patches(self._dependency_index())
        with patches[0], patches[1], patches[2], patches[3]:
            plan = prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, lambda *_: self.fail("spool parser should not run"))
        self.assertEqual(plan["dirtyDetailChunks"], ["z7/1_0"])
        self.assertEqual(plan["reusedDetailChunks"], ["z7/0_0"])

    def test_missing_detail_state_is_fail_closed(self) -> None:
        temporary, root, map_path, asset_dir, sources, spool_contract = self._fixture()
        self.addCleanup(temporary.cleanup)
        output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"})
        state_path = output / ".incremental-state/production-render-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state.pop("detailFiles")
        state_path.write_text(json.dumps(state), encoding="utf-8")
        patches = self._patches(self._dependency_index())
        with patches[0], patches[1], patches[2], patches[3]:
            with self.assertRaisesRegex(RuntimeError, "PRODUCTION_DETAIL_STATE_INVALID"):
                prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, lambda *_: self.fail("spool parser should not run"))

    def test_global_gutter_transition_is_fail_closed(self) -> None:
        temporary, root, map_path, asset_dir, sources, spool_contract = self._fixture()
        self.addCleanup(temporary.cleanup)
        output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"}, gutter="old-gutter")
        patches = self._patches(self._dependency_index(), gutter="new-gutter")
        with patches[0], patches[1], patches[2], patches[3]:
            with self.assertRaisesRegex(RuntimeError, "GLOBAL_GUTTER_PROFILE_CHANGED"):
                prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, lambda *_: self.fail("spool parser should not run"))
        patches = self._patches(self._dependency_index(), gutter="new-gutter")
        with patches[0], patches[1], patches[2], patches[3]:
            plan = prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, lambda *_: self.fail("spool parser should not run"), allow_full_build=True)
        self.assertEqual(plan["dirtyDetailChunks"], ["z7/0_0", "z7/1_0"])
        self.assertIn("GLOBAL_GUTTER_PROFILE_CHANGED", plan["fullBuildReasons"])

    def test_corrupted_spool_is_repaired_from_canonical_source_without_detail_rerender(self) -> None:
        temporary, root, map_path, asset_dir, sources, spool_contract = self._fixture()
        self.addCleanup(temporary.cleanup)
        output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"})
        corrupted = output / ".spool/z7/1_0.bin"
        corrupted.write_bytes(b"corrupt")

        def rebuild(_map: Path, candidate: Path, _chunk_size: int):
            (candidate / "z7").mkdir(parents=True)
            (candidate / "z7/0_0.bin").write_bytes(b"chunk-a")
            (candidate / "z7/1_0.bin").write_bytes(b"chunk-b")
            (candidate / "tile-facts/z7").mkdir(parents=True)
            (candidate / "tile-facts/z7/0_0.jsonl").write_text('{"x":1}\n', encoding="utf-8")
            (candidate / "tile-facts/z7/1_0.jsonl").write_text('{"x":2}\n', encoding="utf-8")
            (candidate / "facts.json").write_text('{"schemaVersion":1}\n', encoding="utf-8")
            (candidate / "spool.json").write_text(json.dumps({
                "schemaVersion": 1,
                "version": 1,
                "tileFactsVersion": 1,
                "chunkSize": 128,
                "tiles": 2,
                "sourceSha256": sha256_file(map_path),
            }), encoding="utf-8")
            return {"tiles": 2}

        patches = self._patches(self._dependency_index())
        with patches[0], patches[1], patches[2], patches[3]:
            plan = prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, rebuild)
        self.assertTrue(plan["spool"]["parsed"])
        self.assertEqual(plan["spool"]["integrity"], "repaired-from-canonical-source")
        self.assertEqual(corrupted.read_bytes(), b"chunk-b")
        self.assertEqual(plan["dirtyDetailChunks"], [])

    def test_changed_map_reconciles_only_changed_render_shard(self) -> None:
        temporary, root, map_path, asset_dir, sources, spool_contract = self._fixture()
        self.addCleanup(temporary.cleanup)
        output = root / "atlas"
        map_path.write_bytes(b"map-v2")
        sources = dict(sources)
        sources["mapSha256"] = sha256_file(map_path)

        def build_candidate(_map: Path, candidate: Path, _chunk_size: int):
            (candidate / "z7").mkdir(parents=True)
            (candidate / "z7/0_0.bin").write_bytes(b"chunk-a")
            (candidate / "z7/1_0.bin").write_bytes(b"chunk-b-new")
            (candidate / "tile-facts/z7").mkdir(parents=True)
            (candidate / "tile-facts/z7/0_0.jsonl").write_text('{"x":1}\n', encoding="utf-8")
            (candidate / "tile-facts/z7/1_0.jsonl").write_text('{"x":22}\n', encoding="utf-8")
            (candidate / "facts.json").write_text('{"schemaVersion":1,"changed":true}\n', encoding="utf-8")
            (candidate / "spool.json").write_text(json.dumps({
                "schemaVersion": 1,
                "version": 1,
                "tileFactsVersion": 1,
                "chunkSize": 128,
                "tiles": 2,
                "sourceSha256": sha256_file(map_path),
            }), encoding="utf-8")
            return {"tiles": 2}

        patches = self._patches(self._dependency_index(a="fp-a", b="fp-b-new"))
        with patches[0], patches[1], patches[2], patches[3]:
            plan = prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, build_candidate)
        self.assertEqual(plan["spool"]["renderShards"]["changed"], ["z7/1_0"])
        self.assertIn("z7/0_0", plan["spool"]["renderShards"]["reused"])
        self.assertTrue(plan["spool"]["factsChanged"])


if __name__ == "__main__":
    unittest.main()
