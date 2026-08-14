"""Compile deterministic factual indices from the vendored pinned CrystalServer corpus."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from .mechanics import resolve_mechanics
from .monster_metadata import scan_monster_definitions
from .npc_services import parse_npc_services
from .npclib_semantics import verify_npc_system
from .raids import parse_raids


def _write(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def compile_facts(crystal_root: Path, output: Path, mechanics: dict[str, object] | None = None) -> dict[str, object]:
    data_global = crystal_root / "data-global"
    monsters = scan_monster_definitions(data_global / "monster", data_global)
    npc = parse_npc_services(data_global / "npc")
    semantics = verify_npc_system(crystal_root / "data/npclib/npc_system")
    raids = parse_raids(data_global / "raids", monsters, data_global / "scripts/raids")
    _write(output / "monster-metadata.json", monsters)
    _write(output / "npc-services.json", npc)
    _write(output / "npc-system-semantics.json", semantics)
    _write(output / "raids-events.json", raids)
    mechanics_report = None
    if mechanics is not None:
        mechanics_report = resolve_mechanics(mechanics, data_global / "scripts")
        _write(output / "mechanics-resolution.json", mechanics_report)
    summary = {
        "schemaVersion": 1,
        "sources": {
            "monster": "data-global/monster",
            "npc": "data-global/npc",
            "scripts": "data-global/scripts",
            "raids": "data-global/raids",
            "npcSystem": "data/npclib/npc_system",
        },
        "statistics": {
            "monsters": monsters["statistics"],
            "npcServices": npc["statistics"],
            "raidsEvents": raids["statistics"],
            "mechanics": None if mechanics_report is None else mechanics_report["statistics"],
        },
        "semantics": semantics,
    }
    _write(output / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("crystal_root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mechanics", type=Path)
    args = parser.parse_args()
    mechanics = None if args.mechanics is None else json.loads(args.mechanics.read_text(encoding="utf-8"))
    compile_facts(args.crystal_root, args.output, mechanics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
