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
updated: 2026-08-01T21:52:44+02:00
lease_expires_at: 2026-08-01T23:52:44+02:00
owned_paths:
  - schema.sql
  - data-otservbr-global/migrations/60.lua
  - src/database/player_writer_fence_repository.hpp
  - src/database/player_writer_fence_repository.cpp
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_writer_fence_repository_it.cpp
  - tests/integration/database/database_migrations_it.cpp
  - .github/workflows/prs-004c-durable-fence-cas.yml
  - docs/architecture/prs-004c-durable-writer-fence-cas.md
  - docs/agents/tasks/active/OTH-20260731-prs004c-durable-fence-cas.md
---

# PRS-004C durable writer-fence CAS repository

## First failure

Live comparison with the terminal PRS-004B schema and accepted PRS-004A model found a released-state mismatch. Resetting generation to zero on release would erase durable monotonic history and allow a stale generation to reacquire authority. The contained correction is schema version 60: released rows retain positive generation and revision while token is null.

Candidate `database.hpp` and `database.cpp` paths were released before modification. A transaction-scoped conditional update and `SELECT ROW_COUNT()` use the existing recursive connection lock, avoiding broad database plumbing.

Exact-head disposable-MariaDB validation then compiled and ran the CAS integration cases successfully but exposed a historical PRS-004B migration assertion that still treated version 59 as the terminal repository schema. The frozen ownership was amended by the single compatibility path `tests/integration/database/database_migrations_it.cpp`; its terminal expectation now follows the complete durable-fence chain through version 60.

## Scope and invariants

Exactly ten paths. MariaDB is authority. Acquire, transfer, release and exact-next revision advance return applied, stale, malformed or database-failure outcomes. Each operation is attempted once. No save, handoff, Redis, retry/replay, credentials, deployment or later-package behavior is included.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-01T21:52:44+02:00
status: validating
phase: validate
head: 3dfe4e2e0d6778e35ed912ed93bbdc86d4686871
head_scope: exact ten-path candidate after containing the historical version-59 migration assertion
branch: dudantas/prs-004c-durable-fence-cas
pr: 285
owned_paths:
  - schema.sql
  - data-otservbr-global/migrations/60.lua
  - src/database/player_writer_fence_repository.hpp
  - src/database/player_writer_fence_repository.cpp
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_writer_fence_repository_it.cpp
  - tests/integration/database/database_migrations_it.cpp
  - .github/workflows/prs-004c-durable-fence-cas.yml
  - docs/architecture/prs-004c-durable-writer-fence-cas.md
  - docs/agents/tasks/active/OTH-20260731-prs004c-durable-fence-cas.md
proven:
  - PRS-004B is terminal through PR 283
  - one canonical PRS-004C issue, branch, task and feature PR exist
  - schema diff contains only version 59 to 60 and the released-state-compatible check constraint
  - candidate database.hpp and database.cpp were released before modification
  - the committed workflow is read-only and contains no branch-writing bootstrap
  - run 30690330628 job 91343782173 compiled the repository and executed disposable-MariaDB tests
  - PRS-004C repository integration cases passed in that run
  - the sole full-suite failure was the historical migration test expecting terminal schema version 59 instead of 60
  - issue 284 records the explicit exact-ten-path containment amendment
unknown:
  - exact-final-head compile, integration, CI, Required, Repository Audit, schema and autofix outcomes after the compatibility correction
  - feature merge and lifecycle metadata
conflicts: []
first_failure:
  marker: historical-migration-terminal-version
  result: CONTAINED
  evidence: tests/integration/database/database_migrations_it.cpp now expects the complete version-58-to-60 durable-fence migration chain; no production behavior changed
rejected_hypotheses:
  - reset durable generation to zero on release
  - add broad affected-row API to Database
  - use Redis or process memory as writer authority
  - retry a zero-row or failed CAS
  - exclude or bypass the historical migration integration test
changed_paths:
  - schema.sql
  - data-otservbr-global/migrations/60.lua
  - src/database/player_writer_fence_repository.hpp
  - src/database/player_writer_fence_repository.cpp
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_writer_fence_repository_it.cpp
  - tests/integration/database/database_migrations_it.cpp
  - .github/workflows/prs-004c-durable-fence-cas.yml
  - docs/architecture/prs-004c-durable-writer-fence-cas.md
  - docs/agents/tasks/active/OTH-20260731-prs004c-durable-fence-cas.md
validation:
  - command: run 30690330628 job 91343782173 artifact linux-debug-test-logs
    result: FIRST_FAILURE_CONTAINED
    evidence: build passed; CAS integration tests passed; only DurableWriterFenceMigrationTest expected 59 while current schema was 60
  - command: exact-final-head validation
    result: IN_PROGRESS
    evidence: compatibility correction requires fresh dedicated, CI, Required, Repository Audit, MySQL Schema Check and autofix runs
blockers: []
next_action: complete exact-final-head validation, discussion audit and base freshness before expected-head merge
```
