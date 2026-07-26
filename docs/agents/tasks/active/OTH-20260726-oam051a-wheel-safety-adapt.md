---
task_id: OTH-20260726-oam051a-wheel-safety-adapt
status: implementing
branch: dudantas/oam-051a-wheel-safety-adapt
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_pr: ""
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
  - tools/ai-agent/oam_051a_materialize.py
  - .github/workflows/oam-051a-materialize.yml
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
updated_at: 2026-07-26T02:15:00+02:00
head: ff90e93d872b6b47720f711483a9832203d5258d
branch: dudantas/oam-051a-wheel-safety-adapt
pr: null
status: implementing
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
  - tools/ai-agent/oam_051a_materialize.py
  - .github/workflows/oam-051a-materialize.yml
proven:
  - Canary OAM-051 preflight merged as a4a35495d4a8dc047bd3315b95c9fb577ac597af after exact-head Ownership and full CI success.
  - Target task-start main is ff90e93d872b6b47720f711483a9832203d5258d and no active Otheryn PR owns Wheel paths.
  - Donor hardening is pinned to Canary PR 220 squash commit 35ff51ac022e36d215db9d0fa86053b326a0bdf0.
  - OAM-051A authorizes atomic allocation validation, temple-only decrease enforcement, saturating point accounting, safe gem mutation/grade/index/state handling, persisted-state validation, permanent-point load ordering, current-protocol malformed-input rejection and focused tests.
  - Otheryn protocolgame.cpp and players test manifest contain target-specific prior OAM changes and require semantic rebasing.
  - Hunting Task Shop PR 230, current 15.25 values/effects, full-resonance bonuses, spell areas, critical healing, stances and replacement spells are explicitly deferred.
derived:
  - The smallest coherent target delivery is wheel-of-destiny ADAPT limited to safety/state integrity.
  - A temporary branch-scoped materializer is required because connector writes cannot patch large source files in place; it must fail closed, commit only the approved paths and be removed before final validation.
unknown:
  - Whether the selected donor hunks apply cleanly to current Otheryn after upstream and prior OAM drift.
  - Exact compile/test repairs required after semantic integration.
conflicts: []
first_failure:
  marker: none
  evidence: Implementation has not run yet.
rejected_hypotheses:
  - Bulk-copy the complete Canary Wheel subsystem.
  - Import WheelBalance values, full-resonance bonuses, combat effects or spell-area changes.
  - Import Hunting Task Shop or client changes in OAM-051A.
  - Replace Otheryn protocolgame.cpp or tests/unit/players/CMakeLists.txt wholesale.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-oam051a-wheel-safety-adapt.md
validation:
  - command: fresh target main and open-PR ownership audit
    result: PASS
    evidence: main remains ff90e93d872b6b47720f711483a9832203d5258d and no live Wheel writer exists
  - command: selected donor and exclusion-boundary review
    result: PASS
    evidence: safety/state hunks are separated from parity-sensitive values/effects and Task Shop
  - command: materialize selected target adaptation
    result: NOT_RUN
    evidence: temporary exact-branch workflow and fail-closed materializer are being staged
blockers: []
next_action: Run the branch-scoped OAM-051A materializer, inspect its exact changed paths and first failure, then remove all temporary materializer files before opening the target draft PR.
```
