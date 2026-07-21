---
task_id: OTH-20260721-oam030-bosstiary-adapt
status: implementing
branch: dudantas/oam-030-bosstiary-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260721-oam030-bosstiary-adapt.md
  - docs/oam-030-bosstiary-adapt.md
  - src/io/io_bosstiary.cpp
  - tests/unit/game/oam_030_bosstiary_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/io/io_bosstiary.cpp
optional_reads: []
---

# OAM-030 Bosstiary target adaptation

## Goal

Apply only the reviewed legacy PR #188 missing `boosted_boss` row initialization correction and add focused proof without importing later multichannel, Bestiary, Charms, protocol or maintained-client changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T09:55:00+02:00
head: 68d48deea999990b1eab30858f3a85fc9fef7067
branch: dudantas/oam-030-bosstiary-adapt
pr: none
status: implementing
context_routes:
  - docs/oam-030-bosstiary-adapt.md
owned_paths:
  - docs/agents/tasks/active/OTH-20260721-oam030-bosstiary-adapt.md
  - docs/oam-030-bosstiary-adapt.md
  - src/io/io_bosstiary.cpp
  - tests/unit/game/oam_030_bosstiary_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 68d48deea999990b1eab30858f3a85fc9fef7067.
  - Target and fresh upstream share io_bosstiary.cpp blob 8e89ce79316e5c193e918661c50278f50d476c83.
  - Merged legacy PR 188 changes exactly one canonical bosstiary production site in IOBosstiary::loadBoostedBoss.
  - The accepted donor removes an early no-row return and initializes the missing boosted_boss row before reroll.
  - Later current-legacy multichannel leadership logic is independent and excluded.
derived:
  - OAM-030 target disposition is bosstiary ADAPT with one production recovery correction plus focused proof.
unknown:
  - Exact final target CI evidence until PR gating completes.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Copy current legacy io_bosstiary.cpp wholesale.
  - Import Bestiary Charms monster-data protocol or maintained-client changes.
changed_paths:
  - docs/agents/tasks/active/OTH-20260721-oam030-bosstiary-adapt.md
  - docs/oam-030-bosstiary-adapt.md
  - src/io/io_bosstiary.cpp
  - tests/unit/game/oam_030_bosstiary_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: exact donor and ownership preflight
    result: PASS
    evidence: PR 188 has one isolated io_bosstiary.cpp hunk applicable to exact target/upstream code
blockers: []
next_action: Materialize the bounded adaptation and focused proof, remove temporary materialization helpers, open the target PR, then require exact-head autofix CI Required Linux-debug Run Tests scope review and no-main-drift before expected-head squash merge.
```
