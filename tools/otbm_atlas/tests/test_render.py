from __future__ import annotations

import unittest

from tools.otbm_atlas.render import _blend


class RenderTests(unittest.TestCase):
	def test_alpha_blend_and_clipping_are_deterministic(self) -> None:
		canvas = bytearray(b"\x00\x00\xff\xff" * 4)
		source = b"\xff\x00\x00\x80" * 4
		_blend(canvas, 2, 2, source, 2, 2, 1, 1)
		self.assertEqual(canvas[12:16], bytes((128, 0, 127, 255)))
		self.assertEqual(canvas[:4], b"\x00\x00\xff\xff")


if __name__ == "__main__":
	unittest.main()
