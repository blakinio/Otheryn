---
task_id: OTH-20260814-otbm-atlas-full-world-release-validation
status: validating
owner: chatgpt
created: 2026-08-14
updated: 2026-08-14T19:08:00+02:00
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

## Live execution evidence

FACT — canonical validation target is exact `main` SHA `1021d08978f078ff845e6f3f82fbbbc482cbf543`, containing the completed PR #381 atlas implementation and the production environment-animation integration.

FACT — because the connected GitHub toolset has no direct workflow-dispatch mutation, a minimal branch-only one-shot dispatcher was used to dispatch the already-trusted release workflow on exact `main`. Dispatcher run `31813766316` completed `success` and created canonical full-world release run `31813869825` on exact SHA `1021d08978f078ff845e6f3f82fbbbc482cbf543`.

FACT — temporary dispatcher `.github/workflows/otbm-atlas-release-dispatch-once.yml` was removed immediately after successful dispatch; removal commit `268c010820249b391659af891f36518efb43dc7b`. It is not part of the branch diff anymore.

FACT — as of `2026-08-14T19:08:00+02:00`, fifteen floors have completed the complete per-floor chain with `success`: Z0, Z1, Z2, Z3, Z4, Z5, Z6, Z8, Z9, Z10, Z11, Z12, Z13, Z14 and Z15. Each completed canonical build, independent verifier, floor evidence assertion and artifact upload. Z7 is the only remaining in-progress floor. No floor has failed.

FACT — independent supporting inspection of the fifteen downloaded floor evidence artifacts reports 3148 chunks, one identical source fingerprint, `atlasVersion == 3`, `chunkSize == 128`, canonical map SHA `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`, `verification.ok == true` for every completed floor, and `missingSprites == {}` for every completed floor. The final 3494-chunk claim is deliberately not made until Z7 and the repository aggregate job pass.

FACT — the release run remains non-terminal only because Z7 is still building. The aggregate job cannot start until all sixteen floor jobs are terminal.

FACT — the release workflow still reparses the full OTBM independently in every floor job. That measured-performance optimization remains out of scope for this certification task.

```yaml
checkpoint_version: 6
updated_at: 2026-08-14T19:08:00+02:00
status: validating
phase: full-world-release-certification
source_task: OTH-20260813-full-otbm-atlas
validation_target_sha: 1021d08978f078ff845e6f3f82fbbbc482cbf543
workflow: .github/workflows/otbm-atlas-full-world-release.yml
release_run_id: 31813869825
dispatcher_run_id: 31813766316
dispatcher_result: success
temporary_dispatcher_removed: true
execution_mode: github-actions
validation_level: full
heavy_validation_runs: 1
verified_floors: [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15]
pending_floors: [7]
failed_floors: []
partial_evidence:
  artifacts: 15
  chunks: 3148
  source_fingerprints: 1
  map_sha256: 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  atlas_version: 3
  chunk_size: 128
  all_verification_ok: true
  all_missing_sprites_empty: true
unknown:
  - terminal Z7 result
  - final aggregate 3494-chunk certification
next_action: continue bounded terminal observation of release run 31813869825; when Z7 becomes terminal, either verify the aggregate success and close the task or inspect the first actionable Z7 failure and perform only an evidence-backed owned repair
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 3
  session_id: chatgpt-20260814T1849+0200
  session_started_at: 2026-08-14T18:49:00+02:00
  checkpointed_at: 2026-08-14T19:08:00+02:00
  last_progress_at: 2026-08-14T19:01:40+02:00
  phase: full-world-release-certification
  exact_head: 1021d08978f078ff845e6f3f82fbbbc482cbf543
  pull_request: none
  active_operation: GitHub Actions full-world release validation run 31813869825; only Z7 remains in progress
  external_run_ids: [31813766316, 31813869825]
  operation_started_at: 2026-08-14T17:19:01+02:00
  wait_deadline_at: 2026-08-14T19:34:00+02:00
  check_generation: full-world-release-main-1021d089-continuation-3
  checks_used: 7
  status: active
  safe_to_resume: true
  resume_condition: Z7 or release run 31813869825 materially changes or reaches a terminal state
  next_action: after at least three minutes, inspect release run 31813869825; on terminal success verify all sixteen floor artifacts and aggregate contract, then perform task archival and PR closeout
```
