---
task_id: OTH-20260720-oam027-houses-adapt
status: implementing
branch: dudantas/oam-027-houses-adapt
base_branch: main
created: 2026-07-20
updated: 2026-07-20
related_pr: ""
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
updated_at: 2026-07-20T21:40:00Z
head: 5003753e491250732910e9d5857b20293d1bd9ab
branch: dudantas/oam-027-houses-adapt
pr: none
status: implementing
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
derived:
  - OAM-027 target disposition is houses ADAPT with exact reviewed PR 60 hunks only.
unknown:
  - Exact CI outcome until the target PR runs.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Copy current legacy house.cpp wholesale.
changed_paths:
  - docs/agents/tasks/active/OTH-20260720-oam027-houses-adapt.md
validation:
  - command: exact donor/context preflight
    result: PASS
    evidence: PR 60 diff applies to the reviewed target transfer functions without requiring legacy multichannel changes
blockers: []
next_action: Materialize the four exact PR 60 transfer-safety hunks in src/map/house/house.cpp, add focused OAM-027 source-contract/basic-state proof, and open the target PR for exact-head CI.
```
