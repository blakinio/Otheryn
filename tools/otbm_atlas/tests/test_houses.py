from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.houses import parse_houses


class HouseTests(unittest.TestCase):
	def test_house_metadata_and_optional_guildhall(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / "world-house.xml"
			path.write_text('<houses><house name="Home" houseid="1" entryx="2" entryy="3" entryz="7" rent="10" townid="4" size="5" clientid="6" beds="1"/></houses>', encoding="utf-8")
			report = parse_houses(path)
			self.assertEqual(report["houses"][0]["entry"], {"x": 2, "y": 3, "z": 7})
			self.assertFalse(report["houses"][0]["guildhall"])


if __name__ == "__main__": unittest.main()
