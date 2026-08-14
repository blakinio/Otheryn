"""Read the atlas tile spool for deterministic post-render enrichers."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import struct
from typing import BinaryIO, Iterator

from .semantic import Item, Position, Tile


def _decode_item(handle: BinaryIO) -> Item:
	payload = handle.read(6)
	if len(payload) != 6:
		raise ValueError("truncated environment spool item")
	server_id, subtype, child_count = struct.unpack("<HHH", payload)
	children = tuple(_decode_item(handle) for _ in range(child_count))
	return Item(server_id, None if subtype == 0xFFFF else subtype, children=children)


def decode_spool_tiles(path: str | Path) -> Iterator[Tile]:
	"""Decode the stable SPOOL_VERSION=1 format emitted by atlas.py."""
	with Path(path).open("rb") as handle:
		while size_data := handle.read(4):
			if len(size_data) != 4:
				raise ValueError("truncated environment spool record size")
			size = struct.unpack("<I", size_data)[0]
			payload = handle.read(size)
			if len(payload) != size:
				raise ValueError("truncated environment spool record")
			record = BytesIO(payload)
			header = record.read(17)
			if len(header) != 17:
				raise ValueError("truncated environment spool tile header")
			x, y, z, house_id, flags, zone_count, item_count = struct.unpack("<HHBIIHH", header)
			zones = []
			for _ in range(zone_count):
				zone_data = record.read(2)
				if len(zone_data) != 2:
					raise ValueError("truncated environment spool tile zone")
				zones.append(struct.unpack("<H", zone_data)[0])
			items = tuple(_decode_item(record) for _ in range(item_count))
			if record.read(1):
				raise ValueError("unconsumed environment spool payload")
			yield Tile(Position(x, y, z), None if house_id == 0xFFFFFFFF else house_id, flags, items[0] if items else None, items[1:] if items else (), tuple(zones))
