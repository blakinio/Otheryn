---
task_id: OTH-20260729-prs003b-database-failure-classification
status: validating
branch: dudantas/prs-003b-database-failure-classification
base_branch: main
start_sha: 6a6007667dfd82010b0240342180961cd553466f
created: 2026-07-29
updated: 2026-07-29
related_issue: "208"
related_pr: "214"
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003b-database-failure-classification.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/database/database_failure_classification.hpp
  - src/database/database.cpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/database/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/agents/tasks/archive/OTH-20260729-prs003a-database-outage-state-machine.md
search_first:
  - docs/agents/tasks/active/
  - docs/agents/tasks/archive/
  - src/database/database.hpp
  - src/database/database.cpp
  - src/database/database_outage_state.hpp
  - src/database/databasetasks.cpp
  - tests/unit/database/
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - vcproj/canary.vcxproj
---

# PRS-003B runtime database failure classification and outage publication

## Goal

Implement one narrow database-layer seam that classifies direct runtime database results into fixed semantic categories and publishes deterministic failures to the existing PRS-003A state owner without changing caller-visible results.

## Coordination and ownership

- issue `#208` owns this package;
- duplicate issue `#210`, created before the reservation was discovered, is closed as duplicate and is not used;
- coordinator issue `#205` serializes shared registration and architecture files;
- the six exact owned paths above were declared before implementation;
- `src/database/database.hpp` was audited but required no change;
- shared database-test registration from PRS-004A remains intact;
- the final refresh is based on `main` `370bf41830fd03d04a6b8b7b2cd15bf5698ef621`, including the independently merged PRS-003C-A feature/lifecycle/finalizer chain through PR `#219`.

## Audited baseline

- task-start `main`: `6a6007667dfd82010b0240342180961cd553466f`;
- PRS-003A feature `#202`, lifecycle `#203` and finalizer `#204` are merged and terminally archived;
- `src/database/database_outage_state.hpp` is the accepted mutex-serialized owner contract and was not recreated or replaced;
- no pre-existing Slice B branch, active task record or feature PR competed for the package;
- the current database layer preserves `false`/`nullptr`, disables implicit reconnect, executes each query once, serializes one handle, and keeps startup/migrations fail closed.

## Implemented contract

- finite operation phases: query, stored-result query, transaction begin, commit and rollback;
- finite native error kinds: none, connection lost, server gone and other;
- finite result kinds: success, known-not-committed failure and unknown commit outcome;
- classification uses operation phase and numeric MySQL error codes, never error-message text;
- begin failure is known not committed; commit failure is unknown;
- query/store connection loss or server-gone failure is conservatively unknown;
- other query/store failures are known not committed;
- rollback failure is unknown and never authorizes replay;
- success and successful empty results publish no event;
- generated events use one mutex-serialized monotonic sequence and steady-clock monotonic time;
- deterministic explicit events retain supplied sequence/time so stale, duplicate and regressing events are rejected by PRS-003A;
- concurrent publication is serialized by the publisher and state-owner mutex;
- original boolean and pointer results remain unchanged.

## Runtime ownership

`src/database/database.cpp` owns exactly one function-local `DatabaseOutageStateMachine` and one narrow `DatabaseOutageEventPublisher`. Positive finite integration durations exist only to produce complete immutable snapshots. This slice does not schedule deadlines, gate gameplay, drain players or claim production RTO/RPO.

## Safety boundaries

- no reconnect, `mysql_ping`, arbitrary SQL replay or retry loop;
- no failure-to-success conversion and no swallowed failure;
- no protocol, login, handoff, gameplay, mutation, player-save or disconnect change;
- no recovery probe or automatic resume;
- no schema, migration, credential, secret, production database or deployment mutation;
- no connection pool;
- no SQL text, player data or unbounded error text in fixed classifications;
- no durable PRS-004 integration or PRS-005/006/007/008 work.

## Deterministic evidence

Focused tests cover known-not-committed and unknown-outcome publication, unchanged `false`/`nullptr`, successful-empty non-publication, stale/duplicate/regressing rejection, numeric classification without message parsing, no reconnect/replay/loop, and concurrent duplicate serialization with exactly one transition.

## Build registration

One header is consumed by the existing `database.cpp` translation unit. One unit source is registered in `tests/unit/database/CMakeLists.txt`; the independent `session_revision_fence_test.cpp` entry remains intact. No standalone server translation unit or Visual Studio source registration is required.

## Rollback

Revert feature PR `#214`; no schema, data or deployment rollback is required. Revert the lifecycle PR only to restore active/archive record placement.

## Remaining separate work

- PRS-003C live protocol wiring beyond the already merged pure admission-policy package;
- PRS-003D mutation admission and bounded draining with PRS-002 final saves;
- PRS-003E bounded recovery probes and controlled failure injection;
- durable PRS-004 schema/CAS integration and all later resilience packages.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T22:42:13+02:00
head: pending-final-refresh-commit
head_scope: final feature candidate rebuilt directly on main 370bf418 after independent PRS-003C-A lifecycle completion
branch: dudantas/prs-003b-database-failure-classification
pr: 214
status: validating
context_routes:
  - production-resilience
  - database
  - outage-handling
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003b-database-failure-classification.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/database/database_failure_classification.hpp
  - src/database/database.cpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/database/CMakeLists.txt
proven:
  - PRS-003A is merged and terminally archived.
  - Issue 208 owns the package; duplicate issue 210 is closed.
  - The implementation uses fixed numeric/phase classification and one serialized publisher/owner.
  - Caller-visible false/nullptr, disabled reconnect and one-shot execution remain explicit.
  - The diff remains restricted to six declared paths and preserves parallel registrations.
  - Head caaa8f039c1aa3fa2f96c8baabcb535ade34367f passed autofix 30486725474, CI 30486725651 and Required 30486725482.
  - Later candidates were intentionally superseded whenever main advanced; no stale head was merged.
derived:
  - The narrow seam preserves caller semantics without message parsing, replay or connection redesign.
unknown:
  - Exact final refreshed feature head SHA and its exact-head gates.
  - Feature merge SHA and lifecycle/finalizer evidence.
conflicts: []
first_failure: null
rejected_hypotheses:
  - recreate or replace PRS-003A
  - reconnect or replay after connection loss
  - parse mysql_error text for correctness
  - change DatabaseTasks callback semantics
  - combine protocol/drain/recovery/durable fencing work
  - add pooling or schema changes
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003b-database-failure-classification.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/database/database_failure_classification.hpp
  - src/database/database.cpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/database/CMakeLists.txt
validation:
  - command: governance, ownership, issue/PR/branch and database preflight
    result: PASS
    evidence: Task-start main, terminal PRS-003A, issue reservation, coordination and database propagation paths were verified.
  - command: focused source/test and exact diff audit
    result: PASS
    evidence: Six paths implement the classifier/publisher seam and deterministic acceptance tests.
  - command: prior exact-head validation
    result: PASS
    evidence: Head caaa8f03 passed autofix, full CI including Linux debug unit tests, and Required.
  - command: final refreshed exact-head validation
    result: NOT_RUN
    evidence: Candidate is being rebuilt on main 370bf418.
blockers: []
next_action: Run final exact-head gates, inspect reviews/freshness/diff, then merge PR 214 and execute lifecycle archive/finalizer PRs.
```
