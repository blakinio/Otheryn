---
task_id: OTH-20260728-prs002h-bounded-checkpoint-queue-admission
status: active
branch: dudantas/prs-002h-bounded-checkpoint-queue-admission
base_branch: main
start_sha: 7d6e4763377ee150e7ce44cfd29c60ce63c62760
created: 2026-07-28
updated: 2026-07-28
related_issue: "183"
related_pr: null
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/player_checkpoint_attempt_test.cpp
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
---

# PRS-002H bounded checkpoint queue admission

## Goal

Bound asynchronous player-checkpoint admission before work is detached to the shared thread pool, while preserving exact-generation dirty ownership when capacity is exhausted.

## Accepted target contract

At most the configured compile-time runtime capacity may be admitted at once. Queue-full rejection must release only the matching in-flight generation, keep it dirty, consume no save-failure budget and require a later explicit scheduling request. An admitted slot must be released on every task exit and before a success follow-up is scheduled.

## Implementation plan

- add `PlayerPersistenceState::abandonCheckpoint(generation)`;
- add an atomic, unit-testable queue-admission helper with named default capacity `1024`;
- integrate admission into `SaveManager::scheduleDirtyPlayer` before `ThreadPool::detach_task`;
- roll back admission and in-flight ownership if detach submission throws;
- release the current slot before generation-safe success follow-up;
- add focused state/admission/concurrency tests;
- document bounded overload behavior and defer operational metrics to PRS-002I.

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
updated_at: 2026-07-28T22:55:00+02:00
head: 7d6e4763377ee150e7ce44cfd29c60ce63c62760
branch: dudantas/prs-002h-bounded-checkpoint-queue-admission
pr: null
status: implementing
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
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260728-prs002h-bounded-checkpoint-queue-admission.md
proven:
  - PRS-002D through PRS-002G are merged and lifecycle-archived.
  - SaveManager currently detaches every accepted dirty generation to the shared unbounded ThreadPool wrapper.
  - PlayerPersistenceState has no non-failure transition for queue admission rejection.
  - No open PR owns the selected paths.
derived:
  - A bounded admission counter plus matching-generation abandon transition is the smallest package that prevents unbounded checkpoint backlog without adding retry policy.
unknown:
  - Exact-head compile, concurrency test and full platform CI results.
conflicts: []
first_failure: null
rejected_hypotheses:
  - expand or replace the shared thread pool
  - block the producer until capacity becomes available
  - count admission rejection as a database save failure
  - add automatic retry or operational metrics in this package
changed_paths:
  - docs/agents/tasks/active/OTH-20260728-prs002h-bounded-checkpoint-queue-admission.md
validation:
  - command: governance, source and conflict preflight
    result: PASS
    evidence: Current main 7d6e4763377ee150e7ce44cfd29c60ce63c62760; no open PR owns the selected paths.
blockers: []
next_action: Implement the state transition, bounded admission helper, SaveManager integration, focused tests and architecture evidence.
```
