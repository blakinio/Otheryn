import json,tempfile,unittest
from pathlib import Path
from tools.otbm_atlas.spatial import write_spatial_data

class SpatialTests(unittest.TestCase):
	def test_records_are_sharded_by_floor_chunk_and_spawn_origin(self):
		with tempfile.TemporaryDirectory() as directory:
			root=Path(directory);stats=write_spatial_data(root,128,{
				"npcSpawns":[
					{"name":"Guide","position":{"x":256,"y":384,"z":7},"origin":"base-map"},
					{"name":"Event Guide","position":{"x":257,"y":384,"z":7},"origin":"annual-event-map"},
				],
				"towns":[{"name":"Thais","temple":{"x":32369,"y":32241,"z":7}}],
			})
			self.assertEqual(stats,{"shards":2,"searchRecords":3})
			chunk=json.loads((root/"data/chunks/z7/2_3.json").read_text())
			self.assertEqual(chunk["npcSpawns"][0]["name"],"Guide")
			self.assertEqual(chunk["supplementalNpcSpawns"][0]["name"],"Event Guide")
			self.assertEqual(chunk["supplementalNpcSpawns"][0]["origin"],"annual-event-map")
