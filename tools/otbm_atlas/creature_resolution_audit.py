"""Audit every generated Atlas creature spawn for explicit resolution state.

The audit consumes generated ``data/spawns.json`` rather than guessing from
names or rendered pixels. It preserves every unresolved/ambiguous spawn record
with provenance and classifies only statuses produced by the canonical creature
resolution pipeline.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


SPRITE_CLASSIFICATION = {
    "ambiguous-definition": "AMBIGUOUS_CANONICAL_DEFINITION",
    "missing-definition": "MISSING_CANONICAL_DEFINITION",
    "missing-outfit": "INVALID_CANONICAL_DEFINITION",
    "missing-look-type": "INVALID_CANONICAL_DEFINITION",
    "missing-creature-appearance": "MISSING_PINNED_APPEARANCE",
    "missing-sprite": "MISSING_PINNED_SPRITE",
}

ANIMATION_EXPECTED_STATIC = {
    "static-only-appearance",
    "static-only-renderer",
}


def _classification(status: str) -> str:
    return SPRITE_CLASSIFICATION.get(status, "UNRESOLVED_OTHER")


def _record(kind: str, record: dict[str, Any]) -> dict[str, Any]:
    keep = (
        "name",
        "position",
        "center",
        "source",
        "origin",
        "spawn_time",
        "radius",
        "direction",
        "weight",
        "spriteStatus",
        "spriteAnimationStatus",
        "lookType",
        "lookHead",
        "lookBody",
        "lookLegs",
        "lookFeet",
        "lookAddons",
        "outfitSource",
    )
    return {"kind": kind, **{key: record[key] for key in keep if key in record}}


def audit_spawns(spawns: dict[str, Any]) -> dict[str, Any]:
    unresolved: list[dict[str, Any]] = []
    animation_nonresolved: list[dict[str, Any]] = []
    sprite_statuses: Counter[str] = Counter()
    animation_statuses: Counter[str] = Counter()
    totals: Counter[str] = Counter()

    for group, kind in (("npcSpawns", "npc"), ("monsterSpawns", "monster")):
        records = spawns.get(group, [])
        if not isinstance(records, list):
            continue
        for raw in records:
            if not isinstance(raw, dict):
                continue
            totals[kind] += 1
            sprite_status = str(raw.get("spriteStatus", "missing-status"))
            animation_status = str(raw.get("spriteAnimationStatus", "missing-status"))
            sprite_statuses[f"{kind}:{sprite_status}"] += 1
            animation_statuses[f"{kind}:{animation_status}"] += 1
            factual = _record(kind, raw)
            if sprite_status != "resolved":
                unresolved.append(
                    {
                        **factual,
                        "classification": _classification(sprite_status),
                        "evidenceBasis": "generated canonical spriteStatus",
                    }
                )
            if sprite_status == "resolved" and animation_status != "resolved":
                animation_nonresolved.append(
                    {
                        **factual,
                        "classification": "EXPECTED_STATIC_CANONICAL" if animation_status in ANIMATION_EXPECTED_STATIC else "ANIMATION_UNRESOLVED_WITH_STATIC_FALLBACK",
                        "evidenceBasis": "generated canonical spriteAnimationStatus with resolved static sprite",
                    }
                )

    unresolved.sort(key=lambda value: (value["kind"], str(value.get("name", "")).casefold(), json.dumps(value.get("position", {}), sort_keys=True), str(value.get("source", ""))))
    animation_nonresolved.sort(key=lambda value: (value["kind"], str(value.get("name", "")).casefold(), json.dumps(value.get("position", {}), sort_keys=True), str(value.get("source", ""))))
    classifications = Counter(str(value["classification"]) for value in unresolved)
    animation_classifications = Counter(str(value["classification"]) for value in animation_nonresolved)
    return {
        "schemaVersion": 1,
        "statistics": {
            "npcSpawns": totals["npc"],
            "monsterSpawns": totals["monster"],
            "unresolvedSpriteRecords": len(unresolved),
            "nonResolvedAnimationRecordsWithStaticFallback": len(animation_nonresolved),
            "spriteStatusCounts": dict(sorted(sprite_statuses.items())),
            "animationStatusCounts": dict(sorted(animation_statuses.items())),
            "unresolvedClassifications": dict(sorted(classifications.items())),
            "animationClassifications": dict(sorted(animation_classifications.items())),
        },
        "unresolvedSpriteRecords": unresolved,
        "nonResolvedAnimationRecordsWithStaticFallback": animation_nonresolved,
        "policy": {
            "source": "generated data/spawns.json from canonical map/definitions/pinned assets",
            "noGuessing": "classification uses explicit generated status only; no fuzzy-name or pixel inference",
            "staticFallback": "non-resolved animation is separately reported when the canonical static sprite is resolved",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("atlas", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-unresolved", action="store_true")
    args = parser.parse_args()
    spawns_path = args.atlas / "data/spawns.json"
    report = audit_spawns(json.loads(spawns_path.read_text(encoding="utf-8")))
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 1 if args.fail_on_unresolved and report["statistics"]["unresolvedSpriteRecords"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
