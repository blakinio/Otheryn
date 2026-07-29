---
task_id: OTH-20260729-prs004a-session-revision-fencing-contract
status: validating
branch: feat/OTH-20260729-prs004a-session-revision-fencing-contract
base_branch: main
start_sha: 6a6007667dfd82010b0240342180961cd553466f
created: 2026-07-29
updated: 2026-07-29
related_issue: "207"
related_pr: "212"
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs004a-session-revision-fencing-contract.md
  - docs/architecture/prs-004-session-revision-fencing-contract.md
  - src/database/session_revision_fence.hpp
  - tests/unit/database/session_revision_fence_test.cpp
  - tests/unit/database/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/game/scheduling/player_persistence_state.hpp
  - src/database/database_outage_state.hpp
search_first:
  - src/database/
  - src/game/scheduling/
  - src/io/
  - tests/unit/database/
  - tests/unit/game/
---

# PRS-004A pure session/revision fencing contract

## Goal

Implement one database-independent deterministic state object defining whether one writer may persist one stable player subject under the current ownership generation and persistence revision.

## Scope

- stable non-zero subject identity;
- monotonic non-zero ownership generation;
- monotonic non-zero writer token;
- monotonic event sequence;
- monotonic persistence revision;
- explicit first acquisition, authority transfer, release/invalidation and persistence-revision advance;
- fixed dispositions and reason codes;
- immutable before/after snapshots;
- internal serialization of concurrent callers;
- deterministic unit and concurrency tests;
- architecture documentation for future database and channel-handoff integration.

## Invariants

1. A writer is authorized only when subject, generation and writer token exactly match one active fence.
2. Ownership generation never decreases or repeats for a different authority.
3. A transfer changes authority atomically while preserving the latest persistence revision.
4. A released writer remains fenced; reacquisition requires a strictly newer ownership generation.
5. Persistence revisions advance by exactly one; lower, equal and skipped revisions do not mutate state.
6. Sequence zero, stale sequences and duplicate sequences never mutate state.
7. Unknown, missing or malformed context fails closed.
8. Concurrent duplicate operations serialize to at most one effective transition.
9. Transition count changes only on effective state changes.
10. No transition depends on wall-clock time.

## Non-goals

- no database schema or migration;
- no SQL compare-and-swap wiring;
- no production player-save integration;
- no protocol or channel-switch runtime wiring;
- no time lease or wall-clock expiry;
- no distributed lock service or external consensus;
- no automatic reconnect, replay or retry;
- no PRS-005 idempotency or PRS-006 reconciliation;
- no durable fencing claim across restart or database failover;
- no production RPO/RTO claim.

## Ownership and shared paths

`tests/unit/database/CMakeLists.txt` is the only shared registration path. Changes there are limited to registering `session_revision_fence_test.cpp`. No PRS-003B/PRS-003C runtime, policy or test path is owned by this task.

## Validation plan

- inspect exact changed paths and full diff;
- run repository CI, Required and autofix against the exact final head;
- verify all deterministic transition, malformed-context and concurrency tests;
- confirm no runtime, schema, migration, protocol or production persistence path changed;
- verify comments, reviews, unresolved threads and base freshness before merge.

## Preflight result

- task-start `main`: `6a6007667dfd82010b0240342180961cd553466f`;
- existing coordinator-reserved issue: `#207`;
- feature PR: `#212`;
- branch ownership declaration published on issue `#207`;
- exact owned paths: five, with one minimal shared CMake registration;
- no existing PRS-004 implementation or competing PR was found;
- no runtime, schema, migration, SQL save or protocol path is changed;
- current `main` drift is coordination/task metadata outside this package's shared implementation paths.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T21:32:00+02:00
head: e65f2172492302f6944378b6fdc19d06b91e53fd
head_scope: implementation head before this PR-metadata task update
branch: feat/OTH-20260729-prs004a-session-revision-fencing-contract
pr: 212
status: validating
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs004a-session-revision-fencing-contract.md
  - docs/architecture/prs-004-session-revision-fencing-contract.md
  - src/database/session_revision_fence.hpp
  - tests/unit/database/session_revision_fence_test.cpp
  - tests/unit/database/CMakeLists.txt
proven:
  - The implementation is database-independent and touches exactly five declared paths.
  - Subject, generation, writer token, revision and event sequence are explicit non-zero fencing inputs.
  - Acquire, transfer, release and persist transitions are mutex-serialized and return immutable snapshots.
  - Missing, malformed, stale and mismatched fencing context fails closed.
  - Architecture documentation leaves durable schema, SQL CAS, player-save and channel-handoff wiring to separate packages.
unknown:
  - Exact-head CI, Required and autofix results.
  - Final branch freshness after parallel packages update shared registration paths.
conflicts: []
first_failure: null
validation:
  - command: governance, issue, branch, ownership and existing-implementation preflight
    result: PASS
    evidence: Issue 207, task record, branch and five exact owned paths were verified against current repository state.
  - command: implementation and changed-path audit
    result: PASS
    evidence: One header, one unit test, one architecture contract, one task record and one minimal CMake entry only.
  - command: exact-head CI, Required and autofix
    result: NOT_RUN
    evidence: PR 212 is open and this metadata update creates the validation head.
blockers: []
next_action: Verify exact-head checks; fix only a confirmed bounded failure, then audit full diff, comments, reviews, threads and base drift before merge.
```

## Rollback

Revert the feature merge. The package owns only an isolated header, deterministic tests, minimal test registration, architecture documentation and its task record.
