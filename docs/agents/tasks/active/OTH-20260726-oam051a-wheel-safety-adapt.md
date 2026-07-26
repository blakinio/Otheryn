---
task_id: OTH-20260726-oam051a-wheel-safety-adapt
status: validating
branch: dudantas/oam-051a-wheel-safety-adapt
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_pr: "115"
owned_paths:
  - src/creatures/players/components/wheel/player_wheel.cpp
  - src/creatures/players/components/wheel/player_wheel.hpp
  - src/creatures/players/components/wheel/wheel_gems.cpp
  - src/creatures/players/components/wheel/wheel_gems.hpp
  - src/io/functions/iologindata_load_player.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/unit/players/oam_051_wheel_safety_adapt_test.cpp
  - tests/unit/players/CMakeLists.txt
  - docs/agents/tasks/active/OTH-20260726-oam051a-wheel-safety-adapt.md
  - docs/oam-051-wheel-safety-adapt.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/creatures/players/components/wheel/player_wheel.cpp
  - src/creatures/players/components/wheel/player_wheel.hpp
  - src/creatures/players/components/wheel/wheel_gems.cpp
  - src/creatures/players/components/wheel/wheel_gems.hpp
  - src/io/functions/iologindata_load_player.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/unit/players/CMakeLists.txt
optional_reads: []
---

# OAM-051A Wheel safety adaptation

## Goal

Adapt only the evidence-backed Wheel safety and state-integrity corrections selected by Canary OAM-051 preflight. Preserve Otheryn protocol-profile, persistence, Lua and test architecture. Do not import Wheel balance values, spell areas, combat effects, critical healing, stances, replacement spells, Hunting Task Shop behavior, client code, generated documentation or Canary-only validation tooling.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T09:36:00+02:00
head: 261397df8390122a555cd083889c99c879ca66dd
branch: dudantas/oam-051a-wheel-safety-adapt
pr: 115
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - real-tibia-parity
  - protocol
  - player-persistence
owned_paths:
  - src/creatures/players/components/wheel/player_wheel.cpp
  - src/creatures/players/components/wheel/player_wheel.hpp
  - src/creatures/players/components/wheel/wheel_gems.cpp
  - src/creatures/players/components/wheel/wheel_gems.hpp
  - src/io/functions/iologindata_load_player.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/unit/players/oam_051_wheel_safety_adapt_test.cpp
  - tests/unit/players/CMakeLists.txt
  - docs/agents/tasks/active/OTH-20260726-oam051a-wheel-safety-adapt.md
  - docs/oam-051-wheel-safety-adapt.md
proven:
  - Canary OAM-051 preflight merged as a4a35495d4a8dc047bd3315b95c9fb577ac597af after exact-head Ownership and full CI success.
  - Target task-start main is ff90e93d872b6b47720f711483a9832203d5258d and no other open Otheryn PR owns Wheel paths.
  - Donor hardening is pinned to Canary PR 220 squash 35ff51ac022e36d215db9d0fa86053b326a0bdf0.
  - OAM-051A implements atomic allocation validation, temple-only decrease enforcement, saturating point accounting, safe gem mutation and grade handling, stale-state cleanup, persisted blob validation, permanent-point load ordering and current-protocol malformed-input rejection.
  - The initial three-way application failed only on player_wheel.cpp; selective application accepted 23 of 25 hunks.
  - The rejected lifecycle hunk was semantically adapted to current Otheryn; the second rejected hunk required no change because the target already preserved active state on an invalid index.
  - Target-specific protocol-profile and test-manifest changes were preserved; no whole-file replacement was used.
  - Temporary materializer workflow and helper files were removed. Final PR scope is eight implementation/test paths plus task and report.
  - Existing Supreme Grade II cost 12000000 and all excluded balance/effect behavior remain unchanged; no WheelBalance or full-resonance helper was imported.
  - The generated test initially contained literal backslash-t sequences; commit 6fe767137b22e055df17c9024881b84577bd9f17 replaced them with valid C++ formatting.
  - Draft-head CI 30192888815 and Required 30192888751 succeeded on 6fe767137b22e055df17c9024881b84577bd9f17, but all affected build/test jobs were skipped because PR 115 remained draft.
  - PR 115 was marked ready for review on head 261397df8390122a555cd083889c99c879ca66dd with ten final changed paths and no temporary helper paths.
derived:
  - wheel-of-destiny ADAPT is bounded to safety and state integrity in OAM-051A.
  - Current protocol compatibility is preserved because existing action shapes are validated without adding an opcode or payload field.
  - This checkpoint commit must be treated as the first eligible exact-ready-head full validation, not as a scope change.
unknown:
  - Exact compile and focused-test outcome on the final ready head.
  - Whether repository formatters or platform builds isolate any target-specific integration defect.
  - Final discussion, review-thread and target-main drift state at merge time.
conflicts: []
first_failure:
  marker: player-wheel-donor-drift
  command: exact selected donor patch application
  result: FAIL_THEN_RESOLVED
  evidence: Initial three-way apply conflicted only in player_wheel.cpp; selective application accepted 23/25 hunks, target-specific lifecycle integration resolved one reject, and the other reject was already satisfied by target behavior.
rejected_hypotheses:
  - Bulk-copy the complete Canary Wheel subsystem.
  - Import WheelBalance values, full-resonance bonuses, combat effects or spell-area changes.
  - Import Hunting Task Shop or client changes in OAM-051A.
  - Replace Otheryn protocolgame.cpp or tests/unit/players/CMakeLists.txt wholesale.
  - Treat draft CI with skipped builds as final validation.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-oam051a-wheel-safety-adapt.md
  - docs/oam-051-wheel-safety-adapt.md
  - src/creatures/players/components/wheel/player_wheel.cpp
  - src/creatures/players/components/wheel/player_wheel.hpp
  - src/creatures/players/components/wheel/wheel_gems.cpp
  - src/creatures/players/components/wheel/wheel_gems.hpp
  - src/io/functions/iologindata_load_player.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/unit/players/CMakeLists.txt
  - tests/unit/players/oam_051_wheel_safety_adapt_test.cpp
validation:
  - command: fresh target main and open-PR ownership audit
    result: PASS
    evidence: Task-start main remains the exact base and no competing Wheel writer was found.
  - command: selected donor materialization and semantic rebase
    result: PASS
    evidence: All approved safety/state changes are present; target-specific conflict handling is recorded and temporary machinery is removed.
  - command: exact final changed-path audit
    result: PASS
    evidence: PR 115 contains only the eight approved implementation/test paths plus task and report.
  - command: parity-exclusion audit
    result: PASS
    evidence: Task Shop, WheelBalance, full resonance, spell areas, combat effects and legacy game parser changes remain absent.
  - command: draft-head CI and Required
    result: PASS_WITH_SKIPS
    evidence: CI 30192888815 and Required 30192888751 succeeded, but build, test and formatter jobs were skipped while the PR was draft.
  - command: exact-ready-head full affected gates
    result: NOT_RUN
    evidence: PR 115 is ready; this checkpoint commit must trigger full affected CI and Required on its resulting exact head.
blockers:
  - exact-ready-head full CI and Required
  - clean discussion, review-thread and target-main drift audit
next_action: Inspect the exact-ready-head full CI and Required triggered by this checkpoint, repair only isolated OAM-051A failures, then audit and expected-head squash merge.
```
