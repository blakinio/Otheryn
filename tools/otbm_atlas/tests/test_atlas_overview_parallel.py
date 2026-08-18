from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
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


def _derivative_paths(output: Path) -> list[Path]:
	return [
		path
		for subdirectory in ("overview", "overview-low")
		for path in (output / subdirectory).rglob("*")
		if path.is_file()
	]


def _capture_build(chunks: list[dict[str, object]], output: Path, workers: int) -> str:
	stream = StringIO()
	with redirect_stdout(stream):
		build_overviews(chunks, output, None, workers=workers)
	return stream.getvalue()


class ParallelOverviewTests(unittest.TestCase):
	def test_single_decode_fast_path_matches_canonical_overviews(self) -> None:
		payload = _detail_png(43)
		results = _make_overviews(payload, (OVERVIEW_FACTOR, LOW_OVERVIEW_FACTOR))
		self.assertEqual(results[OVERVIEW_FACTOR], make_overview(payload, OVERVIEW_FACTOR))
		self.assertEqual(results[LOW_OVERVIEW_FACTOR], make_overview(payload, LOW_OVERVIEW_FACTOR))

	def test_serial_and_parallel_validation_make_identical_reuse_decisions(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			serial = root / "serial"
			parallel = root / "parallel"
			serial_chunks = _write_chunks(serial)
			parallel_chunks = _write_chunks(parallel)
			_capture_build(serial_chunks, serial, 1)
			_capture_build(parallel_chunks, parallel, 3)

			(serial / "overview" / "z7" / "250_251.png").write_bytes(b"tampered")
			(parallel / "overview" / "z7" / "250_251.png").write_bytes(b"tampered")
			serial_log = _capture_build(_write_chunks(serial), serial, 1)
			parallel_log = _capture_build(_write_chunks(parallel), parallel, 3)

			self.assertIn("Overview reuse: 5 valid, 1 dirty", serial_log)
			self.assertIn("Overview reuse: 5 valid, 1 dirty", parallel_log)
			for relative in sorted(path.relative_to(serial).as_posix() for path in _derivative_paths(serial)):
				self.assertEqual((serial / relative).read_bytes(), (parallel / relative).read_bytes(), relative)

	def test_parallel_overviews_are_byte_identical_to_sequential(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			sequential = root / "sequential"
			parallel = root / "parallel"
			sequential_chunks = _write_chunks(sequential)
			parallel_chunks = _write_chunks(parallel)

			_capture_build(sequential_chunks, sequential, 1)
			_capture_build(parallel_chunks, parallel, 3)

			self.assertEqual(sequential_chunks, parallel_chunks)
			for subdirectory in ("overview", "overview-low"):
				sequential_files = sorted(path.relative_to(sequential).as_posix() for path in (sequential / subdirectory).rglob("*") if path.is_file())
				parallel_files = sorted(path.relative_to(parallel).as_posix() for path in (parallel / subdirectory).rglob("*") if path.is_file())
				self.assertEqual(sequential_files, parallel_files)
				for relative in sequential_files:
					self.assertEqual((sequential / relative).read_bytes(), (parallel / relative).read_bytes(), relative)

	def test_parallel_completion_preserves_chunk_order(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory)
			chunks = _write_chunks(output)
			expected = [(chunk["z"], chunk["chunkX"], chunk["chunkY"]) for chunk in chunks]
			_capture_build(chunks, output, 3)
			self.assertEqual(expected, [(chunk["z"], chunk["chunkX"], chunk["chunkY"]) for chunk in chunks])

	def test_valid_overviews_are_reused_without_rewrite(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory)
			chunks = _write_chunks(output)
			_capture_build(chunks, output, 2)
			paths = _derivative_paths(output)
			before = {path: (path.stat().st_mtime_ns, path.read_bytes()) for path in paths}

			reused_chunks = _write_chunks(output)
			log = _capture_build(reused_chunks, output, 3)

			self.assertEqual(chunks, reused_chunks)
			self.assertIn("Overview reuse: 6 valid, 0 dirty", log)
			after = {path: (path.stat().st_mtime_ns, path.read_bytes()) for path in paths}
			self.assertEqual(before, after)

	def test_tampered_overview_png_is_rejected_and_repaired(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory)
			chunks = _write_chunks(output)
			_capture_build(chunks, output, 2)
			path = output / "overview" / "z7" / "250_251.png"
			original = path.read_bytes()
			path.write_bytes(b"tampered-overview")
			log = _capture_build(_write_chunks(output), output, 3)
			self.assertIn("Overview reuse: 5 valid, 1 dirty", log)
			self.assertEqual(original, path.read_bytes())

	def test_wrong_fingerprint_is_rejected_and_repaired(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory)
			chunks = _write_chunks(output)
			_capture_build(chunks, output, 2)
			report_path = output / "overview" / "z7" / "250_251.json"
			report = json.loads(report_path.read_text(encoding="utf-8"))
			report["fingerprint"] = "0" * 64
			report_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
			log = _capture_build(_write_chunks(output), output, 3)
			self.assertIn("Overview reuse: 5 valid, 1 dirty", log)
			self.assertNotEqual("0" * 64, json.loads(report_path.read_text(encoding="utf-8"))["fingerprint"])

	def test_missing_report_is_rejected_and_repaired(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory)
			_capture_build(_write_chunks(output), output, 2)
			report_path = output / "overview-low" / "z7" / "250_251.json"
			report_path.unlink()
			log = _capture_build(_write_chunks(output), output, 3)
			self.assertIn("Overview reuse: 5 valid, 1 dirty", log)
			self.assertTrue(report_path.is_file())

	def test_missing_png_is_rejected_and_repaired(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory)
			_capture_build(_write_chunks(output), output, 2)
			path = output / "overview-low" / "z7" / "250_251.png"
			path.unlink()
			log = _capture_build(_write_chunks(output), output, 3)
			self.assertIn("Overview reuse: 5 valid, 1 dirty", log)
			self.assertTrue(path.is_file())

	def test_checksum_mismatch_is_rejected_and_repaired(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory)
			_capture_build(_write_chunks(output), output, 2)
			report_path = output / "overview" / "z7" / "250_251.json"
			report = json.loads(report_path.read_text(encoding="utf-8"))
			report["checksum"] = "f" * 64
			report_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
			log = _capture_build(_write_chunks(output), output, 3)
			self.assertIn("Overview reuse: 5 valid, 1 dirty", log)
			fixed = json.loads(report_path.read_text(encoding="utf-8"))
			self.assertEqual(hashlib.sha256((output / "overview" / "z7" / "250_251.png").read_bytes()).hexdigest(), fixed["checksum"])

	def test_progress_reporting_does_not_change_semantics(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			one = root / "one"
			many = root / "many"
			one_chunks = _write_chunks(one)
			many_chunks = _write_chunks(many)
			one_log = _capture_build(one_chunks, one, 1)
			many_log = _capture_build(many_chunks, many, 3)
			self.assertIn("Overview validation: 6 candidates | workers=1", one_log)
			self.assertIn("Overview validation: 6/6", one_log)
			self.assertIn("Overview validation: 6 candidates | workers=3", many_log)
			self.assertIn("Overview validation: 6/6", many_log)
			self.assertEqual(one_chunks, many_chunks)


if __name__ == "__main__":
	unittest.main()
