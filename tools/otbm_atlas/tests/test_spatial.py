import json,tempfile,unittest
from pathlib import Path
from tools.otbm_atlas.spatial import write_spatial_data

class SpatialTests(unittest.TestCase):
	def test_records_are_sharded_by_floor_and_chunk(self):
		with tempfile.TemporaryDirectory() as directory:
			root=Path(directory);stats=write_spatial_data(root,128,{"npcSpawns":[{"name":"Guide","position":{"x":256,"y":384,"z":7}}],"towns":[{"name":"Thais","temple":{"x":32369,"y":32241,"z":7}}]})
			self.assertEqual(stats,{"shards":2,"searchRecords":2})
			self.assertEqual(json.loads((root/"data/chunks/z7/2_3.json").read_text())["npcSpawns"][0]["name"],"Guide")
