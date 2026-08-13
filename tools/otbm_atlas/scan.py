"""CLI and reusable scanner for factual OTBM map records."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

from .semantic import Diagnostic, Item, MapHeader, Tile, Town, Waypoint, iter_map_records, walk_items


def _position(value: Any) -> dict[str, int] | None:
	return asdict(value) if value is not None else None


def _sha256(path: Path) -> str:
	digest = hashlib.sha256()
	with path.open("rb") as handle:
		while block := handle.read(1024 * 1024):
			digest.update(block)
	return digest.hexdigest()


def _item_mechanics(item: Item, tile: Tile, source: str) -> Iterable[tuple[str, dict[str, Any]]]:
	base = {"position": _position(tile.position), "serverId": item.server_id, "source": source}
	if item.action_id is not None:
		yield "actionIds", {**base, "actionId": item.action_id}
	if item.unique_id is not None:
		yield "uniqueIds", {**base, "uniqueId": item.unique_id}
	if item.teleport_destination is not None:
		yield "teleports", {**base, "destination": _position(item.teleport_destination)}
	if item.house_door_id is not None:
		yield "houseDoors", {**base, "doorId": item.house_door_id, "houseId": tile.house_id}


def scan(source: str | Path, *, bounds: tuple[int, int, int, int, int] | None = None) -> dict[str, Any]:
	"""Scan one source and return deterministic JSON-compatible facts."""
	source_path = Path(source)
	started = perf_counter()
	counts: Counter[str] = Counter()
	floors: Counter[int] = Counter()
	server_ids: set[int] = set()
	header: MapHeader | None = None
	towns: list[dict[str, Any]] = []
	waypoints: list[dict[str, Any]] = []
	diagnostics: list[dict[str, Any]] = []
	mechanics: dict[str, list[dict[str, Any]]] = {
		"actionIds": [], "uniqueIds": [], "teleports": [], "houseDoors": []
	}

	for record in iter_map_records(source_path):
		if isinstance(record, MapHeader):
			header = record
			continue
		if isinstance(record, Diagnostic):
			diagnostics.append(asdict(record))
			continue
		if isinstance(record, Town):
			towns.append({"id": record.town_id, "name": record.name, "temple": _position(record.temple)})
			continue
		if isinstance(record, Waypoint):
			waypoints.append({"name": record.name, "position": _position(record.position)})
			continue
		if not isinstance(record, Tile):
			continue
		if bounds is not None:
			x1, x2, y1, y2, z = bounds
			if record.position.z != z or not (x1 <= record.position.x <= x2 and y1 <= record.position.y <= y2):
				continue
		counts["tiles"] += 1
		floors[record.position.z] += 1
		if record.house_id is not None:
			counts["houseTiles"] += 1
		if record.zones:
			counts["zonedTiles"] += 1
		items: list[Item] = []
		if record.ground:
			counts["groundItems"] += 1
			items.append(record.ground)
		descendants = tuple(walk_items(record.items))
		counts["childItems"] += len(descendants)
		items.extend(descendants)
		for item in items:
			server_ids.add(item.server_id)
			for group, fact in _item_mechanics(item, record, source_path.as_posix()):
				mechanics[group].append(fact)

	for values in mechanics.values():
		values.sort(key=lambda value: (
			value["position"]["z"], value["position"]["y"], value["position"]["x"], value["serverId"]
		))
	return {
		"schemaVersion": 1,
		"source": source_path.as_posix(),
		"sourceSha256": _sha256(source_path),
		"header": asdict(header) if header else None,
		"bounds": list(bounds) if bounds else None,
		"statistics": {
			**dict(sorted(counts.items())),
			"populatedFloors": dict(sorted(floors.items())),
			"uniqueServerIds": len(server_ids),
			"diagnostics": len(diagnostics),
			"runtimeSeconds": round(perf_counter() - started, 3),
		},
		"mechanics": mechanics,
		"towns": towns,
		"waypoints": waypoints,
		"diagnostics": diagnostics,
	}


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("source", type=Path)
	parser.add_argument("--bounds", nargs=5, type=int, metavar=("X1", "X2", "Y1", "Y2", "Z"))
	parser.add_argument("--output", type=Path)
	args = parser.parse_args()
	result = scan(args.source, bounds=tuple(args.bounds) if args.bounds else None)
	payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
	if args.output:
		args.output.parent.mkdir(parents=True, exist_ok=True)
		temporary = args.output.with_suffix(args.output.suffix + ".tmp")
		temporary.write_text(payload, encoding="utf-8", newline="\n")
		temporary.replace(args.output)
	else:
		print(payload, end="")
	return 1 if result["diagnostics"] else 0


if __name__ == "__main__":
	raise SystemExit(main())
