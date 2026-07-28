---
task_id: OTH-20260728-prs002g-commit-before-ack-crash-evidence
status: review
branch: dudantas/prs-002g-commit-before-ack-crash-evidence
base_branch: main
start_sha: d46e39d6f28557b85f6f4c7e78dc707bb287b77f
created: 2026-07-28
updated: 2026-07-28
related_issue: "179"
related_pr: "180"
owned_paths:
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_checkpoint_commit_before_ack_crash_it.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/player_persistence_state.hpp
  - tests/integration/main.cpp
  - tests/integration/test_database.hpp
  - tests/integration/database/player_checkpoint_kv_post_commit_failure_it.cpp
---

# PRS-002G commit-before-ack crash evidence

## Goal

Prove with a fresh test process and disposable MariaDB that an InnoDB player-domain probe can commit before the process terminates inside the save attempt, preventing any in-memory checkpoint acknowledgement from running.

## Accepted target contract

A process crash after durable SQL commit but before `executePlayerCheckpointAttempt` returns must preserve the committed SQL value. The crashed `PlayerPersistenceState` and its dirty/in-flight generations are process memory only; a newly constructed state cannot infer them or request an automatic retry.

## Current behavior inventory

- `executePlayerCheckpointAttempt` invokes the save callback before calling `acknowledgeSuccess`.
- `PlayerPersistenceState` stores dirty, acknowledged and in-flight generations only in memory.
- integration tests use a disposable MariaDB instance and execute serially.
- GoogleTest threadsafe death tests re-execute a fresh test process instead of sharing the parent's database connection.

## Failure-injection plan

- create one dedicated InnoDB probe table with value `100`;
- start one dirty checkpoint generation inside a threadsafe death-test child;
- commit an update to `200` through `DBTransaction::executeWithinTransaction`;
- call `std::_Exit` immediately inside the save callback, before acknowledgement;
- prove from the parent that value `200` remains durable;
- construct a fresh persistence state and prove it contains no dirty/in-flight/acknowledged generation.

## Rollback plan

Delete the integration test, its CMake registration, the bounded contract note and this task record. The fixture drops its dedicated table; no production schema, data or deployment state requires reversal.

## Explicit non-goals

- no production/shared database access or credentials;
- no production crash hook, scheduler, signal or restart-policy change;
- no automatic whole-world rollback or retry;
- no SQL/KV completeness or RPO claim;
- no queue overload, operational metrics, PRS-003, PRS-004 or PRS-006 work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-28T22:21:00+02:00
head: aeb8fc10943fb39b9f5085d403bddaf8a2defdb8
branch: dudantas/prs-002g-commit-before-ack-crash-evidence
pr: 180
status: validating
context_routes:
  - production-resilience
  - player-persistence
  - process-crash
  - integration-testing
  - agent-governance
owned_paths:
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_checkpoint_commit_before_ack_crash_it.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
proven:
  - PRS-002E and PRS-002F are merged and lifecycle-archived.
  - The save callback runs before checkpoint success acknowledgement.
  - PlayerPersistenceState generations are memory-only.
  - The death-test source exits inside the save callback only after DBTransaction reports commit success.
  - The parent asserts durable value 200 and a fresh clean persistence state.
derived:
  - A threadsafe death test is the smallest cross-platform fresh-process crash injection without production hooks.
unknown:
  - Exact-head compile, death-test runtime and platform results.
conflicts: []
first_failure: null
rejected_hypotheses:
  - add a production crash failpoint
  - use an inherited forked database connection
  - claim automatic retry or measured RPO
changed_paths:
  - docs/agents/tasks/active/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_checkpoint_commit_before_ack_crash_it.cpp
validation:
  - command: governance and conflict preflight
    result: PASS
    evidence: Task started from main d46e39d6f28557b85f6f4c7e78dc707bb287b77f; no open PR owns the selected paths.
  - command: deterministic source audit
    result: PASS
    evidence: Dedicated InnoDB table, threadsafe child, explicit post-commit exit codes, parent durability query and fresh-state assertions are present.
  - command: exact-head repository CI
    result: NOT_RUN
    evidence: PR 180 must complete CI, Required and autofix on its final head.
blockers: []
next_action: Inspect PR 180 exact-head CI and fix only concrete compile, death-test or formatting failures.
```