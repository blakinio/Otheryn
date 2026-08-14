---
task_id: OTH-20260814-otbm-atlas-full-world-release-validation
status: validating
owner: chatgpt
created: 2026-08-14
updated: 2026-08-14T17:14:00+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: false
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

FACT — `.github/workflows/otbm-atlas-full-world-release.yml` has not yet produced a workflow run on `main`; repository Actions currently report zero runs for that workflow. Therefore complete-world release certification is still unproven on the exact merged `main` head.

FACT — historical recovery runs on the PR #381 branch proved upper floors individually against the same canonical map fingerprint. Z8 and Z9 both completed successfully on head `417eaac6bf6e75475e4d3363f6e19c363f5eb2bf`; Z10..Z15 completed successfully on head `c09a4eccf78a4b15d4f529de5d842ee1b62c8ce2`. Example Z8 evidence reported 285 chunks, `verification.ok == true`, and `missingSprites == {}`. These runs are useful engineering evidence but are not a substitute for the exact-main release certification.

FACT — the current release workflow still calls `spool_map()` independently in every floor job, then deletes spool files from the other 15 floors before calling `build_atlas()`. This means every one of the 16 jobs performs a complete canonical OTBM parse before floor-specific rendering.

FACT — `build_atlas()` itself is resumable by spool/source fingerprint and chunk-render fingerprint, but the release workflow deliberately creates a fresh job-local output directory, so no spool or rendered chunk cache is shared between floor jobs.

INFERENCE — the duplicated full-map spooling is avoidable compute, but it was not the dominant cause of the longest historical jobs. Successful upper-floor build steps ranged roughly from 31 minutes on Z15 to 66 minutes on Z9; most elapsed time remains in floor rendering and post-render atlas enrichment rather than in the initial OTBM parse alone.

RECOMMENDATION — do not redesign the release gate around four-floor shards again. Keep one-floor failure isolation, and only optimize the implementation by adding an explicit floor-filtered spooling/build path (or a reusable pre-spool artifact) if profiling proves the duplicated parse materially affects cost. Any such change must preserve exact per-floor verification and the final 16-floor / 3494-chunk aggregate contract.

UNKNOWN — exact Z0..Z7 per-floor runtimes on the final per-floor workflow and complete exact-main 16-floor evidence remain unavailable until `.github/workflows/otbm-atlas-full-world-release.yml` is run.

```yaml
checkpoint_version: 2
updated_at: 2026-08-14T17:14:00+02:00
status: validating
phase: full-world-release-certification
source_task: OTH-20260813-full-otbm-atlas
main_sha: 1021d08978f078ff845e6f3f82fbbbc482cbf543
workflow: .github/workflows/otbm-atlas-full-world-release.yml
merge_blocking_for_pr_381: false
execution_mode: github-actions
execution_reason: trusted workflow_dispatch is required; the GitHub connector exposes workflow reads/reruns but no workflow-dispatch mutation, so a minimal temporary branch-only dispatcher is used under GITHUB_ONLY_EXECUTION.md
validation_level: full
heavy_validation_runs: 1
verified:
  - per-floor release workflow exists on main
  - no exact-main release workflow run exists yet
  - historical Z8-Z15 per-floor recovery evidence passed verifier with canonical map fingerprint
  - current per-floor workflow reparses the full OTBM independently in every job
inference:
  - duplicated spooling is optimizable but historical timings indicate rendering/enrichment remains the larger cost
unknown:
  - final exact-main Z0-Z15 release evidence
  - final exact-main aggregate 3494-chunk certification
next_action: dispatch the trusted full-world release workflow on exact main SHA 1021d08978f078ff845e6f3f82fbbbc482cbf543 via a minimal temporary branch-only GitHub Actions dispatcher
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 1
  session_id: chatgpt-20260814T1714+0200
  session_started_at: 2026-08-14T17:14:00+02:00
  checkpointed_at: 2026-08-14T17:14:00+02:00
  last_progress_at: 2026-08-14T17:14:00+02:00
  phase: full-world-release-certification
  exact_head: 1021d08978f078ff845e6f3f82fbbbc482cbf543
  pull_request: none
  active_operation: prepare one-shot branch-only dispatcher for trusted full-world workflow_dispatch on main
  external_run_ids: []
  operation_started_at: null
  wait_deadline_at: null
  check_generation: full-world-release-main-1021d089
  checks_used: 0
  status: active
  safe_to_resume: true
  resume_condition: one-shot dispatcher has been pushed or can be pushed without changing main
  next_action: create the temporary branch-only dispatcher workflow and confirm that it creates a release run on main SHA 1021d08978f078ff845e6f3f82fbbbc482cbf543
```
