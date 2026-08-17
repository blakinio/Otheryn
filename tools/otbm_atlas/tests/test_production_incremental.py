from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.otbm_atlas.incremental_core import sha256_file, spool_hashes
from tools.otbm_atlas.production_incremental import (
    PRODUCTION_STATE_VERSION,
    commit_production_render_state,
    overview_output_reusable,
    prepare_production_render_plan,
)


class ProductionIncrementalTests(unittest.TestCase):
    def _fixture(self):
        temporary = tempfile.TemporaryDirectory(); root = Path(temporary.name)
        map_path = root / "world.otbm"; map_path.write_bytes(b"map-v1")
        asset_dir = root / "assets"; asset_dir.mkdir()
        output = root / "atlas"; spool = output / ".spool"; (spool / "z7").mkdir(parents=True)
        (spool / "z7/0_0.bin").write_bytes(b"chunk-a"); (spool / "z7/1_0.bin").write_bytes(b"chunk-b")
        (spool / "tile-facts/z7").mkdir(parents=True)
        (spool / "tile-facts/z7/0_0.jsonl").write_text('{"x":1}\n', encoding="utf-8")
        (spool / "tile-facts/z7/1_0.jsonl").write_text('{"x":2}\n', encoding="utf-8")
        (spool / "facts.json").write_text('{"schemaVersion":1}\n', encoding="utf-8")
        spool_contract = {"version": 1, "tileFactsVersion": 1}
        (spool / "spool.json").write_text(json.dumps({"schemaVersion": 1, "version": 1, "tileFactsVersion": 1, "chunkSize": 128, "tiles": 2, "sourceSha256": sha256_file(map_path)}) + "\n", encoding="utf-8")
        sources = {"mapSha256": sha256_file(map_path), "assetsSha256": "assets-v1", "chunkSize": 128, "atlasVersion": 3, "tileFactsVersion": 1}
        hashes = spool_hashes(spool)
        for x in (0, 1):
            text = f"z7/{x}_0"; spool_sha = hashes[text]
            legacy_fp = hashlib.sha256((sources["mapSha256"] + sources["assetsSha256"] + str(sources["atlasVersion"]) + spool_sha).encode()).hexdigest()
            for directory, prefix in (("tiles", b"detail"), ("overview", b"overview"), ("overview-low", b"low")):
                image = output / directory / f"z7/{x}_0.png"; image.parent.mkdir(parents=True, exist_ok=True); image.write_bytes(prefix + bytes([x]))
                report = {"checksum": sha256_file(image), "fingerprint": legacy_fp if directory == "tiles" else f"derived-{directory}-{x}", "imageWidth": 32, "imageHeight": 32, "tiles": 1, "groundItems": 1, "childItems": 0, "renderOperations": 1, "missingAppearances": {}}
                image.with_suffix(".json").write_text(json.dumps(report) + "\n", encoding="utf-8")
        return temporary, root, map_path, asset_dir, sources, spool_contract

    @staticmethod
    def _dependency_index(a="fp-a", b="fp-b"):
        return {"chunks": {"z7/0_0": {"chunkSize": 128, "spoolSha256": "a", "appearanceIds": [], "spriteIds": [], "testFingerprint": a}, "z7/1_0": {"chunkSize": 128, "spoolSha256": "b", "appearanceIds": [], "spriteIds": [], "testFingerprint": b}}, "spriteToChunks": {}}

    def _patches(self, dependency_index, gutter="g1"):
        return (
            patch("tools.otbm_atlas.production_incremental.collect_asset_state", return_value={"stateDigest": "asset-state", "gutterProfile": gutter, "appearanceDigests": {}, "sheets": []}),
            patch("tools.otbm_atlas.production_incremental.render_contract_digest", return_value="render-v1"),
            patch("tools.otbm_atlas.production_incremental.prepare_dependency_index", return_value=(dependency_index, {"dependencyIndexCacheHit": True})),
            patch("tools.otbm_atlas.production_incremental.prepare_production_sprite_digests", return_value={}),
            patch("tools.otbm_atlas.production_incremental._production_detail_fingerprint", side_effect=lambda record, _assets, _digest: str(record["testFingerprint"])),
        )

    @staticmethod
    def _identity(image: Path):
        report_path = image.with_suffix(".json"); report = json.loads(report_path.read_text(encoding="utf-8")); si = image.stat(); sr = report_path.stat()
        return {"size": si.st_size, "mtimeNs": si.st_mtime_ns, "checksum": report["checksum"], "reportSize": sr.st_size, "reportMtimeNs": sr.st_mtime_ns, "reportSha256": sha256_file(report_path)}

    @classmethod
    def _write_state(cls, output: Path, fingerprints, gutter="g1"):
        state_dir = output / ".incremental-state"; state_dir.mkdir(parents=True, exist_ok=True)
        detail = {}; overview = {}
        for text in fingerprints:
            z, stem = text.split("/"); detail[text] = cls._identity(output / "tiles" / z / f"{stem}.png")
            for directory in ("overview", "overview-low"): overview[f"{directory}/{text}"] = cls._identity(output / directory / z / f"{stem}.png")
        state = {"stateVersion": PRODUCTION_STATE_VERSION, "chunkSize": 128, "renderCoreVersion": 1, "renderContractDigest": "render-v1", "gutterProfile": gutter, "assetSheets": [], "spriteDigests": {}, "spoolChunkHashes": spool_hashes(output / ".spool"), "chunkFingerprints": fingerprints, "detailFiles": detail, "overviewFiles": overview}
        (state_dir / "production-render-state.json").write_text(json.dumps(state), encoding="utf-8")

    def _plan(self, map_path, asset_dir, output, root, sources, spool_contract, dependency=None, **kwargs):
        patches = self._patches(dependency or self._dependency_index(), kwargs.pop("gutter", "g1"))
        with patches[0], patches[1], patches[2], patches[3], patches[4]:
            return prepare_production_render_plan(map_path, asset_dir, output, root, 128, sources, spool_contract, kwargs.pop("spool_builder", lambda *_: self.fail("spool parser should not run")), **kwargs)

    def test_identical_committed_state_renders_zero_chunks(self):
        temporary, root, map_path, asset_dir, sources, contract = self._fixture(); self.addCleanup(temporary.cleanup); output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"})
        plan = self._plan(map_path, asset_dir, output, root, sources, contract)
        self.assertEqual(plan["dirtyDetailChunks"], []); self.assertEqual(plan["reusedDetailChunks"], ["z7/0_0", "z7/1_0"]); self.assertEqual(plan["spool"]["integrity"], "verified")

    def test_matching_legacy_publication_is_report_bound_and_adopted_without_render(self):
        temporary, root, map_path, asset_dir, sources, contract = self._fixture(); self.addCleanup(temporary.cleanup); output = root / "atlas"
        (output / "manifest.json").write_text(json.dumps({"schemaVersion": 3, "chunkSize": 128, "sources": sources, "chunks": [{"z": 7, "chunkX": 0, "chunkY": 0}, {"z": 7, "chunkX": 1, "chunkY": 0}]}), encoding="utf-8")
        plan = self._plan(map_path, asset_dir, output, root, sources, contract)
        self.assertTrue(plan["legacyPublicationAdopted"]); self.assertEqual(plan["dirtyDetailChunks"], []); self.assertEqual(plan["spool"]["integrity"], "legacy-report-bound-on-commit")
        commit_production_render_state(output, plan); state = json.loads((output / ".incremental-state/production-render-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["stateVersion"], PRODUCTION_STATE_VERSION); self.assertEqual(set(state["detailFiles"]), {"z7/0_0", "z7/1_0"}); self.assertEqual(len(state["overviewFiles"]), 4)

    def test_one_changed_local_fingerprint_renders_only_that_chunk(self):
        temporary, root, map_path, asset_dir, sources, contract = self._fixture(); self.addCleanup(temporary.cleanup); output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-old"}); plan = self._plan(map_path, asset_dir, output, root, sources, contract)
        self.assertEqual(plan["dirtyDetailChunks"], ["z7/1_0"]); self.assertEqual(plan["reusedDetailChunks"], ["z7/0_0"])

    def test_modified_detail_or_report_marks_only_that_chunk_dirty(self):
        for target in ("png", "json"):
            with self.subTest(target=target):
                temporary, root, map_path, asset_dir, sources, contract = self._fixture(); self.addCleanup(temporary.cleanup); output = root / "atlas"
                self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"})
                path = output / f"tiles/z7/1_0.{target}"; path.write_bytes(b"tampered")
                plan = self._plan(map_path, asset_dir, output, root, sources, contract)
                self.assertEqual(plan["dirtyDetailChunks"], ["z7/1_0"]); self.assertEqual(plan["reusedDetailChunks"], ["z7/0_0"])

    def test_overview_integrity_is_local(self):
        temporary, root, *_rest = self._fixture(); self.addCleanup(temporary.cleanup); output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"}); state = json.loads((output / ".incremental-state/production-render-state.json").read_text(encoding="utf-8"))
        report = json.loads((output / "overview/z7/1_0.json").read_text(encoding="utf-8")); fingerprint = report["fingerprint"]
        self.assertTrue(overview_output_reusable(output, "overview", "z7/1_0", fingerprint, state["overviewFiles"]))
        (output / "overview/z7/1_0.png").write_bytes(b"tampered-overview")
        self.assertFalse(overview_output_reusable(output, "overview", "z7/1_0", fingerprint, state["overviewFiles"]))
        self.assertTrue(overview_output_reusable(output, "overview", "z7/0_0", json.loads((output / "overview/z7/0_0.json").read_text())["fingerprint"], state["overviewFiles"]))

    def test_missing_output_or_asset_state_is_fail_closed(self):
        for missing in ("detailFiles", "overviewFiles", "assetSheets", "spriteDigests"):
            with self.subTest(missing=missing):
                temporary, root, map_path, asset_dir, sources, contract = self._fixture(); self.addCleanup(temporary.cleanup); output = root / "atlas"
                self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"}); state_path = output / ".incremental-state/production-render-state.json"; state = json.loads(state_path.read_text()); state.pop(missing); state_path.write_text(json.dumps(state))
                with self.assertRaisesRegex(RuntimeError, "PRODUCTION_(OUTPUT|ASSET)_STATE_INVALID"):
                    self._plan(map_path, asset_dir, output, root, sources, contract)

    def test_global_gutter_transition_is_fail_closed(self):
        temporary, root, map_path, asset_dir, sources, contract = self._fixture(); self.addCleanup(temporary.cleanup); output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"}, gutter="old")
        with self.assertRaisesRegex(RuntimeError, "GLOBAL_GUTTER_PROFILE_CHANGED"): self._plan(map_path, asset_dir, output, root, sources, contract, gutter="new")
        plan = self._plan(map_path, asset_dir, output, root, sources, contract, gutter="new", allow_full_build=True)
        self.assertEqual(plan["dirtyDetailChunks"], ["z7/0_0", "z7/1_0"])

    def test_corrupted_spool_is_repaired_from_canonical_source_without_detail_rerender(self):
        temporary, root, map_path, asset_dir, sources, contract = self._fixture(); self.addCleanup(temporary.cleanup); output = root / "atlas"
        self._write_state(output, {"z7/0_0": "fp-a", "z7/1_0": "fp-b"}); corrupted = output / ".spool/z7/1_0.bin"; corrupted.write_bytes(b"corrupt")
        def rebuild(_map, candidate, _size):
            (candidate / "z7").mkdir(parents=True); (candidate / "z7/0_0.bin").write_bytes(b"chunk-a"); (candidate / "z7/1_0.bin").write_bytes(b"chunk-b")
            (candidate / "tile-facts/z7").mkdir(parents=True); (candidate / "tile-facts/z7/0_0.jsonl").write_text('{"x":1}\n'); (candidate / "tile-facts/z7/1_0.jsonl").write_text('{"x":2}\n')
            (candidate / "facts.json").write_text('{"schemaVersion":1}\n'); (candidate / "spool.json").write_text(json.dumps({"schemaVersion":1,"version":1,"tileFactsVersion":1,"chunkSize":128,"tiles":2,"sourceSha256":sha256_file(map_path)})); return {"tiles":2}
        plan = self._plan(map_path, asset_dir, output, root, sources, contract, spool_builder=rebuild)
        self.assertEqual(plan["spool"]["integrity"], "repaired-from-canonical-source"); self.assertEqual(corrupted.read_bytes(), b"chunk-b"); self.assertEqual(plan["dirtyDetailChunks"], [])


if __name__ == "__main__": unittest.main()
