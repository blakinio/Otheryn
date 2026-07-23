---
task_id: OTH-20260724-oam041-spawns-reuse
status: active
branch: dudantas/oam-041-spawns-reuse
base_branch: main
created: 2026-07-24
updated: 2026-07-24
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-oam041-spawns-reuse.md
  - docs/oam-041-spawns-reuse.md
  - tests/unit/game/oam_041_spawns_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
  - .github/workflows/oam-041-spawns-proof.yml
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/creatures/monsters/spawns/spawn_monster.cpp
  - src/creatures/npcs/spawns/spawn_npc.cpp
  - data-otservbr-global/world/otservbr-monster.xml
  - data-otservbr-global/world/otservbr-npc.xml
  - tests/unit/game/CMakeLists.txt
optional_reads: []
---

# OAM-041 Spawns target reuse proof

## Goal

Prove the bounded canonical `spawns` module is already correctly represented in the clean Otheryn target, using semantic source-contract coverage plus deterministic external Canary OTBM spawn/NPC evidence. Preserve the target without importing legacy spawn runtime, copying Canary OTBM tooling into Otheryn, duplicating completed raid lifecycle ownership, or mutating production runtime, datapack, map, binary assets, protocol, client, schema or deployment paths unless proof isolates a concrete spawns-owned target defect.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T00:10:00+02:00
head: 9369b0719ff94997a9cf5a2d62853939744e6338
branch: dudantas/oam-041-spawns-reuse
pr: null
status: active
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-oam041-spawns-reuse.md
  - docs/oam-041-spawns-reuse.md
  - tests/unit/game/oam_041_spawns_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
  - .github/workflows/oam-041-spawns-proof.yml
proven:
  - Target task-start main is 9369b0719ff94997a9cf5a2d62853939744e6338.
  - Canary OAM-041 preflight selected canonical spawns as a REUSE candidate after OAM-040 otbm-tooling was formally resolved as an external Canary evidence responsibility.
  - Target spawn_monster.cpp blob is 4c82217631ddf479faa5443025d43f99a0c927d1 and spawn_npc.cpp blob is 21718ad80827a16e9a1b29bc9d649ad603bcf216, matching the reviewed fresh upstream roots recorded by Canary governance.
  - Target config selects data-otservbr-global and mapName otservbr with the v3.6.1 public map download URL.
  - Target monster and NPC runtime preserves center plus child x-y offset with center z, bounded/default spawn intervals, player blocking, removed-creature cleanup and DispatcherLane::Maintenance scheduling.
  - Monster runtime additionally preserves rate/event/boost scaling, one-second to one-day clamp, boss exclusivity and weighted monster selection.
  - Current Canary Phase 4 tooling is an external evidence dependency and must not be copied into Otheryn production paths.
derived:
  - REUSE remains the leading disposition if exact-head deterministic target evidence and source-contract tests pass without a concrete spawns-owned defect.
  - A temporary branch-only proof workflow may execute pinned external Canary tooling and generate uncommitted artifacts; it must be removed before final merge so the delivered target package remains the intended four proof/task paths.
  - Raid registry scheduling and ordered event lifecycle remain outside OAM-041 because OAM-037 already proved canonical raids ownership.
unknown:
  - Exact current Otheryn active-datapack source-scan findings under pinned Canary Phase 4 tooling.
  - Exact v3.6.1 map World Index/reachability and bounded spawn placement correlation findings for the selected proof region.
  - Whether deterministic proof exposes a concrete spawns-owned defect requiring ADAPT.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific target validation failure observed yet.
rejected_hypotheses:
  - Infer final REUSE from blob identity alone; OAM-041 requires semantic and deterministic target-side evidence.
  - Import the divergent legacy Canary spawn runtime; reviewed target/upstream roots retain stronger maintenance-lane scheduling.
  - Copy Canary OTBM tooling into Otheryn; OAM-040 established it as an external evidence dependency.
  - Re-prove raid scheduler lifecycle inside OAM-041; that boundary belongs to completed OAM-037.
changed_paths:
  - docs/agents/tasks/active/OTH-20260724-oam041-spawns-reuse.md
validation:
  - command: fresh target preflight and source semantic review
    result: PASS
    evidence: task-start main and canonical spawn runtime blobs verified; reviewed source semantics match the bounded spawns ownership contract
  - command: deterministic external Canary OTBM target proof
    result: NOT_RUN
    evidence: temporary exact-head proof workflow is the next action
blockers: []
next_action: Add and run the temporary exact-head OAM-041 proof workflow against this Otheryn branch using pinned Canary tooling, capture source-scan, map-index, reachability and bounded placement-correlation artifacts, then classify REUSE versus bounded ADAPT from concrete findings.
```
