---
task_id: OTH-20260729-prs002j-final-player-save
status: implementation
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
  - src/creatures/players/player.cpp
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
- `Player::onRemoveCreature` finalizes login position and `lastLogout`, then calls the generic `SaveManager::savePlayer` path;
- while the player still appears online in that callback, the generic path may detach asynchronous work;
- shutdown removes every player before the later `saveAll`, so per-player removal is the effective shutdown final-save boundary;
- `PlayerPersistenceState` can coalesce an in-flight checkpoint but has no bounded wait-and-claim operation for final ownership.

## Accepted target contract

- final save marks the exact owner dirty after logout fields are finalized;
- an older in-flight generation may finish, but final ownership waits only a fixed finite interval;
- the newest dirty generation is claimed atomically after the older owner releases it;
- final persistence executes synchronously on the exact `Player` object;
- at most two exact-generation attempts are allowed so one concurrent newer mutation may be captured without an unbounded retry loop;
- timeout, save failure, thrown save, rejected acknowledgement or a still-dirty state after the finite attempt budget returns failure and is logged;
- normal logout and forced shutdown removal share the same final-save callback;
- channel handoff and stale-writer fencing remain PRS-004.

## Failure-injection plan

- hold generation 1 in flight while generation 2 becomes dirty, then prove a waiting final claim atomically receives generation 2 after generation 1 settles;
- hold generation 1 beyond a short deterministic timeout and prove the final claim fails without releasing or acknowledging the old owner;
- source-contract tests prove logout uses the synchronous final path and that the final path has a finite wait and attempt budget.

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
updated_at: 2026-07-29T09:12:00+02:00
head: 8fb339146897a3b9695f0788a63d6df199a253a4
head_scope: task start from exact main
branch: dudantas/prs-002j-final-player-save
pr: null
status: implementing
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
  - src/creatures/players/player.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260729-prs002j-final-player-save.md
proven:
  - PRS-002I is terminally archived on main 8fb339146897a3b9695f0788a63d6df199a253a4.
  - Logout and forced shutdown removal converge on Player::onRemoveCreature with isLogout true.
  - Player::onRemoveCreature updates loginPosition and lastLogout before calling the current generic save path.
  - Shutdown removes players before saveAll, so the removal callback is the per-player shutdown final-save boundary.
derived:
  - A bounded wait-and-claim state transition is required to avoid racing a final synchronous save against existing checkpoint ownership.
  - Two finite attempts are sufficient to capture at most one mutation concurrent with the first final save without creating an automatic retry policy.
unknown:
  - Exact-head compile, focused runtime tests and platform CI results.
conflicts: []
first_failure:
  marker: no implementation failure observed during preflight
  evidence: The task branch starts cleanly from main and no PRS-002J issue, branch or PR existed.
rejected_hypotheses:
  - detach another asynchronous logout save
  - wait without a fixed timeout
  - cancel or steal an in-flight generation
  - add session fencing or database-outage behavior
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs002j-final-player-save.md
validation:
  - command: governance and ownership preflight
    result: PASS
    evidence: Task starts from main 8fb339146897a3b9695f0788a63d6df199a253a4 with issue 191 and eight declared paths.
  - command: live logout and shutdown source audit
    result: PASS
    evidence: ProtocolGame logout and forced Player removal both reach Player::onRemoveCreature; shutdown removes players before saveAll.
blockers: []
next_action: Implement the bounded final-checkpoint claim, synchronous final save path, logout wiring, focused tests and contract evidence on the declared branch.
```
