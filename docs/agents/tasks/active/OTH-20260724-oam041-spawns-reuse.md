---
task_id: OTH-20260724-oam041-spawns-reuse
status: validating
branch: dudantas/oam-041-spawns-reuse-closure
base_branch: main
created: 2026-07-24
updated: 2026-07-24
related_pr: "92"
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-oam041-spawns-reuse.md
  - docs/oam-041-spawns-reuse.md
  - tests/unit/game/oam_041_spawns_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
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
updated_at: 2026-07-24T07:05:00+02:00
head: 95e0d0777987efa812a2efbb671daa95040a6ad7
branch: dudantas/oam-041-spawns-reuse-closure
pr: 92
status: validating
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-oam041-spawns-reuse.md
  - docs/oam-041-spawns-reuse.md
  - tests/unit/game/oam_041_spawns_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 9369b0719ff94997a9cf5a2d62853939744e6338.
  - Canary OAM-041 preflight selected canonical spawns as a REUSE candidate after OAM-040 otbm-tooling was formally resolved as an external Canary evidence responsibility.
  - Target spawn_monster.cpp blob is 4c82217631ddf479faa5443025d43f99a0c927d1 and spawn_npc.cpp blob is 21718ad80827a16e9a1b29bc9d649ad603bcf216, matching the reviewed fresh upstream roots recorded by Canary governance.
  - Target monster and NPC runtime preserves center plus child x-y offset with center z, interval bounds/defaulting, player blocking, removed-creature cleanup and DispatcherLane::Maintenance scheduling; monster runtime also preserves rate/event/boost scaling, boss exclusivity and weighted selection.
  - Exact successful deterministic proof run 30049543113 executed on precursor target head 38bf8dcb4d401fa4053e350af052cc2e9c8da4bd using pinned Canary commit d1ad83056ec7930f067986909f66b8f20f1a1f44 and exact Phase 4 tool blobs.
  - The proof verified configured map SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 and generated World Index SHA-256 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a outside Git.
  - Full active-datapack scan found 52903 groups and 84294 static placements with 318 untruncated findings; the two errors are the known duplicate Harlow NPC-definition ambiguity, while 310 nonliteral dynamic creation calls remain explicitly unresolved.
  - Final bounded region 32824,31275,7 through 32873,31324,7 produced complete untruncated reachability diagnostics and confirmed 34 of 34 selected groups plus 39 of 39 selected static placements with zero correlation findings.
  - Temporary proof workflow was removed after artifact capture; intended delivery is exactly four proof/task paths with no production runtime datapack map binary protocol client schema or deployment mutation.
  - CI-only repairs merged to Otheryn main as dee95e2fa011d08daf15e5ba110220691a98b6e0, 05b0a299d4e2bc9a0377323d7967b285244388fe and 5b6f62b33957472afba16f377b94993389abd145; generated Lua API drift was reconciled separately as bdfb71fb4db0caab3d6da41e170790cfb98ba177.
  - Closure PR 92 starts exactly from 5b6f62b33957472afba16f377b94993389abd145 and restores only the intended four OAM-041 paths.
derived:
  - Final OAM-041 target disposition is spawns REUSE if exact-final-head repository gates remain green.
  - Known Harlow ambiguity and unresolved dynamic Lua calls are explicit evidence boundaries, not authorization for guessed or broad source repair.
  - Raid registry scheduling and ordered event lifecycle remain outside OAM-041 because OAM-037 already proved canonical raids ownership.
unknown:
  - Exact final target CI Required and platform-gate evidence until PR 92 finishes validation.
  - Final comment review review-thread and target-main-drift state at merge time.
conflicts: []
first_failure:
  marker: none
  evidence: No concrete spawns-owned target defect was isolated; prior failures were proof-harness sizing, generated-documentation drift or stale CI merge-ref issues repaired outside target production/data scope.
rejected_hypotheses:
  - Infer final REUSE from blob identity alone; OAM-041 added semantic source-contract and deterministic target-side evidence.
  - Treat reachability_diagnostics_truncated from the initial 16-floor proof region as a target defect; it was an intentional fail-closed evidence-harness condition.
  - Accept the second proof with the reachability default sample limit of 200; the final run raised the bound to 10000 and required untruncated evidence.
  - Import the divergent legacy Canary spawn runtime; reviewed target/upstream roots retain stronger maintenance-lane scheduling.
  - Copy Canary OTBM tooling into Otheryn; OAM-040 established it as an external evidence dependency.
  - Re-prove raid scheduler lifecycle inside OAM-041; that boundary belongs to completed OAM-037.
changed_paths:
  - docs/agents/tasks/active/OTH-20260724-oam041-spawns-reuse.md
  - docs/oam-041-spawns-reuse.md
  - tests/unit/game/oam_041_spawns_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: fresh target preflight and source semantic review
    result: PASS
    evidence: task-start main and canonical spawn runtime blobs verified; reviewed source semantics match the bounded spawns ownership contract
  - command: deterministic external Canary OTBM target proof run 30049543113
    result: PASS
    evidence: exact configured map and pinned tool provenance verified; source scan completed; reachability untruncated; 34/34 groups and 39/39 placements confirmed with zero correlation findings
  - command: current-main scope reconstruction
    result: PASS
    evidence: PR 92 starts from 5b6f62b33957472afba16f377b94993389abd145 and recreates exactly the intended four OAM-041 paths
blockers: []
next_action: Run exact-final-head Otheryn CI and Required gates on PR 92, audit changed paths comments reviews review threads and target-main drift, then expected-head squash merge if all gates remain clean.
```
