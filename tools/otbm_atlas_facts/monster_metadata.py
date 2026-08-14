"""Parse monster-definition classification facts without using path names as boss truth."""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import re
from .lua_static import strip_comments

MONSTER_NAME = re.compile(r'Game\.createMonsterType\s*\(\s*["\']([^"\']+)["\']\s*\)')
REWARD_BOSS = re.compile(r"\brewardBoss\s*=\s*(true|false)\b")


def scan_monster_definitions(monster_root: Path, source_root: Path | None = None) -> dict[str, object]:
    source_root = source_root or monster_root.parent
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for path in sorted(monster_root.rglob("*.lua"), key=lambda item: item.relative_to(monster_root).as_posix()):
        text = strip_comments(path.read_text(encoding="utf-8"))
        name_match = MONSTER_NAME.search(text)
        if name_match is None:
            continue
        reward_match = REWARD_BOSS.search(text)
        relative = path.relative_to(source_root).as_posix()
        parts = path.relative_to(monster_root).parts
        groups[name_match.group(1).casefold()].append({
            "name": name_match.group(1),
            "rewardBoss": None if reward_match is None else reward_match.group(1) == "true",
            "source": relative,
            "definitionCategory": parts[0] if len(parts) > 1 else None,
        })
    resolved: dict[str, dict[str, object]] = {}
    for key, candidates in groups.items():
        rewards = {candidate["rewardBoss"] for candidate in candidates}
        if len(rewards) == 1 and None not in rewards:
            status = "RESOLVED"
        elif len(candidates) > 1:
            status = "AMBIGUOUS"
        else:
            status = "UNKNOWN"
        value: dict[str, object] = {"status": status, "name": candidates[0]["name"], "candidates": candidates}
        if status == "RESOLVED":
            value["rewardBoss"] = next(iter(rewards))
            value["verifiedBoss"] = bool(value["rewardBoss"])
        resolved[key] = value
    return {"schemaVersion": 1, "definitions": resolved, "statistics": {
        "names": len(resolved),
        "resolved": sum(value["status"] == "RESOLVED" for value in resolved.values()),
        "ambiguous": sum(value["status"] == "AMBIGUOUS" for value in resolved.values()),
        "unknown": sum(value["status"] == "UNKNOWN" for value in resolved.values()),
        "verifiedBosses": sum(value.get("verifiedBoss") is True for value in resolved.values()),
    }}


def classification_for(name: str, report: dict[str, object]) -> dict[str, object]:
    value = report["definitions"].get(name.casefold())
    return {"status": "UNRESOLVED", "name": name, "candidates": []} if value is None else value
