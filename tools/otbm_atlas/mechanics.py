"""Conservatively resolve factual map AID/UID values to Lua scripts."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
from typing import Iterable

REGISTRATION = re.compile(r":(?P<kind>aid|uid)\s*\((?P<arguments>[^)]*)\)")
INTEGER = re.compile(r"(?<![\w.])\d+(?![\w.])")
TABLE_KEY = re.compile(r"\[\s*(\d+)\s*\]\s*=")
UID_DISPATCH = re.compile(r"\[[^\]\n]*(?:\.uid|getUniqueId\s*\()[^\]\n]*\]")


def _without_line_comments(text: str) -> str:
	return "\n".join(line.split("--", 1)[0] for line in text.splitlines())


def index_scripts(scripts_root: Path) -> dict[str, object]:
	registrations: dict[str, dict[int, list[dict[str, object]]]] = {"aid": defaultdict(list), "uid": defaultdict(list)}
	dynamic: list[dict[str, object]] = []
	for path in sorted(scripts_root.rglob("*.lua"), key=lambda value: value.relative_to(scripts_root).as_posix()):
		relative = path.relative_to(scripts_root).as_posix(); text = _without_line_comments(path.read_text(encoding="utf-8"))
		for match in REGISTRATION.finditer(text):
			arguments = match.group("arguments")
			if re.fullmatch(r"\s*\d+(?:\s*,\s*\d+)*\s*", arguments):
				for value in map(int, INTEGER.findall(arguments)):
					registrations[match.group("kind")][value].append({"script": relative, "basis": "literal-registration"})
			else:
				dynamic.append({"script": relative, "kind": match.group("kind"), "expression": arguments.strip(), "status": "UNKNOWN"})
		# Some legacy Action scripts register a shared AID, then dispatch on item.uid.
		if UID_DISPATCH.search(text):
			for value in map(int, TABLE_KEY.findall(text)):
				registrations["uid"][value].append({"script": relative, "basis": "literal-uid-dispatch-key"})
	for kind in registrations:
		for value in registrations[kind]:
			registrations[kind][value] = sorted(registrations[kind][value], key=lambda item: (str(item["script"]), str(item["basis"])))
	return {"registrations": registrations, "dynamicRegistrations": dynamic}


def resolve_values(values: Iterable[int], kind: str, index: dict[str, object]) -> list[dict[str, object]]:
	registry = index["registrations"][kind]
	result = []
	for value in sorted(set(values)):
		candidates = registry.get(value, [])
		status = "RESOLVED" if len(candidates) == 1 else "AMBIGUOUS" if candidates else "UNRESOLVED"
		result.append({"kind": "ActionID" if kind == "aid" else "UniqueID", "value": value, "status": status, "candidates": candidates})
	return result


def resolve_mechanics(mechanics: dict[str, object], scripts_root: Path) -> dict[str, object]:
	index = index_scripts(scripts_root)
	aids = (entry["actionId"] for entry in mechanics.get("actionIds", []))
	uids = (entry["uniqueId"] for entry in mechanics.get("uniqueIds", []))
	resolutions = resolve_values(aids, "aid", index) + resolve_values(uids, "uid", index)
	statistics = {status: sum(entry["status"] == status for entry in resolutions) for status in ("RESOLVED", "AMBIGUOUS", "UNRESOLVED")}
	return {"schemaVersion": 1, "resolutions": resolutions, "dynamicRegistrations": index["dynamicRegistrations"], "statistics": statistics}


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("mechanics", type=Path); parser.add_argument("scripts", type=Path); parser.add_argument("output", type=Path)
	args = parser.parse_args(); mechanics = json.loads(args.mechanics.read_text(encoding="utf-8")); report = resolve_mechanics(mechanics, args.scripts)
	args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"); return 0


if __name__ == "__main__": raise SystemExit(main())
