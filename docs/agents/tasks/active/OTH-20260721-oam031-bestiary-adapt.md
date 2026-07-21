---
task_id: OTH-20260721-oam031-bestiary-adapt
status: implementing
branch: dudantas/oam-031-bestiary-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260721-oam031-bestiary-adapt.md
  - docs/oam-031-bestiary-adapt.md
  - src/io/iobestiary.cpp
  - tests/unit/game/oam_031_bestiary_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/io/iobestiary.cpp
optional_reads: []
---

# OAM-031 Bestiary target adaptation

## Goal

Apply only the two reviewed legacy PR #188 Bestiary-owned correctness corrections and add focused proof without importing Charm pricing, monster-definition data, protocol or maintained-client changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T13:10:00+02:00
head: 2d599ca7110b5a73d53adb4dd70d694bd1991d83
branch: dudantas/oam-031-bestiary-adapt
pr: none
status: implementing
context_routes:
  - docs/oam-031-bestiary-adapt.md
owned_paths:
  - docs/agents/tasks/active/OTH-20260721-oam031-bestiary-adapt.md
  - docs/oam-031-bestiary-adapt.md
  - src/io/iobestiary.cpp
  - tests/unit/game/oam_031_bestiary_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 6a7e54ee3c9597e3ab265a14c2b783631ef3776f.
  - Target and fresh upstream share iobestiary.cpp blob c0497c4d1814e7950ad8fc27b9a4ec1f86d4a5cd.
  - Merged legacy PR 188 contains exactly two selected Bestiary-owned production corrections.
  - addBestiaryKill now checks player and mtype before dereferencing mtype raceid.
  - calculateDifficult now preserves fractional thresholds with floating-point division.
  - Charm reset-price correction and PR 192 monster definitions are excluded.
  - Initial production-only branch diff was exactly one file with plus 7 minus 3 lines.
derived:
  - OAM-031 target disposition is bestiary ADAPT with two production correctness hunks plus focused proof.
unknown:
  - Exact final target CI evidence until PR gating completes.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed.
rejected_hypotheses:
  - Copy current legacy iobestiary.cpp wholesale.
  - Import Charm reset pricing under Bestiary ownership.
  - Import monster-definition changes from PR 192.
changed_paths:
  - docs/agents/tasks/active/OTH-20260721-oam031-bestiary-adapt.md
  - docs/oam-031-bestiary-adapt.md
  - src/io/iobestiary.cpp
  - tests/unit/game/oam_031_bestiary_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: production-only diff audit
    result: PASS
    evidence: immutable-base comparison showed only src/io/iobestiary.cpp plus 7 minus 3
blockers: []
next_action: Open the target PR, require exact-head autofix CI Required and Linux-debug Run Tests success, audit exactly five intended paths plus comments reviews threads and target-main drift, then expected-head squash merge if all gates remain clean.
```
