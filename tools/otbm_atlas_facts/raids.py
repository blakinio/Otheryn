"""Parse pinned CrystalServer raid/event definitions into factual spatial records."""
from __future__ import annotations
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .lua_static import balanced_region, literal_int, literal_number, literal_position, literal_string, split_arguments, strip_comments, top_level_table_rows
from .monster_metadata import classification_for

SCRIPT_ZONE = re.compile(r'\blocal\s+([A-Za-z_]\w*)\s*=\s*Zone\s*\(\s*["\']([^"\']+)["\']\s*\)')
SCRIPT_RAID = re.compile(r'\blocal\s+([A-Za-z_]\w*)\s*=\s*Raid\s*\(\s*["\']([^"\']+)["\']\s*,\s*\{')
GLOBAL_EVENT = re.compile(r'\bGlobalEvent\s*\(\s*["\']([^"\']+)["\']\s*\)')
CREATE_MONSTER = re.compile(r'\bGame\.createMonster\s*\(\s*["\']([^"\']+)["\']')
CREATE_NPC = re.compile(r'\bGame\.createNpc\s*\(\s*["\']([^"\']+)["\']')


def _int_attr(node: ET.Element, name: str, diagnostics: list[dict[str, object]], source: str, required: bool = True) -> int | None:
    raw = node.attrib.get(name)
    if raw is None:
        if required:
            diagnostics.append({"source": source, "status": "UNKNOWN", "reason": f"missing-{name}"})
        return None
    try:
        return int(raw)
    except ValueError:
        diagnostics.append({"source": source, "status": "UNKNOWN", "reason": f"invalid-{name}", "value": raw})
        return None


def _monster_fact(name: str, amount: int | None, monster_report: dict[str, object] | None) -> dict[str, object]:
    value: dict[str, object] = {"name": name, "amount": amount}
    if monster_report is not None:
        value["classification"] = classification_for(name, monster_report)
    return value


def _raid_xml(path: Path, event: str, raids_root: Path, monster_report: dict[str, object] | None):
    relative = path.relative_to(raids_root.parent.resolve()).as_posix()
    points: list[dict[str, object]] = []
    areas: list[dict[str, object]] = []
    announcements: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        return points, areas, announcements, [{"source": relative, "event": event, "status": "UNKNOWN", "reason": f"xml-error:{exc}"}]
    if root.tag != "raid":
        return points, areas, announcements, [{"source": relative, "event": event, "status": "UNKNOWN", "reason": f"unexpected-root:{root.tag}"}]
    for ordinal, node in enumerate(root):
        if node.tag == "announce":
            announcements.append({"id": f"{event}:announce:{ordinal}", "event": event, "delayMs": _int_attr(node, "delay", diagnostics, relative, False), "type": node.attrib.get("type"), "message": node.attrib.get("message"), "source": relative, "origin": "raid-event"})
        elif node.tag == "singlespawn":
            coordinates = [_int_attr(node, key, diagnostics, relative) for key in ("x", "y", "z")]
            if any(value is None for value in coordinates):
                continue
            name = node.attrib.get("name", "")
            points.append({"id": f"{event}:point:{ordinal}", "event": event, "name": name, "position": {"x": coordinates[0], "y": coordinates[1], "z": coordinates[2]}, "delayMs": _int_attr(node, "delay", diagnostics, relative, False), "monster": _monster_fact(name, 1, monster_report), "source": relative, "origin": "raid-event"})
        elif node.tag == "areaspawn":
            keys = ("fromx", "fromy", "fromz", "tox", "toy", "toz")
            raw = {key: _int_attr(node, key, diagnostics, relative) for key in keys}
            if any(value is None for value in raw.values()):
                continue
            if raw["fromz"] != raw["toz"]:
                diagnostics.append({"source": relative, "event": event, "ordinal": ordinal, "status": "UNKNOWN", "reason": "multi-floor-area", "rawBounds": raw})
                continue
            x1, x2 = sorted((int(raw["fromx"]), int(raw["tox"])))
            y1, y2 = sorted((int(raw["fromy"]), int(raw["toy"])))
            z = int(raw["fromz"])
            monsters = []
            for child in node:
                if child.tag != "monster":
                    diagnostics.append({"source": relative, "event": event, "ordinal": ordinal, "status": "UNKNOWN", "reason": f"unknown-area-child:{child.tag}"})
                    continue
                name = child.attrib.get("name", "")
                monsters.append(_monster_fact(name, _int_attr(child, "amount", diagnostics, relative, False), monster_report))
            areas.append({"id": f"{event}:area:{ordinal}", "event": event, "name": event, "bounds": {"x1": x1, "x2": x2, "y1": y1, "y2": y2, "z": z}, "rawBounds": raw, "position": {"x": (x1 + x2) // 2, "y": (y1 + y2) // 2, "z": z}, "positionRole": "derived-navigation-center", "delayMs": _int_attr(node, "delay", diagnostics, relative, False), "monsters": monsters, "source": relative, "origin": "raid-event"})
        else:
            diagnostics.append({"source": relative, "event": event, "ordinal": ordinal, "status": "UNKNOWN", "reason": f"unknown-tag:{node.tag}"})
    return points, areas, announcements, diagnostics


def _method_calls(text: str, variable: str, method: str):
    pattern = re.compile(rf"\b{re.escape(variable)}\s*:\s*{re.escape(method)}\s*\(")
    cursor = 0
    while True:
        match = pattern.search(text, cursor)
        if match is None:
            return
        body, end = balanced_region(text, match.end() - 1, "(", ")")
        if body is None or end is None:
            return
        yield match.start(), split_arguments(body)
        cursor = end


def _conditions(config: str) -> dict[str, object]:
    result: dict[str, object] = {}
    days = re.search(r"\ballowedDays\s*=\s*\{([^}]*)\}", config, re.DOTALL)
    if days is not None:
        values = [literal_string(part) for part in split_arguments(days.group(1))]
        if all(value is not None for value in values):
            result["allowedDays"] = values
    for key in ("minActivePlayers", "initialChance", "targetChancePerDay", "maxChancePerCheck"):
        match = re.search(rf"\b{key}\s*=\s*([-+]?\d+(?:\.\d+)?)", config)
        if match is not None:
            value = literal_number(match.group(1))
            if value is not None:
                result[key] = value
    return result


def _script_monsters(argument: str, monster_report: dict[str, object] | None) -> list[dict[str, object]]:
    value = argument.strip()
    if not (value.startswith("{") and value.endswith("}")):
        return []
    result = []
    for row in top_level_table_rows(value[1:-1]):
        name_match = re.search(r'\bname\s*=\s*(["\'](?:\\.|[^"\'])*["\'])', row)
        if name_match is None:
            continue
        name = literal_string(name_match.group(1))
        if name is None:
            continue
        amount_match = re.search(r"\bamount\s*=\s*(-?\d+)", row)
        result.append(_monster_fact(name, literal_int(amount_match.group(1)) if amount_match else None, monster_report))
    return result


def _script_events(script_root: Path, monster_report: dict[str, object] | None):
    registry: list[dict[str, object]] = []
    areas: list[dict[str, object]] = []
    dynamic: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for path in sorted(script_root.rglob("*.lua"), key=lambda item: item.relative_to(script_root).as_posix()):
        text = strip_comments(path.read_text(encoding="utf-8"))
        relative = path.relative_to(script_root.parent.parent).as_posix()
        zones: dict[str, dict[str, object]] = {}
        for match in SCRIPT_ZONE.finditer(text):
            variable, zone_name = match.groups()
            zone_areas = []
            for _offset, arguments in _method_calls(text, variable, "addArea"):
                if len(arguments) < 2:
                    continue
                first, second = literal_position(arguments[0]), literal_position(arguments[1])
                if first is None or second is None or first["z"] != second["z"]:
                    continue
                zone_areas.append({"x1": min(first["x"], second["x"]), "x2": max(first["x"], second["x"]), "y1": min(first["y"], second["y"]), "y2": max(first["y"], second["y"]), "z": first["z"]})
            zones[variable] = {"name": zone_name, "areas": zone_areas}
        for raid_match in SCRIPT_RAID.finditer(text):
            variable, event = raid_match.groups()
            config, _end = balanced_region(text, raid_match.end() - 1, "{", "}")
            if config is None:
                diagnostics.append({"source": relative, "event": event, "status": "UNKNOWN", "reason": "unbalanced-raid-config"})
                continue
            zone_match = re.search(r"\bzone\s*=\s*([A-Za-z_]\w*)", config)
            zone = zones.get(zone_match.group(1) if zone_match else "")
            conditions = _conditions(config)
            monsters = []
            for _offset, arguments in _method_calls(text, variable, "addSpawnMonsters"):
                if arguments:
                    monsters.extend(_script_monsters(arguments[0], monster_report))
            registry.append({"name": event, "source": relative, "origin": "script-raid", "conditions": conditions, "zone": None if zone is None else zone["name"], "monsters": monsters})
            if zone is None or not zone["areas"] or not monsters:
                diagnostics.append({"source": relative, "event": event, "status": "UNKNOWN", "reason": "unresolved-script-raid-zone-or-monsters"})
                continue
            for ordinal, bounds in enumerate(zone["areas"]):
                x1, x2, y1, y2, z = (int(bounds[key]) for key in ("x1", "x2", "y1", "y2", "z"))
                areas.append({"id": f"{event}:script-area:{ordinal}", "event": event, "name": event, "bounds": dict(bounds), "position": {"x": (x1 + x2) // 2, "y": (y1 + y2) // 2, "z": z}, "positionRole": "derived-navigation-center", "monsters": monsters, "conditions": conditions, "source": relative, "origin": "script-raid"})
        for event in GLOBAL_EVENT.findall(text):
            dynamic.append({"event": event, "source": relative, "origin": "script-world-event", "status": "PARTIAL_STATIC", "spatialStatus": "UNKNOWN", "literalMonsters": sorted(set(CREATE_MONSTER.findall(text))), "literalNpcs": sorted(set(CREATE_NPC.findall(text)))})
    return registry, areas, dynamic, diagnostics


def parse_raids(raids_root: Path, monster_report: dict[str, object] | None = None, script_raids_root: Path | None = None) -> dict[str, object]:
    registry_path = raids_root / "raids.xml"
    root = ET.parse(registry_path).getroot()
    if root.tag != "raids":
        raise ValueError(f"{registry_path}: expected <raids>")
    diagnostics: list[dict[str, object]] = []
    registry: list[dict[str, object]] = []
    points: list[dict[str, object]] = []
    areas: list[dict[str, object]] = []
    announcements: list[dict[str, object]] = []
    for ordinal, node in enumerate(root):
        if node.tag != "raid":
            diagnostics.append({"source": registry_path.relative_to(raids_root.parent).as_posix(), "ordinal": ordinal, "status": "UNKNOWN", "reason": f"unknown-registry-tag:{node.tag}"})
            continue
        name, relative_file = node.attrib.get("name", ""), node.attrib.get("file")
        entry = {"name": name, "file": relative_file, "intervalMinutes": _int_attr(node, "interval2", diagnostics, registry_path.as_posix(), False), "marginMinutes": _int_attr(node, "margin", diagnostics, registry_path.as_posix(), False), "attributes": dict(sorted(node.attrib.items())), "source": registry_path.relative_to(raids_root.parent).as_posix(), "origin": "raid-event"}
        registry.append(entry)
        if not relative_file:
            diagnostics.append({"source": entry["source"], "event": name, "status": "UNKNOWN", "reason": "missing-file"})
            continue
        path = (raids_root / relative_file).resolve()
        try:
            path.relative_to(raids_root.resolve())
        except ValueError:
            diagnostics.append({"source": entry["source"], "event": name, "status": "UNKNOWN", "reason": "file-outside-raids-root"})
            continue
        if not path.is_file():
            diagnostics.append({"source": entry["source"], "event": name, "status": "UNKNOWN", "reason": f"missing-file:{relative_file}"})
            continue
        p, a, n, d = _raid_xml(path, name, raids_root, monster_report)
        points.extend(p); areas.extend(a); announcements.extend(n); diagnostics.extend(d)
    script_registry: list[dict[str, object]] = []
    dynamic_events: list[dict[str, object]] = []
    if script_raids_root is not None and script_raids_root.is_dir():
        script_registry, script_areas, dynamic_events, findings = _script_events(script_raids_root, monster_report)
        areas.extend(script_areas); diagnostics.extend(findings)
    return {"schemaVersion": 1, "registry": registry, "scriptRegistry": script_registry, "dynamicEvents": dynamic_events, "announcements": announcements, "pointSpawns": points, "areaSpawns": areas, "diagnostics": diagnostics, "statistics": {
        "raids": len(registry), "scriptRaids": len(script_registry), "dynamicEvents": len(dynamic_events), "announcements": len(announcements), "pointSpawns": len(points), "areaSpawns": len(areas),
        "verifiedPointBossSpawns": sum(record.get("monster", {}).get("classification", {}).get("verifiedBoss") is True for record in points),
        "verifiedAreaBossParticipants": sum(monster.get("classification", {}).get("verifiedBoss") is True for record in areas for monster in record.get("monsters", [])),
        "diagnostics": len(diagnostics),
    }}
