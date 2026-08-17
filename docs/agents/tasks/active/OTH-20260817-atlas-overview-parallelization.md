---
task_id: OTH-20260817-atlas-overview-parallelization
status: active
owner: chat-github-atlas-overview-perf
branch: perf/OTH-20260817-atlas-overview-parallelization
base_branch: main
created: "2026-08-17T22:10:00+02:00"
updated: "2026-08-17T22:10:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: ""
ownership_released: false
owned_paths:
  - tools/otbm_atlas/atlas.py
  - tools/otbm_atlas/tests/test_atlas_overview_parallel.py
  - docs/agents/tasks/active/OTH-20260817-atlas-overview-parallelization.md
---

# OTBM Atlas parallel overview generation

## Goal

Remove the verified serial post-render bottleneck in full Atlas builds while preserving exact detail/overview bytes, incremental reuse semantics, manifest ordering, and canonical source identity.

## Live evidence

- Owner desktop build reached detail `3494 / 3494` while `overview` and `overview-low` were only `1149 / 3494`.
- CPU utilization dropped sharply after detail completion.
- `tools/otbm_atlas/atlas.py` currently generates both overview derivatives inside one serial loop after the process-pooled detail phase.
- The owner is building from WSL against a checkout under `/mnt/c`, making unnecessary duplicate detail reads and serialized PNG work especially expensive.

## Acceptance criteria

- [ ] Generate dirty overview derivatives with bounded process parallelism using the existing `workers` budget.
- [ ] Read each detailed chunk at most once when both 4x and 8x derivatives require regeneration.
- [ ] Preserve `make_overview()` byte semantics and atomic image/report writes.
- [ ] Preserve reuse checks for existing valid overview outputs.
- [ ] Preserve deterministic chunk/manifest ordering regardless of worker completion order.
- [ ] Add focused regression coverage proving sequential and parallel overview outputs/metadata are byte-identical.
- [ ] Run focused Atlas tests and repository-required exact-head checks.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-17T22:10:00+02:00
branch: perf/OTH-20260817-atlas-overview-parallelization
base_main: e382f93b7b1b12e39edfe14afe08ccb639c4fe2a
status: implementing
phase: implementation
owned_paths:
  - tools/otbm_atlas/atlas.py
  - tools/otbm_atlas/tests/test_atlas_overview_parallel.py
  - docs/agents/tasks/active/OTH-20260817-atlas-overview-parallelization.md
proven:
  - full detail phase already uses ProcessPoolExecutor(max_workers=workers)
  - overview and overview-low are currently generated serially
  - current overview loop reads the same detail PNG separately for each derivative when both are dirty
unknown:
  - exact speedup on owner WSL/NTFS workload after parallelization
  - exact-head CI outcome
blockers: []
next_action: implement parallel overview generation with byte-equivalence tests, then validate exact head
```
