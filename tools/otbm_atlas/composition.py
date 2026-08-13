"""Classify canonical OTBM additions from repository runtime evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

QUOTED = re.compile(r'''(["'])(.*?)\1''')


def _token(value: str) -> str:
	return "".join(character for character in value.lower() if character.isalnum())


def classify_maps(world_root: Path, repository_root: Path) -> dict[str, object]:
	scripts_root = repository_root / "data-otservbr-global"
	scripts = []
	if scripts_root.exists():
		for path in sorted(scripts_root.rglob("*.lua"), key=lambda value: value.relative_to(repository_root).as_posix()):
			scripts.append((path.relative_to(repository_root).as_posix(), path.read_text(encoding="utf-8").replace("\\", "/")))
	entries = []
	for path in sorted(world_root.rglob("*.otbm"), key=lambda value: value.relative_to(world_root).as_posix()):
		relative = path.relative_to(world_root).as_posix(); stem_path = relative[:-5]
		evidence = []
		if relative == "world.otbm":
			classification = "base-map"; evidence = ["canonical primary map selection"]
		elif relative.startswith("custom/"):
			classification = "conditional-runtime-overlay"
			evidence = ["src/game/game.cpp:Game::loadCustomMaps scans enabled custom/*.otbm files"]
		else:
			parent_fragment = stem_path.rsplit("/", 1)[0] + "/"
			stem = path.stem
			for script_path, text in scripts:
				lower_text = text.lower()
				dynamic_name_evidence = parent_fragment.lower() in lower_text and _token(stem) in {_token(value) for _quote, value in QUOTED.findall(text)}
				if stem_path.lower() in lower_text or dynamic_name_evidence:
					evidence.append(script_path)
			classification = "runtime-loaded-overlay" if evidence else "UNKNOWN"
		entries.append({"source": relative, "classification": classification, "runtimeEvidence": sorted(set(evidence)), "mergedIntoBaseAtlas": False})
	statistics = {key: sum(entry["classification"] == key for entry in entries) for key in sorted({entry["classification"] for entry in entries})}
	return {"schemaVersion": 1, "maps": entries, "statistics": statistics, "policy": "Only world.otbm is rendered as the base atlas; additional maps remain separate even when runtime loading is proven."}


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("world", type=Path); parser.add_argument("repository", type=Path); parser.add_argument("output", type=Path)
	args = parser.parse_args(); report = classify_maps(args.world, args.repository); args.output.parent.mkdir(parents=True, exist_ok=True)
	args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"); return 0


if __name__ == "__main__": raise SystemExit(main())
