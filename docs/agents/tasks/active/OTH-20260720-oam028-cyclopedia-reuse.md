---
task_id: OTH-20260720-oam028-cyclopedia-reuse
status: implementing
branch: dudantas/oam-028-cyclopedia-reuse
base_branch: main
created: 2026-07-20
updated: 2026-07-20
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260720-oam028-cyclopedia-reuse.md
  - docs/oam-028-cyclopedia-reuse.md
  - tests/unit/game/oam_028_cyclopedia_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/server/network/protocol/protocolgame.hpp
  - src/io/iobestiary.hpp
  - src/io/io_bosstiary.hpp
  - src/creatures/players/components/player_cyclopedia.hpp
  - src/creatures/players/components/player_title.hpp
optional_reads: []
---

# OAM-028 cyclopedia umbrella reuse proof

## Goal

Prove the clean target already carries the required Cyclopedia umbrella protocol surface and the TSD-004 child delegation boundaries, without mutating production protocol, child runtime/data, or maintained OTClient paths.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T22:45:00Z
head: 2a008f1c8cfa679c9b70281e4c8c16120a7567fa
branch: dudantas/oam-028-cyclopedia-reuse
pr: none
status: implementing
context_routes:
  - docs/agents/tasks/active/OTH-20260720-oam028-cyclopedia-reuse.md
  - docs/oam-028-cyclopedia-reuse.md
owned_paths:
  - docs/agents/tasks/active/OTH-20260720-oam028-cyclopedia-reuse.md
  - docs/oam-028-cyclopedia-reuse.md
  - tests/unit/game/oam_028_cyclopedia_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 2a008f1c8cfa679c9b70281e4c8c16120a7567fa.
  - Target and fresh upstream share protocolgame.hpp blob 082d66596a424fc44143298c41fe01ff4007a439.
  - Target, fresh upstream and legacy share player_cyclopedia.hpp enum blob 45fed9ad2f3b7e35bdc7afd9dbd52d5d1b736311.
  - TSD-004 preserves cyclopedia as a broad compatibility/discovery umbrella and gives independent roots to bestiary, bosstiary, cyclopedia-character and titles while charms and houses remain separate.
  - Reviewed legacy PR 188 production changes belong to child boundaries and explicitly do not change protocol or maintained OTClient.
  - Reviewed legacy PR 192 production changes are Bestiary/Bosstiary data only and explicitly do not change protocol or maintained OTClient.
  - No target production path needs mutation for the selected umbrella boundary.
derived:
  - OAM-028 target disposition is cyclopedia REUSE with proof-only target changes.
unknown:
  - Exact CI outcome until the target PR runs.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Copy legacy Cyclopedia remediation wholesale into the umbrella package.
  - Reopen child runtime/data ownership while proving the umbrella.
changed_paths:
  - docs/agents/tasks/active/OTH-20260720-oam028-cyclopedia-reuse.md
validation:
  - command: exact umbrella/child boundary preflight
    result: PASS
    evidence: target/upstream protocol header identity plus TSD-004 child decomposition and reviewed legacy PR 188/192 scope
blockers: []
next_action: Add proof-only OAM-028 evidence and a focused source-contract test that verifies the existing umbrella protocol declarations plus the independent TSD-004 child implementation roots, register the test, then open the target PR for exact-head CI.
```
