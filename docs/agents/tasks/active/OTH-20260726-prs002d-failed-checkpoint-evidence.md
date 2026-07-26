---
task_id: OTH-20260726-prs002d-failed-checkpoint-evidence
status: ready
branch: dudantas/prs-002d-failed-checkpoint-evidence
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "158"
related_pr: "none"
owned_paths:
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/player_persistence_state.hpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/agents/tasks/active/OTH-20260726-prs002d-failed-checkpoint-evidence.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/player_persistence_state.hpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
optional_reads:
  - src/io/iologindata.cpp
  - docs/architecture/oam-004d-player-save-failure-propagation.md
---

# PRS-002D failed checkpoint acknowledgement evidence

## Goal

Add deterministic controlled-failure evidence for the merged PRS-002 generation-aware player save path without changing production database behavior, adding retry timers or starting PRS-003 outage handling.

## Scope

The task must prove that a failed asynchronous persistence attempt acknowledges only its captured generation, leaves the exact Player object dirty, schedules no implicit retry, permits a later explicit retry and does not block another Player object's successful state transition.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T23:52:00+02:00
head: a2f606d90d6c7887b103495ef05b8742e98b6836
branch: dudantas/prs-002d-failed-checkpoint-evidence
pr: none
status: ready
context_routes:
  - production-resilience
  - player-persistence
  - save-scheduling
  - failure-injection
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/player_persistence_state.hpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/agents/tasks/active/OTH-20260726-prs002d-failed-checkpoint-evidence.md
proven:
  - PRS-002 discovery, pure generation state, generation-aware asynchronous save scheduling and bounded PlayerStorage dirty marking are merged and lifecycle-archived through main commit a2f606d90d6c7887b103495ef05b8742e98b6836.
  - PlayerPersistenceState already preserves dirty state after matching failure and rejects stale acknowledgement.
  - SaveManager already schedules a follow-up only after successful acknowledgement when a newer generation remains dirty.
  - PRS-002C dirty marking does not schedule work by itself.
  - Issue 158 owns only deterministic failure evidence and a minimal test seam around the asynchronous per-player persistence attempt.
derived:
  - The smallest safe package should inject the persistence result at the SaveManager attempt boundary rather than simulate a production database outage.
  - Failure-path tests must distinguish no implicit retry from a later explicit save request that is allowed to retry the still-dirty state.
  - Independent exact Player ownership states can prove one failing player does not block another without introducing a production queue policy.
unknown:
  - The smallest seam shape that avoids exposing production-only test hooks or changing IOLoginData behavior.
  - Whether existing unit fixtures can construct two independent Player objects and observe scheduling without binding the complete database and KV graph.
  - Whether the failure evidence belongs entirely in a pure scheduling helper or requires a narrow SaveManager collaborator.
conflicts: []
first_failure:
  marker: failure-injection-test-seam-not-yet-defined
  evidence: Main proves state transitions and successful scheduling, but there is no deterministic seam that forces a per-player asynchronous persistence result to fail without using a real database failure.
rejected_hypotheses:
  - Fail a production or shared development database to obtain evidence.
  - Add automatic retry, backoff, a checkpoint interval or queue expansion in the same package.
  - Begin PRS-003 outage-state handling, PRS-004 fencing or automatic query replay.
  - Broaden mutation instrumentation beyond merged PlayerStorage coverage.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-prs002d-failed-checkpoint-evidence.md
validation:
  - command: PRS-002C exact-head CI 30220979446, Required 30220979380 and autofix.ci 30220979368
    result: PASS
    evidence: Bounded PlayerStorage mutation coverage passed full CI before feature merge dba32b6390b933774499c5b4be91ac59ea7ac101 and lifecycle merge a2f606d90d6c7887b103495ef05b8742e98b6836.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/OTH-20260726-prs002d-failed-checkpoint-evidence.md --require-checkpoint
    result: NOT_RUN
    evidence: Run after this active task is materialized on the branch.
blockers: []
next_action: Read the required routing documents, inventory the current SaveManager asynchronous attempt and unit-test seams, then choose the smallest deterministic failure-injection design before modifying runtime code.
```
