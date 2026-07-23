---
task_id: OTH-20260723-oam037-raids-reuse
status: validating
branch: dudantas/oam-037-raids-reuse
base_branch: main
created: 2026-07-23
updated: 2026-07-23
related_pr: "76"
owned_paths:
  - docs/agents/tasks/active/OTH-20260723-oam037-raids-reuse.md
  - docs/oam-037-raids-reuse.md
  - tests/unit/game/oam_037_raids_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/lua/creature/raids.cpp
  - src/lua/creature/raids.hpp
  - tests/unit/game/CMakeLists.txt
optional_reads: []
---

# OAM-037 Raids target reuse proof

## Goal

Prove the bounded canonical `raids` runtime is already present in the clean Otheryn target and preserve it without importing unrelated boss encounters, generic creature AI/definitions, non-raid spawn scheduling, raid data expansion, Bosstiary, quest/cooldown, protocol/client, map, asset, schema or deployment work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T09:30:00+02:00
head: 0ddcc3f0b821fdd16b5605f2234ff8c80c0d88db
branch: dudantas/oam-037-raids-reuse
pr: 76
status: validating
context_routes:
  - lua-runtime
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260723-oam037-raids-reuse.md
  - docs/oam-037-raids-reuse.md
  - tests/unit/game/oam_037_raids_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e.
  - Canary OAM-037 preflight merged as 8bdeb2747356727df80a3b95073aa29a4dca7818 and selected canonical raids as a REUSE candidate.
  - Canary bounded target-proof plan merged as 817da293a141880f7090194699a4ac38e567a2fb.
  - Otheryn and the reviewed fresh upstream baseline share exact raids.cpp blob d46a549a341e0872474bd723b10d1208fa22da8c and raids.hpp blob 777558e3e199816bb596636fc7487c38c29224ee.
  - Semantic review maps registry load reload interval margin repeat periodic selection running state event ordering reset cleanup and announce single-spawn area-spawn script dispatch to the canonical raids roots.
  - Target uses DispatcherLane::Maintenance for periodic checks and raid event scheduling and handles initial subsequent and periodic scheduling failure without requiring a legacy donor import.
  - The reviewed older legacy Canary raids.cpp is not a stronger whole-module donor than the target and fresh upstream canonical roots.
  - PR 76 is the single bounded OAM-037 target owner and changes exactly four intended proof/task paths with no production path.
derived:
  - OAM-037 final disposition is raids REUSE if the bounded source-contract proof and exact-head target gates pass without production repair.
  - No maintained-client mutation is expected because the selected boundary is server-side raid orchestration and does not alter the wire contract.
unknown:
  - Exact final target CI Required and platform-gate evidence until PR gating completes.
  - Whether exact-head validation exposes a concrete raids-owned target defect requiring reclassification to ADAPT.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed.
rejected_hypotheses:
  - Infer final REUSE from blob identity alone; this package adds semantic source-contract proof for the owned raid lifecycle.
  - Import the divergent legacy raids.cpp wholesale; target and fresh upstream retain stronger maintenance-lane scheduling and scheduling-failure safeguards.
  - Expand OAM-037 into boss encounters generic spawns raid content parity Bosstiary quests or protocol/client work because those are separate ownership boundaries.
changed_paths:
  - docs/agents/tasks/active/OTH-20260723-oam037-raids-reuse.md
  - docs/oam-037-raids-reuse.md
  - tests/unit/game/oam_037_raids_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: exact-root and semantic target preflight
    result: PASS
    evidence: canonical target roots match the reviewed fresh upstream blobs and lifecycle semantics map to raids ownership
  - command: bounded source-contract proof construction
    result: PASS
    evidence: proof covers registry scheduler failure recovery lifecycle cleanup and all four canonical raid event kinds without production mutation
  - command: immutable-base changed-path audit
    result: PASS
    evidence: PR 76 changes exactly the four intended proof/task paths and no production path
blockers: []
next_action: Require exact-current-head CI and Required platform gates for PR 76, audit comments reviews review threads and target-main drift, then expected-head squash merge if all gates remain clean.
```
