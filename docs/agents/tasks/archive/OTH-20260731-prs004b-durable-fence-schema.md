---
task_id: OTH-20260731-prs004b-durable-fence-schema
status: completed
project_lane: otheryn-runtime
policy_version: 2
task_kind: implementation
implementation_authorized: true
branch: dudantas/prs-004b-durable-fence-schema
base_branch: main
start_sha: d478323ebb0d047eaf219522ac2a18f48af08d15
issue: "276"
feature_pr: "279"
feature_head_sha: 0793f4478520b123d395077d01fe989aa741e09f
feature_merge_sha: 5672b9d561cba1b9a482519df10e4472119bc8da
lifecycle_pr: pending
lifecycle_head_sha: pending
lifecycle_merge_sha: pending
finalizer_pr: pending
finalizer_head_sha: pending
finalizer_merge_sha: pending
created: 2026-07-31
updated: 2026-07-31T19:22:00+02:00
owned_paths:
  - schema.sql
  - data-otservbr-global/migrations/59.lua
  - tests/integration/database/database_migrations_it.cpp
  - tests/integration/prs_004b/run_durable_fence_schema.sh
  - .github/workflows/prs-004b-durable-fence-schema.yml
  - docs/architecture/prs-004b-durable-writer-fence-schema.md
  - docs/agents/tasks/active/OTH-20260731-prs004b-durable-fence-schema.md
---

# PRS-004B durable MariaDB writer-fence schema — completed

## Delivered contract

A dedicated `player_writer_fence` MariaDB authority table now stores stable player subject, ownership generation, exact nullable `BINARY(16)` writer token and state revision. It enforces subject primary-key ownership, global token uniqueness, active/inactive shape and player foreign-key cascade. Existing and newly created players receive fail-closed inactive rows.

Migration 59, canonical schema 59 and a bounded rollback/re-upgrade procedure describe the same object. This slice adds no CAS API, protected-save wiring, handoff, Redis authority, retry/replay, production credentials, deployment or RPO/RTO claim.

## Exact feature evidence

- issue #276: closed completed;
- feature PR #279: expected-head squash merged;
- exact feature head: `0793f4478520b123d395077d01fe989aa741e09f`;
- feature merge: `5672b9d561cba1b9a482519df10e4472119bc8da`;
- changed paths: exactly seven declared owned paths;
- base freshness: `behind_by=0` before merge;
- discussions, reviews and review threads: empty;
- PRS-004B Durable Fence Schema run `30649631382`: PASS;
- CI run `30649631473`: PASS;
- Required run `30649631397`: PASS;
- Repository Audit run `30649631320`: PASS;
- autofix run `30649631361`: PASS;
- MySQL Schema Check run `30649631189`: PASS.

## Safety evidence

- no `MYSQL_OPT_RECONNECT`, `mysql_ping`, reconnect loop or SQL replay;
- no CAS/save/handoff behavior in the schema slice;
- no production database access, credentials or deployment;
- rollback is bounded, explicit and disposable-test proven, not an automatic production framework.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T19:22:00+02:00
status: completed
phase: archive
head: 0793f4478520b123d395077d01fe989aa741e09f
head_scope: exact validated feature head
feature_pr: 279
feature_merge_sha: 5672b9d561cba1b9a482519df10e4472119bc8da
lifecycle_pr: pending
finalizer_pr: pending
proven:
  - exact seven-path scope
  - clean schema import and migration 58 to 59
  - fail-closed backfill and creation trigger
  - constraints, duplicate-token rejection, bounded rollback and re-upgrade
  - exact-head dedicated, CI, Required, Repository Audit, autofix and schema checks
unknown:
  - lifecycle PR head, Required and merge
  - finalizer PR head, Required and merge
conflicts: []
blockers: []
next_action: merge the two-path lifecycle PR, then complete one-file finalizer and terminal metadata
```
