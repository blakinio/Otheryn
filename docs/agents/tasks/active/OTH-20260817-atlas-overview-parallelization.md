---
task_id: OTH-20260817-atlas-overview-parallelization
status: waiting
owner: chat-github-atlas-overview-perf
branch: perf/OTH-20260817-atlas-overview-parallelization
base_branch: main
created: "2026-08-17T22:10:00+02:00"
updated: "2026-08-17T22:33:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "446"
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

## Delivery classification

```yaml
feature_scope:
  type: infrastructure
  user_facing: false
  backend_required: false
  frontend_required: false
  integration_required: true
  e2e_required: true
```

The real system boundary is the owner WSL full-world build: canonical OTBM plus supplied asset corpus through detail/overview generation, independent verification, and observable CPU/throughput behaviour.

## Live evidence

- Owner desktop build reached detail `3494 / 3494` while `overview` and `overview-low` were only `1149 / 3494`.
- CPU utilization dropped sharply after detail completion.
- Canonical `tools/otbm_atlas/atlas.py` generates both overview derivatives inside one serial loop after the process-pooled detail phase.
- The owner build runs in WSL from a checkout under `/mnt/c`; its generated Atlas had already reached roughly 13 GB, making serialized PNG work plus DrvFS/NTFS metadata traffic a material bottleneck.

## Implementation

- Added `local_parallel_build.py` as a bounded desktop/full-build adapter over the existing production Atlas primitives.
- Missing 4x/8x derivatives for one chunk are grouped into one process job and use the same explicit `workers` budget as detail rendering.
- With Pillow available, one detailed PNG decode now feeds both canonical NEAREST derivatives; fallback environments continue to call the existing `make_overview()` implementation per factor.
- Existing `overview_output_reusable()` checks remain authoritative; reusable derivatives are not rewritten.
- Result metadata is applied back to the original ordered chunk list, so worker completion order does not change manifest ordering.
- The one-command local launcher detects WSL checkouts under `/mnt/*` and defaults heavy cache/spool/output/log paths to `$HOME/.cache/otheryn-atlas` on the native WSL filesystem. `ATLAS_LOCAL_WORK_ROOT` can override that default.
- The launcher reuses a previously verified ZIP from the old checkout cache when available, keeps the real Python runner/forkserver fix, and exposes the repository root through `PYTHONPATH`.

## Acceptance criteria

- [x] Generate dirty overview derivatives with bounded process parallelism using the existing `workers` budget.
- [x] Read each detailed chunk at most once when both 4x and 8x derivatives require regeneration.
- [x] Decode the detailed PNG at most once for the paired 4x/8x Pillow fast path.
- [x] Preserve canonical `make_overview()` byte semantics and atomic image/report writes.
- [x] Preserve reuse checks for existing valid overview outputs.
- [x] Preserve deterministic chunk/manifest ordering regardless of worker completion order.
- [x] Add focused regression coverage proving sequential and parallel overview outputs/metadata are byte-identical.
- [x] Focused Atlas tests pass on the validated implementation head.
- [x] Repository-required exact-head checks pass on the validated implementation head.
- [ ] Owner WSL runtime confirms the expected throughput improvement on a real 3494-chunk build.
- [ ] Fresh independent post-implementation audit records zero material findings.
- [ ] Final closeout head satisfies exact-head validation and related-PR cleanup.

## Validation evidence

```yaml
validated_implementation_head: c5db2fd5600417f5a1915dee27d088343f7933d4
pull_request: 446
focused:
  atlas_unit_and_runtime_tests:
    result: PASS
    tests: 207
    skipped: 5
    evidence:
      - single-decode fast path is byte-identical to canonical make_overview for 4x and 8x
      - sequential and 3-worker overview outputs/reports are byte-identical
      - valid overview outputs are reused without rewrite
component:
  otbm_atlas_incremental: PASS
  otbm_creature_animation_audit: PASS
exact_head:
  CI: PASS
  Required: PASS
review:
  unresolved_threads: 0
  comments: 0
pending_external_evidence:
  - owner WSL full-world throughput/CPU benchmark using the optimized launcher
```

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
task_kind: implementation
implementation_authorized: true
updated_at: 2026-08-17T22:33:00+02:00
phase: validate
session_id: chat-20260817-atlas-overview-perf
session_role: implementer
execution_mode: chat-github
execution_reason: bounded Atlas Python/shell optimization using GitHub connector and Actions validation
project_lane: otheryn-content
branch: perf/OTH-20260817-atlas-overview-parallelization
pr: 446
validated_implementation_head: c5db2fd5600417f5a1915dee27d088343f7933d4
status: waiting
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: high
decomposition_decision: single
decomposition_reason: one cohesive owner-desktop Atlas build bottleneck with shared output semantics
validation_level: full
session_rotation_count: 0
heavy_validation_runs: 1
stale_takeover_count: 0
human_interruptions: 0
invocation_started_at: 2026-08-17T22:10:00+02:00
last_progress_at: 2026-08-17T22:28:51+02:00
ci_checks_for_current_head: 10
ci_check_count_precision: lower-bound
unchanged_state_checks: 4
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 0
stall_warnings: 1
anti_stall_note: exact-head polling limit was exceeded before the nested docs/agents governance was re-read; no further CI polling is permitted in this invocation
owned_paths:
  - tools/otbm_atlas/local_parallel_build.py
  - tools/otbm_atlas/build_latest_local.sh
  - tools/otbm_atlas/tests/test_atlas_overview_parallel.py
  - docs/agents/tasks/active/OTH-20260817-atlas-overview-parallelization.md
proven:
  - owner evidence isolates the serial overview phase after all 3494 detail chunks existed
  - paired overview work is process-parallel and bounded by the configured worker count
  - paired Pillow overview generation decodes detail once and matches canonical bytes in exact-head tests
  - WSL launcher moves heavy generated state off /mnt/c by default
  - source map/asset SHA gates and detail renderer semantics remain unchanged
  - exact validated implementation head passed 207 Atlas tests, OTBM Atlas Incremental, CI and Required
  - PR 446 has zero review threads and zero comments
unknown:
  - measured owner-machine speedup and CPU utilization on a real optimized 3494-chunk run
  - fresh independent audit result
blockers: []
next_action: owner benchmarks PR 446 optimized launcher on WSL after the currently running legacy build is no longer consuming the machine and returns the overview progress/timing plus CPU observation
```
