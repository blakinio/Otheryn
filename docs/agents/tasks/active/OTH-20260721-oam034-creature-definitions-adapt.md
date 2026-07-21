---
task_id: OTH-20260721-oam034-creature-definitions-adapt
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-034
status: implementing
branch: task/OAM-034-creature-definitions-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
modules_touched:
  - creature-definitions
owned_paths:
  - data-otservbr-global/monster/birds/agrestic_chicken.lua
  - data-otservbr-global/monster/mammals/terrified_elephant.lua
  - data-otservbr-global/monster/quests/heart_of_destruction/eradicator2.lua
  - data-otservbr-global/monster/quests/soul_war/normal_monsters/monk's_apparition.lua
  - data-otservbr-global/monster/quests/the_first_dragon/haunted_dragon.lua
  - data-otservbr-global/monster/undeads/crypt_warrior.lua
  - tests/unit/game/CMakeLists.txt
  - tests/unit/game/oam_034_creature_definitions_adapt_test.cpp
  - docs/oam-034-creature-definitions-adapt.md
  - docs/agents/tasks/active/OTH-20260721-oam034-creature-definitions-adapt.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - merged legacy PR #192 monster-definition data
  - canonical creature-definitions registry record
  - open PR ownership overlapping selected monster definitions
---

# OAM-034 Creature definitions adaptation

## Goal

Adapt the smallest evidence-backed `creature-definitions` correction boundary from reviewed legacy PR #192 into clean Otheryn without importing Creature AI, spawns, raids, boss orchestration, Cyclopedia validator infrastructure or unrelated data/runtime work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T23:40:00+02:00
head: e03ab4e26b9c7504e88be3bafbd1e6a9033d4af0
branch: task/OAM-034-creature-definitions-adapt
status: implementing
context_routes:
  - cpp-runtime
  - cross-repo
  - testing
owned_paths:
  - data-otservbr-global/monster/birds/agrestic_chicken.lua
  - data-otservbr-global/monster/mammals/terrified_elephant.lua
  - data-otservbr-global/monster/quests/heart_of_destruction/eradicator2.lua
  - data-otservbr-global/monster/quests/soul_war/normal_monsters/monk's_apparition.lua
  - data-otservbr-global/monster/quests/the_first_dragon/haunted_dragon.lua
  - data-otservbr-global/monster/undeads/crypt_warrior.lua
  - tests/unit/game/CMakeLists.txt
  - tests/unit/game/oam_034_creature_definitions_adapt_test.cpp
  - docs/oam-034-creature-definitions-adapt.md
  - docs/agents/tasks/active/OTH-20260721-oam034-creature-definitions-adapt.md
proven:
  - OAM-033 is fully complete through target archive merge 2fe646dfff3d4fc0672c3fbeca85708dabc4ce87 and Canary reconciliation ab2fb5548260544f42f786d11d4dd1b600c39a06.
  - Canonical creature-definitions has no fundamental dependencies and owns monster definition data.
  - Fresh OAM-034 baselines are Canary ab2fb5548260544f42f786d11d4dd1b600c39a06, Otheryn 2fe646dfff3d4fc0672c3fbeca85708dabc4ce87, upstream 71a0f92b4da3f550b292fa7536a0e35c2769f1ae and maintained OTClient 465b7a2192b176cf8cb9d58e000c38863e4a6e4c.
  - OAM-034 disposition is creature-definitions ADAPT using exactly six reviewed production corrections from merged legacy PR 192.
  - For all six selected files task-start target equals fresh upstream pre-fix content while current legacy preserves the exact reviewed correction.
  - No open Otheryn PR and no open Canary monster or creature-definitions PR overlaps the selected six-file production boundary.
  - PR 192 validator tests logs and governance files are excluded; OAM-034 adds one target-local focused source-contract proof.
derived:
  - The smallest valid package is six production definition files plus focused target proof task and evidence.
unknown:
  - Exact target CI and full Linux-debug evidence until PR validation completes.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation or validation failure observed before target PR creation.
rejected_hypotheses:
  - Treat creature AI spawns raids or boss encounter orchestration as part of creature-definitions; canonical registry keeps those separate.
  - Import all PR 192 validator and Cyclopedia infrastructure; those paths are not required for the selected target package.
changed_paths:
  - data-otservbr-global/monster/birds/agrestic_chicken.lua
  - data-otservbr-global/monster/mammals/terrified_elephant.lua
  - data-otservbr-global/monster/quests/heart_of_destruction/eradicator2.lua
  - data-otservbr-global/monster/quests/soul_war/normal_monsters/monk's_apparition.lua
  - data-otservbr-global/monster/quests/the_first_dragon/haunted_dragon.lua
  - data-otservbr-global/monster/undeads/crypt_warrior.lua
  - tests/unit/game/CMakeLists.txt
  - tests/unit/game/oam_034_creature_definitions_adapt_test.cpp
  - docs/oam-034-creature-definitions-adapt.md
  - docs/agents/tasks/active/OTH-20260721-oam034-creature-definitions-adapt.md
validation:
  - command: exact target upstream legacy six-file comparison
    result: PASS
    evidence: all six target files match fresh upstream pre-fix blobs and legacy contains exact PR 192 corrections
blockers: []
next_action: Open the bounded Otheryn target PR and run exact-head autofix Repository Audit CI Required and Linux-debug full tests; then audit final scope reviews threads and main drift before expected-head squash merge.
```
