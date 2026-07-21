---
task_id: OTH-20260721-oam033-charms-adapt
status: validating
branch: dudantas/oam-033-charms-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: "67"
owned_paths:
  - data/scripts/lib/register_bestiary_charm.lua
  - src/io/iobestiary.cpp
  - docs/agents/tasks/active/OTH-20260721-oam033-charms-adapt.md
  - docs/oam-033-charms-adapt.md
  - tests/unit/game/oam_031_bestiary_adapt_test.cpp
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
updated_at: 2026-07-21T23:25:00+02:00
head: 3ca61ccf67af29d696f90b81a05d33eb28d68a53
branch: dudantas/oam-033-charms-adapt
pr: 67
status: validating
context_routes:
  - docs/oam-033-charms-adapt.md
owned_paths:
  - data/scripts/lib/register_bestiary_charm.lua
  - src/io/iobestiary.cpp
  - docs/agents/tasks/active/OTH-20260721-oam033-charms-adapt.md
  - docs/oam-033-charms-adapt.md
  - tests/unit/game/oam_031_bestiary_adapt_test.cpp
  - tests/unit/game/oam_033_charms_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Canary task-start main is f05ea5e916af00ab1469a2332aaec2d3c9df7478.
  - Otheryn task-start main is 1a4bbceda2c805bc69c68c1592e04e63d7e9a269.
  - Fresh upstream Canary is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical charms depends only on completed combat cyclopedia player-persistence and protocol.
  - TSD-004 preserves independent Charm ownership for definitions costs unlock state assignment and combat effects.
  - Open Canary PRs do not touch the two selected production paths or OAM-033 paths and Otheryn had no open PRs at preflight.
  - Merged legacy PR 188 contains exactly two selected Charm-owned corrections.
  - Target and fresh upstream still guard category registration with mask.type while current legacy uses mask.category.
  - Target and fresh upstream charge playerLevel times 11000 above level 100 while current legacy charges only levels above 100.
  - Initial target CI head 88804b02857e76039fe694dfffc99fcc4fa49c51 passed compile runtime smoke schema Fast Checks Lua autofix and Repository Audit.
  - Initial Linux-debug full suite ran 422 tests; the only failure was superseded OAM-031 boundary assertion CharmResetPricingRemainsOutsideBestiaryPackage.
  - The OAM-031 assertion encoded the pre-OAM-033 old Charm formula and became invalid once Charm ownership intentionally changed the formula; both new OAM-033 focused tests passed.
  - Production corrections were unchanged while the superseded OAM-031 Charm-specific boundary assertion was retired.
derived:
  - OAM-033 disposition is charms ADAPT with exactly two production corrections and one prior-package proof-boundary maintenance change.
unknown:
  - Exact final target CI evidence until validation reruns complete on the repaired head.
conflicts: []
first_failure:
  marker: superseded OAM-031 ownership-boundary assertion
  evidence: Initial CI 230 Linux-debug Run Tests failed only test 206 Oam031BestiaryAdaptTest.CharmResetPricingRemainsOutsideBestiaryPackage; 421 of 422 tests passed and the OAM-033 proof itself passed.
rejected_hypotheses:
  - Treat the Linux-debug failure as a production Charm regression; the failing assertion required the intentionally superseded old reset-price formula.
  - Import Bestiary null-safety or difficulty fixes under Charms ownership; those are completed OAM-031.
  - Import Bosstiary or Cyclopedia Character PR 188 hunks; they are completed child packages.
changed_paths:
  - data/scripts/lib/register_bestiary_charm.lua
  - src/io/iobestiary.cpp
  - docs/agents/tasks/active/OTH-20260721-oam033-charms-adapt.md
  - docs/oam-033-charms-adapt.md
  - tests/unit/game/oam_031_bestiary_adapt_test.cpp
  - tests/unit/game/oam_033_charms_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: live dependency donor ownership and open-PR preflight
    result: PASS
    evidence: two bounded Charm-owned PR 188 corrections selected with no current writer overlap
  - command: initial exact-head CI 230 Linux-debug full suite
    result: FAIL_EXPECTED_BOUNDARY_MAINTENANCE
    evidence: 421/422 passed; sole failure was the superseded OAM-031 old-formula assertion, not an OAM-033 proof or production runtime failure
blockers: []
next_action: Require exact-head autofix CI Required and Linux-debug Run Tests success on the repaired head, then audit seven intended paths review threads and target-main drift before expected-head squash merge.
```
