---
task_id: OTH-20260729-prs003a-database-outage-state
status: active
branch: dudantas/prs-003a-database-outage-state
base_branch: main
start_sha: 322264e69a64b0204c9ab98534b421046e6d5602
created: 2026-07-29
updated: 2026-07-29
related_issue: "201"
related_pr: null
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003a-database-outage-state.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/database/database_outage_state.hpp
  - tests/unit/game/database_outage_state_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/architecture/oam-004a-database-transaction-integrity.md
  - docs/architecture/oam-004d-player-save-failure-propagation.md
search_first:
  - src/database/database.hpp
  - src/database/database.cpp
  - src/database/databasetasks.hpp
  - src/database/databasetasks.cpp
  - src/game/scheduling/player_persistence_state.hpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/CMakeLists.txt
---

# PRS-003A pure database-outage state machine

## Goal

Implement only Slice A from the accepted PRS-003 contract: one thread-safe, database-independent policy state object with caller-supplied deterministic time, injected finite durations, immutable snapshots and explicit transition records.

## Current behavior inventory

- the completed PRS-003 discovery contract is terminally archived on `main` at `322264e69a64b0204c9ab98534b421046e6d5602`;
- startup database failure is fail closed, while runtime database failures do not publish a process-level outage transition;
- no `DEGRADED` or `DRAINING` runtime state currently exists;
- `PlayerPersistenceState` demonstrates the accepted local pattern for a header-only, internally synchronized, database-independent state object with deterministic tests;
- no runtime call site is authorized in this slice.

## Accepted implementation boundary

- add `DatabaseOutageState` under `src/database/` without including or calling `Database`;
- use fixed state, failure, commit-outcome and transition-reason enums;
- acquire no wall clock internally: all event methods receive a caller-supplied `TimePoint` and constructor-injected positive durations;
- serialize all state mutation with one mutex;
- return an optional transition record containing immutable before/after snapshots and the transition timestamp;
- preserve one first-failure timestamp and original degraded deadline through escalation;
- reject early deadlines, stale events and duplicate terminal events without reversing state or incrementing transition count;
- require accepted recovery evidence before explicit resume from degraded or maintenance;
- never permit direct draining-to-healthy recovery;
- keep all database classification, protocols, gameplay admission, drain orchestration, metrics and probes outside this slice.

## Failure-injection plan

- first known-not-committed failure enters degraded exactly once;
- unknown outcome enters draining directly;
- repeated degraded failure enters draining without resetting the original interval;
- degraded deadline is inert before expiry and escalates at or after expiry;
- drain completion and timeout produce distinct maintenance reasons;
- recovery evidence never auto-resumes;
- operator resume fails without evidence and succeeds only from degraded or maintenance;
- operator maintenance works from healthy, degraded and draining and is idempotent once active;
- stale events cannot reverse maintenance or healthy state;
- concurrent known failures serialize to at most degraded then draining.

## Rollback plan

Revert the feature merge. The state object is not wired into runtime, database, protocols or gameplay, so rollback removes only the isolated header, tests, registration and contract status update.

## Explicit non-goals

- no `Database`, `DatabaseTasks`, protocol, gameplay, `GameState_t`, scheduler or metrics integration;
- no database health probe, reconnect, replay, connection pool or retry policy;
- no drain/disconnect orchestration or PRS-002 invocation;
- no schema, migration, credential, production database or deployment change;
- no PRS-004 through PRS-008 work;
- no production duration, RPO or RTO claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T18:24:00+02:00
head: 322264e69a64b0204c9ab98534b421046e6d5602
head_scope: task-start main before Slice A implementation commits
branch: dudantas/prs-003a-database-outage-state
pr: null
status: implementing
context_routes:
  - production-resilience
  - database
  - concurrency
  - state-machine
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003a-database-outage-state.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/database/database_outage_state.hpp
  - tests/unit/game/database_outage_state_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - PRS-003 discovery is completed and terminally archived on main 322264e69a64b0204c9ab98534b421046e6d5602.
  - Issue 201 owns the bounded pure-state Slice A.
  - No existing runtime outage state is present.
  - Header-only synchronized state objects and deterministic game unit tests are established repository patterns.
derived:
  - Caller-supplied time avoids runtime clock ownership and makes deadline tests deterministic.
  - Returning before/after transition snapshots preserves interval evidence while allowing the current healthy snapshot to clear active outage fields after resume.
unknown:
  - Exact API compile compatibility and concurrency behavior until focused tests and full CI run.
conflicts: []
first_failure:
  marker: null
  evidence: No implementation or validation failure has occurred.
rejected_hypotheses:
  - wire failure classification into Database in Slice A
  - reuse GameState_t for database health
  - acquire steady_clock internally in event methods
  - auto-resume after recovery evidence
  - allow draining to return directly to healthy
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003a-database-outage-state.md
validation:
  - command: fresh governance and ownership preflight
    result: PASS
    evidence: Issue 201 and branch start from exact main 322264e69a64b0204c9ab98534b421046e6d5602 with five declared paths.
  - command: implementation and focused deterministic tests
    result: NOT_RUN
    evidence: Slice A files are being created.
blockers: []
next_action: Add the isolated DatabaseOutageState header, deterministic unit tests, CMake registration and Slice A contract status, then validate and open the exact-scope pull request.
```
