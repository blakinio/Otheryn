"""Resolve factual map AID/UID values to pinned Lua scripts and proven static destinations."""
from __future__ import annotations
from collections import defaultdict
import json
from pathlib import Path
import re
from typing import Iterable

from .lua_static import containing_function, literal_position, named_tables, numeric_table_entries, strip_comments

REGISTRATION = re.compile(r":(?P<kind>aid|uid)\s*\((?P<arguments>[^)]*)\)")
INTEGER = re.compile(r"(?<![\w.])\d+(?![\w.])")
PAIR_LOOP = re.compile(r"\bfor\s+(?P<key>[A-Za-z_]\w*)(?:\s*,\s*[A-Za-z_]\w*)?\s+in\s+pairs\s*\(\s*(?P<table>[A-Za-z_]\w*)\s*\)\s+do")
POSITION_FIELD = re.compile(r"\b([A-Za-z_]\w*)\s*=\s*Position\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")
SELECTOR = re.compile(r"(?:local\s+)?(?P<variable>[A-Za-z_]\w*)\s*=\s*(?P<table>[A-Za-z_]\w*)\s*\[\s*item\.(?P<selector>actionid|uid)\s*\]")


def _table_positions(value: str) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    direct = literal_position(value.strip())
    if direct is not None:
        result["__direct__"] = direct
    for match in POSITION_FIELD.finditer(value):
        result[match.group(1)] = {"x": int(match.group(2)), "y": int(match.group(3)), "z": int(match.group(4))}
    return result


def _simple_pair_registrations(text: str, tables: dict[str, dict[int, str]]) -> list[tuple[str, str, set[int], str]]:
    result = []
    for loop in PAIR_LOOP.finditer(text):
        key, table = loop.group("key"), loop.group("table")
        if table not in tables:
            continue
        terminator = re.search(r"\bend\b", text[loop.end():])
        if terminator is None:
            continue
        body = text[loop.end():loop.end() + terminator.start()]
        match = re.search(rf":(?P<kind>aid|uid)\s*\(\s*{re.escape(key)}\s*\)", body)
        if match is not None:
            result.append((match.group("kind"), table, set(tables[table]), key))
    return result


def _static_transitions(text: str, tables: dict[str, dict[int, str]]) -> dict[tuple[str, int], list[dict[str, object]]]:
    result: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    positions = {name: {key: _table_positions(value) for key, value in entries.items()} for name, entries in tables.items()}
    for selector in SELECTOR.finditer(text):
        variable, table = selector.group("variable"), selector.group("table")
        kind = "aid" if selector.group("selector") == "actionid" else "uid"
        entries = positions.get(table)
        region = containing_function(text, selector.start())
        if not entries or region is None:
            continue
        suffix = text[selector.end():region.body_end]
        direct_use = re.search(rf":teleportTo\s*\(\s*{re.escape(variable)}\s*\)", suffix)
        local_fields = {match.group(1): match.group(2) for match in re.finditer(rf"(?:local\s+)?([A-Za-z_]\w*)\s*=\s*{re.escape(variable)}\.([A-Za-z_]\w*)", suffix)}
        used_fields = {match.group(1) for match in re.finditer(rf":teleportTo\s*\(\s*{re.escape(variable)}\.([A-Za-z_]\w*)\s*\)", suffix)}
        for local_name, field in local_fields.items():
            if re.search(rf":teleportTo\s*\(\s*{re.escape(local_name)}\s*\)", suffix):
                used_fields.add(field)
        for key, fields in entries.items():
            destinations: list[tuple[str, dict[str, int]]] = []
            if direct_use is not None and "__direct__" in fields:
                destinations.append(("direct-table-position", fields["__direct__"]))
            destinations.extend((f"table-field:{field}", fields[field]) for field in sorted(used_fields) if field in fields)
            unique = {(value["x"], value["y"], value["z"]): (basis, value) for basis, value in destinations}
            for basis, destination in unique.values():
                result[(kind, key)].append({"destination": destination, "basis": basis, "behavior": "scripted-teleport", "conditional": True, "proofStatus": "PROVEN_STATIC"})
    return result


def index_scripts(scripts_root: Path) -> dict[str, object]:
    registrations: dict[str, dict[int, list[dict[str, object]]]] = {"aid": defaultdict(list), "uid": defaultdict(list)}
    dynamic: list[dict[str, object]] = []
    for path in sorted(scripts_root.rglob("*.lua"), key=lambda value: value.relative_to(scripts_root).as_posix()):
        relative = path.relative_to(scripts_root).as_posix()
        text = strip_comments(path.read_text(encoding="utf-8"))
        table_values = {name: numeric_table_entries(body) for name, body in named_tables(text).items()}
        loop_regs = _simple_pair_registrations(text, table_values)
        loop_expressions = {(kind, key) for kind, _table, _values, key in loop_regs}
        transitions = _static_transitions(text, table_values)
        for kind, table, values, _key in loop_regs:
            for value in sorted(values):
                candidate: dict[str, object] = {"script": relative, "basis": f"numeric-table-key-loop:{table}"}
                if transitions.get((kind, value)):
                    candidate["transitions"] = transitions[(kind, value)]
                registrations[kind][value].append(candidate)
        for match in REGISTRATION.finditer(text):
            kind, arguments = match.group("kind"), match.group("arguments")
            if re.fullmatch(r"\s*\d+(?:\s*,\s*\d+)*\s*", arguments):
                for value in map(int, INTEGER.findall(arguments)):
                    candidate = {"script": relative, "basis": "literal-registration"}
                    if transitions.get((kind, value)):
                        candidate["transitions"] = transitions[(kind, value)]
                    registrations[kind][value].append(candidate)
            elif (kind, arguments.strip()) not in loop_expressions:
                dynamic.append({"script": relative, "kind": kind, "expression": arguments.strip(), "status": "UNKNOWN"})
    for values in registrations.values():
        for value, candidates in values.items():
            by_script: dict[str, dict[str, object]] = {}
            for candidate in candidates:
                script = str(candidate["script"])
                existing = by_script.get(script)
                if existing is None:
                    by_script[script] = candidate
                    continue
                existing["basis"] = "+".join(sorted(set(str(existing["basis"]).split("+") + str(candidate["basis"]).split("+"))))
                transitions = list(existing.get("transitions", [])) + list(candidate.get("transitions", []))
                if transitions:
                    dedup = {(item["destination"]["x"], item["destination"]["y"], item["destination"]["z"], item["basis"]): item for item in transitions}
                    existing["transitions"] = list(dedup.values())
            values[value] = sorted(by_script.values(), key=lambda item: str(item["script"]))
    return {"registrations": registrations, "dynamicRegistrations": sorted(dynamic, key=lambda item: (str(item["script"]), str(item["kind"]), str(item["expression"])))}


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
    resolutions = resolve_values((entry["actionId"] for entry in mechanics.get("actionIds", [])), "aid", index)
    resolutions += resolve_values((entry["uniqueId"] for entry in mechanics.get("uniqueIds", [])), "uid", index)
    statistics = {status: sum(entry["status"] == status for entry in resolutions) for status in ("RESOLVED", "AMBIGUOUS", "UNRESOLVED")}
    statistics["provenStaticTransitions"] = sum(len(candidate.get("transitions", [])) for entry in resolutions if entry["status"] == "RESOLVED" for candidate in entry["candidates"])
    return {"schemaVersion": 2, "resolutions": resolutions, "dynamicRegistrations": index["dynamicRegistrations"], "statistics": statistics}


def write_report(mechanics: dict[str, object], scripts_root: Path, output: Path) -> dict[str, object]:
    report = resolve_mechanics(mechanics, scripts_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
