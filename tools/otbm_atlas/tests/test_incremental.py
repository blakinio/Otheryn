from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.otbm_atlas.incremental import (
    classify_changed_paths,
    compose_publication,
    plan_from_states,
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
            ],
            "gutterProfile": {"maxSpriteWidth": 32, "maxSpriteHeight": 32, "minShiftX": 0, "maxShiftX": 0, "minShiftY": 0, "maxShiftY": 0},
        }

    def test_appearance_change_invalidates_only_reverse_dependencies(self) -> None:
        target = json.loads(json.dumps(self.base_assets))
        target["appearanceDigests"]["100"] = "changed"
        plan = plan_from_states(
            {"z7/1_1": "a", "z7/2_1": "b"},
            {"z7/1_1": "a", "z7/2_1": "b"},
            self.dependencies,
            self.base_assets,
            target,
            "render",
            "render",
            "overview",
            "overview",
        )
        self.assertFalse(plan["fullBuildRequired"])
        self.assertEqual(plan["detail"]["dirtyChunks"], ["z7/1_1"])

    def test_sprite_sheet_change_invalidates_only_chunks_using_its_range(self) -> None:
        target = json.loads(json.dumps(self.base_assets))
        target["sheets"][1]["sha256"] = "changed"
        plan = plan_from_states(
            {"z7/1_1": "a", "z7/2_1": "b"},
            {"z7/1_1": "a", "z7/2_1": "b"},
            self.dependencies,
            self.base_assets,
            target,
            "render",
            "render",
            "overview",
            "overview",
        )
        self.assertEqual(plan["detail"]["dirtyChunks"], ["z7/2_1"])

    def test_one_map_chunk_change_does_not_rebuild_other_chunk(self) -> None:
        plan = plan_from_states(
            {"z7/1_1": "a", "z7/2_1": "b"},
            {"z7/1_1": "changed", "z7/2_1": "b"},
            self.dependencies,
            self.base_assets,
            self.base_assets,
            "render",
            "render",
            "overview",
            "overview",
        )
        self.assertEqual(plan["detail"]["dirtyChunks"], ["z7/1_1"])
        self.assertEqual(plan["overview"]["dirtyChunks"], ["z7/1_1"])

    def test_overview_contract_change_does_not_force_detail_render(self) -> None:
        plan = plan_from_states(
            {"z7/1_1": "a", "z7/2_1": "b"},
            {"z7/1_1": "a", "z7/2_1": "b"},
            self.dependencies,
            self.base_assets,
            self.base_assets,
            "render",
            "render",
            "overview-a",
            "overview-b",
        )
        self.assertEqual(plan["detail"]["dirtyChunks"], [])
        self.assertEqual(plan["overview"]["dirtyChunks"], ["z7/1_1", "z7/2_1"])

    def test_gutter_change_requires_explicit_full_build(self) -> None:
        target = json.loads(json.dumps(self.base_assets))
        target["gutterProfile"]["maxSpriteWidth"] = 64
        plan = plan_from_states(
            {"z7/1_1": "a", "z7/2_1": "b"},
            {"z7/1_1": "a", "z7/2_1": "b"},
            self.dependencies,
            self.base_assets,
            target,
            "render",
            "render",
            "overview",
            "overview",
        )
        self.assertTrue(plan["fullBuildRequired"])
        self.assertIn("GLOBAL_GUTTER_PROFILE_CHANGED", plan["fullBuildReasons"])
        self.assertEqual(plan["detail"]["dirtyChunks"], ["z7/1_1", "z7/2_1"])
        with self.assertRaises(RuntimeError):
            require_full_build_authorization(plan, allow_full_build=False)
        require_full_build_authorization(plan, allow_full_build=True)

    def test_render_contract_change_is_fail_closed(self) -> None:
        plan = plan_from_states(
            {"z7/1_1": "a", "z7/2_1": "b"},
            {"z7/1_1": "a", "z7/2_1": "b"},
            self.dependencies,
            self.base_assets,
            self.base_assets,
            "render-a",
            "render-b",
            "overview",
            "overview",
        )
        self.assertEqual(plan["fullBuildReasons"], ["RENDER_CONTRACT_CHANGED"])

    def test_change_domains_do_not_equate_documentation_with_render(self) -> None:
        classified = classify_changed_paths([
            "docs/maps/example.md",
            "tools/otbm_atlas/viewer_app.js",
            "vendor/map-analysis/crystalserver/data-global/world/foo-monster.xml",
        ])
        self.assertEqual(classified["domains"], ["documentation", "frontend", "spawns"])


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


class PublicationTests(unittest.TestCase):
    def test_content_addressed_patch_reuses_unchanged_object(self) -> None:
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
            target = compose_publication(base, changed, [])
            patch = diff_publication_manifests(base, target)
            self.assertEqual(patch["changed"], ["b.txt"])
            self.assertEqual(patch["unchanged"], ["a.txt"])
            self.assertEqual(base["entries"]["a.txt"], target["entries"]["a.txt"])


if __name__ == "__main__":
    unittest.main()
