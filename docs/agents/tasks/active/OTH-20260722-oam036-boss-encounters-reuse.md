---
task_id: OTH-20260722-oam036-boss-encounters-reuse
status: implementing
branch: dudantas/oam-036-boss-encounters-reuse
base_branch: main
created: 2026-07-22
updated: 2026-07-22
related_pr: "74"
owned_paths:
  - docs/agents/tasks/active/OTH-20260722-oam036-boss-encounters-reuse.md
  - docs/oam-036-boss-encounters-reuse.md
  - tests/unit/game/oam_036_boss_encounters_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - data/libs/systems/reward_boss.lua
  - data/scripts/systems/reward_chest.lua
optional_reads: []
---

# OAM-036 Boss Encounters target reuse proof

## Goal

Prove the bounded canonical `boss-encounters` runtime is already present in the clean Otheryn target and preserve it without importing unrelated boss AI/definitions, spawns, raids, Bosstiary, encounter-specific quest/cooldown logic, protocol/client, map, asset, schema or deployment work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T11:40:00+02:00
head: 630abcfecb381a3d5d7515c2e7250e6ee85cacf2
branch: dudantas/oam-036-boss-encounters-reuse
pr: 74
status: validating
context_routes:
  - lua-runtime
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260722-oam036-boss-encounters-reuse.md
  - docs/oam-036-boss-encounters-reuse.md
  - tests/unit/game/oam_036_boss_encounters_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 6275021bbb83dc28d2f5d6cf8db5b16aa7206544.
  - Canary OAM-036 preflight merged as 08434e88435cbebe6965d4bd2f13382fdc8a586e and selected canonical boss-encounters as a REUSE candidate.
  - Fresh upstream Canary baseline is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient baseline is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical boss-encounters depends only on completed creature-definitions and player-persistence.
  - Otheryn fresh upstream and legacy Canary share exact reward_boss.lua blob 72476dfcbdd8fd92d6b5bd3ad3015efef87cf2f3 and reward_chest.lua blob 4abe17ad2f3103f30f172f23ebdca391197f8646.
  - Semantic review confirms reward_boss owns reward-container serialization participation state and target-list activity while reward_chest owns boss-death scoring reward generation chest insertion offline save handoff and participation event accounting.
  - No stronger delivered legacy donor or open target writer was identified for the selected canonical roots.
  - PR 74 is the single bounded OAM-036 target owner and changes exactly four intended proof/task paths with no production path.
derived:
  - OAM-036 final disposition is boss-encounters REUSE if the bounded source-contract proof and exact-head target gates pass without production repair.
  - No maintained-client mutation is expected because the selected boundary is server-side encounter/reward lifecycle and does not alter the wire contract.
unknown:
  - Exact final target CI and Required evidence until PR gating completes.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed.
rejected_hypotheses:
  - Infer final REUSE from blob identity alone; this target package adds semantic source-contract proof for the owned encounter lifecycle.
  - Expand OAM-036 into boss AI definitions spawns raids Bosstiary or quest cooldowns because those are separate ownership boundaries.
changed_paths:
  - docs/agents/tasks/active/OTH-20260722-oam036-boss-encounters-reuse.md
  - docs/oam-036-boss-encounters-reuse.md
  - tests/unit/game/oam_036_boss_encounters_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: exact-root and semantic target preflight
    result: PASS
    evidence: exact canonical roots match upstream and legacy and reviewed lifecycle semantics map to boss-encounters ownership
  - command: immutable-base changed-path audit
    result: PASS
    evidence: exactly four intended proof/task paths and no production change
blockers: []
next_action: Mark PR 74 ready and require exact-current-head autofix CI Required and Linux-debug full Run Tests success, audit comments reviews threads and target-main drift, then expected-head squash merge if all gates remain clean.
```
