from __future__ import annotations

import tempfile
from pathlib import Path
import struct
import unittest

from tools.otbm_atlas.scan import scan
from tools.otbm_atlas.tests.test_semantic import node, string


class ScanTests(unittest.TestCase):
	def test_region_scan_indexes_mechanics_and_provenance(self) -> None:
		attributes = b"\x04" + struct.pack("<H", 7)
		attributes += b"\x05" + struct.pack("<H", 8)
		attributes += b"\x08" + struct.pack("<HHB", 50, 60, 7)
		item = node(b"\x06" + struct.pack("<H", 200) + attributes)
		tile = node(b"\x05\x03\x04\x09" + struct.pack("<H", 100), item)
		area = node(b"\x04" + struct.pack("<HHB", 32000, 32100, 7), tile)
		root = node(b"\x00" + struct.pack("<IHHII", 4, 10, 10, 3, 57), node(b"\x02\x01" + string("fixture"), area))
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory, "fixture.otbm")
			path.write_bytes(b"OTBM" + root)
			result = scan(path, bounds=(32000, 32100, 32000, 32200, 7))
		self.assertEqual(result["statistics"]["tiles"], 1)
		self.assertEqual(result["statistics"]["groundItems"], 1)
		self.assertEqual(result["statistics"]["childItems"], 1)
		self.assertEqual(result["statistics"]["diagnostics"], 0)
		self.assertEqual(result["mechanics"]["actionIds"][0]["actionId"], 7)
		self.assertEqual(result["mechanics"]["uniqueIds"][0]["uniqueId"], 8)
		self.assertEqual(result["mechanics"]["teleports"][0]["destination"], {"x": 50, "y": 60, "z": 7})
		self.assertEqual(len(result["sourceSha256"]), 64)


if __name__ == "__main__":
	unittest.main()
