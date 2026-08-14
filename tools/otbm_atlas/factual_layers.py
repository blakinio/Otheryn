"""Transform pinned CrystalServer factual reports into bounded atlas overlay records."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import json
from pathlib import Path
from typing import Iterable

from tools.otbm_atlas_facts.build import compile_facts
from tools.otbm_atlas_facts.monster_metadata import classification_for

CANONICAL_WORLD_SHA256 = "3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034"
_NEW_KINDS = ("scriptedTeleports", "raidPointSpawns", "raidAreas", "npcServices", "verifiedBossSpawns")


def _resolution_index(report: dict[str, object]) -> dict[tuple[str, int], dict[str, object]]:
    return {(str(entry["kind"]), int(entry["value"])): entry for entry in report.get("resolutions", [])}


def _mechanic_records(mechanics: dict[str, object], resolution_report: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    index = _resolution_index(resolution_report)
    action_records: list[dict[str, object]] = []
    unique_records: list[dict[str, object]] = []
    scripted: list[dict[str, object]] = []
    for records, field, kind, output in (
        (mechanics.get("actionIds", []), "actionId", "ActionID", action_records),
        (mechanics.get("uniqueIds", []), "uniqueId", "UniqueID", unique_records),
    ):
        for occurrence in records:
            value = int(occurrence[field])
            resolution = index.get((kind, value), {"status": "UNRESOLVED", "candidates": []})
            output.append({**occurrence, "mechanics": resolution})
            if resolution.get("status") != "RESOLVED":
                continue
            candidates = resolution.get("candidates", [])
            if len(candidates) != 1:
                continue
            candidate = candidates[0]
            for ordinal, transition in enumerate(candidate.get("transitions", [])):
                if transition.get("proofStatus") != "PROVEN_STATIC" or transition.get("behavior") != "scripted-teleport":
                    continue
                destination = transition.get("destination")
                if not isinstance(destination, dict) or not {"x", "y", "z"} <= set(destination):
                    continue
                short_kind = "AID" if kind == "ActionID" else "UID"
                scripted.append({
                    **occurrence,
                    "name": f"{short_kind} {value}",
                    "mechanicKind": kind,
                    "value": value,
                    "script": candidate.get("script"),
                    "registrationBasis": candidate.get("basis"),
                    "destination": dict(destination),
                    "transitionBasis": transition.get("basis"),
                    "conditional": bool(transition.get("conditional")),
                    "proofStatus": "PROVEN_STATIC",
                    "origin": "scripted-mechanic",
                    "transitionOrdinal": ordinal,
                })
    return action_records, unique_records, scripted


def _npc_service_spawns(spawns: Iterable[dict[str, object]], npc_report: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, int]]:
    result: list[dict[str, object]] = []
    stats = {"resolved": 0, "ambiguous": 0, "unresolved": 0, "supplementalSkipped": 0}
    definitions = npc_report.get("npcs", {})
    for spawn in spawns:
        if spawn.get("origin") != "base-map":
            stats["supplementalSkipped"] += 1
            continue
        service = definitions.get(str(spawn.get("name", "")).casefold())
        if service is None:
            stats["unresolved"] += 1
            continue
        status = str(service.get("status", "UNKNOWN"))
        if status == "RESOLVED":
            stats["resolved"] += 1
        elif status == "AMBIGUOUS":
            stats["ambiguous"] += 1
        else:
            stats["unresolved"] += 1
            continue
        result.append({**spawn, "serviceStatus": status, "services": list(service.get("services", [])), "serviceEvidence": deepcopy(service), "origin": "base-map+npc-definition"})
    return result, stats


def _verified_boss_spawns(spawns: Iterable[dict[str, object]], monster_report: dict[str, object]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for spawn in spawns:
        if spawn.get("origin") != "base-map":
            continue
        classification = classification_for(str(spawn.get("name", "")), monster_report)
        if classification.get("status") != "RESOLVED" or classification.get("verifiedBoss") is not True:
            continue
        result.append({**spawn, "bossEvidence": classification, "evidenceBasis": "explicit-rewardBoss=true", "origin": "base-map+monster-definition"})
    return result


def _raid_records(raid_report: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    points = [deepcopy(record) for record in raid_report.get("pointSpawns", [])]
    areas = [deepcopy(record) for record in raid_report.get("areaSpawns", [])]
    verified_points: list[dict[str, object]] = []
    for record in points:
        classification = record.get("monster", {}).get("classification", {})
        if classification.get("status") == "RESOLVED" and classification.get("verifiedBoss") is True:
            verified_points.append({**record, "bossEvidence": classification, "evidenceBasis": "explicit-rewardBoss=true+raid-point"})
    for record in areas:
        record["verifiedBossParticipants"] = sorted({
            str(monster.get("name"))
            for monster in record.get("monsters", [])
            if monster.get("classification", {}).get("status") == "RESOLVED" and monster.get("classification", {}).get("verifiedBoss") is True
        })
    return points, areas, verified_points


def build_factual_layers(mechanics: dict[str, object], resolution_report: dict[str, object], spawns: dict[str, object], npc_report: dict[str, object], raid_report: dict[str, object], monster_report: dict[str, object]) -> dict[str, object]:
    """Return renderer-safe records while retaining full uncertain reports separately."""
    action_records, unique_records, scripted = _mechanic_records(mechanics, resolution_report)
    npc_services, npc_stats = _npc_service_spawns(spawns.get("npcSpawns", []), npc_report)
    static_bosses = _verified_boss_spawns(spawns.get("monsterSpawns", []), monster_report)
    raid_points, raid_areas, raid_point_bosses = _raid_records(raid_report)
    verified_bosses = static_bosses + raid_point_bosses
    groups = {"scriptedTeleports": scripted, "raidPointSpawns": raid_points, "raidAreas": raid_areas, "npcServices": npc_services, "verifiedBossSpawns": verified_bosses}
    return {
        "schemaVersion": 1,
        "groups": groups,
        "actionIds": action_records,
        "uniqueIds": unique_records,
        "statistics": {
            "scriptedTeleports": len(scripted), "raidPointSpawns": len(raid_points), "raidAreas": len(raid_areas),
            "npcServiceSpawns": len(npc_services), "verifiedBossSpawns": len(verified_bosses), "npcServiceResolution": npc_stats,
            "mechanicsResolution": resolution_report.get("statistics", {}),
            "dynamicMechanicsUnknown": len(resolution_report.get("dynamicRegistrations", [])),
            "dynamicEventsUnknown": sum(event.get("spatialStatus") == "UNKNOWN" for event in raid_report.get("dynamicEvents", [])),
        },
        "renderPolicy": {
            "scriptedTeleports": "RESOLVED registration + PROVEN_STATIC transition only",
            "verifiedBossSpawns": "RESOLVED explicit rewardBoss=true only",
            "raidAreas": "exact source bounds; position is derived navigation center only",
            "npcServices": "base-map NPC spawn + RESOLVED/AMBIGUOUS definition only",
            "uncertainFacts": "retained in source reports, never promoted to certain spatial links",
        },
    }


def _position(record: dict[str, object]) -> dict[str, object] | None:
    value = record.get("position")
    return value if isinstance(value, dict) and {"x", "y", "z"} <= set(value) else None


def _chunk_key(position: dict[str, object], chunk_size: int) -> tuple[int, int, int]:
    return int(position["z"]), int(position["x"]) // chunk_size, int(position["y"]) // chunk_size


def _merge_spatial(output: Path, chunk_size: int, factual: dict[str, object]) -> dict[str, int]:
    by_chunk: dict[tuple[int, int, int], dict[str, list[dict[str, object]]]] = defaultdict(lambda: defaultdict(list))
    for kind, records in factual["groups"].items():
        for record in records:
            position = _position(record)
            if position is not None:
                by_chunk[_chunk_key(position, chunk_size)][kind].append({**record, "kind": kind})
    for kind, records in (("actionIds", factual["actionIds"]), ("uniqueIds", factual["uniqueIds"])):
        for record in records:
            position = _position(record)
            if position is not None:
                by_chunk[_chunk_key(position, chunk_size)][kind].append({**record, "kind": kind})

    root = output / "data" / "chunks"
    for (z, chunk_x, chunk_y), groups in by_chunk.items():
        path = root / f"z{z}" / f"{chunk_x}_{chunk_y}.json"
        content = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"schemaVersion": 1}
        for kind, records in groups.items():
            content[kind] = records
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")

    search_path = output / "data" / "search-index.json"
    search_report = json.loads(search_path.read_text(encoding="utf-8")) if search_path.exists() else {"schemaVersion": 1, "records": []}
    retained = [record for record in search_report.get("records", []) if record.get("kind") not in _NEW_KINDS]
    seen = {(str(record.get("kind")), str(record.get("label", "")).casefold()) for record in retained}
    for kind, records in factual["groups"].items():
        for record in records:
            position = _position(record)
            label = record.get("name") or record.get("actionId") or record.get("uniqueId")
            if position is None or label is None:
                continue
            key = (kind, str(label).casefold())
            if key in seen:
                continue
            seen.add(key)
            retained.append({"kind": kind, "label": str(label), "position": position})
    search_report["records"] = sorted(retained, key=lambda value: (str(value["label"]).casefold(), str(value["kind"])))
    search_path.write_text(json.dumps(search_report, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
    return {"touchedShards": len(by_chunk), "searchRecords": len(search_report["records"])}


def enrich_existing_atlas(output: Path, repository_root: Path = Path("."), force: bool = False) -> dict[str, object]:
    """Enrich a canonical atlas after base spatial sharding, without loading facts in the browser globally."""
    manifest_path = output / "manifest.json"
    mechanics_path = output / "data" / "mechanics.json"
    spawns_path = output / "data" / "spawns.json"
    if not manifest_path.is_file() or not mechanics_path.is_file() or not spawns_path.is_file():
        return {"status": "NOT_APPLICABLE", "reason": "missing-atlas-inputs"}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    map_sha = str(manifest.get("sources", {}).get("mapSha256", ""))
    if not force and map_sha != CANONICAL_WORLD_SHA256:
        return {"status": "NOT_APPLICABLE", "reason": "noncanonical-map", "mapSha256": map_sha}

    crystal_root = repository_root / "vendor/map-analysis/crystalserver"
    source_manifest_path = crystal_root / "supplemental-sources-manifest.json"
    if not source_manifest_path.is_file():
        return {"status": "NOT_APPLICABLE", "reason": "missing-pinned-crystal-sources"}
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    mechanics = json.loads(mechanics_path.read_text(encoding="utf-8"))
    spawns = json.loads(spawns_path.read_text(encoding="utf-8"))
    data_dir = output / "data"
    compile_facts(crystal_root, data_dir, mechanics)
    resolutions = json.loads((data_dir / "mechanics-resolution.json").read_text(encoding="utf-8"))
    npc_report = json.loads((data_dir / "npc-services.json").read_text(encoding="utf-8"))
    raid_report = json.loads((data_dir / "raids-events.json").read_text(encoding="utf-8"))
    monster_report = json.loads((data_dir / "monster-metadata.json").read_text(encoding="utf-8"))
    factual = build_factual_layers(mechanics, resolutions, spawns, npc_report, raid_report, monster_report)
    spatial = _merge_spatial(output, int(manifest.get("chunkSize", 128)), factual)
    report = {
        "schemaVersion": 1,
        "status": "RESOLVED",
        "source": {
            "repository": source_manifest.get("repository"),
            "commit": source_manifest.get("commit"),
            "trees": source_manifest.get("trees"),
            "contentManifestSha256": source_manifest.get("contentManifestSha256"),
        },
        "statistics": factual["statistics"],
        "renderPolicy": factual["renderPolicy"],
        "spatial": spatial,
    }
    (data_dir / "factual-layers.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    statistics_path = data_dir / "statistics.json"
    if statistics_path.is_file():
        statistics = json.loads(statistics_path.read_text(encoding="utf-8"))
        statistics["mechanicsResolution"] = resolutions.get("statistics", {})
        statistics["factualLayers"] = factual["statistics"]
        statistics_path.write_text(json.dumps(statistics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
