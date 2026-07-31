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
updated: 2026-07-31T11:00:00+02:00
lease_expires_at: 2026-07-31T11:45:00+02:00
owned_paths:
  - schema.sql
  - data-otservbr-global/migrations/59.lua
  - tests/integration/database/database_migrations_it.cpp
  - tests/integration/prs_004b/run_durable_fence_schema.sh
  - .github/workflows/prs-004b-durable-fence-schema.yml
  - docs/architecture/prs-004b-durable-writer-fence-schema.md
  - docs/agents/tasks/active/OTH-20260731-prs004b-durable-fence-schema.md
---

# PRS-004B durable MariaDB writer-fence schema

## Decision

Use one dedicated `player_writer_fence` authority table keyed by `player_id`. It separates authority lifecycle from the broad player persistence row, supports a globally unique exact binary token and gives later CAS a subject-primary-key lookup.

Inactive authority is fail closed: generation `0`, token `NULL`, revision `0`. Active authority requires generation greater than zero and a non-null 16-byte token. Existing players are backfilled inactive and later players receive the same inactive row through a bounded database trigger.

Rejected alternative: nullable/default fencing columns on `players`, because it couples authority transitions to broad player persistence and increases later write blast radius.

## Exact scope

Seven frozen paths only. The existing migration integration source is already registered, so no shared CMake path is claimed. The existing PRS-004A architecture contract is read-only; PRS-004B owns a separate schema-specific document.

## Explicit non-goals

- no CAS acquire/transfer/release API or affected-row plumbing;
- no player save/update fencing or handoff wiring;
- no Redis authority;
- no stale-write retry/replay;
- no generic rollback framework;
- no later package, production credential/data, deployment or RPO/RTO claim.

## Rollback

Disposable/manual bounded rollback only: verify version 59 and expected objects, drop the creation trigger, drop the authority table, restore version 58, then prove deterministic re-upgrade. Production rollback is an explicit operator procedure, not an automated framework.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-07-31T11:00:00+02:00
phase: implement
session_id: chat-github-20260731-prs004b-01
session_role: implementer
execution_mode: chat-github
lease_expires_at: 2026-07-31T11:45:00+02:00
task_kind: implementation
implementation_authorized: true
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: high
decomposition_decision: phased
validation_level: focused
session_rotation_count: 0
heavy_validation_runs: 0
stale_takeover_count: 0
human_interruptions: 0
head: aa267bfc0f21c13c9a293e9b18e4fa2498ae0609
head_scope: task record plus migration before remaining schema/test evidence
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
  - docs/architecture/prs-004b-durable-writer-fence-schema.md
  - docs/agents/tasks/active/OTH-20260731-prs004b-durable-fence-schema.md
proven:
  - terminal PRS-003D and PRS-003E opened only PRS-004B
  - main d478323ebb0d047eaf219522ac2a18f48af08d15 had no PRS-004B branch, PR or active task before claim
  - schema version is 58 and migration 58 is latest
  - real migration integration seam exists and is already registered
  - exact seven paths are frozen in issue 276 and this task record
  - shared PRS-004A architecture path was released without modification after discovery
unknown:
  - exact complete implementation head and focused MariaDB result
  - feature PR and exact-final-head check runs
conflicts: []
first_failure:
  marker: existing-prs004a-architecture-path
  result: CONTAINED
  evidence: create attempt returned existing-file conflict; the shared PRS-004A contract was not modified and ownership moved to a new PRS-004B-specific document before further implementation
rejected_hypotheses:
  - fencing columns on the broad players row
  - shared CMake edit
  - modifying the shared PRS-004A architecture contract
  - CAS or save/handoff implementation in this slice
changed_paths:
  - data-otservbr-global/migrations/59.lua
  - docs/agents/tasks/active/OTH-20260731-prs004b-durable-fence-schema.md
validation:
  - command: live dependency, source and ownership audit
    result: PASS
    evidence: corrected seven-path freeze on issue 276 and this task
blockers: []
last_completed_step: architecture ownership conflict contained and migration 59 persisted
next_action: create PRS-004B architecture, test runner and migration integration evidence, then materialize the canonical schema change
```
