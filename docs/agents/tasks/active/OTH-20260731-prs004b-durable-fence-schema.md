---
task_id: OTH-20260731-prs004b-durable-fence-schema
status: active
project_lane: otheryn-runtime
policy_version: 2
task_kind: implementation
implementation_authorized: true
decomposition_decision: phased
decomposition_reason: one cohesive schema slice requires migration, clean-schema and rollback evidence on the same durable object
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: high
phase: implement
session_id: chat-github-20260731-prs004b-01
session_role: implementer
execution_mode: chat-github
execution_reason: exact bounded path set can be authored through GitHub; full build and disposable MariaDB evidence run in Actions
session_rotation_count: 0
heavy_validation_runs: 0
stale_takeover_count: 0
human_interruptions: 0
branch: dudantas/prs-004b-durable-fence-schema
base_branch: main
start_sha: d478323ebb0d047eaf219522ac2a18f48af08d15
issue: "276"
feature_pr: null
created: 2026-07-31
updated: 2026-07-31T10:50:00+02:00
lease_expires_at: 2026-07-31T11:35:00+02:00
owned_paths:
  - schema.sql
  - data-otservbr-global/migrations/59.lua
  - tests/integration/database/database_migrations_it.cpp
  - tests/integration/prs_004b/run_durable_fence_schema.sh
  - .github/workflows/prs-004b-durable-fence-schema.yml
  - docs/architecture/prs-004-session-revision-fencing-contract.md
  - docs/agents/tasks/active/OTH-20260731-prs004b-durable-fence-schema.md
---

# PRS-004B durable MariaDB writer-fence schema

## Decision

Use one dedicated `player_writer_fence` authority table keyed by `player_id`. It separates durable authority lifecycle from the broad player persistence row, supports a globally unique exact binary writer token and gives later CAS a subject-primary-key lookup.

Inactive authority is fail closed: generation `0`, token `NULL`, revision `0`. Active authority requires generation greater than zero and a non-null 16-byte token. Existing players are backfilled inactive and later players receive the same inactive row through a bounded database trigger.

Rejected alternative: nullable/default fencing columns on `players`, because it couples authority transitions to broad player persistence and increases later write blast radius.

## Exact scope

Seven frozen paths only. Existing `database_migrations_it.cpp` is already registered by integration CMake, so no shared build manifest is claimed.

## Explicit non-goals

- no CAS acquire/transfer/release API or affected-row plumbing;
- no player save/update fencing or handoff wiring;
- no Redis authority;
- no stale-write retry/replay;
- no generic rollback framework;
- no later PRS package, production credential/data, deployment or RPO/RTO claim.

## Rollback

Disposable/manual bounded rollback only: verify version 59 and the expected objects, drop the creation trigger, drop `player_writer_fence`, restore `db_version` to 58, then prove deterministic re-upgrade through migration 59. Production rollback remains an explicit operator procedure and is not automated by this slice.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-07-31T10:50:00+02:00
phase: implement
session_id: chat-github-20260731-prs004b-01
session_role: implementer
execution_mode: chat-github
execution_reason: bounded seven-path schema implementation through GitHub with exact-head Actions validation
lease_expires_at: 2026-07-31T11:35:00+02:00
task_kind: implementation
implementation_authorized: true
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: high
decomposition_decision: phased
decomposition_reason: schema, migration and rollback evidence share one durable object and acceptance boundary
validation_level: focused
session_rotation_count: 0
heavy_validation_runs: 0
stale_takeover_count: 0
human_interruptions: 0
head: pending-task-record-commit
branch: dudantas/prs-004b-durable-fence-schema
pr: null
status: active
project_lane: otheryn-runtime
owned_paths:
  - schema.sql
  - data-otservbr-global/migrations/59.lua
  - tests/integration/database/database_migrations_it.cpp
  - tests/integration/prs_004b/run_durable_fence_schema.sh
  - .github/workflows/prs-004b-durable-fence-schema.yml
  - docs/architecture/prs-004-session-revision-fencing-contract.md
  - docs/agents/tasks/active/OTH-20260731-prs004b-durable-fence-schema.md
proven:
  - terminal PRS-003D and PRS-003E opened only PRS-004B
  - current main d478323ebb0d047eaf219522ac2a18f48af08d15 has no PRS-004B branch, PR or active task before claim
  - schema version is 58 and migration 58 is latest
  - real DatabaseManager migration integration seam exists and is already registered
  - exact seven paths are frozen in issue 276 and this task record
unknown:
  - exact schema/migration implementation head
  - focused disposable MariaDB result
  - feature PR and exact-final-head check runs
conflicts: []
first_failure: null
rejected_hypotheses:
  - fencing columns on the broad players row
  - shared CMake edit
  - CAS or save/handoff implementation in this slice
changed_paths:
  - docs/agents/tasks/active/OTH-20260731-prs004b-durable-fence-schema.md
validation:
  - command: live dependency, source and ownership audit
    result: PASS
    evidence: issue 276 and exact seven-path freeze on main d478323ebb0d047eaf219522ac2a18f48af08d15
blockers: []
last_completed_step: schema placement decision and exact ownership persisted before implementation
next_action: add migration, schema contract evidence, clean-schema materialization and focused real migration tests
```
