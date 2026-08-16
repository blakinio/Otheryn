from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]


class ProductRebaseContractTests(unittest.TestCase):
    def test_atlas_keeps_resumable_environment_exporter(self) -> None:
        source = (ROOT / "tools/otbm_atlas/atlas.py").read_text(encoding="utf-8")
        self.assertIn(
            "from .environment_animation_resume import enrich_environment_animations_resumable as enrich_environment_animations",
            source,
        )
        self.assertNotIn(
            "from .environment_animation import enrich_environment_animations\n",
            source,
        )

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
