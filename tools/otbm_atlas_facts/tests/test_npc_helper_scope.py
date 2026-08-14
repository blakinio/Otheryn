from __future__ import annotations

import unittest

from tools.otbm_atlas_facts.npc_services import _travel_routes


class NpcTravelHelperScopeTests(unittest.TestCase):
    def test_neighbor_function_cannot_prove_travel_helper(self) -> None:
        text = '''
local function unrelated(keyword, cost, destination)
    return destination
end

local function actualTravel(keyword, cost, destination)
    local route = keywordHandler:addKeyword({ keyword }, StdModule.say, {})
    route:addChildKeyword({ "yes" }, StdModule.travel, { destination = destination, cost = cost })
end

unrelated("fake", 1, Position(1, 2, 3))
actualTravel("real", 2, Position(4, 5, 6))
'''
        has_travel, routes, diagnostics = _travel_routes(text)
        self.assertTrue(has_travel)
        self.assertEqual(diagnostics, [])
        self.assertEqual([route["keyword"] for route in routes], ["real"])
        self.assertEqual(routes[0]["destination"], {"x": 4, "y": 5, "z": 6})


if __name__ == "__main__":
    unittest.main()
