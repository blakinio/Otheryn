---
task_id: OTH-20260731-prs004b-durable-fence-schema
status: validating
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
phase: validate
session_id: chat-github-20260731-prs004b-02
session_role: implementer
execution_mode: chat-github
execution_reason: exact bounded path set is authored through GitHub; full build and disposable MariaDB evidence run in Actions
session_rotation_count: 1
heavy_validation_runs: 1
stale_takeover_count: 1
human_interruptions: 0
branch: dudantas/prs-004b-durable-fence-schema
base_branch: main
start_sha: d478323ebb0d047eaf219522ac2a18f48af08d15
issue: "276"
feature_pr: "279"
created: 2026-07-31
updated: 2026-07-31T19:00:00+02:00
lease_expires_at: 2026-07-31T20:30:00+02:00
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
updated_at: 2026-07-31T19:00:00+02:00
phase: validate
session_id: chat-github-20260731-prs004b-02
session_role: implementer
execution_mode: chat-github
lease_expires_at: 2026-07-31T20:30:00+02:00
task_kind: implementation
implementation_authorized: true
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: high
decomposition_decision: phased
validation_level: full
session_rotation_count: 1
heavy_validation_runs: 1
stale_takeover_count: 1
human_interruptions: 0
head: 61e95906719f7c0a2b47acb4a2d41e0b1861aac8
head_scope: exact seven-path candidate after focused runner repair
branch: dudantas/prs-004b-durable-fence-schema
pr: 279
status: validating
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
  - one canonical PRS-004B issue, branch, task and feature PR exist
  - exact seven changed paths match frozen ownership
  - clean schema version 59 and migration 59 define the same durable authority object
  - no shared CMake, production C++, save, handoff, Redis, deployment or credential path is modified
  - CI and MySQL Schema Check passed on the previous candidate head before the focused runner repair
unknown:
  - exact-final-head dedicated MariaDB, CI, Required, Repository Audit and autofix outcomes
  - feature merge and lifecycle metadata
conflicts: []
first_failure:
  marker: focused-runner-shell-syntax
  result: CONTAINED
  evidence: dedicated workflow isolated an unexpected closing brace caused by malformed nested substitutions; only the owned runner was repaired
rejected_hypotheses:
  - fencing columns on the broad players row
  - shared CMake edit
  - modifying the shared PRS-004A architecture contract
  - CAS or save/handoff implementation in this slice
changed_paths:
  - schema.sql
  - data-otservbr-global/migrations/59.lua
  - tests/integration/database/database_migrations_it.cpp
  - tests/integration/prs_004b/run_durable_fence_schema.sh
  - .github/workflows/prs-004b-durable-fence-schema.yml
  - docs/architecture/prs-004b-durable-writer-fence-schema.md
  - docs/agents/tasks/active/OTH-20260731-prs004b-durable-fence-schema.md
validation:
  - command: live dependency, source, branch and ownership audit
    result: PASS
    evidence: one canonical package and exact seven-path diff with no overlap
  - command: CI and MySQL Schema Check on pre-repair candidate
    result: PASS
    evidence: CI 694 and MySQL Schema Check 2 completed successfully
  - command: exact-final-head dedicated MariaDB, CI, Required, Repository Audit and autofix
    result: IN_PROGRESS
    evidence: new exact head requires fresh checks after runner repair
blockers: []
last_completed_step: dedicated runner syntax repaired without scope growth
next_action: complete exact-final-head validation, freshness and discussion audit before expected-head merge
```
