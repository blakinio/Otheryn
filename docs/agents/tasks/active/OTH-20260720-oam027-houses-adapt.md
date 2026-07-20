---
task_id: OTH-20260720-oam027-houses-adapt
status: ready
branch: dudantas/oam-027-houses-adapt
base_branch: main
created: 2026-07-20
updated: 2026-07-20
related_pr: "55"
owned_paths:
  - docs/agents/tasks/active/OTH-20260720-oam027-houses-adapt.md
  - docs/oam-027-houses-adapt.md
  - src/map/house/house.cpp
  - tests/unit/game/oam_027_houses_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/map/house/house.cpp
optional_reads: []
---

# OAM-027 houses target adaptation

## Goal

Apply only the reviewed legacy PR #60 transfer-safety correction to the clean target house runtime and add focused proof without importing legacy multichannel house ownership/mirroring.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T22:04:00Z
head: 0d3d1e3049d9259a87540a034c3f0c0c016a2c24
branch: dudantas/oam-027-houses-adapt
pr: 55
status: ready
context_routes:
  - docs/agents/tasks/active/OTH-20260720-oam027-houses-adapt.md
  - docs/oam-027-houses-adapt.md
owned_paths:
  - docs/agents/tasks/active/OTH-20260720-oam027-houses-adapt.md
  - docs/oam-027-houses-adapt.md
  - src/map/house/house.cpp
  - tests/unit/game/oam_027_houses_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 5003753e491250732910e9d5857b20293d1bd9ab.
  - Target and fresh upstream house.cpp share blob 25fa954a55763bc9473234682d143c9761843403.
  - Merged legacy PR 60 changes only house.cpp and fixes transfer iteration invalidation, stale snapshot entries, duplicate move-queue processing and invalid wrapped-item dereference.
  - Whole-file legacy copy is forbidden because current legacy house.cpp includes separately owned multichannel house architecture.
  - The target branch contains exactly the four reviewed PR 60 transfer-safety hunks; temporary materializer paths were removed before PR creation.
  - PR 55 changed paths are exactly the active task, OAM-027 evidence doc, house.cpp, focused test and game test CMake registration.
  - Draft CI 197 and Required 179 passed on head 447f21837dcfb57701c6b1835611048e30201ff0.
  - Ready-state head e3c18e52940df481521ae9c8c413c3f5420a383f passed autofix, Fast Checks, Lua, Linux release, macOS and both Windows builds; Linux debug compiled and runtime smoke passed.
  - Linux debug CTest on e3c18e52940df481521ae9c8c413c3f5420a383f passed 411/412; the focused transfer-safety source-contract test passed.
  - The sole failure was the new synthetic PreservesBasicHouseIdentityAndState test segfaulting while constructing House without full runtime state; that harness-only test was removed without changing production code or donor-contract assertions.
derived:
  - OAM-027 target disposition remains houses ADAPT with exact reviewed PR 60 hunks only.
  - The first ready-state CTest failure was a proof-harness defect, not evidence against the production adaptation.
unknown:
  - Final exact-head CI outcome after removing the invalid synthetic House harness.
conflicts: []
first_failure:
  marker: Oam027HousesAdaptTest.PreservesBasicHouseIdentityAndState SEGFAULT
  evidence: CI 200 linux-debug CTest 411/412; artifact 8477116498 digest sha256:c2ecbd48b468df6cc6b7df1c6d599e46e7e70ceb9ff5ee8d7f4d166f4db854c9
rejected_hypotheses:
  - Copy current legacy house.cpp wholesale.
  - Treat the synthetic House-construction SEGFAULT as a target production defect; the independent transfer-safety contract test passed and the failing harness did not exercise the adapted functions.
changed_paths:
  - docs/agents/tasks/active/OTH-20260720-oam027-houses-adapt.md
  - docs/oam-027-houses-adapt.md
  - src/map/house/house.cpp
  - tests/unit/game/oam_027_houses_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: exact donor/context preflight
    result: PASS
    evidence: PR 60 diff applies without legacy multichannel changes
  - command: draft target CI 197 and Required 179
    result: PASS
    evidence: exact head 447f21837dcfb57701c6b1835611048e30201ff0
  - command: ready-state CI 200 linux-debug CTest
    result: FAIL
    evidence: 411/412 passed; sole failure Oam027HousesAdaptTest.PreservesBasicHouseIdentityAndState SEGFAULT; source-contract proof passed
  - command: remove invalid synthetic House proof harness
    result: PASS
    evidence: commit 0d3d1e3049d9259a87540a034c3f0c0c016a2c24 changes only the focused test
blockers: []
next_action: Require autofix, CI and Required success on the resulting exact final PR 55 head after the harness repair, verify the focused OAM-027 source-contract test passes in Linux debug, audit five-file scope plus comments/reviews/threads and target-main drift, then expected-head squash merge if all gates remain clean.
```
