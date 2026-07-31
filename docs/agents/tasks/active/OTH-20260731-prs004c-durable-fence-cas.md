---
task_id: OTH-20260731-prs004c-durable-fence-cas
status: validating
project_lane: otheryn-runtime
policy_version: 2
task_kind: implementation
implementation_authorized: true
decomposition_decision: atomic
decomposition_reason: one durable CAS repository and its minimal released-state compatibility migration form one inseparable authority contract
context_pressure: medium
context_growth: stable
context_score: 9
estimate_confidence: high
phase: validate
session_id: chat-github-20260731-prs004c-01
session_role: implementer
execution_mode: chat-github
branch: dudantas/prs-004c-durable-fence-cas
base_branch: main
start_sha: 049c79f36752adc812b62bcdf0b293e7abafc705
issue: "284"
feature_pr: "285"
created: 2026-07-31
updated: 2026-07-31T20:25:00+02:00
lease_expires_at: 2026-07-31T22:00:00+02:00
owned_paths:
  - schema.sql
  - data-otservbr-global/migrations/60.lua
  - src/database/player_writer_fence_repository.hpp
  - src/database/player_writer_fence_repository.cpp
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_writer_fence_repository_it.cpp
  - .github/workflows/prs-004c-durable-fence-cas.yml
  - docs/architecture/prs-004c-durable-writer-fence-cas.md
  - docs/agents/tasks/active/OTH-20260731-prs004c-durable-fence-cas.md
---

# PRS-004C durable writer-fence CAS repository

## First failure

Live comparison with the terminal PRS-004B schema and accepted PRS-004A model found a released-state mismatch. Resetting generation to zero on release would erase durable monotonic history and allow a stale generation to reacquire authority. The contained correction is schema version 60: released rows retain positive generation and revision while token is null.

Candidate `database.hpp` and `database.cpp` paths were released before modification. A transaction-scoped conditional update and `SELECT ROW_COUNT()` use the existing recursive connection lock, avoiding broad database plumbing.

## Scope and invariants

Exactly nine paths. MariaDB is authority. Acquire, transfer, release and exact-next revision advance return applied, stale, malformed or database-failure outcomes. Each operation is attempted once. No save, handoff, Redis, retry/replay, credentials, deployment or later-package behavior is included.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T20:25:00+02:00
status: validating
phase: validate
head: 9d084bdb879aa8600594b56ad5bcffd8a53ae04d
head_scope: exact nine-path candidate after canonical schema correction and read-only workflow cleanup
branch: dudantas/prs-004c-durable-fence-cas
pr: 285
owned_paths:
  - schema.sql
  - data-otservbr-global/migrations/60.lua
  - src/database/player_writer_fence_repository.hpp
  - src/database/player_writer_fence_repository.cpp
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_writer_fence_repository_it.cpp
  - .github/workflows/prs-004c-durable-fence-cas.yml
  - docs/architecture/prs-004c-durable-writer-fence-cas.md
  - docs/agents/tasks/active/OTH-20260731-prs004c-durable-fence-cas.md
proven:
  - PRS-004B is terminal through PR 283
  - one canonical PRS-004C issue, branch, task and feature PR exist
  - exact nine changed paths match frozen ownership
  - schema diff contains only version 59 to 60 and the released-state-compatible check constraint
  - candidate database.hpp and database.cpp were released before modification
  - the committed workflow is read-only and contains no branch-writing bootstrap
unknown:
  - exact-final-head compile, integration, CI, Required, Repository Audit, schema and autofix outcomes
  - feature merge and lifecycle metadata
conflicts: []
first_failure:
  marker: released-state-schema-mismatch
  result: CONTAINED
  evidence: version 60 widens only the check constraint while preserving table, token representation and all unrelated schema
rejected_hypotheses:
  - reset durable generation to zero on release
  - add broad affected-row API to Database
  - use Redis or process memory as writer authority
  - retry a zero-row or failed CAS
changed_paths:
  - schema.sql
  - data-otservbr-global/migrations/60.lua
  - src/database/player_writer_fence_repository.hpp
  - src/database/player_writer_fence_repository.cpp
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_writer_fence_repository_it.cpp
  - .github/workflows/prs-004c-durable-fence-cas.yml
  - docs/architecture/prs-004c-durable-writer-fence-cas.md
  - docs/agents/tasks/active/OTH-20260731-prs004c-durable-fence-cas.md
validation:
  - command: live dependency, ownership, changed-path and patch audit
    result: PASS
    evidence: exact nine paths; schema has only two intended hunks and no unrelated drift
  - command: exact-final-head validation
    result: IN_PROGRESS
    evidence: new checkpoint head requires fresh dedicated, CI, Required, Repository Audit, MySQL Schema Check and autofix runs
blockers: []
next_action: complete exact-final-head validation, discussion audit and base freshness before expected-head merge
```
