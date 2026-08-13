import unittest
from tools.otbm_atlas.assets import encode_png
from tools.otbm_atlas.overview import decode_rgba_png, make_overview

class OverviewTests(unittest.TestCase):
	def test_overview_is_deterministic_canonical_derivative(self):
		rgba=bytes([255,0,0,255])*64
		result=make_overview(encode_png(8,8,rgba),8)
		self.assertEqual(decode_rgba_png(result),(1,1,bytes([255,0,0,255])))
		self.assertEqual(result,make_overview(encode_png(8,8,rgba),8))
