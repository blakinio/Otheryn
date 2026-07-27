---
task_id: OTH-20260727-prs002f-kv-post-commit-failure-evidence
status: review
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
  - docs/agents/tasks/active/OTH-20260727-prs002f-kv-post-commit-failure-evidence.md
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

## Goal

Add one real, disposable MariaDB proof that KV persistence failure after a successful SQL-domain commit leaves the exact-owner checkpoint dirty and permits only a later explicit retry.

## Accepted target contract

When the SQL-domain mutation commits and the separately staged `KVSQL::saveAll()` fails afterward, the combined checkpoint attempt must report failure, preserve already durable SQL, leave the captured generation dirty, release the in-flight generation, request no implicit follow-up and retain the staged KV key for a later explicit generation.

## Failure-injection plan

- create and remove one dedicated SQL commit probe table in the integration-test database;
- instantiate a standalone `KVSQL` and stage one dedicated key only after the probe transaction commits;
- temporarily rename the disposable `kv_store` table so the real KV batch transaction fails;
- restore `kv_store` immediately and again defensively in teardown;
- prove SQL remains committed, the KV row is absent and checkpoint state remains dirty;
- issue one later explicit generation, persist the still-staged key and prove clean acknowledgement.

## Rollback plan

Delete the integration test, its CMake registration, the bounded contract note and this task record. The fixture restores `kv_store`, deletes its dedicated key and drops its probe table; no production schema, data or deployment state requires reversal.

## Explicit non-goals

- no production/shared database access or credentials;
- no production modification of `IOLoginData`, `SaveManager`, `KVSQL`, `Database` or `DBTransaction`;
- no automatic rollback of already committed SQL;
- no retry timer, backoff, queue policy, metrics backend or RPO claim;
- no process-crash, queue-overload, PRS-003 outage state or PRS-004 fencing work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T10:52:00+02:00
head: 16dd8e2540b8d52ee6ed342a30f08baeebea418a
branch: dudantas/prs-002f-kv-post-commit-failure-evidence
pr: 172
status: validating
context_routes:
  - production-resilience
  - player-persistence
  - sql-kv-boundary
  - failure-injection
  - integration-testing
  - agent-governance
owned_paths:
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_checkpoint_kv_post_commit_failure_it.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260727-prs002f-kv-post-commit-failure-evidence.md
proven:
  - PRS-002E is merged and lifecycle-archived on main.
  - IOLoginData commits its SQL transaction before staging wheel KV data.
  - KVSQL persists its in-memory snapshot in a separate DBTransaction and returns false when that batch fails.
  - KVStore retains staged in-memory entries after saveAll failure.
  - The fixture restores kv_store before setup, immediately after the injected failure and again in teardown.
  - The test commits a dedicated SQL probe, forces the real KV batch to fail, proves SQL remains durable and the KV row is absent, then persists the retained key on one explicit later generation.
  - Integration tests use a disposable MariaDB database and execute serially.
  - Open PRs 162 and 165 do not own the selected paths.
derived:
  - Temporarily renaming disposable kv_store is the smallest real-KV failure injection without a production hook.
unknown:
  - Exact-head integration-test, compile, formatting and platform results.
conflicts: []
first_failure: null
rejected_hypotheses:
  - fail a production or shared database
  - add a mutable global KV failure hook
  - roll back already committed SQL automatically
  - combine process-crash or queue-overload evidence
changed_paths:
  - docs/agents/tasks/active/OTH-20260727-prs002f-kv-post-commit-failure-evidence.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_checkpoint_kv_post_commit_failure_it.cpp
validation:
  - command: source and conflict preflight
    result: PASS
    evidence: Current main 4ad8c0f2ed1c6bd60da9b747b8ff180ced60b593; selected paths do not overlap open PRs.
  - command: deterministic fixture audit
    result: PASS
    evidence: Dedicated SQL table/key, defensive kv_store restoration, explicit persisted-state queries and one retained-key retry are present.
  - command: exact-head repository CI
    result: NOT_RUN
    evidence: PR 172 must complete CI, Required and autofix on its final head.
blockers:
  - Exact-head CI, Required and autofix
next_action: Inspect PR 172 exact-head CI and fix only concrete compile, integration-test or formatting failures.
```
