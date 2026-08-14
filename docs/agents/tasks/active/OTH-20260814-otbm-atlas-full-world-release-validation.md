---
task_id: OTH-20260814-otbm-atlas-full-world-release-validation
status: waiting
owner: none
created: 2026-08-14
updated: 2026-08-14T18:04:34+02:00
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

FACT — canonical validation target is exact `main` SHA `1021d08978f078ff845e6f3f82fbbbc482cbf543`, containing the per-floor release workflow and completed PR #381 implementation closeout.

FACT — historical recovery runs on the PR #381 branch proved upper floors individually against the same canonical map fingerprint. Z8 and Z9 completed successfully on head `417eaac6bf6e75475e4d3363f6e19c363f5eb2bf`; Z10..Z15 completed successfully on head `c09a4eccf78a4b15d4f529de5d842ee1b62c8ce2`. These are supporting evidence only, not a substitute for exact-main release certification.

FACT — the release workflow calls `spool_map()` independently in every floor job and deletes spools for other floors before `build_atlas()`. The duplicated full-map parse remains a later measured performance opportunity, not part of this certification task.

## 2026-08-14 execution checkpoint

FACT — the GitHub connector exposes workflow reads/reruns but no direct workflow-dispatch mutation. A minimal branch-only one-shot dispatcher was used under the trusted-base `GITHUB_ONLY_EXECUTION.md` contract to dispatch the already-trusted release workflow on exact `main`.

FACT — dispatcher run `31813766316` completed `success` and produced canonical full-world release run `31813869825` on exact main SHA `1021d08978f078ff845e6f3f82fbbbc482cbf543`.

FACT — the temporary dispatcher workflow `.github/workflows/otbm-atlas-release-dispatch-once.yml` was removed from the checkpoint branch immediately after successful dispatch; removal commit `268c010820249b391659af891f36518efb43dc7b`.

FACT — at the bounded terminal-wait deadline, run `31813869825` had six fully successful floor jobs: Z0, Z1, Z2, Z3, Z4 and Z5. Each completed build, independent verification, evidence assertion and artifact upload. Z6, Z7, Z8, Z9, Z10, Z11, Z12 and Z13 remained in progress; Z14 and Z15 remained queued. No floor job had failed.

FACT — the run is still non-terminal, so the final 16-floor / 3494-chunk aggregate certification is not yet available. Repository anti-stall policy caps the bounded terminal wait at 45 minutes and that deadline (`2026-08-14T18:04:01+02:00`) has elapsed.

```yaml
checkpoint_version: 4
updated_at: 2026-08-14T18:04:34+02:00
status: waiting
phase: full-world-release-certification
source_task: OTH-20260813-full-otbm-atlas
main_sha: 1021d08978f078ff845e6f3f82fbbbc482cbf543
workflow: .github/workflows/otbm-atlas-full-world-release.yml
release_run_id: 31813869825
dispatcher_run_id: 31813766316
dispatcher_result: success
temporary_dispatcher_removed: true
merge_blocking_for_pr_381: false
execution_mode: github-actions
validation_level: full
heavy_validation_runs: 1
verified:
  - trusted release workflow dispatched on exact canonical main SHA
  - dispatcher run 31813766316 completed successfully
  - temporary dispatcher workflow removed from checkpoint branch
  - Z0 Z1 Z2 Z3 Z4 Z5 completed full per-floor validation successfully
  - no floor failure observed through the terminal-wait deadline
unknown:
  - terminal results of Z6 Z7 Z8 Z9 Z10 Z11 Z12 Z13 Z14 Z15
  - final exact-main aggregate 3494-chunk certification
next_action: in a fresh continuation invocation, inspect release run 31813869825; if terminal success, verify all 16 floor evidence artifacts plus the aggregate 3494-chunk contract and complete closeout; if any floor failed, inspect the first actionable failed-job log and perform only an evidence-backed owned repair
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 2
  session_id: chatgpt-20260814T1754+0200
  session_started_at: 2026-08-14T17:54:00+02:00
  checkpointed_at: 2026-08-14T18:04:34+02:00
  last_progress_at: 2026-08-14T17:57:00+02:00
  phase: full-world-release-certification
  exact_head: 1021d08978f078ff845e6f3f82fbbbc482cbf543
  pull_request: none
  active_operation: GitHub Actions full-world release validation run 31813869825
  external_run_ids: [31813766316, 31813869825]
  operation_started_at: 2026-08-14T17:19:01+02:00
  wait_deadline_at: 2026-08-14T18:04:01+02:00
  check_generation: full-world-release-main-1021d089
  checks_used: 4
  status: waiting
  safe_to_resume: true
  resume_condition: release run 31813869825 materially changes or reaches a terminal state
  next_action: inspect aggregate state of release run 31813869825; on terminal success verify all 16 floor evidence artifacts and the aggregate 3494-chunk contract, then finalize task closeout
```
