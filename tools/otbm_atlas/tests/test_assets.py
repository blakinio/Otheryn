from __future__ import annotations

import struct
import unittest

from tools.otbm_atlas.assets import SpriteSheet, encode_png, extract_sprite, load_object_appearances
from tools.otbm_atlas.tests.test_semantic import string


def varint(value: int) -> bytes:
	result = bytearray()
	while value > 0x7f:
		result.append((value & 0x7f) | 0x80); value >>= 7
	result.append(value)
	return bytes(result)


def field(number: int, payload: bytes) -> bytes:
	return varint(number << 3 | 2) + varint(len(payload)) + payload


class AssetTests(unittest.TestCase):
	def test_png_encoder_is_deterministic(self) -> None:
		payload = encode_png(1, 1, b"\xff\x00\x00\xff")
		self.assertEqual(payload[:8], b"\x89PNG\r\n\x1a\n")
		self.assertEqual(payload, encode_png(1, 1, b"\xff\x00\x00\xff"))

	def test_appearance_wire_decoder_reads_ground_flags_and_sprite_info(self) -> None:
		sprite_info = varint(1 << 3) + b"\x02" + varint(2 << 3) + b"\x01"
		sprite_info += varint(3 << 3) + b"\x01" + varint(4 << 3) + b"\x01"
		sprite_info += varint(5 << 3) + varint(123)
		frame = field(3, sprite_info)
		flags = field(1, varint(1 << 3) + b"\x01")
		flags += varint(6 << 3) + b"\x01" + varint(12 << 3) + b"\x01" + varint(19 << 3) + b"\x01"
		appearance = varint(1 << 3) + varint(100) + field(2, frame) + field(3, flags) + field(4, b"ground")
		root = field(1, appearance)
		import tempfile
		from pathlib import Path
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory, "appearances.dat"); path.write_bytes(root)
			decoded = load_object_appearances(path)[100]
		self.assertTrue(decoded.is_ground)
		self.assertTrue(decoded.stackable)
		self.assertTrue(decoded.splash)
		self.assertTrue(decoded.fluid_container)
		self.assertEqual(decoded.frames[0].sprite_ids, (123,))
		self.assertEqual((decoded.frames[0].pattern_width, decoded.frames[0].pattern_height), (2, 1))
		self.assertEqual(decoded.frames[0].default_start_phase, 0)

	def test_extract_sprite_uses_catalog_layout_grid(self) -> None:
		pixels = bytearray(384 * 384 * 4)
		for y in range(32):
			for x in range(32, 64):
				pixels[(y * 384 + x) * 4 : (y * 384 + x) * 4 + 4] = b"\x01\x02\x03\x04"
		width, height, sprite = extract_sprite(SpriteSheet(__import__('pathlib').Path('x'), 10, 20, 0), bytes(pixels), 11)
		self.assertEqual((width, height), (32, 32))
		self.assertEqual(sprite[:4], b"\x01\x02\x03\x04")


if __name__ == "__main__":
	unittest.main()
