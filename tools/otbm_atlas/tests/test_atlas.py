from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

from types import SimpleNamespace

from tools.otbm_atlas.atlas import canonical_source_paths, chunk_render_bounds, decode_tiles, encode_tile
from tools.otbm_atlas.repair_asset_checkout import repair_crlf_asset
from tools.otbm_atlas.semantic import Item, Position, Tile


class AtlasTests(unittest.TestCase):
	def test_canonical_asset_checkout_bytes_are_stable(self) -> None:
		repository = Path(__file__).parents[3]
		relative = Path("vendor/map-analysis/tibia-client/15.25.bd5a04/assets/proficiencies-1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22.json")
		asset = repository / relative
		self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(), "1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22")
		attribute = subprocess.run(
			["git", "check-attr", "text", "--", relative.as_posix()],
			cwd=repository,
			check=True,
			capture_output=True,
			text=True,
		).stdout.strip()
		self.assertEqual(attribute, f"{relative.as_posix()}: text: unset")

	def test_legacy_crlf_asset_checkout_can_be_repaired_safely(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			repository = Path(directory)
			subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
			subprocess.run(["git", "config", "user.name", "Atlas Test"], cwd=repository, check=True)
			subprocess.run(["git", "config", "user.email", "atlas-test@example.invalid"], cwd=repository, check=True)
			relative = Path("assets/example.json")
			asset = repository / relative
			asset.parent.mkdir(); asset.write_bytes(b'{\n  "value": 1\n}\n')
			subprocess.run(["git", "add", relative.as_posix()], cwd=repository, check=True)
			subprocess.run(["git", "commit", "-qm", "fixture"], cwd=repository, check=True)
			asset.write_bytes(b'{\r\n  "value": 1\r\n}\r\n')
			self.assertTrue(repair_crlf_asset(repository, relative))
			self.assertEqual(asset.read_bytes(), b'{\n  "value": 1\n}\n')
			self.assertFalse(repair_crlf_asset(repository, relative))
			asset.write_bytes(b'{\n  "value": 2\n}\n')
			with self.assertRaisesRegex(ValueError, "non-CRLF"):
				repair_crlf_asset(repository, relative)

	def test_spool_codec_round_trip_preserves_render_structure(self) -> None:
		tile = Tile(Position(123, 456, 7), 42, 3, Item(100), (Item(200, 5, children=(Item(201),)),), (8, 9))
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory, "chunk.bin"); path.write_bytes(encode_tile(tile))
			decoded = list(decode_tiles(path))
		self.assertEqual(decoded, [tile])

	def test_spool_codec_rejects_truncated_tile_header(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory, "chunk.bin"); path.write_bytes(b"\x01\x00\x00\x00\x00")
			with self.assertRaisesRegex(ValueError, "tile header"):
				list(decode_tiles(path))

	def test_chunk_bounds_crop_empty_space_and_keep_sprite_gutter(self) -> None:
		tiles = [Tile(Position(100, 200, 7), None, 0, Item(100), (), ()), Tile(Position(102, 203, 7), None, 0, Item(100), (), ())]
		renderer = SimpleNamespace(
			sheets=[SimpleNamespace(sprite_size=(64, 64))],
			appearances={100: SimpleNamespace(shift=(25, 24))},
		)
		self.assertEqual(chunk_render_bounds(tiles, renderer), (98, 102, 198, 203, 7))

	def test_canonical_source_contract_is_vendor_map_analysis_only(self) -> None:
		root = Path("/repo")
		sources = canonical_source_paths(root)
		for value in sources.values():
			self.assertTrue(value.as_posix().startswith("/repo/vendor/map-analysis/"), value)
		code_root = Path(__file__).parents[1]
		for path in sorted(code_root.iterdir()):
			if not path.is_file() or path.suffix not in {".py", ".js"}:
				continue
			text = path.read_text(encoding="utf-8")
			self.assertNotIn("data-otservbr-global", text, path.name)


if __name__ == "__main__": unittest.main()
