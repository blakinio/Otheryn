---
task_id: OTH-20260817-atlas-overview-parallelization
status: validating
owner: chat-github-atlas-overview-perf
branch: perf/OTH-20260817-atlas-overview-parallelization
base_branch: main
created: "2026-08-17T22:10:00+02:00"
updated: "2026-08-17T23:16:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "446"
ownership_released: false
owned_paths:
  - tools/otbm_atlas/local_parallel_build.py
  - tools/otbm_atlas/build_latest_local.sh
  - tools/otbm_atlas/resume_partial_local.py
  - tools/otbm_atlas/resume_latest_local.sh
  - tools/otbm_atlas/tests/test_atlas_overview_parallel.py
  - tools/otbm_atlas/tests/test_atlas_partial_resume.py
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

- Owner desktop build reached detail `3494 / 3494` while `overview` and `overview-low` lagged far behind and CPU utilization collapsed.
- At the interruption decision point the owner had all `3494` detail chunks and more than two thousand overview pairs already persisted.
- Canonical `tools/otbm_atlas/atlas.py` generates both overview derivatives inside one serial loop after the process-pooled detail phase.
- The owner build runs in WSL from a checkout under `/mnt/c`; its generated Atlas had already reached roughly 13 GB, making serialized PNG work plus DrvFS/NTFS metadata traffic a material bottleneck.

## Implementation

- Added `local_parallel_build.py` as a bounded desktop/full-build adapter over the existing production Atlas primitives.
- Missing 4x/8x derivatives for one chunk are grouped into one process job and use the same explicit `workers` budget as detail rendering.
- With Pillow available, one detailed PNG decode feeds both canonical NEAREST derivatives; fallback environments continue to call the existing `make_overview()` implementation per factor.
- Existing `overview_output_reusable()` checks remain authoritative; reusable derivatives are not rewritten.
- Result metadata is applied back to the original ordered chunk list, so worker completion order does not change manifest ordering.
- The one-command local launcher detects WSL checkouts under `/mnt/*` and defaults heavy cache/spool/output/log paths to `$HOME/.cache/otheryn-atlas` on the native WSL filesystem.
- Added a fail-closed interrupted-build resume path. It reconstructs production fingerprints from the existing spool and current asset dependency state, then adopts all existing detail outputs only after every detail report fingerprint and PNG checksum matches. It never silently rerenders or accepts mismatched detail bytes.
- The resume launcher requires the complete `3494`-detail phase, reuses already-valid overview outputs, parallelizes only missing derivatives, finalizes manifest/production state/data, and runs independent Atlas verification.

## Acceptance criteria

- [x] Generate dirty overview derivatives with bounded process parallelism using the existing `workers` budget.
- [x] Read each detailed chunk at most once when both 4x and 8x derivatives require regeneration.
- [x] Decode the detailed PNG at most once for the paired 4x/8x Pillow fast path.
- [x] Preserve canonical `make_overview()` byte semantics and atomic image/report writes.
- [x] Preserve reuse checks for existing valid overview outputs.
- [x] Preserve deterministic chunk/manifest ordering regardless of worker completion order.
- [x] Add fail-closed partial-resume adoption for a complete detail phase.
- [x] Reject tampered detail PNGs, wrong fingerprints, incomplete reports and incomplete detail inventory during resume.
- [x] Add focused regression coverage for sequential/parallel equivalence and resume safety.
- [ ] Final exact-head focused Atlas tests pass after resume additions.
- [ ] Final repository-required exact-head checks pass after resume additions.
- [ ] Owner WSL resume confirms missing overview throughput improvement and final verification on the real 3494-chunk corpus.
- [ ] Fresh independent post-implementation audit records zero material findings.
- [ ] Final closeout head satisfies exact-head validation and related-PR cleanup.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
task_kind: implementation
implementation_authorized: true
updated_at: 2026-08-17T23:16:00+02:00
phase: validate
session_id: chat-20260817-2312-atlas-resume
session_role: implementer
execution_mode: chat-github
project_lane: otheryn-content
branch: perf/OTH-20260817-atlas-overview-parallelization
pr: 446
status: validating
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: high
decomposition_decision: single
decomposition_reason: partial resume is a bounded continuation of the same owner-desktop Atlas build bottleneck
invocation_started_at: 2026-08-17T23:12:00+02:00
last_progress_at: 2026-08-17T23:16:00+02:00
ci_checks_for_current_head: 1
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 0
stall_warnings: 0
proven:
  - existing owner build has complete 3494-detail phase
  - resume code validates current spool source SHA, dependency-derived detail fingerprints and actual detail PNG checksums before adoption
  - missing overview derivatives use the optimized bounded worker pool
  - existing valid overviews remain reusable
unknown:
  - exact-head CI outcome for resume additions
  - real owner-machine resume throughput and final verification
blockers: []
next_action: after focused exact-head validation is green, owner stops the legacy serial overview phase and runs tools/otbm_atlas/resume_latest_local.sh from PR 446
```
