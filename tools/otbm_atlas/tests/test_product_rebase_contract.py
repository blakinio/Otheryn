from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]


class ProductRebaseContractTests(unittest.TestCase):
    def test_atlas_keeps_resumable_environment_exporter(self) -> None:
        atlas_source = (ROOT / "tools/otbm_atlas/atlas.py").read_text(encoding="utf-8")
        production_source = (ROOT / "tools/otbm_atlas/production_data.py").read_text(encoding="utf-8")
        self.assertIn("from .production_data import build_incremental_production_data", atlas_source)
        self.assertIn("build_incremental_production_data(", atlas_source)
        self.assertIn(
            "from .environment_animation_resume import enrich_environment_animations_resumable",
            production_source,
        )
        self.assertIn(
            "environment_statistics_override: Mapping[str, object] | None = None",
            production_source,
        )
        self.assertIn(
            "else enrich_environment_animations_resumable(asset_dir, output)",
            production_source,
        )
        self.assertNotIn(
            "from .environment_animation import enrich_environment_animations\n",
            atlas_source + production_source,
        )

    def test_atlas_emits_exact_per_chunk_tile_facts(self) -> None:
        source = (ROOT / "tools/otbm_atlas/atlas.py").read_text(encoding="utf-8")
        self.assertIn("TILE_FACTS_VERSION = 1", source)
        self.assertIn('_TileFactWriterPool(spool_dir / "tile-facts")', source)
        self.assertIn('"ground": None if record.ground is None else _tile_fact_item(record.ground)', source)
        self.assertIn('"items": [_tile_fact_item(item) for item in record.items]', source)
        self.assertIn('"tileFactsVersion": TILE_FACTS_VERSION', source)

    def test_mobile_viewer_keeps_layer_controls_visible(self) -> None:
        source = (ROOT / "tools/otbm_atlas/viewer.py").read_text(encoding="utf-8")
        self.assertNotIn(".controls .layers{display:none}", source)
        self.assertIn(".controls{top:112px;right:12px;max-width:none}", source)

    def test_mobile_acceptance_checks_overflow_and_layers(self) -> None:
        source = (ROOT / "tools/otbm_atlas/product_acceptance_probe.py").read_text(encoding="utf-8")
        self.assertIn("mobile_no_overflow", source)
        self.assertIn("mobile_layer_controls", source)
        self.assertIn('"noHorizontalOverflow": mobile_no_overflow', source)
        self.assertIn('"layerControlsVisible": mobile_layer_controls', source)


if __name__ == "__main__":
    unittest.main()
