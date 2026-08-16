from __future__ import annotations

import unittest

from tools.otbm_atlas.product_acceptance_probe import _expected_inspector_lines


class ProductAcceptanceProbeTests(unittest.TestCase):
    def test_expected_inspector_lines_preserve_ground_and_stack_order(self) -> None:
        record = {
            "x": 100,
            "y": 200,
            "z": 7,
            "ground": {"serverId": 10},
            "items": [{"serverId": 20}, {"serverId": 30}],
        }
        self.assertEqual(
            _expected_inspector_lines(record),
            ["X 100  Y 200  Z 7", "Ground ID: 10", "Item 1: 20", "Item 2: 30"],
        )

    def test_empty_stack_is_explicit(self) -> None:
        record = {"x": 1, "y": 2, "z": 3, "ground": None, "items": []}
        self.assertEqual(
            _expected_inspector_lines(record),
            ["X 1  Y 2  Z 3", "Ground ID: none", "Items: none"],
        )


if __name__ == "__main__":
    unittest.main()
