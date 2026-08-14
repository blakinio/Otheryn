"""Transform pinned CrystalServer factual reports into bounded atlas overlay records."""
from __future__ import annotations

from copy import deepcopy
from typing import Iterable

from tools.otbm_atlas_facts.monster_metadata import classification_for


def _resolution_index(report: dict[str, object]) -> dict[tuple[str, int], dict[str, object]]:
    return {
        (str(entry["kind"]), int(entry["value"])): entry
        for entry in report.get("resolutions", [])
    }


def _mechanic_records(
    mechanics: dict[str, object], resolution_report: dict[str, object]
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
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
                scripted.append(
                    {
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
                    }
                )
    return action_records, unique_records, scripted


def _npc_service_spawns(
    spawns: Iterable[dict[str, object]], npc_report: dict[str, object]
) -> tuple[list[dict[str, object]], dict[str, int]]:
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
        result.append(
            {
                **spawn,
                "serviceStatus": status,
                "services": list(service.get("services", [])),
                "serviceEvidence": deepcopy(service),
                "origin": "base-map+npc-definition",
            }
        )
    return result, stats


def _verified_boss_spawns(
    spawns: Iterable[dict[str, object]], monster_report: dict[str, object]
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for spawn in spawns:
        if spawn.get("origin") != "base-map":
            continue
        classification = classification_for(str(spawn.get("name", "")), monster_report)
        if classification.get("status") != "RESOLVED" or classification.get("verifiedBoss") is not True:
            continue
        result.append(
            {
                **spawn,
                "bossEvidence": classification,
                "evidenceBasis": "explicit-rewardBoss=true",
                "origin": "base-map+monster-definition",
            }
        )
    return result


def _raid_records(
    raid_report: dict[str, object]
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    points = [deepcopy(record) for record in raid_report.get("pointSpawns", [])]
    areas = [deepcopy(record) for record in raid_report.get("areaSpawns", [])]
    verified_points: list[dict[str, object]] = []
    for record in points:
        classification = record.get("monster", {}).get("classification", {})
        if classification.get("status") == "RESOLVED" and classification.get("verifiedBoss") is True:
            verified_points.append(
                {
                    **record,
                    "bossEvidence": classification,
                    "evidenceBasis": "explicit-rewardBoss=true+raid-point",
                }
            )
    for record in areas:
        record["verifiedBossParticipants"] = sorted(
            {
                str(monster.get("name"))
                for monster in record.get("monsters", [])
                if monster.get("classification", {}).get("status") == "RESOLVED"
                and monster.get("classification", {}).get("verifiedBoss") is True
            }
        )
    return points, areas, verified_points


def build_factual_layers(
    mechanics: dict[str, object],
    resolution_report: dict[str, object],
    spawns: dict[str, object],
    npc_report: dict[str, object],
    raid_report: dict[str, object],
    monster_report: dict[str, object],
) -> dict[str, object]:
    """Return renderer-safe records while retaining full uncertain reports separately."""
    action_records, unique_records, scripted = _mechanic_records(mechanics, resolution_report)
    npc_services, npc_stats = _npc_service_spawns(spawns.get("npcSpawns", []), npc_report)
    static_bosses = _verified_boss_spawns(spawns.get("monsterSpawns", []), monster_report)
    raid_points, raid_areas, raid_point_bosses = _raid_records(raid_report)
    verified_bosses = static_bosses + raid_point_bosses
    groups = {
        "scriptedTeleports": scripted,
        "raidPointSpawns": raid_points,
        "raidAreas": raid_areas,
        "npcServices": npc_services,
        "verifiedBossSpawns": verified_bosses,
    }
    return {
        "schemaVersion": 1,
        "groups": groups,
        "actionIds": action_records,
        "uniqueIds": unique_records,
        "statistics": {
            "scriptedTeleports": len(scripted),
            "raidPointSpawns": len(raid_points),
            "raidAreas": len(raid_areas),
            "npcServiceSpawns": len(npc_services),
            "verifiedBossSpawns": len(verified_bosses),
            "npcServiceResolution": npc_stats,
            "mechanicsResolution": resolution_report.get("statistics", {}),
            "dynamicMechanicsUnknown": len(resolution_report.get("dynamicRegistrations", [])),
            "dynamicEventsUnknown": sum(
                event.get("spatialStatus") == "UNKNOWN"
                for event in raid_report.get("dynamicEvents", [])
            ),
        },
        "renderPolicy": {
            "scriptedTeleports": "RESOLVED registration + PROVEN_STATIC transition only",
            "verifiedBossSpawns": "RESOLVED explicit rewardBoss=true only",
            "raidAreas": "exact source bounds; position is derived navigation center only",
            "npcServices": "base-map NPC spawn + RESOLVED/AMBIGUOUS definition only",
            "uncertainFacts": "retained in source reports, never promoted to certain spatial links",
        },
    }
