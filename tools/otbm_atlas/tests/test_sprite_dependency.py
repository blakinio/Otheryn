from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from tools.otbm_atlas.sprite_dependency import exact_asset_impact, prepare_production_sprite_digests


class ExactSpriteDependencyTests(unittest.TestCase):
    def test_same_changed_sheet_only_dirties_chunks_using_changed_sprite(self) -> None:
        dependency = {
            "appearanceToChunks": {},
            "spriteToChunks": {"10": ["z7/1_1"], "20": ["z7/2_1"]},
        }
        coarse = {
            "changedAppearanceIds": [],
            "changedSheetPaths": ["sheet.spr"],
            "affectedChunks": ["z7/1_1", "z7/2_1"],
            "globalReasons": [],
        }
        with patch("tools.otbm_atlas.sprite_dependency.exact_changed_sprite_ids", return_value=[20]):
            impact = exact_asset_impact(Path("base"), Path("target"), {"sheets": []}, {"sheets": []}, dependency, coarse)
        self.assertEqual(impact["changedSpriteIds"], [20])
        self.assertEqual(impact["affectedChunks"], ["z7/2_1"])

    def test_production_reuses_digest_when_sheet_identity_is_unchanged(self) -> None:
        sheet = {"path": "a.spr", "sha256": "same", "firstSpriteId": 1, "lastSpriteId": 100, "layout": 3, "spriteSize": [32, 32]}
        state = {"assetSheets": [sheet], "spriteDigests": {"10": "digest-10"}}
        dependency = {"spriteToChunks": {"10": ["z7/1_1"]}}
        with patch("tools.otbm_atlas.sprite_dependency.sprite_digests") as compute:
            result = prepare_production_sprite_digests(Path("assets"), {"sheets": [sheet]}, dependency, state)
        self.assertEqual(result, {"10": "digest-10"})
        compute.assert_called_once_with(Path("assets"), [])

    def test_production_recomputes_only_ids_from_changed_sheet(self) -> None:
        old_a = {"path": "a.spr", "sha256": "old", "firstSpriteId": 1, "lastSpriteId": 100, "layout": 3, "spriteSize": [32, 32]}
        new_a = {**old_a, "sha256": "new"}
        same_b = {"path": "b.spr", "sha256": "same", "firstSpriteId": 101, "lastSpriteId": 200, "layout": 3, "spriteSize": [32, 32]}
        state = {"assetSheets": [old_a, same_b], "spriteDigests": {"10": "old-10", "110": "same-110"}}
        dependency = {"spriteToChunks": {"10": ["z7/1_1"], "110": ["z7/2_1"]}}
        with patch("tools.otbm_atlas.sprite_dependency.sprite_digests", return_value={"10": "new-10"}) as compute:
            result = prepare_production_sprite_digests(Path("assets"), {"sheets": [new_a, same_b]}, dependency, state)
        self.assertEqual(result, {"10": "new-10", "110": "same-110"})
        compute.assert_called_once_with(Path("assets"), [10])


if __name__ == "__main__": unittest.main()
