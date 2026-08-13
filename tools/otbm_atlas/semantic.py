"""Version-aware semantic decoding for OTBM node streams."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
import struct
from typing import Any, BinaryIO, Iterator

from .nodefile import NodeEventKind, NodeFileError, iter_node_events


class NodeType(IntEnum):
	ROOT = 0
	MAP_DATA = 2
	TILE_AREA = 4
	TILE = 5
	ITEM = 6
	TOWNS = 12
	TOWN = 13
	HOUSE_TILE = 14
	WAYPOINTS = 15
	WAYPOINT = 16
	TILE_ZONE = 19


class Attribute(IntEnum):
	DESCRIPTION = 1
	TILE_FLAGS = 3
	ACTION_ID = 4
	UNIQUE_ID = 5
	TEXT = 6
	DESC = 7
	TELE_DEST = 8
	ITEM = 9
	DEPOT_ID = 10
	SPAWN_MONSTER_FILE = 11
	RUNE_CHARGES = 12
	HOUSE_FILE = 13
	HOUSE_DOOR_ID = 14
	COUNT = 15
	DURATION = 16
	DECAYING_STATE = 17
	WRITTEN_DATE = 18
	WRITTEN_BY = 19
	SLEEPER_GUID = 20
	SLEEP_START = 21
	CHARGES = 22
	SPAWN_NPC_FILE = 23
	ZONE_FILE = 24
	ATTRIBUTE_MAP = 128


@dataclass(frozen=True, slots=True)
class Position:
	x: int
	y: int
	z: int


@dataclass(frozen=True, slots=True)
class Diagnostic:
	kind: str
	offset: int
	node_type: int | None
	position: Position | None
	detail: str


@dataclass(frozen=True, slots=True)
class MapHeader:
	version: int
	width: int
	height: int
	items_major: int
	items_minor: int
	description: str | None = None
	spawn_monster_file: str | None = None
	spawn_npc_file: str | None = None
	house_file: str | None = None
	zone_file: str | None = None


@dataclass(frozen=True, slots=True)
class Item:
	server_id: int
	subtype: int | None = None
	action_id: int | None = None
	unique_id: int | None = None
	text: str | None = None
	description: str | None = None
	teleport_destination: Position | None = None
	house_door_id: int | None = None
	attributes: dict[str, Any] = field(default_factory=dict)
	children: tuple["Item", ...] = ()


@dataclass(frozen=True, slots=True)
class Tile:
	position: Position
	house_id: int | None
	flags: int
	ground: Item | None
	items: tuple[Item, ...]
	zones: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class Town:
	town_id: int
	name: str
	temple: Position


@dataclass(frozen=True, slots=True)
class Waypoint:
	name: str
	position: Position


MapRecord = MapHeader | Tile | Town | Waypoint | Diagnostic


def walk_items(items: tuple[Item, ...]) -> Iterator[Item]:
	"""Yield items in stable pre-order, including container descendants."""
	for item in items:
		yield item
		yield from walk_items(item.children)


class _Cursor:
	def __init__(self, data: bytes, offset: int) -> None:
		self.data = data
		self.index = 0
		self.offset = offset

	def remaining(self) -> int:
		return len(self.data) - self.index

	def take(self, size: int) -> bytes:
		if size < 0 or self.remaining() < size:
			raise NodeFileError("truncated semantic payload", self.offset + self.index)
		value = self.data[self.index : self.index + size]
		self.index += size
		return value

	def u8(self) -> int:
		return self.take(1)[0]

	def u16(self) -> int:
		return struct.unpack("<H", self.take(2))[0]

	def u32(self) -> int:
		return struct.unpack("<I", self.take(4))[0]

	def u64(self) -> int:
		return struct.unpack("<Q", self.take(8))[0]

	def string(self) -> str:
		return self.take(self.u16()).decode("utf-8", errors="surrogateescape")

	def long_string(self) -> str:
		return self.take(self.u32()).decode("utf-8", errors="surrogateescape")


@dataclass(slots=True)
class _Context:
	offset: int
	node_type: int | None = None
	position: Position | None = None
	area: Position | None = None
	value: Any = None
	children: list[Any] = field(default_factory=list)


def _attribute_value(cursor: _Cursor) -> Any:
	kind = cursor.u8()
	if kind == 1:
		return cursor.long_string()
	if kind == 2:
		return struct.unpack("<i", cursor.take(4))[0]
	if kind == 3:
		return struct.unpack("<f", cursor.take(4))[0]
	if kind == 4:
		return bool(cursor.u8())
	if kind == 5:
		return struct.unpack("<d", cursor.take(8))[0]
	raise NodeFileError(f"unknown attribute-map value type {kind}", cursor.offset + cursor.index - 1)


def _attribute_map(cursor: _Cursor) -> dict[str, Any]:
	values: dict[str, Any] = {}
	for _ in range(cursor.u16()):
		key = cursor.string()
		values[key] = _attribute_value(cursor)
	return values


def _parse_item(cursor: _Cursor) -> dict[str, Any]:
	item: dict[str, Any] = {"server_id": cursor.u16(), "attributes": {}}
	while cursor.remaining():
		attribute_offset = cursor.offset + cursor.index
		attribute = cursor.u8()
		if attribute in (Attribute.COUNT, Attribute.RUNE_CHARGES, Attribute.DECAYING_STATE, Attribute.HOUSE_DOOR_ID):
			value = cursor.u8()
		elif attribute in (Attribute.ACTION_ID, Attribute.UNIQUE_ID, Attribute.DEPOT_ID, Attribute.CHARGES):
			value = cursor.u16()
		elif attribute in (Attribute.DURATION, Attribute.WRITTEN_DATE, Attribute.SLEEPER_GUID, Attribute.SLEEP_START):
			value = cursor.u32()
		elif attribute in (Attribute.TEXT, Attribute.DESC, Attribute.WRITTEN_BY):
			value = cursor.string()
		elif attribute == Attribute.TELE_DEST:
			value = Position(cursor.u16(), cursor.u16(), cursor.u8())
		elif attribute == Attribute.ATTRIBUTE_MAP:
			item["attributes"].update(_attribute_map(cursor))
			continue
		else:
			raise NodeFileError(f"unknown item attribute {attribute}", attribute_offset)
		item[Attribute(attribute).name.lower()] = value
	return item


def _finish_item(value: dict[str, Any], children: list[Any]) -> Item:
	attributes = value["attributes"]
	return Item(
		server_id=value["server_id"],
		subtype=value.get("count", value.get("charges")),
		action_id=value.get("action_id", attributes.get("aid")),
		unique_id=value.get("unique_id", attributes.get("uid")),
		text=value.get("text", attributes.get("text")),
		description=value.get("desc", attributes.get("desc")),
		teleport_destination=value.get("tele_dest"),
		house_door_id=value.get("house_door_id"),
		attributes=attributes,
		children=tuple(child for child in children if isinstance(child, Item)),
	)


def iter_map_records(
	source: str | Path | BinaryIO,
	*,
	strict: bool = False,
) -> Iterator[MapRecord]:
	"""Decode semantic records while retaining at most one tile/item stack."""
	stack: list[_Context] = []
	header: MapHeader | None = None

	for event in iter_node_events(source):
		if event.kind is NodeEventKind.START:
			stack.append(_Context(event.offset))
			continue
		if event.kind is NodeEventKind.DATA:
			context = stack[-1]
			parent = stack[-2] if len(stack) > 1 else None
			cursor = _Cursor(event.data, event.offset)
			try:
				context.node_type = cursor.u8()
				if parent is None:
					if context.node_type != NodeType.ROOT:
						raise NodeFileError(f"unexpected root type {context.node_type}", event.offset)
					header = MapHeader(cursor.u32(), cursor.u16(), cursor.u16(), cursor.u32(), cursor.u32())
					context.value = header
				elif context.node_type == NodeType.MAP_DATA:
					if header is None:
						raise NodeFileError("map data before root header", event.offset)
					values = dict(header.__dict__) if hasattr(header, "__dict__") else {
						name: getattr(header, name) for name in header.__dataclass_fields__
					}
					keys = {1: "description", 11: "spawn_monster_file", 13: "house_file", 23: "spawn_npc_file", 24: "zone_file"}
					while cursor.remaining():
						attribute = cursor.u8()
						if attribute not in keys:
							raise NodeFileError(f"unknown map attribute {attribute}", cursor.offset + cursor.index - 1)
						values[keys[attribute]] = cursor.string()
					header = MapHeader(**values)
					context.value = header
					yield header
				elif context.node_type == NodeType.TILE_AREA:
					context.area = Position(cursor.u16(), cursor.u16(), cursor.u8())
				elif context.node_type in (NodeType.TILE, NodeType.HOUSE_TILE):
					area = parent.area if parent else None
					if area is None:
						raise NodeFileError("tile outside tile area", event.offset)
					context.position = Position(area.x + cursor.u8(), area.y + cursor.u8(), area.z)
					house_id = cursor.u32() if context.node_type == NodeType.HOUSE_TILE else None
					value: dict[str, Any] = {"house_id": house_id, "flags": 0, "compact_items": [], "zones": []}
					while cursor.remaining():
						attribute_offset = cursor.offset + cursor.index
						attribute = cursor.u8()
						if attribute == Attribute.TILE_FLAGS:
							value["flags"] = cursor.u32()
						elif attribute == Attribute.ITEM:
							value["compact_items"].append(Item(cursor.u16()))
						else:
							raise NodeFileError(f"unknown tile attribute {attribute}", attribute_offset)
					context.value = value
				elif context.node_type == NodeType.ITEM:
					context.position = next((entry.position for entry in reversed(stack[:-1]) if entry.position), None)
					context.value = _parse_item(cursor)
				elif context.node_type == NodeType.TILE_ZONE:
					context.value = tuple(cursor.u16() for _ in range(cursor.u16()))
				elif context.node_type == NodeType.TOWN:
					context.value = Town(cursor.u32(), cursor.string(), Position(cursor.u16(), cursor.u16(), cursor.u8()))
				elif context.node_type == NodeType.WAYPOINT:
					context.value = Waypoint(cursor.string(), Position(cursor.u16(), cursor.u16(), cursor.u8()))
				elif context.node_type not in (NodeType.TOWNS, NodeType.WAYPOINTS):
					raise NodeFileError(f"unknown OTBM node type {context.node_type}", event.offset)
				if cursor.remaining():
					raise NodeFileError("unconsumed semantic payload", cursor.offset + cursor.index)
			except (NodeFileError, ValueError) as error:
				diagnostic = Diagnostic(
					kind="semantic_error",
					offset=getattr(error, "offset", event.offset),
					node_type=context.node_type,
					position=context.position,
					detail=str(error),
				)
				if strict:
					raise
				context.value = diagnostic
				yield diagnostic
			continue

		context = stack.pop()
		value = context.value
		if context.node_type == NodeType.ITEM and isinstance(value, dict):
			value = _finish_item(value, context.children)
		elif context.node_type in (NodeType.TILE, NodeType.HOUSE_TILE) and isinstance(value, dict):
			compact_items = value["compact_items"]
			ground = compact_items[0] if compact_items else None
			items = tuple(compact_items[1:]) + tuple(child for child in context.children if isinstance(child, Item))
			zones = tuple(zone for child in context.children if isinstance(child, tuple) for zone in child)
			value = Tile(context.position, value["house_id"], value["flags"], ground, items, zones)  # type: ignore[arg-type]

		if stack:
			stack[-1].children.append(value)
		if isinstance(value, (Tile, Town, Waypoint)):
			yield value
