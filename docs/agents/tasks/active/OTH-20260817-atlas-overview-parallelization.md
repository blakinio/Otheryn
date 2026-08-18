---
task_id: OTH-20260817-atlas-overview-parallelization
status: validating
owner: chat-github-atlas-overview-perf
branch: perf/OTH-20260817-atlas-overview-parallelization
base_branch: main
created: "2026-08-17T22:10:00+02:00"
updated: "2026-08-18T06:44:21+02:00"
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

Remove the verified serial post-render and resume overview bottlenecks on the owner desktop while preserving exact detail/overview bytes, fail-closed reuse semantics, deterministic manifest ordering, canonical sources, and resumability of the existing `/mnt/c` corpus.

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

The real system boundary is the owner WSL full-world build: canonical OTBM plus supplied asset corpus through detail validation, overview reuse/generation, final production data, independent verification, and observable throughput.

## Live evidence

- Owner corpus has complete detail `3494 / 3494`, overview 4x `3494 / 3494`, and overview 8x `3494 / 3494`.
- Missing-overview generation was already parallelized successfully with the explicit worker budget.
- After `Resume detail validation: PASS`, reuse validation still walked `6988` existing overview derivatives serially.
- The old path read each overview report once in `build_overviews()` and again in `overview_output_reusable()`, then hashed the PNG on legacy/resume adoption.
- Owner telemetry during that phase showed low CPU and low physical NVMe utilization, so no claim is made that the Samsung NVMe itself is the bottleneck; DrvFS/VFS/syscall/hash serialization remains the supported explanation for this optimization target.

## Implementation

- Existing and missing 4x/8x overview derivatives use the same explicit `workers` budget (`ATLAS_WORKERS` / `--workers`).
- Overview reuse validation is bounded-parallel with one process job per detail chunk and up to the requested worker count.
- Each validation candidate reads its report bytes once and its PNG bytes once; the report is parsed from the already-read bytes and both payloads are hashed from those bytes without a second file read.
- Reuse remains fail-closed: required PNG/report presence, expected overview fingerprint, report checksum, report dimensions for the factor, actual PNG checksum, and (when production state exists) the committed PNG/report identities must all agree.
- The existing fingerprint remains `sha256(OVERVIEW_VERSION:factor:detail_checksum)`, preserving factor/version/source-detail dependency binding.
- Tampered PNG, wrong fingerprint, missing PNG/report, or checksum mismatch becomes dirty and is regenerated from the existing validated detail PNG.
- Validation results are collected by original chunk index and applied in canonical chunk order, independent of worker completion order.
- Valid overviews are adopted into chunk metadata without rewrite; dirty generation retains the canonical NEAREST byte path and paired single-detail decode optimization.
- Resume progress now emits bounded milestones: candidate count/worker count, approximately every 256 validated derivatives, final validation count, and valid/dirty totals.
- Existing `/mnt/c` resume defaults are unchanged. The native-WSL work-root optimization remains only the default for new full builds; no automatic migration/copy of the existing 13+ GB corpus was added.

## Finalization audit scope

Reviewed the post-overview orchestration in `production_data.py`: unknown-items, spawns/sprites, houses, composition, spatial/factual, tile-inspector, environment-animation resume, and viewer already use production phase caches or resumable paths where applicable. No additional serial phase currently has owner-runtime evidence satisfying the requested threshold (material duration + one-core behavior + thousands of independent operations), so no speculative finalization refactor is included. `commit_production_render_state()` remains a possible observation point if owner benchmark evidence later proves it material, but it is not changed without runtime proof.

## Regression coverage

Focused overview tests now cover:

1. serial versus parallel validation reuse/dirty equivalence;
2. deterministic chunk ordering;
3. valid overview reuse without rewrite;
4. tampered overview PNG rejection and repair;
5. wrong fingerprint rejection and repair;
6. missing report rejection and repair;
7. missing PNG rejection and repair;
8. checksum mismatch rejection and repair;
9. one worker versus multiple workers semantic equivalence;
10. progress reporting without semantic change;
11. canonical paired single-decode byte equivalence.

The existing partial-resume and production-incremental suites remain part of the required exact-head Atlas validation.

## Acceptance criteria

- [x] Generate dirty overview derivatives with bounded process parallelism using the existing `workers` budget.
- [x] Validate existing overview derivatives with bounded process parallelism using the existing `workers` budget.
- [x] Avoid duplicate report/PNG reads within the validation candidate path.
- [x] Read each detailed chunk at most once when both 4x and 8x derivatives require regeneration.
- [x] Decode the detailed PNG at most once for the paired 4x/8x Pillow fast path.
- [x] Preserve canonical `make_overview()` byte semantics and atomic image/report writes.
- [x] Preserve and strengthen fail-closed reuse checks for existing overview outputs.
- [x] Preserve deterministic chunk/manifest ordering regardless of worker completion order.
- [x] Add fail-closed partial-resume adoption for a complete detail phase.
- [x] Reject tampered overview/detail PNGs, wrong fingerprints, missing reports/PNGs, checksum mismatches, incomplete reports and incomplete detail inventory.
- [x] Add focused regression coverage for sequential/parallel equivalence, validation safety, progress, and resume safety.
- [ ] Final exact-head Atlas test workflow passes.
- [ ] Final exact-head incremental workflow passes.
- [ ] Final repository-required exact-head checks pass.
- [ ] Owner WSL resume confirms parallel validation throughput and final verification on the real 3494-chunk corpus.
- [ ] Fresh independent post-implementation audit records zero material findings on the exact implementation diff.
- [ ] Final closeout head satisfies review/CI/owner-runtime evidence and related-PR cleanup.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
task_kind: implementation
implementation_authorized: true
updated_at: 2026-08-18T06:44:21+02:00
phase: validate
session_id: chat-20260818-0639-atlas-parallel-validation
session_role: validator
execution_mode: chat-github
execution_reason: GitHub connector supports owned-path edits and exact-head Actions evidence without owner-funded AI
project_lane: otheryn-content
branch: perf/OTH-20260817-atlas-overview-parallelization
pr: 446
status: validating
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: high
decomposition_decision: single
decomposition_reason: bounded continuation of the same Atlas desktop/resume bottleneck
invocation_started_at: 2026-08-18T06:39:00+02:00
last_progress_at: 2026-08-18T06:44:21+02:00
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 0
stall_warnings: 0
heavy_validation_runs: 0
proven:
  - overview validation is now bounded-parallel and consumes the same explicit worker budget
  - each validation candidate reads report bytes once and overview PNG bytes once
  - actual PNG checksum and expected fingerprint remain mandatory for reuse
  - factor/version/source-detail dependency remains bound by the unchanged overview fingerprint formula
  - valid derivatives are not rewritten and worker completion order cannot reorder manifest chunks
  - existing owner /mnt/c resume paths and complete-detail adoption contract are unchanged
  - review thread inventory was empty before final exact-head validation
unknown:
  - exact-head Atlas/incremental/required CI outcome after this checkpoint commit
  - real owner-machine validation throughput and full finalization/verify runtime
blockers: []
next_action: verify exact-head Atlas, incremental and required CI plus fresh audit/review hygiene; when green, run the owner WSL resume benchmark on the existing corpus
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 1
  session_id: chat-20260818-0639-atlas-parallel-validation
  session_started_at: 2026-08-18T06:39:00+02:00
  checkpointed_at: 2026-08-18T06:44:21+02:00
  last_progress_at: 2026-08-18T06:44:21+02:00
  phase: validate
  exact_head: pending-this-checkpoint-commit
  pull_request: 446
  active_operation: exact-head GitHub Actions validation after checkpoint commit
  external_run_ids: []
  operation_started_at: null
  wait_deadline_at: null
  check_generation: final-checkpoint-head
  checks_used: 0
  status: ready
  safe_to_resume: true
  resume_condition: PR 446 head equals this checkpoint commit and exact-head workflows are discoverable
  next_action: inspect one aggregate exact-head CI snapshot and audit any failure before owner benchmark
```
