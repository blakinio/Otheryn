"""Decode pinned Tibia appearance metadata and sprite sheets."""

from __future__ import annotations

from dataclasses import dataclass
import json
import lzma
from pathlib import Path
import struct
import zlib
from typing import Iterator


class AssetError(ValueError):
	pass


@dataclass(frozen=True, slots=True)
class SpriteInfo:
	pattern_width: int
	pattern_height: int
	pattern_depth: int
	layers: int
	sprite_ids: tuple[int, ...]
	animation_phases: int
	default_start_phase: int


@dataclass(frozen=True, slots=True)
class Appearance:
	appearance_id: int
	name: str
	is_ground: bool
	clip: bool
	bottom: bool
	top: bool
	stackable: bool
	splash: bool
	fluid_container: bool
	shift: tuple[int, int] | None
	height: int | None
	frames: tuple[SpriteInfo, ...]


@dataclass(frozen=True, slots=True)
class SpriteSheet:
	path: Path
	first_id: int
	last_id: int
	layout: int

	@property
	def sprite_size(self) -> tuple[int, int]:
		return ((32, 32), (32, 64), (64, 32), (64, 64))[self.layout]


def _varint(data: bytes, offset: int) -> tuple[int, int]:
	value = 0
	shift = 0
	while offset < len(data) and shift < 70:
		byte = data[offset]
		offset += 1
		value |= (byte & 0x7F) << shift
		if byte < 0x80:
			return value, offset
		shift += 7
	raise AssetError(f"invalid protobuf varint at offset {offset}")


def _fields(data: bytes) -> Iterator[tuple[int, int, int | bytes]]:
	offset = 0
	while offset < len(data):
		key, offset = _varint(data, offset)
		field = key >> 3
		wire = key & 7
		if field == 0:
			raise AssetError(f"invalid protobuf field zero at offset {offset}")
		if wire == 0:
			value, offset = _varint(data, offset)
		elif wire == 1:
			if offset + 8 > len(data): raise AssetError("truncated fixed64 field")
			value = data[offset : offset + 8]; offset += 8
		elif wire == 2:
			size, offset = _varint(data, offset)
			if offset + size > len(data): raise AssetError("truncated length-delimited field")
			value = data[offset : offset + size]; offset += size
		elif wire == 5:
			if offset + 4 > len(data): raise AssetError("truncated fixed32 field")
			value = data[offset : offset + 4]; offset += 4
		else:
			raise AssetError(f"unsupported protobuf wire type {wire}")
		yield field, wire, value


def _embedded(data: bytes, field_number: int) -> Iterator[bytes]:
	for field, wire, value in _fields(data):
		if field == field_number and wire == 2:
			yield value  # type: ignore[misc]


def _message_values(data: bytes) -> dict[int, list[int | bytes]]:
	values: dict[int, list[int | bytes]] = {}
	for field, _wire, value in _fields(data):
		values.setdefault(field, []).append(value)
	return values


def _first_int(values: dict[int, list[int | bytes]], field: int, default: int = 0) -> int:
	entries = values.get(field)
	return int(entries[0]) if entries and isinstance(entries[0], int) else default


def _sprite_info(data: bytes) -> SpriteInfo:
	values = _message_values(data)
	animation = values.get(6, [])
	animation_values = _message_values(animation[0]) if animation and isinstance(animation[0], bytes) else {}
	phases = len(animation_values.get(6, []))
	return SpriteInfo(
		pattern_width=max(1, _first_int(values, 1, 1)),
		pattern_height=max(1, _first_int(values, 2, 1)),
		pattern_depth=max(1, _first_int(values, 3, 1)),
		layers=max(1, _first_int(values, 4, 1)),
		sprite_ids=tuple(int(value) for value in values.get(5, []) if isinstance(value, int)),
		animation_phases=max(1, phases),
		default_start_phase=_first_int(animation_values, 1),
	)


def _flag_message(values: dict[int, list[int | bytes]], field: int) -> bytes | None:
	entries = values.get(field)
	return entries[0] if entries and isinstance(entries[0], bytes) else None


def _appearance(data: bytes) -> Appearance:
	values = _message_values(data)
	flags_data = _flag_message(values, 3) or b""
	flags = _message_values(flags_data)
	frames = []
	for frame_data in (value for value in values.get(2, []) if isinstance(value, bytes)):
		frame = _message_values(frame_data)
		sprite_payload = _flag_message(frame, 3)
		if sprite_payload is not None:
			frames.append(_sprite_info(sprite_payload))
	shift_data = _flag_message(flags, 26)
	shift = None
	if shift_data is not None:
		shift_values = _message_values(shift_data)
		shift = (_first_int(shift_values, 1), _first_int(shift_values, 2))
	height_data = _flag_message(flags, 27)
	height = None
	if height_data is not None:
		height = _first_int(_message_values(height_data), 1)
	name_value = values.get(4, [b""])[0]
	return Appearance(
		appearance_id=_first_int(values, 1),
		name=name_value.decode("utf-8", "replace") if isinstance(name_value, bytes) else "",
		is_ground=1 in flags,
		clip=2 in flags,
		bottom=3 in flags,
		top=4 in flags,
		stackable=bool(_first_int(flags, 6)),
		splash=bool(_first_int(flags, 12)),
		fluid_container=bool(_first_int(flags, 19)),
		shift=shift,
		height=height,
		frames=tuple(frames),
	)


def load_appearances(path: str | Path, category_field: int) -> dict[int, Appearance]:
	"""Load one appearance category from the pinned Tibia asset file.

	The asset protobuf keeps item, creature and effect appearances in separate
	repeated fields.  Atlas tiles use items (field 1); NPC outfits use creatures
	(field 2) and must never be guessed from an item appearance.
	"""
	data = Path(path).read_bytes()
	result: dict[int, Appearance] = {}
	for payload in _embedded(data, category_field):
		appearance = _appearance(payload)
		if appearance.appearance_id in result:
			raise AssetError(f"duplicate appearance id {appearance.appearance_id}")
		result[appearance.appearance_id] = appearance
	return result


def load_object_appearances(path: str | Path) -> dict[int, Appearance]:
	return load_appearances(path, 1)


def load_creature_appearances(path: str | Path) -> dict[int, Appearance]:
	return load_appearances(path, 2)


def load_sprite_catalog(asset_dir: str | Path) -> list[SpriteSheet]:
	base = Path(asset_dir)
	catalog = json.loads((base / "catalog-content.json").read_text(encoding="utf-8"))
	result = [
		SpriteSheet(base / entry["file"], entry["firstspriteid"], entry["lastspriteid"], entry["spritetype"])
		for entry in catalog if entry.get("type") == "sprite"
	]
	result.sort(key=lambda sheet: sheet.last_id)
	return result


def sheet_for_sprite(sheets: list[SpriteSheet], sprite_id: int) -> SpriteSheet | None:
	left, right = 0, len(sheets)
	while left < right:
		middle = (left + right) // 2
		if sheets[middle].last_id < sprite_id: left = middle + 1
		else: right = middle
	if left == len(sheets) or sprite_id < sheets[left].first_id:
		return None
	return sheets[left]


def decode_sheet(path: str | Path) -> tuple[int, int, bytes]:
	"""Return top-down 384x384 RGBA bytes from a CipSoft LZMA-wrapped BMP."""
	data = Path(path).read_bytes()
	position = 0
	while position < len(data) and data[position] == 0:
		position += 1
	if data[position : position + 5] != b"\x70\x0a\xfa\x80\x24":
		raise AssetError("invalid CipSoft sprite sheet header")
	position += 5
	while position < len(data) and data[position] & 0x80:
		position += 1
	position += 1
	if position + 13 > len(data):
		raise AssetError("truncated LZMA properties")
	properties = data[position]
	lc = properties % 9
	remainder = properties // 9
	lp, pb = remainder % 5, remainder // 5
	dictionary = int.from_bytes(data[position + 1 : position + 5], "little")
	position += 13
	bmp = lzma.decompress(data[position:], format=lzma.FORMAT_RAW, filters=[{
		"id": lzma.FILTER_LZMA1, "dict_size": dictionary, "lc": lc, "lp": lp, "pb": pb,
	}])
	if bmp[:2] != b"BM":
		raise AssetError("decoded sprite sheet is not BMP")
	pixel_offset = int.from_bytes(bmp[10:14], "little")
	width = int.from_bytes(bmp[18:22], "little", signed=True)
	height = int.from_bytes(bmp[22:26], "little", signed=True)
	if width != 384 or abs(height) != 384:
		raise AssetError(f"unexpected sprite sheet dimensions {width}x{height}")
	pixels = bmp[pixel_offset : pixel_offset + width * abs(height) * 4]
	if len(pixels) != width * abs(height) * 4:
		raise AssetError("truncated sprite pixels")
	rows = [pixels[index * width * 4 : (index + 1) * width * 4] for index in range(abs(height))]
	if height > 0:
		rows.reverse()
	rgba = bytearray()
	for row in rows:
		for index in range(0, len(row), 4):
			blue, green, red, alpha = row[index : index + 4]
			rgba.extend((red, green, blue, alpha))
	return width, abs(height), bytes(rgba)


def extract_sprite(sheet: SpriteSheet, rgba: bytes, sprite_id: int) -> tuple[int, int, bytes]:
	if not sheet.first_id <= sprite_id <= sheet.last_id:
		raise AssetError(f"sprite {sprite_id} is outside sheet range")
	width, height = sheet.sprite_size
	columns = 384 // width
	offset = sprite_id - sheet.first_id
	x, y = (offset % columns) * width, (offset // columns) * height
	result = bytearray()
	for row in range(y, y + height):
		start = (row * 384 + x) * 4
		result.extend(rgba[start : start + width * 4])
	return width, height, bytes(result)


def encode_png(width: int, height: int, rgba: bytes) -> bytes:
	if len(rgba) != width * height * 4:
		raise AssetError("RGBA buffer size does not match dimensions")
	def chunk(kind: bytes, payload: bytes) -> bytes:
		body = kind + payload
		return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
	rows = b"".join(b"\x00" + rgba[y * width * 4 : (y + 1) * width * 4] for y in range(height))
	return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
