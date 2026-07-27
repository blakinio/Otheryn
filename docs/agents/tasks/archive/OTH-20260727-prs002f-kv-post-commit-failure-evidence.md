---
task_id: OTH-20260727-prs002f-kv-post-commit-failure-evidence
status: complete
branch: dudantas/prs-002f-kv-post-commit-failure-evidence
base_branch: main
created: 2026-07-27
updated: 2026-07-27
related_issue: "171"
related_pr: "172"
owned_paths:
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_checkpoint_kv_post_commit_failure_it.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/archive/OTH-20260727-prs002f-kv-post-commit-failure-evidence.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/operations/backup-and-pitr-policy.md
  - docs/operations/production-recovery-runbook.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/io/iologindata.cpp
  - src/kv/kv.hpp
  - src/kv/kv.cpp
  - src/kv/kv_sql.cpp
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - tests/integration/database/player_checkpoint_sql_failure_it.cpp
optional_reads:
  - docs/architecture/oam-004d-player-save-failure-propagation.md
---

# PRS-002F KV post-commit failure evidence

## Result

A disposable MariaDB integration test now proves the bounded post-commit split-domain failure contract:

- one dedicated SQL-domain mutation commits successfully;
- a real `KVSQL::saveAll()` batch fails afterward while `kv_store` is temporarily unavailable;
- the already committed SQL mutation remains durable;
- the KV row is absent after the failed batch;
- the captured checkpoint generation remains dirty and its in-flight ownership is released;
- no implicit follow-up is requested by the failed attempt;
- the staged KV entry remains available for one later explicitly scheduled generation;
- the later explicit attempt persists the pending KV key and acknowledges the checkpoint cleanly.

The fixture restores `kv_store` immediately after failure and defensively during teardown. It uses only the disposable integration-test database.

## Safety boundary

No production/shared database, credential, migration, deployment, runtime failure hook, automatic SQL rollback, retry timer, backoff policy, queue-overload behavior, crash proof, PRS-003 outage state or PRS-004 fencing behavior was introduced.

## Delivery evidence

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T23:50:00+02:00
status: complete
issue: 171
pr: 172
feature_head: 593834b3a55d30f9f19a182579473c7e44b3be00
feature_merge: 1d7029f5fb6b493609d47ec28b00e07d4bdbd1d1
context_routes:
  - production-resilience
  - player-persistence
  - sql-kv-boundary
  - failure-injection
  - integration-testing
  - agent-governance
proven:
  - PRS-002E was already merged and lifecycle-archived before this package.
  - IOLoginData commits its SQL transaction before separately staged wheel KV persistence.
  - KVSQL reports false when its real batch transaction fails and retains staged in-memory entries.
  - The PRS-002F fixture commits a dedicated SQL probe before forcing the real KV batch failure.
  - The SQL probe remains durable while the failed KV row is absent.
  - executePlayerCheckpointAttempt preserves dirty state, releases in-flight ownership and requests no implicit follow-up after the combined failure.
  - One later explicit generation persists the retained KV key and clears dirty state.
  - The fixture restores kv_store before setup, immediately after injected failure and defensively in teardown.
  - The final feature diff contained exactly four owned paths and was synchronized with main at behind_by zero.
  - PR 172 had no review threads or submitted change requests before merge.
validation:
  - command: exact-head CI 30306555630
    result: PASS
    evidence: CI run 556 passed Fast Checks, Lua, platform builds, MariaDB schema import and Linux debug full CTest.
  - command: exact-head Required 30306555451
    result: PASS
    evidence: Required run 593 accepted all applicable workflows for feature head 593834b3a55d30f9f19a182579473c7e44b3be00.
  - command: exact-head autofix 30306555480
    result: PASS
    evidence: autofix run 478 completed successfully without moving the final feature head.
  - command: Linux debug MariaDB CTest
    result: PASS
    evidence: Schema import and Run Tests completed successfully in job 90112863591.
  - command: final drift and review audit
    result: PASS
    evidence: behind_by zero, mergeable true, exactly four changed paths and no review threads.
  - command: squash merge PR 172
    result: PASS
    evidence: Feature merged to main as 1d7029f5fb6b493609d47ec28b00e07d4bdbd1d1 and issue 171 closed completed.
unknown:
  - process-crash behavior before save
  - process-crash behavior after commit but before acknowledgement
  - overloaded checkpoint queue behavior
conflicts: []
blockers: []
next_action: Select one remaining production-resilience gap under a separately scoped issue; do not extend this archived package.
```
