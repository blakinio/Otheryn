---
task_id: OTH-20260721-oam033-charms-adapt
status: implementing
branch: dudantas/oam-033-charms-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: ""
owned_paths:
  - data/scripts/lib/register_bestiary_charm.lua
  - src/io/iobestiary.cpp
  - docs/agents/tasks/active/OTH-20260721-oam033-charms-adapt.md
  - docs/oam-033-charms-adapt.md
  - tests/unit/game/oam_033_charms_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - data/scripts/lib/register_bestiary_charm.lua
  - src/io/iobestiary.cpp
optional_reads: []
---

# OAM-033 Charms target adaptation

## Goal

Apply only the two reviewed Charm-owned corrections from merged legacy PR #188 while preserving Bestiary ownership, broad protocol/client surfaces and unrelated Cyclopedia fixes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T23:10:00+02:00
head: 1a4bbceda2c805bc69c68c1592e04e63d7e9a269
branch: dudantas/oam-033-charms-adapt
pr: none
status: implementing
context_routes:
  - docs/oam-033-charms-adapt.md
owned_paths:
  - data/scripts/lib/register_bestiary_charm.lua
  - src/io/iobestiary.cpp
  - docs/agents/tasks/active/OTH-20260721-oam033-charms-adapt.md
  - docs/oam-033-charms-adapt.md
  - tests/unit/game/oam_033_charms_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Canary task-start main is f05ea5e916af00ab1469a2332aaec2d3c9df7478.
  - Otheryn task-start main is 1a4bbceda2c805bc69c68c1592e04e63d7e9a269.
  - Fresh upstream Canary is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical charms depends only on completed combat cyclopedia player-persistence and protocol.
  - TSD-004 preserves independent Charm ownership for definitions costs unlock state assignment and combat effects.
  - Open Canary PRs do not touch the two selected production paths or OAM-033 paths and Otheryn has no open PRs.
  - Merged legacy PR 188 contains exactly two selected Charm-owned corrections.
  - Target and fresh upstream still guard category registration with mask.type while current legacy uses mask.category.
  - Target and fresh upstream charge playerLevel times 11000 above level 100 while current legacy charges only levels above 100.
derived:
  - OAM-033 disposition is charms ADAPT with exactly two production corrections.
unknown:
  - Exact final target CI evidence until PR gating completes.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed.
rejected_hypotheses:
  - Import Bestiary null-safety or difficulty fixes under Charms ownership; those are completed OAM-031.
  - Import Bosstiary or Cyclopedia Character PR 188 hunks; they are completed child packages.
changed_paths:
  - data/scripts/lib/register_bestiary_charm.lua
  - src/io/iobestiary.cpp
  - docs/agents/tasks/active/OTH-20260721-oam033-charms-adapt.md
  - docs/oam-033-charms-adapt.md
  - tests/unit/game/oam_033_charms_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: live dependency donor ownership and open-PR preflight
    result: PASS
    evidence: two bounded Charm-owned PR 188 corrections selected with no current writer overlap
blockers: []
next_action: Materialize the two production fixes, add focused proof, open the target PR, require exact-head autofix CI Required and Linux-debug Run Tests success, then audit scope review threads and target-main drift before expected-head squash merge.
```
