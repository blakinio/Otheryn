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
session_id: chat-github-20260803-prs004c-recovery
session_role: implementer
execution_mode: chat-github
branch: dudantas/prs-004c-durable-fence-cas
base_branch: main
start_sha: 049c79f36752adc812b62bcdf0b293e7abafc705
issue: "284"
feature_pr: "285"
created: 2026-07-31
updated: 2026-08-03T23:05:00+02:00
lease_expires_at: 2026-08-04T01:05:00+02:00
invocation_started_at: 2026-08-03T22:57:00+02:00
last_progress_at: 2026-08-03T23:05:00+02:00
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 0
stall_warnings: 0
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

## Scope and invariants

Exactly ten paths. MariaDB is the durable authority. Acquire, transfer, release and exact-next revision advance return applied, stale, malformed or database-failure outcomes. Each operation is attempted once. No save wiring, handoff, Redis authority, retry/replay, credentials, deployment or later-package behavior is included.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-03T23:05:00+02:00
status: validating
phase: validate
head: ca71c383eae2690abe5850f4cf0badbcf3bcab70
head_scope: exact ten-path implementation after non-overlapping current-main integration; this checkpoint-only commit follows it
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
  - PRS-004B is terminal through PRs 279, 281, 282 and 283
  - PR 328 merged current main 1f316400053f489e58608d13961069835871ab0e into the canonical feature branch without path conflicts
  - compare main to ca71c383eae2690abe5850f4cf0badbcf3bcab70 reports behind_by 0 and exactly the frozen ten paths
  - intervening main changes were governance and audit documentation only and did not overlap PRS-004C ownership
  - PR 285 has zero comments, zero reviews and zero review threads
  - historical exact-head run generation on a43e14a330bd311fc55442305baa0daf39678fe0 passed dedicated, CI, Required, Repository Audit, MySQL Schema Check and autofix
  - schema version 60 preserves released generation and revision while clearing only the writer token
  - repository operations classify one-row applied, zero-row stale, malformed context and database failure without retry or replay
unknown:
  - fresh exact-final-head workflow outcomes after current-main integration and checkpoint refresh
  - feature merge and lifecycle metadata
conflicts: []
first_failure:
  marker: stale-base-and-checkpoint
  evidence: contained by PR 328 branch integration and this refreshed checkpoint
rejected_hypotheses:
  - merge the stale head directly
  - force-update or rewrite the canonical branch
  - broaden Database affected-row plumbing
  - use Redis or process memory as writer authority
  - retry a stale or failed CAS
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
  - command: compare main...dudantas/prs-004c-durable-fence-cas
    result: PASS
    evidence: behind_by 0; exact ten changed paths; merge base current main
  - command: fresh exact-final-head validation
    result: NOT_RUN
    evidence: new check generation begins after this checkpoint commit
blockers: []
next_action: verify fresh exact-final-head checks, unchanged ten-path scope, clean discussion and mergeability, then squash-merge PR 285 with expected-head protection
```
