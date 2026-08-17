from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.assets import encode_png
from tools.otbm_atlas.local_parallel_build import _make_overviews, build_overviews
from tools.otbm_atlas.overview import LOW_OVERVIEW_FACTOR, OVERVIEW_FACTOR, make_overview


def _detail_png(seed: int, width: int = 64, height: int = 64) -> bytes:
	pixels = bytearray()
	for y in range(height):
		for x in range(width):
			pixels.extend(((x * 3 + seed) % 256, (y * 5 + seed) % 256, (x + y + seed) % 256, 255))
	return encode_png(width, height, bytes(pixels))


def _write_chunks(output: Path) -> list[dict[str, object]]:
	chunks: list[dict[str, object]] = []
	for index, (chunk_x, chunk_y, seed) in enumerate(((250, 251, 7), (252, 253, 19), (254, 255, 31))):
		payload = _detail_png(seed)
		path = output / "tiles" / "z7" / f"{chunk_x}_{chunk_y}.png"
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_bytes(payload)
		chunks.append({
			"z": 7,
			"chunkX": chunk_x,
			"chunkY": chunk_y,
			"path": path.relative_to(output).as_posix(),
			"checksum": hashlib.sha256(payload).hexdigest(),
			"imageWidth": 64,
			"imageHeight": 64,
			"tiles": index + 1,
		})
	return chunks


class ParallelOverviewTests(unittest.TestCase):
	def test_single_decode_fast_path_matches_canonical_overviews(self) -> None:
		payload = _detail_png(43)
		results = _make_overviews(payload, (OVERVIEW_FACTOR, LOW_OVERVIEW_FACTOR))
		self.assertEqual(results[OVERVIEW_FACTOR], make_overview(payload, OVERVIEW_FACTOR))
		self.assertEqual(results[LOW_OVERVIEW_FACTOR], make_overview(payload, LOW_OVERVIEW_FACTOR))

	def test_parallel_overviews_are_byte_identical_to_sequential(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			sequential = root / "sequential"
			parallel = root / "parallel"
			sequential_chunks = _write_chunks(sequential)
			parallel_chunks = _write_chunks(parallel)

			build_overviews(sequential_chunks, sequential, None, workers=1)
			build_overviews(parallel_chunks, parallel, None, workers=3)

			self.assertEqual(sequential_chunks, parallel_chunks)
			for subdirectory in ("overview", "overview-low"):
				sequential_files = sorted(path.relative_to(sequential).as_posix() for path in (sequential / subdirectory).rglob("*") if path.is_file())
				parallel_files = sorted(path.relative_to(parallel).as_posix() for path in (parallel / subdirectory).rglob("*") if path.is_file())
				self.assertEqual(sequential_files, parallel_files)
				for relative in sequential_files:
					self.assertEqual((sequential / relative).read_bytes(), (parallel / relative).read_bytes(), relative)

	def test_valid_overviews_are_reused_without_rewrite(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory)
			chunks = _write_chunks(output)
			build_overviews(chunks, output, None, workers=2)

			paths = [
				path
				for subdirectory in ("overview", "overview-low")
				for path in (output / subdirectory).rglob("*")
				if path.is_file()
			]
			before = {path: (path.stat().st_mtime_ns, path.read_bytes()) for path in paths}

			reused_chunks = _write_chunks(output)
			build_overviews(reused_chunks, output, None, workers=3)

			self.assertEqual(chunks, reused_chunks)
			after = {path: (path.stat().st_mtime_ns, path.read_bytes()) for path in paths}
			self.assertEqual(before, after)


if __name__ == "__main__":
	unittest.main()
