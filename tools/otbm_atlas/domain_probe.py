"""Run only non-render Atlas validation domains selected by an impact plan."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from .houses import parse_houses
from .mechanics import index_scripts
from .monster_sprites import parse_monster_definition_index
from .npc_sprites import parse_npc_definition_index
from .spawns import scan_spawns

CRYSTAL_ROOT = Path("vendor/map-analysis/crystalserver/data-global")
WORLD_ROOT = CRYSTAL_ROOT / "world"
NPC_ROOT = CRYSTAL_ROOT / "npc"
MONSTER_ROOT = CRYSTAL_ROOT / "monster"
SCRIPTS_ROOT = CRYSTAL_ROOT / "scripts"


def _definition_stats(index: object) -> dict[str, int]:
    return {
        "resolved": len(index.resolved),
        "ambiguous": len(index.ambiguous),
        "invalid": len(index.invalid),
        "aliases": len(index.aliases),
    }


def run_domain_probe(plan: Mapping[str, object], repository_root: Path) -> dict[str, object]:
    classification = plan.get("classification", {})
    domains = set(classification.get("domains", [])) if isinstance(classification, Mapping) else set()
    root = repository_root.resolve()
    report: dict[str, object] = {"schemaVersion": 1, "domains": sorted(domains), "validated": {}}
    validated = report["validated"]
    assert isinstance(validated, dict)

    if "spawns" in domains:
        spawns = scan_spawns(root / WORLD_ROOT)
        validated["spawns"] = spawns["statistics"]
    if "houses" in domains:
        houses = parse_houses(root / WORLD_ROOT / "world-house.xml")
        validated["houses"] = houses["statistics"]
    if "npcDefinitions" in domains:
        validated["npcDefinitions"] = _definition_stats(parse_npc_definition_index(root / NPC_ROOT, root / CRYSTAL_ROOT))
    if "monsterDefinitions" in domains:
        validated["monsterDefinitions"] = _definition_stats(parse_monster_definition_index(root / MONSTER_ROOT, root / CRYSTAL_ROOT))
    if "mechanics" in domains:
        scripts = index_scripts(root / SCRIPTS_ROOT)
        registrations = scripts["registrations"]
        validated["mechanics"] = {
            "aidValues": len(registrations["aid"]),
            "uidValues": len(registrations["uid"]),
            "dynamicRegistrations": len(scripts["dynamicRegistrations"]),
        }
    if "factualData" in domains:
        # Factual extraction has its own targeted GitHub-hosted workflow. This
        # probe records the delegation instead of rebuilding unrelated map data.
        validated["factualData"] = {"delegatedWorkflow": "OTBM Atlas Factual Layers"}
    if "frontend" in domains:
        # Browser/runtime validation remains in Atlas Tests. No map render is a
        # prerequisite merely because viewer code changed.
        validated["frontend"] = {"delegatedWorkflow": "OTBM Atlas Tests"}
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--repository", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    report = run_domain_probe(plan, args.repository)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
