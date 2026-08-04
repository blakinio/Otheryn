---
task_id: OTH-20260731-prs004c-durable-fence-cas
status: completed
project_lane: otheryn-runtime
policy_version: 2
task_kind: implementation
implementation_authorized: true
branch: dudantas/prs-004c-durable-fence-cas
base_branch: main
start_sha: 049c79f36752adc812b62bcdf0b293e7abafc705
issue: "284"
feature_pr: "285"
feature_head_sha: 5c84b591dc00626190b1cc6c58149379529694b1
feature_merge_sha: 3186099e69b05ba17966f1ebe8caeedc3302ae51
lifecycle_pr: pending
lifecycle_head_sha: pending
lifecycle_required_run: pending
lifecycle_merge_sha: pending
finalizer_pr: pending
finalizer_head_sha: pending
finalizer_required_run: pending
finalizer_merge_sha: pending
created: 2026-07-31
updated: 2026-08-03T23:38:00+02:00
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

# PRS-004C durable writer-fence CAS repository — completed

## Delivered contract

MariaDB is the durable writer-fence authority. The repository provides typed acquire, transfer, release and exact-next revision operations. One conditional update and `ROW_COUNT()` execute under the same transaction and recursive connection lock. Exactly one affected row is `Applied`, zero rows is `StaleConflict`, malformed context is rejected before SQL and transaction/query/commit failure is `DatabaseFailure`.

Schema version 60 preserves ownership generation and state revision after release while clearing only the writer token. No player-save integration, handoff, Redis authority, reconnect, retry, SQL replay, production credential/data access, deployment or later-package behavior is included.

## Exact feature evidence

- issue #284: closed completed;
- feature PR #285 exact head `5c84b591dc00626190b1cc6c58149379529694b1`;
- expected-head squash merge `3186099e69b05ba17966f1ebe8caeedc3302ae51`;
- exact ten declared paths, `behind_by=0`, merge base current `main` and clean mergeability;
- comments, reviews and review threads: empty;
- dedicated PRS-004C run `30853158644`: PASS;
- CI run `30853158985`: PASS;
- Required run `30853158315`: PASS;
- Repository Audit run `30853158231`: PASS;
- MySQL Schema Check run `30853159385`: PASS;
- autofix run `30853157097`: PASS with no replacement commit.

## Validation and audit evidence

- disposable MariaDB integration proves monotonic acquire/transfer/release/reacquire history, exact-next revision, zero-row stale classification, one-winner concurrent acquisition and rollback preservation;
- source audit confirms one conditional update per operation, exact owner predicates, no retry/replay and no process-memory or Redis authority;
- full CI passed Linux debug/release, Windows CMake/solution, macOS, Docker, Lua, formatting and repository policy jobs on the unchanged exact feature head;
- runtime E2E is not applicable to this repository-only slice because no player-save or handoff consumer is introduced; disposable MariaDB is the complete applicable integration boundary.

## Recovery and PR hygiene

- stale-base defect was contained by integration PR #328, which merged current `main` into the canonical feature branch without overlapping the ten owned paths;
- historical bootstrap/synchronization PRs #286, #287, #288, #289, #290, #291, #293 and #295 are closed merged and intentionally terminal;
- PR #328 is closed merged and intentionally terminal;
- canonical feature PR #285 is closed merged;
- `dudantas/prs-004c-refresh-base-20260803` is a redundant non-owning staging branch retained only because no authorized branch-delete action was available; it must not be reused.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-03T23:38:00+02:00
status: completed
phase: archive
feature_pr: 285
feature_head_sha: 5c84b591dc00626190b1cc6c58149379529694b1
feature_merge_sha: 3186099e69b05ba17966f1ebe8caeedc3302ae51
feature_checks:
  dedicated: PASS:30853158644
  ci: PASS:30853158985
  required: PASS:30853158315
  repository_audit: PASS:30853158231
  mysql_schema_check: PASS:30853159385
  autofix: PASS:30853157097
lifecycle_pr: pending
finalizer_pr: pending
proven:
  - exact ten-path scope and base freshness
  - complete exact-head validation and clean discussion
  - issue completed and feature merged with expected-head protection
  - durable CAS semantics and applicable disposable-MariaDB integration evidence
unknown:
  - lifecycle PR exact head, Required and merge
  - finalizer PR exact head, Required and merge
  - historical terminal-evidence repair after finalizer
conflicts: []
blockers: []
next_action: merge the two-path active-to-archive lifecycle PR, then complete one-file finalizer and terminal-evidence metadata
```
