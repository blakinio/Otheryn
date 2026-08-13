"""Parse canonical Canary/CrystalServer monster and NPC spawn XML files."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Spawn:
	kind: str
	name: str
	position: dict[str, int]
	center: dict[str, int]
	spawn_time: int
	radius: int
	direction: int | None
	weight: int | None
	source: str
	origin: str


def _origin(path: Path, world_root: Path) -> str:
	relative = path.relative_to(world_root).as_posix()
	if "/" not in relative: return "base-map"
	if relative.startswith("custom/"): return "conditional-custom-map"
	if relative.startswith("world_changes/"): return "runtime-world-change"
	if relative.startswith("annual_events/"): return "annual-event-map"
	if relative.startswith("quest/"): return "quest-map"
	return "UNKNOWN"


def parse_spawn_file(path: Path, world_root: Path, kind: str) -> list[Spawn]:
	root = ET.parse(path).getroot()
	expected_root = "monsters" if kind == "monster" else "npcs"
	if root.tag != expected_root: raise ValueError(f"{path}: expected <{expected_root}>, got <{root.tag}>")
	result: list[Spawn] = []
	for group in root:
		if group.tag != kind: raise ValueError(f"{path}: unknown group <{group.tag}>")
		center_keys = {"centerx", "centery", "centerz", "radius"}
		unknown = set(group.attrib) - center_keys
		if unknown: raise ValueError(f"{path}: unknown {kind} group attributes {sorted(unknown)}")
		if not center_keys <= set(group.attrib): raise ValueError(f"{path}: incomplete {kind} group")
		cx, cy, cz, radius = (int(group.attrib[key]) for key in ("centerx", "centery", "centerz", "radius"))
		for entry in group:
			if entry.tag != kind: raise ValueError(f"{path}: unknown spawn <{entry.tag}>")
			allowed = {"name", "x", "y", "z", "spawntime", "direction", "weight"}
			unknown = set(entry.attrib) - allowed
			if unknown: raise ValueError(f"{path}: unknown {kind} attributes {sorted(unknown)}")
			required = {"name", "x", "y", "z", "spawntime"}
			if not required <= set(entry.attrib): raise ValueError(f"{path}: incomplete {kind} spawn")
			# Canary spawn XML stores X/Y relative to the group center, while Z is absolute.
			position = {"x": cx + int(entry.attrib["x"]), "y": cy + int(entry.attrib["y"]), "z": int(entry.attrib["z"])}
			result.append(Spawn(
				kind=kind, name=entry.attrib["name"], position=position,
				center={"x": cx, "y": cy, "z": cz}, spawn_time=int(entry.attrib["spawntime"]), radius=radius,
				direction=int(entry.attrib["direction"]) if "direction" in entry.attrib else None,
				weight=int(entry.attrib["weight"]) if "weight" in entry.attrib else None,
				source=path.relative_to(world_root).as_posix(), origin=_origin(path, world_root),
			))
	return result


def scan_spawns(world_root: Path) -> dict[str, object]:
	groups: dict[str, list[dict[str, object]]] = {"monsterSpawns": [], "npcSpawns": []}
	files: list[dict[str, object]] = []
	for kind, key in (("monster", "monsterSpawns"), ("npc", "npcSpawns")):
		for path in sorted(world_root.rglob(f"*-{kind}.xml"), key=lambda value: value.relative_to(world_root).as_posix()):
			entries = parse_spawn_file(path, world_root, kind)
			groups[key].extend(asdict(entry) for entry in entries)
			files.append({"source": path.relative_to(world_root).as_posix(), "kind": kind, "origin": _origin(path, world_root), "spawns": len(entries)})
	return {"schemaVersion": 1, **groups, "sources": files, "statistics": {"monsterSpawns": len(groups["monsterSpawns"]), "npcSpawns": len(groups["npcSpawns"]), "files": len(files)}}


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("world", type=Path); parser.add_argument("output", type=Path)
	args = parser.parse_args(); report = scan_spawns(args.world); args.output.parent.mkdir(parents=True, exist_ok=True)
	args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"); return 0


if __name__ == "__main__": raise SystemExit(main())
