"""Verify a generated atlas without trusting its manifest or chunk reports."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
from typing import Any

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
REQUIRED_DATA = ("mechanics.json", "mechanics-resolution.json", "spawns.json", "composition.json", "unknown-items.json", "houses.json", "statistics.json")


def _sha256(path: Path) -> str:
	digest = hashlib.sha256()
	with path.open("rb") as handle:
		while block := handle.read(1024 * 1024): digest.update(block)
	return digest.hexdigest()


def _png_dimensions(path: Path) -> tuple[int, int]:
	with path.open("rb") as handle: header = handle.read(24)
	if len(header) != 24 or header[:8] != PNG_MAGIC or header[12:16] != b"IHDR": raise ValueError(f"{path}: invalid PNG header")
	return struct.unpack(">II", header[16:24])


def verify_atlas(root: Path) -> dict[str, Any]:
	errors: list[str] = []
	manifest_path = root / "manifest.json"
	if not manifest_path.is_file(): return {"ok": False, "errors": ["missing manifest.json"]}
	manifest = json.loads(manifest_path.read_text(encoding="utf-8")); chunks = manifest.get("chunks", [])
	floors: Counter[int] = Counter(); missing_appearances: Counter[int] = Counter(); missing_sprites: Counter[int] = Counter()
	statistics = Counter(); seen_paths: set[str] = set()
	for index, chunk in enumerate(chunks):
		label = f"chunk[{index}]"
		try:
			relative = str(chunk["path"]); path = root / relative
			if relative in seen_paths: errors.append(f"{label}: duplicate path {relative}")
			seen_paths.add(relative); floors[int(chunk["z"])] += 1
			if not path.is_file(): errors.append(f"{label}: missing {relative}"); continue
			if _sha256(path) != chunk["checksum"]: errors.append(f"{label}: checksum mismatch {relative}")
			if _png_dimensions(path) != (int(chunk["imageWidth"]), int(chunk["imageHeight"])): errors.append(f"{label}: PNG dimensions mismatch {relative}")
			for key in ("tiles", "groundItems", "childItems", "renderOperations"): statistics[key] += int(chunk[key])
			missing_appearances.update({int(key): int(value) for key, value in chunk["missingAppearances"].items()})
			missing_sprites.update({int(key): int(value) for key, value in chunk["missingSprites"].items()})
		except (KeyError, TypeError, ValueError, OSError) as error: errors.append(f"{label}: {error}")
	expected_pngs = {path.relative_to(root).as_posix() for path in (root / "tiles").glob("z*/*.png")}
	if expected_pngs != seen_paths: errors.append(f"tile file set differs from manifest: disk={len(expected_pngs)} manifest={len(seen_paths)}")
	for relative in ("index.html", *[f"data/{name}" for name in REQUIRED_DATA]):
		if not (root / relative).is_file(): errors.append(f"missing {relative}")
	return {
		"ok": not errors, "errors": errors, "chunks": len(chunks), "floors": dict(sorted(floors.items())),
		"statistics": dict(statistics), "missingAppearances": dict(sorted(missing_appearances.items())), "missingSprites": dict(sorted(missing_sprites.items())),
	}


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("atlas", type=Path); parser.add_argument("--output", type=Path)
	args = parser.parse_args(); report = verify_atlas(args.atlas); payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
	if args.output: args.output.write_text(payload, encoding="utf-8")
	else: print(payload, end="")
	return 0 if report["ok"] else 1


if __name__ == "__main__": raise SystemExit(main())
