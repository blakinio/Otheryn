---
task_id: OTH-20260729-prs003a-database-outage-state-machine
status: implementing
branch: dudantas/prs-003a-database-outage-state-machine
base_branch: main
start_sha: 322264e69a64b0204c9ab98534b421046e6d5602
created: 2026-07-29
updated: 2026-07-29
related_issue: "201"
related_pr: null
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003a-database-outage-state-machine.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/database/database_outage_state.hpp
  - tests/unit/database/database_outage_state_test.cpp
  - tests/unit/database/CMakeLists.txt
  - vcproj/canary.vcxproj
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
search_first:
  - src/database/
  - src/game/scheduling/player_persistence_state.hpp
  - tests/unit/database/
  - tests/unit/game/player_persistence_state_test.cpp
  - vcproj/canary.vcxproj
---

# PRS-003A pure database-outage state machine

## Goal

Implement Slice A of the accepted PRS-003 contract as one thread-safe, database-independent policy state machine with deterministic caller-supplied monotonic time, finite injected durations, immutable snapshots and explicit event results.

## Accepted contract

- fixed `HEALTHY`, `DEGRADED`, `DRAINING` and `MAINTENANCE` states;
- fixed low-cardinality runtime failure reasons and `KNOWN_NOT_COMMITTED` / `UNKNOWN` outcomes;
- first known-not-committed failure enters degraded and fixes one first-failure time and degraded deadline;
- unknown outcome enters draining directly;
- repeated degraded failure or degraded-deadline expiry enters draining without resetting the first interval;
- drain completion and drain timeout enter maintenance with distinct reasons;
- recovery evidence changes eligibility only and never auto-resumes;
- explicit resume is accepted only from degraded or maintenance after recovery evidence;
- operator maintenance is explicit and never auto-resumes;
- event sequence and event time are monotonic; stale or duplicate events are rejected;
- all methods serialize concurrent callers and return immutable before/after snapshots;
- transition count increases only on state changes.

## Failure semantics

- constructor rejects zero or negative degraded/drain durations;
- stale sequence numbers, duplicate sequence numbers and regressing event times are rejected without mutation;
- deadline events before their recorded deadline are rejected;
- events in an invalid source state are rejected and cannot reverse state;
- unknown commit outcome never authorizes replay;
- recovery evidence does not itself change state;
- resume emits the final failure-interval snapshot before clearing active interval fields.

## Bounded scope

- one header-only state object under `src/database/`, following the existing `PlayerPersistenceState` synchronization pattern;
- one focused deterministic unit/concurrency test source;
- test CMake registration and Visual Studio header registration;
- architecture contract status update for implemented Slice A.

## Deterministic evidence

Tests must cover initial state, finite-duration validation, known and unknown first failures, repeated failure, degraded expiry, drain completion, drain timeout, recovery eligibility, explicit resume, operator maintenance, stale sequence/time rejection and concurrent duplicate serialization.

## Rollback

Revert the feature merge. The package changes only one database-independent header, deterministic tests, build registration, architecture documentation and this task record. It performs no database, schema, credential, deployment or production mutation.

## Explicit non-goals

- no wiring into `Database`, `DatabaseTasks`, protocols, gameplay, `GameState_t`, metrics or configuration;
- no reconnect, query replay, database probe, connection pool, scheduler or retry loop;
- no player disconnect or drain orchestration;
- no schema, migration, credential, secret, production database or deployment change;
- no PRS-004 fencing, PRS-005 idempotency, PRS-006 reconciliation, PRS-007 failover or PRS-008 Compose work;
- no production degraded duration, RPO or RTO claim.

## Preflight

- current `main`: `322264e69a64b0204c9ab98534b421046e6d5602`;
- issue `#201` is the existing owner for this exact package;
- no open PR or PRS-003 branch competes for the scope;
- no other active task record is present on `main`;
- `docs/agents/REPOSITORY_MAP.md`, `docs/agents/CONTEXT_ROUTING.md` and `docs/agents/EXECUTION_MODE_ROUTING.md` are absent on current `main`;
- repository search found no existing database-outage state-machine implementation;
- the header-only implementation pattern avoids parallel infrastructure and does not require a new runtime `.cpp` registration.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T19:12:00+02:00
head: 322264e69a64b0204c9ab98534b421046e6d5602
head_scope: task-start main before the active-record commit
branch: dudantas/prs-003a-database-outage-state-machine
pr: null
status: implementing
context_routes:
  - production-resilience
  - database
  - outage-handling
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003a-database-outage-state-machine.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/database/database_outage_state.hpp
  - tests/unit/database/database_outage_state_test.cpp
  - tests/unit/database/CMakeLists.txt
  - vcproj/canary.vcxproj
proven:
  - PRS-003 discovery contract is merged and terminally archived.
  - Issue 201 owns the pure database-independent Slice A package.
  - Existing PlayerPersistenceState proves a repository-supported header-only mutex-protected state-object pattern.
  - No existing outage state machine, competing PR, competing branch or active task owns these paths.
derived:
  - A header-only state object plus focused tests is the smallest independently provable Slice A.
unknown:
  - Exact implementation head and validation results until code and tests are committed.
conflicts: []
first_failure:
  marker: null
  evidence: No implementation or validation failure has occurred.
rejected_hypotheses:
  - wire the first slice directly into Database or protocols
  - reuse GameState_t as an undocumented outage state
  - add reconnect, query replay or recovery probes
  - combine draining orchestration or PRS-004 fencing into this task
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003a-database-outage-state-machine.md
validation:
  - command: governance, issue, branch, ownership and existing-implementation preflight
    result: PASS
    evidence: Exact main, issue 201, empty active ownership, no competing PR/branch and no existing outage implementation were confirmed.
  - command: implementation and focused tests
    result: NOT_RUN
    evidence: Pending implementation.
blockers: []
next_action: Implement the header-only state machine, deterministic tests and exact build/document registration within the six owned paths.
```
