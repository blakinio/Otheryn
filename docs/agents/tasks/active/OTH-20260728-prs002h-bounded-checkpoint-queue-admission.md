---
task_id: OTH-20260728-prs002h-bounded-checkpoint-queue-admission
status: review
branch: dudantas/prs-002h-bounded-checkpoint-queue-admission
base_branch: main
start_sha: 7d6e4763377ee150e7ce44cfd29c60ce63c62760
created: 2026-07-28
updated: 2026-07-28
related_issue: "183"
related_pr: "184"
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/player_checkpoint_attempt_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260728-prs002h-bounded-checkpoint-queue-admission.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/lib/thread/thread_pool.hpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/player_checkpoint_attempt_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
---

# PRS-002H bounded checkpoint queue admission

## Goal

Bound asynchronous player-checkpoint admission before work is detached to the shared thread pool, while preserving exact-generation dirty ownership when capacity is exhausted.

## Accepted target contract

At most the named runtime capacity may be admitted at once. Queue-full rejection releases only the matching in-flight generation, keeps it dirty, consumes no save-failure budget, returns rejection to `savePlayer()` and requires a later explicit scheduling request. An admitted slot is released on every task exit and before a success follow-up is scheduled.

## Implemented behavior

- `PlayerPersistenceState::abandonCheckpoint(generation)` rejects stale generations, releases the exact in-flight owner and preserves dirty/failure state;
- `PlayerCheckpointQueueAdmission` uses atomic compare/exchange with default capacity `1024` and injectable smaller capacities;
- `tryAdmitPlayerCheckpoint` abandons the exact generation only when admission is full;
- `SaveManager` acquires before `ThreadPool::detach_task`, returns `false` on overload and rolls back admission if submission throws;
- `PlayerCheckpointQueueSlot` releases on every worker exit and is released early before a successful follow-up;
- focused tests cover rejection, explicit retry, concurrent capacity, stale abandonment, slot reuse and source ordering.

## Rollback plan

Revert the feature merge. No schema, database data, KV data, credentials, deployment state or generated assets are changed.

## Explicit non-goals

- no blocking producer or unbounded backlog;
- no timer, automatic retry, backoff or replay after admission rejection;
- no Prometheus/ostream export, oldest-dirty-age tracking or alerting;
- no database/KV failure injection or production access;
- no PRS-003, PRS-004, PRS-005 or PRS-006 implementation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-28T23:04:00+02:00
head: deee1117282b4c6df7f3c4e17d528ecf09f9d27d
branch: dudantas/prs-002h-bounded-checkpoint-queue-admission
pr: 184
status: validating
context_routes:
  - production-resilience
  - player-persistence
  - save-scheduling
  - queue-overload
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/player_checkpoint_attempt_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260728-prs002h-bounded-checkpoint-queue-admission.md
proven:
  - PRS-002D through PRS-002G are merged and lifecycle-archived.
  - The feature branch started from main 7d6e4763377ee150e7ce44cfd29c60ce63c62760 with no conflicting open PR.
  - Admission is acquired before detach and queue-full abandonment preserves dirty state without incrementing failures.
  - savePlayer propagates admission rejection instead of returning a false success.
  - The current slot is released before a newer generation follow-up.
  - Focused tests cover capacity one overload/retry, 32-way concurrent admission against capacity three and exact-generation abandonment.
derived:
  - This package bounds player-checkpoint submissions without replacing or globally bounding the shared ThreadPool.
unknown:
  - Exact-head compile, focused test runtime and full platform CI results.
conflicts: []
first_failure: null
rejected_hypotheses:
  - expand or replace the shared thread pool
  - block the producer until capacity becomes available
  - count admission rejection as a database save failure
  - hide queue rejection behind a successful savePlayer result
  - add automatic retry or operational metrics in this package
changed_paths:
  - docs/agents/tasks/active/OTH-20260728-prs002h-bounded-checkpoint-queue-admission.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/save_manager.hpp
  - tests/unit/game/player_checkpoint_attempt_test.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
validation:
  - command: governance, source and conflict preflight
    result: PASS
    evidence: Main 7d6e4763377ee150e7ce44cfd29c60ce63c62760; no open PR owned the selected paths.
  - command: deterministic source audit
    result: PASS
    evidence: Exact-generation abandon, bounded CAS admission, pre-detach acquisition, submission rollback, early follow-up release and rejection propagation are present.
  - command: changed-path audit
    result: PASS
    evidence: Branch is behind_by zero and changes exactly nine owned paths.
  - command: exact-head repository CI
    result: NOT_RUN
    evidence: PR 184 must complete CI, Required and autofix on its final head.
blockers: []
next_action: Inspect PR 184 exact-head CI and fix only concrete compile, test or formatting failures.
```
