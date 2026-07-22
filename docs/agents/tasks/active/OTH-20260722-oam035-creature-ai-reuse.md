---
task_id: OTH-20260722-oam035-creature-ai-reuse
status: validating
branch: dudantas/oam-035-creature-ai-reuse
base_branch: main
created: 2026-07-22
updated: 2026-07-22
related_pr: "72"
owned_paths:
  - docs/agents/tasks/active/OTH-20260722-oam035-creature-ai-reuse.md
  - docs/oam-035-creature-ai-reuse.md
  - tests/unit/game/oam_035_creature_ai_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/creatures/monsters/monster.cpp
  - src/creatures/monsters/monster.hpp
  - tests/unit/game/monster_targeting_test.cpp
  - tests/unit/game/monster_pathfinding_test.cpp
  - tests/unit/game/monster_combat_intention_test.cpp
  - tests/unit/game/monster_compute_service_test.cpp
  - tests/unit/game/monster_relevance_test.cpp
optional_reads: []
---

# OAM-035 Creature AI target reuse proof

## Goal

Prove the bounded canonical `creature-ai` runtime is already present in the clean Otheryn target and preserve it without importing the older divergent legacy Monster core or unrelated creature definitions, spawns, raids, boss encounters, generic combat, protocol, client, map, asset, schema or deployment work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T10:12:00+02:00
head: 963a90d208d3fb02483efb45f8b429693e61852f
branch: dudantas/oam-035-creature-ai-reuse
pr: 72
status: validating
context_routes:
  - cpp-runtime
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260722-oam035-creature-ai-reuse.md
  - docs/oam-035-creature-ai-reuse.md
  - tests/unit/game/oam_035_creature_ai_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 4771350b44665c5a37b0c058b3d413c0c0de542d.
  - Canary OAM-035 preflight merged as 0f288fe2722d66753c74d859196688a7f9f60e60 and selected canonical creature-ai as the next dependency-valid package.
  - Fresh upstream Canary baseline is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient baseline is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical creature-ai depends only on completed creature-definitions.
  - Otheryn and fresh upstream share exact monster.cpp blob 30cdadf4076d29116eb96fb8bb5f7f46bebddcd5 and monster.hpp blob a5426fdd22533179a9d54834dbe7b340a5d45012.
  - Legacy Canary diverges on both canonical owned core blobs and is not selected as a whole-module donor.
  - The target Monster core preserves explicit runtime think target friend follow flee movement attack defense spawn/despawn and summon interaction surfaces.
  - The target Monster core is wired to modular monster_targeting monster_pathfinding monster_combat_intention and MonsterComputeService boundaries.
  - Existing focused unit tests already cover monster targeting pathfinding combat intention compute service and relevance behavior.
  - Otheryn had no open pull requests at target task start.
  - PR 72 is open as the single bounded OAM-035 target owner and changes exactly four intended proof/task paths with no production path.
derived:
  - OAM-035 final disposition is creature-ai REUSE with proof-only target changes.
  - No production runtime or maintained-client mutation is required for this package.
unknown:
  - Exact final target CI and Required evidence until PR gating completes.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed.
rejected_hypotheses:
  - Import the older divergent legacy Monster core as a donor because the clean target already matches fresh upstream on the canonical owned core.
  - Expand OAM-035 into creature definitions spawns raids boss encounters generic combat protocol or client behavior because those are separate canonical ownership boundaries.
changed_paths:
  - docs/agents/tasks/active/OTH-20260722-oam035-creature-ai-reuse.md
  - docs/oam-035-creature-ai-reuse.md
  - tests/unit/game/oam_035_creature_ai_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: fresh target upstream legacy blob ownership and open-PR preflight
    result: PASS
    evidence: target and upstream owned core blobs match exactly legacy diverges and no open Otheryn writer existed at task start
  - command: existing focused creature AI unit-test inventory
    result: PASS
    evidence: targeting pathfinding combat intention compute service and relevance focused tests are already registered in canary_ut
  - command: immutable-base changed-path audit
    result: PASS
    evidence: exactly four intended proof/task paths and no production change
blockers: []
next_action: Require exact-current-head autofix CI Required and Linux-debug Run Tests success on PR 72, audit comments reviews threads and target-main drift, then expected-head squash merge if all gates remain clean.
```
