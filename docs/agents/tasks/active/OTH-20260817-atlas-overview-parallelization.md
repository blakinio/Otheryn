---
task_id: OTH-20260817-atlas-overview-parallelization
status: validating
owner: chat-github-atlas-overview-perf
branch: perf/OTH-20260817-atlas-overview-parallelization
base_branch: main
created: "2026-08-17T22:10:00+02:00"
updated: "2026-08-17T22:24:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: ""
ownership_released: false
owned_paths:
  - tools/otbm_atlas/local_parallel_build.py
  - tools/otbm_atlas/build_latest_local.sh
  - tools/otbm_atlas/tests/test_atlas_overview_parallel.py
  - docs/agents/tasks/active/OTH-20260817-atlas-overview-parallelization.md
---

# OTBM Atlas parallel overview generation

## Goal

Remove the verified serial post-render bottleneck in owner desktop full Atlas builds while preserving exact detail/overview bytes, incremental reuse semantics, manifest ordering, and source hashes.

## Live evidence

- Owner desktop build reached detail `3494 / 3494` while `overview` and `overview-low` were only `1149 / 3494`.
- CPU utilization dropped sharply after detail completion.
- Canonical `tools/otbm_atlas/atlas.py` generates both overview derivatives inside one serial loop after the process-pooled detail phase.
- The owner build runs in WSL from a checkout under `/mnt/c`; its generated Atlas had already reached roughly 13 GB, making serialized PNG work plus DrvFS/NTFS metadata traffic a material bottleneck.

## Implementation

- Added `local_parallel_build.py` as a bounded desktop/full-build adapter over the existing production Atlas primitives.
- Missing 4x/8x derivatives for one chunk are grouped into one process job, so the detail PNG is read once when both derivatives are dirty.
- Overview jobs use the same explicit `workers` budget as detail rendering and update the existing ordered chunk records only after each future completes.
- Existing `overview_output_reusable()` checks remain authoritative; reusable derivatives are not rewritten.
- Existing `make_overview()` is used unchanged, preserving derivative pixel/PNG semantics.
- The one-command local launcher detects WSL checkouts under `/mnt/*` and defaults heavy cache/spool/output/log paths to `$HOME/.cache/otheryn-atlas` on the native WSL filesystem. `ATLAS_LOCAL_WORK_ROOT` can override that default.
- The launcher reuses a previously verified ZIP from the old checkout cache when available, keeps the real Python runner/forkserver fix, and exposes the repository root through `PYTHONPATH`.

## Acceptance criteria

- [x] Generate dirty overview derivatives with bounded process parallelism using the existing `workers` budget.
- [x] Read each detailed chunk at most once when both 4x and 8x derivatives require regeneration.
- [x] Preserve `make_overview()` byte semantics and atomic image/report writes.
- [x] Preserve reuse checks for existing valid overview outputs.
- [x] Preserve deterministic chunk/manifest ordering regardless of worker completion order.
- [x] Add focused regression coverage proving sequential and parallel overview outputs/metadata are byte-identical.
- [ ] Focused Atlas tests pass on exact head.
- [ ] Repository-required exact-head checks pass.
- [ ] Owner WSL runtime confirms the expected throughput improvement on a real 3494-chunk build.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-17T22:24:00+02:00
branch: perf/OTH-20260817-atlas-overview-parallelization
base_main: e382f93b7b1b12e39edfe14afe08ccb639c4fe2a
status: validating
phase: pre-pr-validation
owned_paths:
  - tools/otbm_atlas/local_parallel_build.py
  - tools/otbm_atlas/build_latest_local.sh
  - tools/otbm_atlas/tests/test_atlas_overview_parallel.py
  - docs/agents/tasks/active/OTH-20260817-atlas-overview-parallelization.md
proven:
  - existing detail phase uses bounded ProcessPoolExecutor workers
  - existing overview loop is serial
  - new local overview jobs group both derivatives per detail read
  - new launcher defaults heavy writes away from /mnt/c on WSL
  - source map/assets hashes and existing derivative encoder functions are unchanged
unknown:
  - exact owner-machine speedup before the next real run
  - exact-head CI outcome
blockers: []
next_action: open PR, run focused/exact-head validation, repair only evidenced failures, then owner benchmarks the merged launcher on WSL
```
