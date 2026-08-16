from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.otbm_atlas.assets import encode_png
from tools.otbm_atlas.incremental import (
    _paths_require_render_scan,
    _render_core_transition_reasons,
    classify_changed_paths,
    compose_publication,
    plan_from_states,
    render_overview_chunks,
    require_full_build_authorization,
)
from tools.otbm_atlas.incremental_core import (
    build_content_addressed_manifest,
    decode_tiles,
    diff_publication_manifests,
    encode_tile,
    reconcile_spool,
    sha256_file,
)
from tools.otbm_atlas.semantic import Item, Position, Tile


class IncrementalPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dependencies = {
            "chunks": {
                "z7/1_1": {"chunkSize": 128, "spoolSha256": "a", "appearanceIds": [100], "spriteIds": [200]},
                "z7/2_1": {"chunkSize": 128, "spoolSha256": "b", "appearanceIds": [101], "spriteIds": [300]},
            },
            "appearanceToChunks": {"100": ["z7/1_1"], "101": ["z7/2_1"]},
            "spriteToChunks": {"200": ["z7/1_1"], "300": ["z7/2_1"]},
        }
        self.base_assets = {
            "appearanceDigests": {"100": "aa", "101": "bb"},
            "sheets": [
                {"path": "sheet-a.lzma", "firstId": 1, "lastId": 250, "layout": 0, "sha256": "s1"},
                {"path": "sheet-b.lzma", "firstId": 251, "lastId": 400, "layout": 0, "sha256": "s2"},
                {"path": "sheet-unused.lzma", "firstId": 401, "lastId": 500, "layout": 0, "sha256": "s3"},
            ],
            "gutterProfile": {"maxSpriteWidth": 32, "maxSpriteHeight": 32, "minShiftX": 0, "maxShiftX": 0, "minShiftY": 0, "maxShiftY": 0},
        }

    def _plan(self, *, base_spool=None, target_spool=None, assets=None, render="render", overview="overview", reasons=()):
        return plan_from_states(
            base_spool or {"z7/1_1": "a", "z7/2_1": "b"},
            target_spool or {"z7/1_1": "a", "z7/2_1": "b"},
            self.dependencies,
            self.base_assets,
            assets or self.base_assets,
            "render",
            render,
            "overview",
            overview,
            additional_full_reasons=reasons,
        )

    def test_identical_inputs_produce_zero_dirty_chunks(self) -> None:
        plan = self._plan()
        self.assertFalse(plan["fullBuildRequired"])
        self.assertEqual(plan["detail"]["dirtyChunks"], [])
        self.assertEqual(plan["overview"]["dirtyChunks"], [])

    def test_appearance_change_invalidates_only_reverse_dependencies(self) -> None:
        target = json.loads(json.dumps(self.base_assets))
        target["appearanceDigests"]["100"] = "changed"
        plan = self._plan(assets=target)
        self.assertFalse(plan["fullBuildRequired"])
        self.assertEqual(plan["detail"]["dirtyChunks"], ["z7/1_1"])

    def test_sprite_sheet_change_invalidates_only_chunks_using_its_range(self) -> None:
        target = json.loads(json.dumps(self.base_assets))
        target["sheets"][1]["sha256"] = "changed"
        plan = self._plan(assets=target)
        self.assertEqual(plan["detail"]["dirtyChunks"], ["z7/2_1"])

    def test_unused_sprite_sheet_change_does_not_render_map(self) -> None:
        target = json.loads(json.dumps(self.base_assets))
        target["sheets"][2]["sha256"] = "changed"
        plan = self._plan(assets=target)
        self.assertEqual(plan["detail"]["dirtyChunks"], [])

    def test_one_map_chunk_change_does_not_rebuild_other_chunk(self) -> None:
        plan = self._plan(target_spool={"z7/1_1": "changed", "z7/2_1": "b"})
        self.assertEqual(plan["detail"]["dirtyChunks"], ["z7/1_1"])
        self.assertEqual(plan["overview"]["dirtyChunks"], ["z7/1_1"])

    def test_overview_contract_change_does_not_force_detail_render(self) -> None:
        plan = self._plan(overview="overview-b")
        self.assertEqual(plan["detail"]["dirtyChunks"], [])
        self.assertEqual(plan["overview"]["dirtyChunks"], ["z7/1_1", "z7/2_1"])

    def test_gutter_change_requires_explicit_full_build(self) -> None:
        target = json.loads(json.dumps(self.base_assets))
        target["gutterProfile"]["maxSpriteWidth"] = 64
        plan = self._plan(assets=target)
        self.assertTrue(plan["fullBuildRequired"])
        self.assertIn("GLOBAL_GUTTER_PROFILE_CHANGED", plan["fullBuildReasons"])
        self.assertEqual(plan["detail"]["dirtyChunks"], ["z7/1_1", "z7/2_1"])
        with self.assertRaises(RuntimeError):
            require_full_build_authorization(plan, allow_full_build=False)
        require_full_build_authorization(plan, allow_full_build=True)

    def test_render_contract_change_is_fail_closed(self) -> None:
        plan = self._plan(render="render-b")
        self.assertEqual(plan["fullBuildReasons"], ["RENDER_CONTRACT_CHANGED"])

    def test_additional_render_core_reason_is_fail_closed(self) -> None:
        plan = self._plan(reasons=["RENDER_CORE_VERSION_CHANGED"])
        self.assertTrue(plan["fullBuildRequired"])
        self.assertEqual(plan["detail"]["dirtyChunks"], ["z7/1_1", "z7/2_1"])
        self.assertIn("RENDER_CORE_VERSION_CHANGED", plan["fullBuildReasons"])

    def test_change_domains_are_sorted_deterministically_and_docs_do_not_imply_render(self) -> None:
        classified = classify_changed_paths([
            "tools/otbm_atlas/viewer_app.js",
            "docs/maps/example.md",
            "vendor/map-analysis/crystalserver/data-global/world/foo-monster.xml",
            "vendor/map-analysis/crystalserver/data-global/world/world-house.xml",
            "tools/otbm_atlas/incremental.py",
            "docs/maps/example.md",
        ])
        self.assertEqual(classified["changedPaths"], sorted(set(classified["changedPaths"])))
        self.assertEqual(classified["domains"], ["documentation", "frontend", "houses", "incrementalInfra", "spawns"])

    def test_unrelated_domain_skips_render_scan(self) -> None:
        self.assertFalse(_paths_require_render_scan(["docs/maps/example.md"], []))
        self.assertFalse(_paths_require_render_scan(["vendor/map-analysis/crystalserver/data-global/world/foo-monster.xml"], []))
        self.assertTrue(_paths_require_render_scan(["vendor/map-analysis/crystalserver/data-global/world/world.otbm"], []))
        self.assertTrue(_paths_require_render_scan(["docs/maps/example.md"], ["RENDER_CORE_VERSION_CHANGED"]))
        self.assertTrue(_paths_require_render_scan([], []))


class RenderCoreVersionTests(unittest.TestCase):
    @staticmethod
    def _core_source(version: int, marker: int) -> str:
        functions = [
            "encode_tile",
            "decode_tiles",
            "_dependency_ids_for_tile",
            "build_dependency_index",
            "collect_asset_state",
            "asset_impact",
            "detail_fingerprint",
            "chunk_render_bounds",
            "render_selected_chunks",
        ]
        lines = [f"RENDER_CORE_VERSION = {version}"]
        for name in functions:
            lines.extend(["", f"def {name}():", f"    return {marker if name == 'chunk_render_bounds' else 0}"])
        return "\n".join(lines) + "\n"

    def _write_core(self, root: Path, version: int, marker: int) -> None:
        path = root / "tools/otbm_atlas/incremental_core.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._core_source(version, marker), encoding="utf-8")

    def test_semantic_change_without_version_bump_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base, target = root / "base", root / "target"
            self._write_core(base, 1, 0)
            self._write_core(target, 1, 1)
            self.assertEqual(_render_core_transition_reasons(base, target), ["RENDER_CORE_SEMANTICS_CHANGED_WITHOUT_VERSION_BUMP"])

    def test_semantic_change_with_version_bump_requires_explicit_full_build(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base, target = root / "base", root / "target"
            self._write_core(base, 1, 0)
            self._write_core(target, 2, 1)
            self.assertEqual(_render_core_transition_reasons(base, target), ["RENDER_CORE_VERSION_CHANGED"])

    def test_bootstrap_from_legacy_without_incremental_core_is_not_false_full(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base, target = root / "base", root / "target"
            base.mkdir()
            self._write_core(target, 1, 0)
            self.assertEqual(_render_core_transition_reasons(base, target), [])


class IncrementalSpoolTests(unittest.TestCase):
    def test_tile_spool_round_trip_preserves_render_semantics_and_children(self) -> None:
        tile = Tile(
            Position(32000, 32001, 7),
            42,
            5,
            Item(100, 3),
            (Item(200, 8, children=(Item(201, 2),)),),
            (1, 3),
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "chunk.bin"
            path.write_bytes(encode_tile(tile))
            self.assertEqual(list(decode_tiles(path)), [tile])

    def test_reconcile_rewrites_only_changed_chunks_and_removes_deleted(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            stable = root / "stable"
            candidate = root / "candidate"
            for base in (stable, candidate):
                (base / "z7").mkdir(parents=True)
            (stable / "z7/1_1.bin").write_bytes(b"same")
            (stable / "z7/2_1.bin").write_bytes(b"old")
            (stable / "z7/3_1.bin").write_bytes(b"deleted")
            (candidate / "z7/1_1.bin").write_bytes(b"same")
            (candidate / "z7/2_1.bin").write_bytes(b"new")
            (candidate / "z7/4_1.bin").write_bytes(b"added")
            metadata = {"schemaVersion": 1, "chunkSize": 128, "tiles": 4, "sourceSha256": "target"}
            (stable / "spool.json").write_text(json.dumps({**metadata, "sourceSha256": "base"}), encoding="utf-8")
            (candidate / "spool.json").write_text(json.dumps(metadata), encoding="utf-8")
            same_before = sha256_file(stable / "z7/1_1.bin")
            result = reconcile_spool(candidate, stable)
            self.assertEqual(result["reused"], ["z7/1_1"])
            self.assertEqual(result["changed"], ["z7/2_1", "z7/4_1"])
            self.assertEqual(result["deleted"], ["z7/3_1"])
            self.assertEqual(sha256_file(stable / "z7/1_1.bin"), same_before)
            self.assertEqual((stable / "z7/2_1.bin").read_bytes(), b"new")
            self.assertFalse((stable / "z7/3_1.bin").exists())


class OverviewExecutionTests(unittest.TestCase):
    def test_overview_only_rebuild_uses_existing_detail_without_detail_render(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            detail = root / "detail"
            output = root / "output"
            path = detail / "tiles/z7/1_1.png"
            path.parent.mkdir(parents=True)
            path.write_bytes(encode_png(32, 32, bytes(32 * 32 * 4)))
            result = render_overview_chunks(detail, output, ["z7/1_1"])
            self.assertEqual(result["chunks"][0]["chunk"], "z7/1_1")
            self.assertTrue((output / "overview/z7/1_1.png").is_file())
            self.assertTrue((output / "overview-low/z7/1_1.png").is_file())
            self.assertFalse((output / "tiles/z7/1_1.png").exists())


class PublicationTests(unittest.TestCase):
    def test_content_addressed_patch_reuses_unchanged_object_and_matches_clean_manifest(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "render"
            objects = root / "objects"
            source.mkdir()
            (source / "a.txt").write_text("same", encoding="utf-8")
            (source / "b.txt").write_text("before", encoding="utf-8")
            base = build_content_addressed_manifest(source, ["a.txt", "b.txt"], objects)
            (source / "b.txt").write_text("after", encoding="utf-8")
            changed = build_content_addressed_manifest(source, ["b.txt"], objects)
            incremental_target = compose_publication(base, changed, [])
            clean_target = build_content_addressed_manifest(source, ["a.txt", "b.txt"], objects)
            patch = diff_publication_manifests(base, incremental_target)
            self.assertEqual(patch["changed"], ["b.txt"])
            self.assertEqual(patch["unchanged"], ["a.txt"])
            self.assertEqual(base["entries"]["a.txt"], incremental_target["entries"]["a.txt"])
            self.assertEqual(incremental_target, clean_target)


if __name__ == "__main__":
    unittest.main()
