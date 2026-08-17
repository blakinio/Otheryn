from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.production_phases import ProductionPhaseCache


class ProductionPhaseCacheTests(unittest.TestCase):
    def test_identical_outputs_hit_and_tamper_misses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary); data = output / "data"; data.mkdir()
            one = data / "one.json"; two = data / "two.json"; one.write_text("one", encoding="utf-8"); two.write_text("two", encoding="utf-8")
            cache = ProductionPhaseCache(output); cache.commit("facts", "fp-a", ("data/*.json",), {"count": 2})
            self.assertTrue(ProductionPhaseCache(output).current("facts", "fp-a", ("data/*.json",)))
            self.assertFalse(ProductionPhaseCache(output).current("facts", "fp-b", ("data/*.json",)))
            two.write_text("tampered", encoding="utf-8")
            self.assertFalse(ProductionPhaseCache(output).current("facts", "fp-a", ("data/*.json",)))

    def test_unexpected_extra_output_invalidates_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary); data = output / "data"; data.mkdir(); (data / "one.json").write_text("one")
            ProductionPhaseCache(output).commit("facts", "fp", ("data/*.json",))
            (data / "two.json").write_text("two")
            self.assertFalse(ProductionPhaseCache(output).current("facts", "fp", ("data/*.json",)))

    def test_cached_result_is_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary); (output / "data").mkdir(); (output / "data/a.json").write_text("a")
            cache = ProductionPhaseCache(output); cache.commit("x", "fp", ("data/a.json",), {"value": 7})
            self.assertEqual(ProductionPhaseCache(output).result("x"), {"value": 7})


if __name__ == "__main__": unittest.main()
