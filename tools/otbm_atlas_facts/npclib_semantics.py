"""Prove the shared NPC helper semantics used by statically indexed NPC definitions."""
from __future__ import annotations
from pathlib import Path
import re
from .lua_static import containing_function, strip_comments

TRAVEL_DECL = re.compile(r"\bfunction\s+StdModule\.travel\s*\(")


def verify_npc_system(npc_system_root: Path) -> dict[str, object]:
    modules_path = npc_system_root / "modules.lua"
    bank_path = npc_system_root / "bank_system.lua"
    modules = strip_comments(modules_path.read_text(encoding="utf-8"))
    travel = TRAVEL_DECL.search(modules)
    travel_proven = False
    if travel is not None:
        region = containing_function(modules, travel.start())
        if region is not None:
            body = modules[region.body_start:region.body_end]
            travel_proven = bool(re.search(r"\blocal\s+destination\s*=\s*parameters\.destination\b", body) and re.search(r"\bplayer:teleportTo\s*\(\s*destination\s*\)", body))
    bank = strip_comments(bank_path.read_text(encoding="utf-8"))
    bank_markers = {
        "parseBank": "parseBank" in bank,
        "parseBankMessages": "parseBankMessages" in bank,
        "parseGuildBank": "parseGuildBank" in bank,
    }
    return {
        "schemaVersion": 1,
        "travel": {"status": "RESOLVED" if travel_proven else "UNKNOWN", "teleportsToDestination": travel_proven, "source": "npc_system/modules.lua"},
        "bank": {"status": "RESOLVED" if all(bank_markers.values()) else "UNKNOWN", "markers": bank_markers, "source": "npc_system/bank_system.lua"},
    }
