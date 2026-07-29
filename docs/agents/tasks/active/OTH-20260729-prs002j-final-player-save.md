---
task_id: OTH-20260729-prs002j-final-player-save
status: review
branch: dudantas/prs-002j-final-player-save
base_branch: main
start_sha: 8fb339146897a3b9695f0788a63d6df199a253a4
created: 2026-07-29
updated: 2026-07-29
related_issue: "191"
related_pr: null
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260729-prs002j-final-player-save.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/creatures/players/player.cpp
  - src/server/network/protocol/protocolgame.cpp
  - src/game/game.cpp
---

# PRS-002J bounded final player save

## Goal

Provide one synchronous, finite-attempt final save for the exact live `Player` object after logout fields are finalized, while waiting only a bounded interval for an older asynchronous checkpoint to release generation ownership.

## Current behavior inventory

- normal and forced logout converge on `Game::removeCreature(..., true)` and `Player::onRemoveCreature`;
- `Player::onRemoveCreature` finalizes login position and `lastLogout`, then calls `SaveManager::savePlayer` while the exact object still reports online;
- shutdown removes every player before the later `saveAll`, so per-player removal is the effective shutdown final-save boundary;
- `PlayerPersistenceState` previously coalesced an in-flight checkpoint but had no bounded wait-and-claim operation for final ownership.

## Accepted target contract

- final save marks the exact owner dirty after logout fields are finalized;
- an older in-flight generation may finish, but final ownership waits at most five seconds;
- the newest dirty generation is claimed atomically after the older owner releases it;
- final persistence executes synchronously on the exact `Player` object;
- at most two exact-generation attempts are allowed so one concurrent newer mutation may be captured without an unbounded retry loop;
- timeout, save failure, thrown save, rejected acknowledgement or a still-dirty state after the finite attempt budget returns failure and is logged;
- normal logout and forced shutdown removal share the existing player-removal callback and are recognized from the finalized logout timestamp;
- channel handoff and stale-writer fencing remain PRS-004.

## Implemented behavior

- `PlayerPersistenceState::beginFinalCheckpoint` uses a condition variable to wait for existing ownership without polling or stealing it;
- acknowledgement and abandonment notify bounded final waiters after releasing the exact generation;
- `SaveManager::savePlayer` recognizes the already-finalized logout lifecycle through `lastLogout >= lastLoginSaved` on the still-online object;
- `SaveManager::savePlayerFinal` marks the final state dirty, waits at most five seconds, and executes at most two synchronous attempts through `executePlayerCheckpointAttempt`;
- final attempts reuse the existing exact-generation acknowledgement, counters, gauges, latency measurement and fixed low-cardinality failure reasons;
- no final attempt calls `detach_task` or `scheduleDirtyPlayer`;
- timeout, failed/thrown persistence, acknowledgement rejection and attempt-budget exhaustion are logged and returned as failure.

## Failure-injection evidence

- a held generation 1 with generation 2 dirty is released while another thread waits; the waiter atomically claims generation 2 and clears it successfully;
- a one-millisecond timeout preserves the old in-flight generation, dirty generation 2 and zero acknowledgement;
- source-contract tests prove finite constants, synchronous final execution, finalized-logout dispatch and shutdown ordering.

## Rollback plan

Revert this bounded feature merge. No schema, database data, KV data, credentials, deployment state or generated assets are changed.

## Explicit non-goals

- no database-outage state machine;
- no channel-handoff ownership or session/revision fencing;
- no retry timer, backoff, silent replay or automatic rollback;
- no production RPO or save-latency guarantee;
- no database, KV, schema, credential or deployment change.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T09:18:00+02:00
head: da5bf10d6999ff2ed91341f383871ad0a234d660
head_scope: implementation before PR-link checkpoint commit
branch: dudantas/prs-002j-final-player-save
pr: null
status: validating
context_routes:
  - production-resilience
  - player-persistence
  - logout
  - shutdown
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260729-prs002j-final-player-save.md
proven:
  - PRS-002I is terminally archived on main 8fb339146897a3b9695f0788a63d6df199a253a4.
  - Logout and forced shutdown removal converge on Player::onRemoveCreature with isLogout true.
  - Player::onRemoveCreature updates loginPosition and lastLogout before calling SaveManager::savePlayer.
  - Shutdown removes players before saveAll, so the removal callback is the per-player shutdown final-save boundary.
  - The implementation changes exactly seven declared paths and is behind main by zero.
  - Final ownership waits on a condition variable and never steals or acknowledges an older owner.
  - The final save is synchronous, exact-owner, limited to five seconds per claim and two attempts.
  - Deterministic tests cover generation handoff, timeout preservation and source wiring.
derived:
  - Recognizing finalized logout state inside SaveManager preserves the existing Player callback while preventing another detached logout checkpoint.
  - Two finite attempts can capture one mutation concurrent with the first final save without creating an automatic retry policy.
unknown:
  - Exact-head compile, focused runtime tests and full platform CI results.
conflicts: []
first_failure:
  marker: no failing validation observed before CI
  evidence: Source and changed-path audits agree with the bounded contract; exact-head CI has not run yet.
rejected_hypotheses:
  - detach another asynchronous logout save
  - wait without a fixed timeout
  - cancel or steal an in-flight generation
  - modify the large player callback when its existing ordering already provides a stable dispatch boundary
  - add session fencing or database-outage behavior
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs002j-final-player-save.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/save_manager.hpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
validation:
  - command: governance and ownership preflight
    result: PASS
    evidence: Task starts from main 8fb339146897a3b9695f0788a63d6df199a253a4 with issue 191 and seven final owned paths.
  - command: live logout and shutdown source audit
    result: PASS
    evidence: ProtocolGame logout and forced Player removal both reach Player::onRemoveCreature; logout fields precede SaveManager dispatch and shutdown removes players before saveAll.
  - command: deterministic implementation audit
    result: PASS
    evidence: Bounded condition-variable ownership, two-attempt synchronous final path, exact-generation helper reuse and deterministic tests are present.
  - command: exact-head repository CI
    result: NOT_RUN
    evidence: A feature PR must run full applicable CI, Required and autofix on its exact final head.
blockers: []
next_action: Open the PR, inspect exact-head CI, and fix only concrete compile, test or formatting failures within the seven declared paths.
```
