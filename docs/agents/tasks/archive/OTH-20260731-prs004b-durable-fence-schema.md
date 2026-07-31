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
lifecycle_pr: "281"
lifecycle_head_sha: e231c3211cc2195c369db22c629b6c8b7af3bb1c
lifecycle_required_run: 30650937957
lifecycle_merge_sha: 20654da5ce2388a5ab16f60c45d428c9c5cf75c7
finalizer_pr: "282"
finalizer_head_sha: 71123b285b3f03ec37e8c952fa7251a08c7f8054
finalizer_required_run: 30651088635
finalizer_merge_sha: 5db64e7ca5c1196a78ce13bcc7d2c3e329b89607
created: 2026-07-31
updated: 2026-07-31T19:30:00+02:00
owned_paths:
  - schema.sql
  - data-otservbr-global/migrations/59.lua
  - tests/integration/database/database_migrations_it.cpp
  - tests/integration/prs_004b/run_durable_fence_schema.sh
  - .github/workflows/prs-004b-durable-fence-schema.yml
  - docs/architecture/prs-004b-durable-writer-fence-schema.md
  - docs/agents/tasks/active/OTH-20260731-prs004b-durable-fence-schema.md
---

# PRS-004B durable MariaDB writer-fence schema — terminal

## Delivered contract

A dedicated `player_writer_fence` MariaDB authority table stores stable player subject, ownership generation, exact nullable `BINARY(16)` writer token and state revision. It enforces subject primary-key ownership, global token uniqueness, active/inactive shape and player foreign-key cascade. Existing and newly created players receive fail-closed inactive rows.

Migration 59, canonical schema 59 and a bounded rollback/re-upgrade procedure describe the same object. This slice adds no CAS API, protected-save wiring, handoff, Redis authority, retry/replay, production credentials, deployment or RPO/RTO claim.

## Exact evidence

- issue #276: closed completed;
- feature PR #279 exact head `0793f4478520b123d395077d01fe989aa741e09f`, merge `5672b9d561cba1b9a482519df10e4472119bc8da`;
- feature checks: dedicated `30649631382`, CI `30649631473`, Required `30649631397`, Repository Audit `30649631320`, autofix `30649631361`, MySQL Schema Check `30649631189`: PASS;
- lifecycle PR #281 exact head `e231c3211cc2195c369db22c629b6c8b7af3bb1c`, Required `30650937957`, merge `20654da5ce2388a5ab16f60c45d428c9c5cf75c7`;
- finalizer PR #282 exact head `71123b285b3f03ec37e8c952fa7251a08c7f8054`, Required `30651088635`, merge `5db64e7ca5c1196a78ce13bcc7d2c3e329b89607`;
- feature scope exactly seven paths; lifecycle exactly active deletion plus archive addition; finalizer exactly one archive path;
- clean discussions, reviews and review threads; feature `behind_by=0` before expected-head merge;
- active record absent.

## Safety evidence

- no reconnect, ping, retry or SQL replay;
- no CAS/save/handoff behavior in the schema slice;
- no production database access, credentials or deployment;
- rollback is bounded and explicit, not an automatic production framework.

## Terminal checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T19:30:00+02:00
status: completed
phase: terminal
feature_pr: 279
feature_head_sha: 0793f4478520b123d395077d01fe989aa741e09f
feature_merge_sha: 5672b9d561cba1b9a482519df10e4472119bc8da
lifecycle_pr: 281
lifecycle_head_sha: e231c3211cc2195c369db22c629b6c8b7af3bb1c
lifecycle_required_run: 30650937957
lifecycle_merge_sha: 20654da5ce2388a5ab16f60c45d428c9c5cf75c7
finalizer_pr: 282
finalizer_head_sha: 71123b285b3f03ec37e8c952fa7251a08c7f8054
finalizer_required_run: 30651088635
finalizer_merge_sha: 5db64e7ca5c1196a78ce13bcc7d2c3e329b89607
proven:
  - exact seven-path feature scope and exact-head green checks
  - schema import, migration, constraints, backfill, trigger and bounded rollback/re-upgrade
  - completed issue and full feature-to-archive-to-finalizer lifecycle
  - active record absent and no unresolved discussion
unknown: []
conflicts: []
blockers: []
next_action: none
```
