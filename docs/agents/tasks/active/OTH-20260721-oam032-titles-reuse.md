---
task_id: OTH-20260721-oam032-titles-reuse
status: implementing
branch: dudantas/oam-032-titles-reuse
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260721-oam032-titles-reuse.md
  - docs/oam-032-titles-reuse.md
  - tests/unit/game/oam_032_titles_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/creatures/players/components/player_title.cpp
  - src/creatures/players/components/player_title.hpp
optional_reads: []
---

# OAM-032 Titles target reuse proof

## Goal

Prove the bounded canonical `titles` server lifecycle is already present in the clean target and preserve it without importing unrelated Cyclopedia, Charm, appearance, protocol or client work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T21:50:00+02:00
head: ad2bd2f187df057c47d05c121351159ce30cc457
branch: dudantas/oam-032-titles-reuse
pr: none
status: implementing
context_routes:
  - docs/oam-032-titles-reuse.md
owned_paths:
  - docs/agents/tasks/active/OTH-20260721-oam032-titles-reuse.md
  - docs/oam-032-titles-reuse.md
  - tests/unit/game/oam_032_titles_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is ad2bd2f187df057c47d05c121351159ce30cc457.
  - Canary task-start main is db7cf6af480285ad4a87c3be2981a873f175eab6.
  - Fresh upstream Canary is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical titles depends only on completed cyclopedia-character and player-persistence.
  - TSD-004 owns the narrow server root src/creatures/players/components/player_title.*.
  - Target legacy and upstream share player_title.cpp blob c885d5ee55970d8ce93a80bb477bc317fb9faa98.
  - Target legacy and upstream share player_title.hpp blob 118806fee9ca6d939d73067af14c63c59d291f25.
  - Legacy PR 188 contains no player_title path.
  - Legacy PR 192 contains only monster data validator and documentation paths.
  - Legacy PR 243 contains validator workflow control only.
  - Current open Canary PRs do not overlap player_title or OAM-032 paths and Otheryn has no open PRs.
derived:
  - OAM-032 disposition is titles REUSE with proof-only target changes.
unknown:
  - Exact final target CI evidence until PR gating completes.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed.
rejected_hypotheses:
  - Import Cyclopedia runtime fixes from PR 188 under Titles ownership because that PR has no Titles path.
  - Treat TSD-004 inventory as proof of full Titles parity because it explicitly does not prove title definitions thresholds persistence protocol runtime or client correctness.
changed_paths:
  - docs/agents/tasks/active/OTH-20260721-oam032-titles-reuse.md
  - docs/oam-032-titles-reuse.md
  - tests/unit/game/oam_032_titles_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: live target legacy upstream blob and ownership preflight
    result: PASS
    evidence: exact player_title cpp and hpp blobs match across all three server trees and no accepted donor delta owns Titles
blockers: []
next_action: Add focused proof registration, open the target PR, require exact-head autofix CI Required and Linux-debug Run Tests success, audit exactly four intended proof paths plus comments reviews threads and target-main drift, then expected-head squash merge if all gates remain clean.
```
