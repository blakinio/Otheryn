---
task_id: OTH-20260726-prs002d-failed-checkpoint-evidence
status: active
branch: dudantas/prs-002d-failed-checkpoint-evidence
base_branch: main
created: 2026-07-26
updated: 2026-07-27
related_issue: "158"
related_pr: "none"
owned_paths:
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/CMakeLists.txt
  - tests/unit/game/player_checkpoint_attempt_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260726-prs002d-failed-checkpoint-evidence.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/operations/backup-and-pitr-policy.md
  - docs/operations/production-recovery-runbook.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
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

## Accepted target contract

A failed asynchronous persistence attempt must acknowledge only its captured generation, leave the exact Player object dirty, schedule no implicit retry, permit a later explicit retry and remain independent from another Player object's successful state transition.

## Failure-injection plan

- inject a `false` persistence result at a database-independent attempt boundary;
- inject an exception at the same boundary;
- hold one failing attempt while another exact-owner state completes successfully;
- mutate during a successful attempt and prove exactly one follow-up signal remains required;
- retain source-contract evidence that SaveManager schedules follow-up only after successful acknowledgement.

## Rollback plan

The package adds one pure header helper and focused tests, then routes the existing SaveManager result/acknowledgement sequence through that helper. Rollback is deletion of the helper/tests plus restoration of the previous inline SaveManager block; no schema, stored data, deployment state or production configuration requires reversal.

## Explicit non-goals

- no real database outage or production credentials;
- no retry timer, backoff, periodic checkpoint or queue expansion;
- no metrics backend or RPO claim;
- no broader mutation instrumentation beyond merged PlayerStorage coverage;
- no PRS-003 outage state, PRS-004 fencing or automatic query replay;
- no claim that commit-before-ack, queue overload or process-crash evidence is complete.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T09:04:00+02:00
head: 9703da845384423ad85883216bf8853642c21bcd
branch: dudantas/prs-002d-failed-checkpoint-evidence
pr: none
status: implementing
context_routes:
  - production-resilience
  - player-persistence
  - save-scheduling
  - failure-injection
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/CMakeLists.txt
  - tests/unit/game/player_checkpoint_attempt_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260726-prs002d-failed-checkpoint-evidence.md
proven:
  - PRS-002A through PRS-002C are merged and lifecycle-archived on main.
  - PlayerPersistenceState preserves dirty state after matching failure and rejects stale acknowledgement.
  - SaveManager currently schedules a follow-up only after successful acknowledgement when a newer generation remains dirty.
  - PRS-002C dirty marking does not schedule work by itself.
  - Issue 158 authorizes only deterministic failed-attempt evidence and a minimal test seam.
  - Current main is 9703da845384423ad85883216bf8853642c21bcd and open PRs 162 and 165 do not own the selected paths.
  - The stale branch state was preserved as backup/PRS-002D-pre-rebase-20260727 before resetting the working branch to current main.
derived:
  - A pure attempt-result helper is the smallest seam that avoids production database failure and test-only global hooks.
  - Returning acknowledgement and follow-up decisions from the helper permits deterministic tests without constructing the complete DI/database graph.
unknown:
  - Repository compile, formatting and full CTest result for the selected helper integration.
conflicts: []
first_failure:
  marker: local-github-clone-unavailable
  result: CONTAINED
  evidence: Sandbox DNS cannot resolve github.com; source work continues through the authorized GitHub connector and local standalone C++ validation.
rejected_hypotheses:
  - fail a production or shared development database
  - expose a mutable global test hook in SaveManager
  - add automatic retry or queue policy in this package
  - broaden Player mutation coverage
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-prs002d-failed-checkpoint-evidence.md
validation:
  - command: standalone C++20 attempt-helper prototype with -Wall -Wextra -Werror
    result: PASS
    evidence: Boolean failure, exception, explicit retry, newer mutation and independent-state scenarios passed locally.
  - command: repository checkpoint validator
    result: NOT_RUN
    evidence: Run through repository CI after implementation is materialized.
blockers: []
next_action: Add the pure attempt helper, integrate the existing SaveManager acknowledgement path, register focused tests and update the bounded PRS-002 contract evidence.
```
