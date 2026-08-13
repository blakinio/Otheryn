from __future__ import annotations

import io
import gzip
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.nodefile import NodeEventKind, NodeFileError, iter_node_events


class NodeFileTests(unittest.TestCase):
	def events(self, payload: bytes, block_size: int = 2):
		return list(iter_node_events(io.BytesIO(b"OTBM" + payload), block_size=block_size))

	def test_nested_nodes_and_escaped_controls_cross_blocks(self) -> None:
		events = self.events(b"\xfe\x01\xfd\xfe\xfe\x02\xfd\xff\xff\xff", 1)
		self.assertEqual(
			[(event.kind, event.depth, event.data) for event in events],
			[
				(NodeEventKind.START, 1, b""),
				(NodeEventKind.DATA, 1, b"\x01\xfe"),
				(NodeEventKind.START, 2, b""),
				(NodeEventKind.DATA, 2, b"\x02\xff"),
				(NodeEventKind.END, 2, b""),
				(NodeEventKind.END, 1, b""),
			],
		)

	def test_rejects_data_outside_root(self) -> None:
		with self.assertRaisesRegex(NodeFileError, "data outside root node"):
			self.events(b"\x00\xfe\xff")

	def test_rejects_dangling_escape(self) -> None:
		with self.assertRaisesRegex(NodeFileError, "dangling escape byte"):
			self.events(b"\xfe\xfd")

	def test_rejects_unterminated_node(self) -> None:
		with self.assertRaisesRegex(NodeFileError, "unterminated node"):
			self.events(b"\xfe\x01")

	def test_rejects_multiple_roots(self) -> None:
		with self.assertRaisesRegex(NodeFileError, "multiple root nodes"):
			self.events(b"\xfe\xff\xfe\xff")

	def test_path_input_detects_gzip_by_magic_bytes(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory, "map.otbm")
			path.write_bytes(gzip.compress(b"OTBM\xfe\x01\xff", mtime=0))
			events = list(iter_node_events(path))
		self.assertEqual(events[1].data, b"\x01")


if __name__ == "__main__":
	unittest.main()
