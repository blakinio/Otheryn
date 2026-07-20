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
updated_at: 2026-07-20T21:46:00Z
head: 447f21837dcfb57701c6b1835611048e30201ff0
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
derived:
  - OAM-027 target disposition is houses ADAPT with exact reviewed PR 60 hunks only.
unknown:
  - Final ready-state exact-head CI outcome.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Copy current legacy house.cpp wholesale.
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
  - command: draft target CI 197
    result: PASS
    evidence: exact head 447f21837dcfb57701c6b1835611048e30201ff0
  - command: draft Required 179
    result: PASS
    evidence: exact head 447f21837dcfb57701c6b1835611048e30201ff0
blockers: []
next_action: Mark PR 55 ready, require CI and Required success on the resulting exact final head, audit five-file scope plus comments/reviews/threads and target-main drift, then expected-head squash merge if all gates remain clean.
```
