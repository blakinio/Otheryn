"""Extract factual NPC service metadata from pinned CrystalServer definitions without executing Lua."""
from __future__ import annotations
from collections import defaultdict
import json
from pathlib import Path
import re
from .lua_static import assigned_table, function_regions, iter_calls, literal_int, literal_position, literal_string, strip_comments, top_level_table_rows

NPC_NAME = re.compile(r'local\s+internalNpcName\s*=\s*["\']([^"\']+)["\']')
SIMPLE_FIELD = re.compile(r"\b([A-Za-z_]\w*)\s*=\s*(\"(?:\\.|[^\"])*\"|'(?:\\.|[^'])*'|-?\d+|true|false)")
HELPER_DECL = re.compile(r"\blocal\s+function\s+([A-Za-z_]\w*)\s*\(([^)]*)\)")
BANK_MARKERS = {"bank": ("parseBank(", "parseBankMessages(", "NpcBankGreetCallback"), "guildBank": ("parseGuildBank(",)}


def _simple_fields(row: str) -> dict[str, object]:
    result: dict[str, object] = {}
    for match in SIMPLE_FIELD.finditer(row):
        key, raw = match.groups()
        if raw in ("true", "false"):
            result[key] = raw == "true"
        elif raw.startswith(("'", '"')):
            result[key] = raw[1:-1]
        else:
            result[key] = int(raw)
    return result


def _shop(text: str):
    body = assigned_table(text, "npcConfig.shop")
    if body is None:
        return False, [], []
    items, diagnostics = [], []
    for ordinal, row in enumerate(top_level_table_rows(body)):
        fields = _simple_fields(row)
        if fields:
            items.append(fields)
        else:
            diagnostics.append({"kind": "shop", "ordinal": ordinal, "status": "UNKNOWN", "reason": "nonliteral-row"})
    return True, items, diagnostics


def _travel_helpers(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    if "StdModule.travel" not in text:
        return result
    regions = {region.start: region for region in function_regions(text)}
    for match in HELPER_DECL.finditer(text):
        name = match.group(1)
        parameters = [value.strip() for value in match.group(2).split(",")]
        function_offset = text.find("function", match.start(), match.end())
        region = regions.get(function_offset)
        if region is None:
            continue
        body = text[region.body_start:region.body_end]
        if (
            "destination" in parameters
            and "StdModule.travel" in body
            and re.search(r"\bdestination\s*=\s*destination\b", body)
        ):
            result[name] = parameters
    return result


def _travel_routes(text: str):
    helpers = _travel_helpers(text)
    routes: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for helper, parameters in helpers.items():
        for offset, arguments in iter_calls(text, helper):
            if not arguments or literal_string(arguments[0]) is None:
                continue
            keyword = literal_string(arguments[0])
            cost = literal_int(arguments[1]) if len(arguments) > 1 else None
            destination = literal_position(arguments[2]) if len(arguments) > 2 else None
            if keyword is None or destination is None:
                diagnostics.append({"kind": "travel", "helper": helper, "offset": offset, "status": "UNKNOWN", "reason": "nonliteral-route"})
                continue
            by_name = {parameters[index]: arguments[index] for index in range(min(len(parameters), len(arguments)))}
            condition = by_name.get("condition")
            routes.append({"keyword": keyword, "cost": cost, "destination": destination, "conditional": condition is not None and condition.strip() != "nil", "basis": f"local-helper:{helper}->StdModule.travel", "proofStatus": "PROVEN_STATIC"})
    return bool(routes) or "StdModule.travel" in text, routes, diagnostics


def _definition(path: Path, npc_root: Path) -> dict[str, object] | None:
    text = strip_comments(path.read_text(encoding="utf-8"))
    name_match = NPC_NAME.search(text)
    if name_match is None:
        return None
    has_shop, shop_items, shop_diagnostics = _shop(text)
    has_travel, routes, travel_diagnostics = _travel_routes(text)
    services: list[str] = []
    if has_shop:
        services.append("shop")
    for service, markers in BANK_MARKERS.items():
        if any(marker in text for marker in markers):
            services.append(service)
    if has_travel:
        services.append("travel")
    return {"name": name_match.group(1), "source": path.relative_to(npc_root.parent).as_posix(), "services": sorted(set(services)), "shop": {"items": shop_items} if has_shop else None, "travel": {"routes": routes} if has_travel else None, "diagnostics": shop_diagnostics + travel_diagnostics}


def parse_npc_services(npc_root: Path) -> dict[str, object]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for path in sorted(npc_root.rglob("*.lua"), key=lambda item: item.relative_to(npc_root).as_posix()):
        definition = _definition(path, npc_root)
        if definition is not None:
            groups[str(definition["name"]).casefold()].append(definition)
    records: dict[str, dict[str, object]] = {}
    for key, candidates in groups.items():
        def signature(candidate: dict[str, object]) -> str:
            return json.dumps({"services": candidate["services"], "shop": candidate["shop"], "travel": candidate["travel"]}, sort_keys=True, separators=(",", ":"))
        if len({signature(candidate) for candidate in candidates}) == 1:
            canonical = candidates[0]
            records[key] = {"name": canonical["name"], "status": "RESOLVED", "services": canonical["services"], "shop": canonical["shop"], "travel": canonical["travel"], "sources": sorted(candidate["source"] for candidate in candidates), "diagnostics": [finding for candidate in candidates for finding in candidate["diagnostics"]]}
        else:
            records[key] = {"name": candidates[0]["name"], "status": "AMBIGUOUS", "services": [], "shop": None, "travel": None, "candidates": candidates}
    return {"schemaVersion": 1, "npcs": records, "statistics": {
        "names": len(records),
        "resolved": sum(record["status"] == "RESOLVED" for record in records.values()),
        "ambiguous": sum(record["status"] == "AMBIGUOUS" for record in records.values()),
        "shops": sum("shop" in record.get("services", []) for record in records.values()),
        "banks": sum("bank" in record.get("services", []) for record in records.values()),
        "guildBanks": sum("guildBank" in record.get("services", []) for record in records.values()),
        "travel": sum("travel" in record.get("services", []) for record in records.values()),
        "travelRoutes": sum(len((record.get("travel") or {}).get("routes", [])) for record in records.values()),
    }}


def enrich_npc_service_spawns(records: list[dict[str, object]], report: dict[str, object]) -> dict[str, int]:
    statistics = {"resolved": 0, "ambiguous": 0, "unresolved": 0}
    for record in records:
        service = report["npcs"].get(str(record["name"]).casefold())
        if service is None:
            record["serviceResolution"] = {"status": "UNRESOLVED", "services": []}
            statistics["unresolved"] += 1
        else:
            record["serviceResolution"] = service
            statistics["resolved" if service["status"] == "RESOLVED" else "ambiguous"] += 1
    return statistics
