---
task_id: OTH-20260727-prs002e-sql-failure-rollback-evidence
status: active
branch: dudantas/prs-002e-sql-failure-rollback-evidence
base_branch: main
created: 2026-07-27
updated: 2026-07-27
related_issue: "168"
related_pr: "none"
owned_paths:
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_checkpoint_sql_failure_it.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260727-prs002e-sql-failure-rollback-evidence.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/operations/backup-and-pitr-policy.md
  - docs/operations/production-recovery-runbook.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/database/database.hpp
  - src/io/iologindata.cpp
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - tests/integration/database/world_persistence_it.cpp
optional_reads:
  - docs/architecture/oam-004d-player-save-failure-propagation.md
---

# PRS-002E SQL failure rollback evidence

## Goal

Add one real, disposable MariaDB failure-injection proof for the merged player checkpoint acknowledgement path without changing production code, schema, credentials or deployment behavior.

## Accepted target contract

A failed SQL statement inside an InnoDB transaction used as a player-checkpoint persistence attempt must roll back earlier writes, return a failed checkpoint outcome, leave the captured exact-owner generation dirty, release the in-flight generation, request no implicit retry and permit a later explicit generation to commit successfully.

## Failure-injection plan

- create and remove one dedicated disposable InnoDB probe table in the integration-test database;
- update a sentinel row and then execute a deliberately invalid statement inside `DBTransaction::executeWithinTransaction`;
- route the failed transaction result through `executePlayerCheckpointAttempt`;
- prove the sentinel value rolled back and the state remains dirty with one failure;
- issue one later explicit generation and prove a valid transaction commits and clears the state.

## Rollback plan

Delete the integration test, its CMake registration, the bounded contract note and this task record. The test drops its probe table in teardown; no repository schema, production data or deployment state requires reversal.

## Explicit non-goals

- no production/shared database access or credentials;
- no modification of `IOLoginData::savePlayer`, `SaveManager`, `Database` or `DBTransaction` production behavior;
- no persistent schema migration;
- no retry timer, backoff, queue policy, metrics backend or RPO claim;
- no KV post-commit failure, process-crash or queue-overload evidence;
- no PRS-003 outage state, PRS-004 fencing or automatic query replay.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T10:12:00+02:00
head: 92bcaeb41a90a5beb84ac972a93d65e9e879fda1
branch: dudantas/prs-002e-sql-failure-rollback-evidence
pr: none
status: validating
context_routes:
  - production-resilience
  - player-persistence
  - sql-transactions
  - failure-injection
  - integration-testing
  - agent-governance
owned_paths:
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_checkpoint_sql_failure_it.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260727-prs002e-sql-failure-rollback-evidence.md
proven:
  - PRS-002D is merged and lifecycle-archived on main.
  - DBTransaction rolls back when its callback returns false.
  - Integration tests initialize a disposable MariaDB database through TestDatabase.
  - The existing checkpoint-attempt helper maps a false persistence result to exact-generation failure acknowledgement without an implicit follow-up.
  - The integration test creates and drops one dedicated InnoDB probe table, performs one valid update followed by an invalid-column statement and inspects the persisted sentinel after rollback.
  - The same test package exercises one later explicit generation with a valid transaction and verifies clean acknowledgement after commit.
  - Open PRs 162 and 165 do not own the selected paths.
derived:
  - A dedicated integration probe is the smallest real-SQL evidence package and requires no production seam.
unknown:
  - Exact-head integration-test, compile, formatting and platform results.
conflicts: []
first_failure: null
rejected_hypotheses:
  - fail a production or shared database
  - add a mutable global SQL failure hook
  - alter transaction or save runtime behavior
  - combine KV, crash and queue-overload evidence
changed_paths:
  - docs/agents/tasks/active/OTH-20260727-prs002e-sql-failure-rollback-evidence.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_checkpoint_sql_failure_it.cpp
validation:
  - command: source and conflict preflight
    result: PASS
    evidence: Current main ec5038a7f132a4c2ed030edda38a56b5b1ec916a; selected paths do not overlap open PRs.
  - command: deterministic test-structure audit
    result: PASS
    evidence: The fixture owns a unique probe table, drops it before and after each test, checks rollback state and performs an explicit successful retry.
blockers: []
next_action: Open the bounded PR, run exact-head repository CI and fix only concrete failures.
```
