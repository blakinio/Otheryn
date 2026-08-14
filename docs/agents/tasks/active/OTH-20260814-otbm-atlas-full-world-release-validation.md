---
task_id: OTH-20260814-otbm-atlas-full-world-release-validation
status: waiting
owner: none
created: 2026-08-14
updated: 2026-08-14T17:18:00+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: true
modules_touched:
  - otbm-atlas
---

# OTBM atlas full-world release validation

This task owns the expensive complete-world certification intentionally deferred from `OTH-20260813-full-otbm-atlas` by explicit owner decision.

## Trigger

Run `.github/workflows/otbm-atlas-full-world-release.yml` manually only when a release/certification of the complete generated atlas is required. It is not a normal PR synchronize-time development gate.

## Required evidence

The workflow must:

- run one independent job per canonical floor Z0..15;
- build from `vendor/map-analysis/crystalserver/data-global/world/world.otbm` and the pinned Tibia 15.25 vendored assets;
- independently verify every floor;
- require `verification.ok == true` and `missingSprites == {}` for every floor;
- aggregate exactly 16 floor evidence artifacts;
- require exactly 3494 chunks across Z0..15;
- require identical canonical source fingerprints across all floors;
- require map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`;
- keep this certification separate from routine atlas implementation CI.

## Rationale

The previous four-floor-per-job gate repeatedly exceeded GitHub Actions 90- and 120-minute limits. Those cancellations occurred inside `build_atlas()` and did not report a functional verifier/renderer failure. Per-floor isolation bounds each job independently and prevents one expensive floor group from invalidating all remaining evidence.

## 2026-08-14 live analysis checkpoint

FACT — current `main` is `1021d08978f078ff845e6f3f82fbbbc482cbf543` and contains the per-floor release workflow plus the completed PR #381 implementation closeout.

FACT — `.github/workflows/otbm-atlas-full-world-release.yml` had not produced a workflow run on `main` before this validation invocation. Therefore complete-world release certification was still unproven on the exact merged `main` head at task start.

FACT — historical recovery runs on the PR #381 branch proved upper floors individually against the same canonical map fingerprint. Z8 and Z9 both completed successfully on head `417eaac6bf6e75475e4d3363f6e19c363f5eb2bf`; Z10..Z15 completed successfully on head `c09a4eccf78a4b15d4f529de5d842ee1b62c8ce2`. Example Z8 evidence reported 285 chunks, `verification.ok == true`, and `missingSprites == {}`. These runs are useful engineering evidence but are not a substitute for the exact-main release certification.

FACT — the current release workflow still calls `spool_map()` independently in every floor job, then deletes spool files from the other 15 floors before calling `build_atlas()`. This means every one of the 16 jobs performs a complete canonical OTBM parse before floor-specific rendering.

FACT — `build_atlas()` itself is resumable by spool/source fingerprint and chunk-render fingerprint, but the release workflow deliberately creates a fresh job-local output directory, so no spool or rendered chunk cache is shared between floor jobs.

INFERENCE — the duplicated full-map spooling is avoidable compute, but it was not the dominant cause of the longest historical jobs. Successful upper-floor build steps ranged roughly from 31 minutes on Z15 to 66 minutes on Z9; most elapsed time remains in floor rendering and post-render atlas enrichment rather than in the initial OTBM parse alone.

RECOMMENDATION — do not redesign the release gate around four-floor shards again. Keep one-floor failure isolation, and only optimize the implementation by adding an explicit floor-filtered spooling/build path (or a reusable pre-spool artifact) if profiling proves the duplicated parse materially affects cost. Any such change must preserve exact per-floor verification and the final 16-floor / 3494-chunk aggregate contract.

UNKNOWN — exact Z0..Z7 per-floor runtimes on the final per-floor workflow and complete exact-main 16-floor evidence remain unavailable until `.github/workflows/otbm-atlas-full-world-release.yml` completes.

## 2026-08-14 execution checkpoint

FACT — repository `main` was re-verified at `1021d08978f078ff845e6f3f82fbbbc482cbf543` immediately before dispatch preparation.

FACT — the connected GitHub toolset exposes workflow reads and reruns but no workflow-dispatch mutation. Under the trusted-base `GITHUB_ONLY_EXECUTION.md` temporary-workflow rule, a minimal branch-only dispatcher was added at `.github/workflows/otbm-atlas-release-dispatch-once.yml` on the checkpoint branch. It has no deploy path or secrets, grants only `contents: read` and `actions: write`, asserts the exact expected `main` SHA, and requests `workflow_dispatch` of the already-trusted release workflow on `ref: main`.

FACT — dispatcher workflow run `31813766316` was created from branch head `4c248c81ea7a4de39483a5a92e9af10d8044cbcd`. Two bounded observations both reported it `queued`; no full-world release run existed at the first release-workflow observation. No further unchanged polling is permitted in this invocation.

```yaml
checkpoint_version: 2
updated_at: 2026-08-14T17:18:00+02:00
status: waiting
phase: full-world-release-certification
source_task: OTH-20260813-full-otbm-atlas
main_sha: 1021d08978f078ff845e6f3f82fbbbc482cbf543
workflow: .github/workflows/otbm-atlas-full-world-release.yml
merge_blocking_for_pr_381: false
execution_mode: github-actions
execution_reason: trusted workflow_dispatch is required; the GitHub connector exposes workflow reads/reruns but no workflow-dispatch mutation, so a minimal temporary branch-only dispatcher is used under GITHUB_ONLY_EXECUTION.md
validation_level: full
heavy_validation_runs: 1
dispatcher_workflow: .github/workflows/otbm-atlas-release-dispatch-once.yml
dispatcher_run_id: 31813766316
dispatcher_head: 4c248c81ea7a4de39483a5a92e9af10d8044cbcd
verified:
  - per-floor release workflow exists on main
  - main remained 1021d08978f078ff845e6f3f82fbbbc482cbf543 before dispatcher creation
  - historical Z8-Z15 per-floor recovery evidence passed verifier with canonical map fingerprint
  - current per-floor workflow reparses the full OTBM independently in every job
  - temporary dispatcher run 31813766316 exists and is queued
inference:
  - duplicated spooling is optimizable but historical timings indicate rendering/enrichment remains the larger cost
unknown:
  - whether dispatcher run 31813766316 succeeds
  - full-world release run id
  - final exact-main Z0-Z15 release evidence
  - final exact-main aggregate 3494-chunk certification
next_action: after dispatcher run 31813766316 reaches a terminal state, verify its result; on success capture the generated full-world release run for main SHA 1021d08978f078ff845e6f3f82fbbbc482cbf543 and remove the temporary dispatcher workflow
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 1
  session_id: chatgpt-20260814T1714+0200
  session_started_at: 2026-08-14T17:14:00+02:00
  checkpointed_at: 2026-08-14T17:18:00+02:00
  last_progress_at: 2026-08-14T17:18:00+02:00
  phase: full-world-release-certification
  exact_head: 1021d08978f078ff845e6f3f82fbbbc482cbf543
  pull_request: none
  active_operation: GitHub Actions dispatcher run 31813766316 queued
  external_run_ids: [31813766316]
  operation_started_at: 2026-08-14T17:17:45+02:00
  wait_deadline_at: null
  check_generation: dispatcher-4c248c81
  checks_used: 2
  status: waiting
  safe_to_resume: true
  resume_condition: dispatcher run 31813766316 is no longer queued
  next_action: inspect dispatcher run 31813766316 after it leaves queued; if successful, capture the generated full-world release run for main SHA 1021d08978f078ff845e6f3f82fbbbc482cbf543 and remove `.github/workflows/otbm-atlas-release-dispatch-once.yml`
```
