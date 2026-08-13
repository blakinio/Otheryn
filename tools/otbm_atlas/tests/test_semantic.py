from __future__ import annotations

import io
import struct
import unittest

from tools.otbm_atlas.nodefile import NodeFileError
from tools.otbm_atlas.semantic import Diagnostic, Item, MapHeader, Position, Tile, Town, Waypoint, iter_map_records, walk_items


def escaped(data: bytes) -> bytes:
	result = bytearray()
	for value in data:
		if value in (0xFD, 0xFE, 0xFF):
			result.append(0xFD)
		result.append(value)
	return bytes(result)


def node(payload: bytes, *children: bytes) -> bytes:
	return b"\xfe" + escaped(payload) + b"".join(children) + b"\xff"


def string(value: str) -> bytes:
	data = value.encode()
	return struct.pack("<H", len(data)) + data


class SemanticTests(unittest.TestCase):
	def fixture(self) -> bytes:
		item = node(b"\x06" + struct.pack("<H", 200) + b"\x04" + struct.pack("<H", 5555))
		tile = node(b"\x05\x03\x04\x03" + struct.pack("<I", 7) + b"\x09" + struct.pack("<H", 100), item)
		area = node(b"\x04" + struct.pack("<HHB", 32000, 32100, 7), tile)
		town = node(b"\x0d" + struct.pack("<I", 1) + string("Thais") + struct.pack("<HHB", 32369, 32241, 7))
		waypoint = node(b"\x10" + string("gate") + struct.pack("<HHB", 32001, 32102, 7))
		map_data = node(b"\x02\x01" + string("fixture"), area, node(b"\x0c", town), node(b"\x0f", waypoint))
		root = node(b"\x00" + struct.pack("<IHHII", 4, 65000, 65000, 3, 57), map_data)
		return b"OTBM" + root

	def test_decodes_header_tile_item_town_and_waypoint(self) -> None:
		records = list(iter_map_records(io.BytesIO(self.fixture()), strict=True))
		self.assertEqual(records[0], MapHeader(4, 65000, 65000, 3, 57, description="fixture"))
		tile = next(record for record in records if isinstance(record, Tile))
		self.assertEqual(tile.position, Position(32003, 32104, 7))
		self.assertEqual(tile.flags, 7)
		self.assertEqual(tile.ground, Item(100))
		self.assertEqual(tile.items[0].action_id, 5555)
		self.assertTrue(any(isinstance(record, Town) for record in records))
		self.assertTrue(any(isinstance(record, Waypoint) for record in records))

	def test_repeated_compact_items_preserve_ground_then_stack_order(self) -> None:
		compact = b"\x09" + struct.pack("<H", 100) + b"\x09" + struct.pack("<H", 101)
		tile = node(b"\x05\x00\x00" + compact, node(b"\x06" + struct.pack("<H", 102)))
		area = node(b"\x04" + struct.pack("<HHB", 1, 2, 3), tile)
		root = node(b"\x00" + struct.pack("<IHHII", 4, 10, 10, 3, 57), node(b"\x02", area))
		record = next(record for record in iter_map_records(io.BytesIO(b"OTBM" + root), strict=True) if isinstance(record, Tile))
		self.assertEqual(record.ground.server_id, 100)  # type: ignore[union-attr]
		self.assertEqual([item.server_id for item in record.items], [101, 102])

	def test_unknown_item_attribute_is_fail_visible(self) -> None:
		bad_item = node(b"\x06" + struct.pack("<H", 200) + b"\x7f")
		tile = node(b"\x05\x00\x00", bad_item)
		area = node(b"\x04" + struct.pack("<HHB", 1, 2, 3), tile)
		root = node(b"\x00" + struct.pack("<IHHII", 4, 10, 10, 3, 57), node(b"\x02", area))
		records = list(iter_map_records(io.BytesIO(b"OTBM" + root)))
		self.assertTrue(any(isinstance(record, Diagnostic) and "unknown item attribute 127" in record.detail for record in records))

	def test_attribute_map_and_nested_container_item(self) -> None:
		attribute_map = b"\x80" + struct.pack("<H", 2)
		attribute_map += string("aid") + b"\x02" + struct.pack("<i", 5555)
		attribute_map += string("enabled") + b"\x04\x01"
		child = node(b"\x06" + struct.pack("<H", 201))
		container = node(b"\x06" + struct.pack("<H", 200) + attribute_map, child)
		tile = node(b"\x05\x00\x00", container)
		area = node(b"\x04" + struct.pack("<HHB", 1, 2, 3), tile)
		root = node(b"\x00" + struct.pack("<IHHII", 4, 10, 10, 3, 57), node(b"\x02", area))
		records = list(iter_map_records(io.BytesIO(b"OTBM" + root), strict=True))
		item = next(record for record in records if isinstance(record, Tile)).items[0]
		self.assertEqual(item.action_id, 5555)
		self.assertIs(item.attributes["enabled"], True)
		self.assertEqual(item.children[0].server_id, 201)
		self.assertEqual([entry.server_id for entry in walk_items((item,))], [200, 201])

	def test_teleport_house_tile_door_and_zones(self) -> None:
		teleport = node(b"\x06" + struct.pack("<H", 300) + b"\x08" + struct.pack("<HHB", 9, 8, 7))
		door = node(b"\x06" + struct.pack("<H", 301) + b"\x0e\x04")
		zones = node(b"\x13" + struct.pack("<HHH", 2, 101, 102))
		tile = node(b"\x0e\x01\x02" + struct.pack("<I", 42), teleport, door, zones)
		area = node(b"\x04" + struct.pack("<HHB", 100, 200, 3), tile)
		root = node(b"\x00" + struct.pack("<IHHII", 4, 10, 10, 3, 57), node(b"\x02", area))
		record = next(record for record in iter_map_records(io.BytesIO(b"OTBM" + root), strict=True) if isinstance(record, Tile))
		self.assertEqual(record.house_id, 42)
		self.assertEqual(record.items[0].teleport_destination, Position(9, 8, 7))
		self.assertEqual(record.items[1].house_door_id, 4)
		self.assertEqual(record.zones, (101, 102))

	def test_unknown_node_strictness_is_explicit(self) -> None:
		bad = node(b"\x63")
		root = node(b"\x00" + struct.pack("<IHHII", 4, 10, 10, 3, 57), node(b"\x02", bad))
		payload = b"OTBM" + root
		with self.assertRaisesRegex(NodeFileError, "unknown OTBM node type 99"):
			list(iter_map_records(io.BytesIO(payload), strict=True))
		records = list(iter_map_records(io.BytesIO(payload)))
		self.assertTrue(any(isinstance(record, Diagnostic) and "unknown OTBM node type 99" in record.detail for record in records))


if __name__ == "__main__":
	unittest.main()
