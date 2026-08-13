"""Deterministic lightweight derivatives of canonical atlas PNG chunks."""

from __future__ import annotations

import struct
import zlib

from .assets import encode_png

OVERVIEW_FACTOR = 4
LOW_OVERVIEW_FACTOR = 8
OVERVIEW_VERSION = 1


def decode_rgba_png(payload: bytes) -> tuple[int, int, bytes]:
	if payload[:8] != b"\x89PNG\r\n\x1a\n": raise ValueError("not a PNG")
	offset, width, height, compressed = 8, 0, 0, bytearray()
	while offset < len(payload):
		length = struct.unpack(">I", payload[offset:offset + 4])[0]
		kind, data = payload[offset + 4:offset + 8], payload[offset + 8:offset + 8 + length]
		offset += 12 + length
		if kind == b"IHDR":
			width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", data)
			if (depth, color, compression, filtering, interlace) != (8, 6, 0, 0, 0): raise ValueError("unsupported PNG format")
		elif kind == b"IDAT": compressed.extend(data)
		elif kind == b"IEND": break
	raw, rows = zlib.decompress(bytes(compressed)), bytearray()
	stride = width * 4
	if len(raw) != height * (stride + 1): raise ValueError("invalid PNG payload length")
	for y in range(height):
		row = raw[y * (stride + 1):(y + 1) * (stride + 1)]
		if row[0] != 0: raise ValueError("unsupported PNG filter")
		rows.extend(row[1:])
	return width, height, bytes(rows)


def make_overview(payload: bytes, factor: int = OVERVIEW_FACTOR) -> bytes:
	width, height, rgba = decode_rgba_png(payload)
	if factor <= 0 or width % factor or height % factor: raise ValueError("PNG dimensions must be divisible by overview factor")
	out_width, out_height = width // factor, height // factor
	out = bytearray(out_width * out_height * 4)
	for oy in range(out_height):
		for ox in range(out_width):
			r = g = b = a = 0
			for y in range(oy * factor, (oy + 1) * factor):
				for x in range(ox * factor, (ox + 1) * factor):
					i = (y * width + x) * 4; alpha = rgba[i + 3]
					r += rgba[i] * alpha; g += rgba[i + 1] * alpha; b += rgba[i + 2] * alpha; a += alpha
			o = (oy * out_width + ox) * 4; count = factor * factor
			out[o:o + 4] = bytes((r // a if a else 0, g // a if a else 0, b // a if a else 0, a // count))
	return encode_png(out_width, out_height, bytes(out))
