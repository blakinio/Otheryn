"""Bounded-memory reader for the escaped node stream used by OTBM files.

The framing constants and escape semantics follow Remere's Map Editor
``source/filehandle.h`` and ``source/filehandle.cpp``.  This module deliberately
does not interpret node payloads; semantic decoding belongs to the OTBM layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import gzip
from pathlib import Path
from typing import BinaryIO, Iterator

NODE_START = 0xFE
NODE_END = 0xFF
ESCAPE = 0xFD
DEFAULT_BLOCK_SIZE = 64 * 1024


class NodeFileError(ValueError):
	"""A structural node-stream error with an exact byte offset."""

	def __init__(self, message: str, offset: int) -> None:
		super().__init__(f"{message} at byte offset {offset}")
		self.offset = offset


class NodeEventKind(str, Enum):
	START = "start"
	DATA = "data"
	END = "end"


@dataclass(frozen=True, slots=True)
class NodeEvent:
	kind: NodeEventKind
	offset: int
	depth: int
	data: bytes = b""


def _open_source(source: str | Path | BinaryIO) -> tuple[BinaryIO, bool]:
	if hasattr(source, "read"):
		return source, False  # type: ignore[return-value]
	raw = Path(source).open("rb")
	magic = raw.read(2)
	raw.seek(0)
	if magic == b"\x1f\x8b":
		raw.close()
		return gzip.open(Path(source), "rb"), True
	return raw, True


def iter_node_events(
	source: str | Path | BinaryIO,
	*,
	identifier_size: int = 4,
	block_size: int = DEFAULT_BLOCK_SIZE,
) -> Iterator[NodeEvent]:
	"""Yield an OTBM node stream without retaining the complete tree in memory.

	The four-byte file identifier is skipped but not interpreted here. Escaped
	control bytes are emitted as ordinary DATA. Truncation, illegal top-level
	data, multiple roots, dangling escapes, and unbalanced nodes are errors.
	"""
	if identifier_size < 0:
		raise ValueError("identifier_size must be non-negative")
	if block_size < 1:
		raise ValueError("block_size must be positive")

	handle, should_close = _open_source(source)
	try:
		identifier = handle.read(identifier_size)
		if len(identifier) != identifier_size:
			raise NodeFileError("truncated file identifier", len(identifier))

		offset = identifier_size
		depth = 0
		root_seen = False
		escaped = False
		data = bytearray()
		data_offset = offset

		while chunk := handle.read(block_size):
			for value in chunk:
				current_offset = offset
				offset += 1
				if escaped:
					if not data:
						data_offset = current_offset - 1
					data.append(value)
					escaped = False
					continue
				if value == ESCAPE:
					escaped = True
					continue
				if value not in (NODE_START, NODE_END):
					if depth == 0:
						raise NodeFileError("data outside root node", current_offset)
					if not data:
						data_offset = current_offset
					data.append(value)
					continue

				if data:
					yield NodeEvent(NodeEventKind.DATA, data_offset, depth, bytes(data))
					data.clear()
				if value == NODE_START:
					if depth == 0:
						if root_seen:
							raise NodeFileError("multiple root nodes", current_offset)
						root_seen = True
					depth += 1
					yield NodeEvent(NodeEventKind.START, current_offset, depth)
				else:
					if depth == 0:
						raise NodeFileError("unexpected node end", current_offset)
					yield NodeEvent(NodeEventKind.END, current_offset, depth)
					depth -= 1

		if escaped:
			raise NodeFileError("dangling escape byte", offset - 1)
		if data:
			yield NodeEvent(NodeEventKind.DATA, data_offset, depth, bytes(data))
		if not root_seen:
			raise NodeFileError("missing root node", offset)
		if depth:
			raise NodeFileError("unterminated node", offset)
	finally:
		if should_close:
			handle.close()
