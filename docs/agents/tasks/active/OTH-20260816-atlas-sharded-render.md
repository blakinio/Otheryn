---
task_id: OTH-20260816-atlas-sharded-render
status: validating
owner: chat-github-atlas-shards
branch: perf/OTH-20260816-atlas-sharded-render
base_branch: main
created: "2026-08-16T13:50:00+02:00"
updated: "2026-08-16T14:02:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: ""
ownership_released: false
owned_paths:
  - tools/otbm_atlas/incremental_shards.py
  - tools/otbm_atlas/incremental_sharded.py
  - tools/otbm_atlas/tests/test_incremental_shards.py
  - .github/workflows/otbm-atlas-incremental.yml
  - docs/maps/otbm-atlas-sharded-render.md
  - docs/agents/tasks/active/OTH-20260816-atlas-sharded-render.md
---

# OTBM Atlas sharded incremental rendering

## Goal

After PR #421 introduced per-chunk spatial invalidation, make the actual dirty render CPU-parallel without repeating OTBM preprocessing and without distributing generated map imagery through public GitHub artifacts.

## Verified baseline

- PR #421 merged as `32f7d5c58a889b78de5637ff9fbea56686b79bcd`.
- The merged incremental planner has per-chunk spool hashes, dependency/reverse-dependency indexes, fail-closed full-build reasons, source-derived persistent cache and content-addressed publication primitives.
- Exact PR #421 head `af013af273f49c205632ec146a56465370e2c38d` passed `OTBM Atlas Incremental` run `31937396891`, `CI` `31937396876`, `Required` `31937396831`, Atlas tests, environment E2E and creature validation.
- The old dirty-render executor still rendered planned chunks serially inside one job.
- PR #419 remains the active owner of `tools/otbm_atlas/atlas.py`; this task does not modify that file.
- Current v3 recovery run `31938980540` is independent and must not be restarted/cancelled by this optimization task.

## Implementation

- `incremental_shards.py` deterministically partitions dirty chunks using exact spool bytes and LPT scheduling.
- Each shard executes the existing certified `incremental_core.render_selected_chunks()` in an isolated process/output directory.
- The parent writes the final render manifest only after all shards succeed and exact planned coverage is proven.
- `incremental_sharded.py` exposes the existing impact plan as a sharded command; default worker count is local CPU count and default shard count is four per worker.
- GitHub-hosted incremental CI uses `nproc` workers and `4 * nproc` execution shards after the single cached preprocessing/impact-plan stage.
- No generated map corpus is uploaded or handed between GitHub jobs.

## Acceptance inventory

- [x] Single spatial preprocessing remains upstream of dirty execution.
- [x] Deterministic weighted shard planning exists.
- [x] Every dirty chunk is assigned exactly once.
- [x] Worker/shard counts are bounded and invalid values fail closed.
- [x] Each worker renders through existing incremental render semantics rather than a new renderer.
- [x] Final manifest is written only after all shard futures succeed and exact coverage matches.
- [x] Workflow invokes sharded dirty execution on GitHub-hosted runner CPU.
- [x] No cross-job generated-image artifact transport introduced.
- [ ] Focused exact-head tests pass.
- [ ] Real two-chunk sharded canonical pixel-equivalence E2E passes.
- [ ] Exact-head repository CI/Required passes.
- [ ] Fresh review/audit has zero unresolved material findings.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-16T14:02:00+02:00
branch: perf/OTH-20260816-atlas-sharded-render
base_main: 32f7d5c58a889b78de5637ff9fbea56686b79bcd
status: validating
phase: pre-pr-validation
changed_paths:
  - tools/otbm_atlas/incremental_shards.py
  - tools/otbm_atlas/incremental_sharded.py
  - tools/otbm_atlas/tests/test_incremental_shards.py
  - .github/workflows/otbm-atlas-incremental.yml
  - docs/maps/otbm-atlas-sharded-render.md
  - docs/agents/tasks/active/OTH-20260816-atlas-sharded-render.md
proven:
  - PR 421 incremental foundation is merged and exact-head green
  - this change leaves render-core/pixel functions untouched
  - execution shards share one already-produced spatial spool
  - generated images remain same-job ephemeral data
unknown:
  - exact-head focused test result
  - real canonical two-shard E2E result
  - exact-head CI/Required result
blockers: []
next_action: open PR, inspect first exact-head workflow failures if any, repair root causes, and merge only after sharded E2E plus repository gates are green
```
