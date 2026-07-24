---
task_id: OTH-20260724-oam042-npcs-reuse
status: completed
branch: dudantas/oam-042-npcs-reuse-proof
base_branch: main
created: 2026-07-24
updated: 2026-07-24
completed: 2026-07-24T10:14:00+02:00
last_verified_commit: "0d01f077f80c2d4cd3d4231d2ffb9416874ba54e"
related_pr: "96"
owned_paths:
  - docs/agents/tasks/archive/OTH-20260724-oam042-npcs-reuse.md
  - docs/oam-042-npcs-reuse.md
  - tests/unit/game/oam_042_npcs_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - docs/oam-042-npcs-reuse.md
optional_reads: []
---

# OAM-042 NPC target reuse proof

## Final disposition

`REUSE` with explicit evidence boundaries.

The clean Otheryn target reuses the reviewed current-upstream NPC runtime, registration, callback, dialogue, travel, shop and representative quest-hook contracts. No production runtime, datapack, map, binary, protocol, client, schema or deployment mutation was required.

Duplicate Harlow definition ambiguity, the exact NPC-owned subset of nonliteral dynamic creation/quest-hook calls, full factual completeness of every NPC conversation and production gameplay parity remain explicit bounded unknowns. They were not silently promoted to handled.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T10:14:00+02:00
head: 0d01f077f80c2d4cd3d4231d2ffb9416874ba54e
branch: main
pr: 96
status: completed
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/archive/OTH-20260724-oam042-npcs-reuse.md
  - docs/oam-042-npcs-reuse.md
  - tests/unit/game/oam_042_npcs_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Canary OAM-042 preflight PR 859 merged as c86e805910d87dc8db9a212b18645e27c28c779c.
  - Reviewed target and current opentibiabr/canary NPC runtime, npclib, Harlow, Rashid and placement files have identical Git blobs recorded in docs/oam-042-npcs-reuse.md.
  - OAM-041 placement/definition correlation evidence was reused without copying Canary OTBM tooling into Otheryn.
  - The source-contract test covers loader and case-insensitive registration, NPC callback events, Lua NPC interaction/shop surface, StdModule.travel, Harlow storage-gated travel and Rashid quest/shop gating.
  - Exact ready-head e7b8f3a121f931a83ef016ceb6d30ad21dcdf74d passed Fast Checks, Lua Tests, Linux release/debug, Windows CMake/Solution, macOS, runtime smoke tests and Required in CI run 30077147345 and Required run 30077147262.
  - PR 96 had no comments, reviews or review threads and no main drift before merge.
  - PR 96 squash-merged as 0d01f077f80c2d4cd3d4231d2ffb9416874ba54e.
derived:
  - The evidence supports bounded canonical npcs REUSE; no target-local adaptation or rewrite is justified.
unknown:
  - Full factual completeness of every individual NPC conversation.
  - Whether both Harlow definitions reported by the external scanner are active under exact target configuration.
  - Exact NPC-owned subset of nonliteral dynamic creation and quest-hook calls.
  - Production gameplay parity.
conflicts: []
first_failure:
  marker: none
  evidence: No concrete NPC-owned target defect was isolated.
rejected_hypotheses:
  - Treat OAM-041 placement evidence as proof of every dialogue/shop/travel/quest-hook contract.
  - Guess away duplicate Harlow or nonliteral dynamic calls.
  - Copy Canary OTBM tooling into Otheryn.
  - Require ADAPT or REWRITE without a target-local defect.
changed_paths:
  - docs/oam-042-npcs-reuse.md
  - tests/unit/game/oam_042_npcs_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
  - docs/agents/tasks/archive/OTH-20260724-oam042-npcs-reuse.md
validation:
  - command: full exact-head CI 30077147345
    result: PASS
    evidence: All selected compiled platforms, tests, formatting and runtime smoke checks succeeded.
  - command: Required 30077147262
    result: PASS
    evidence: Exact-head required gate succeeded.
  - command: squash merge PR 96
    result: PASS
    evidence: GitHub created merge commit 0d01f077f80c2d4cd3d4231d2ffb9416874ba54e.
blockers: []
next_action: NONE
```
