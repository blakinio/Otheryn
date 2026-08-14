---
task_id: OTH-20260814-otbm-atlas-full-world-release-validation
status: validating
owner: chatgpt
created: 2026-08-14
updated: 2026-08-14T19:11:32+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: false
modules_touched:
  - otbm-atlas
---

# OTBM atlas full-world release validation

This task owns the expensive complete-world certification intentionally deferred from `OTH-20260813-full-otbm-atlas` by explicit owner decision.

## Required evidence

The release certification must:

- run one independent job per canonical floor Z0..15;
- build from `vendor/map-analysis/crystalserver/data-global/world/world.otbm` and the pinned Tibia 15.25 vendored assets;
- independently verify every floor;
- require `verification.ok == true` and `missingSprites == {}` for every floor;
- aggregate exactly 16 floor evidence artifacts;
- require exactly 3494 chunks across Z0..15;
- require identical canonical source fingerprints across all floors;
- require map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`;
- keep this certification separate from routine atlas implementation CI.

## Execution evidence

FACT — validation target is exact SHA `1021d08978f078ff845e6f3f82fbbbc482cbf543`. Canonical release run is GitHub Actions `31813869825`.

FACT — dispatcher run `31813766316` completed `success`. Its temporary branch-only workflow was removed immediately afterwards in commit `268c010820249b391659af891f36518efb43dc7b`; it is not part of the final branch diff.

FACT — all sixteen floor jobs Z0..Z15 have now completed `success`. Every job completed canonical build, independent verifier, floor evidence assertion and evidence artifact upload.

FACT — all sixteen floor evidence artifacts were downloaded and independently rechecked outside the workflow aggregate job. The independent check proves:

- floor set exactly `0..15`;
- per-floor chunk counts: Z0=87, Z1=120, Z2=150, Z3=183, Z4=213, Z5=240, Z6=251, Z7=346, Z8=285, Z9=286, Z10=265, Z11=238, Z12=234, Z13=201, Z14=210, Z15=185;
- total chunks exactly `3494`;
- exactly one identical source fingerprint across all sixteen reports;
- map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`;
- assets SHA-256 `4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7`;
- `chunkSize == 128` and `atlasVersion == 3`;
- `verification.ok == true` for all sixteen floors;
- `missingSprites == {}` for all sixteen floors.

FACT — repository aggregate job `94839712570` has been created and is queued. The overall workflow remains non-terminal until this separate aggregate runner validates the same complete evidence set.

FACT — the release workflow still reparses the full OTBM independently in every floor job. That is a later measured performance optimization and is not part of this completed certification evidence.

```yaml
checkpoint_version: 7
updated_at: 2026-08-14T19:11:32+02:00
status: validating
phase: aggregate-certification
source_task: OTH-20260813-full-otbm-atlas
validation_target_sha: 1021d08978f078ff845e6f3f82fbbbc482cbf543
workflow: .github/workflows/otbm-atlas-full-world-release.yml
release_run_id: 31813869825
aggregate_job_id: 94839712570
dispatcher_run_id: 31813766316
dispatcher_result: success
temporary_dispatcher_removed: true
execution_mode: github-actions
validation_level: full
heavy_validation_runs: 1
verified_floors: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
failed_floors: []
independent_artifact_audit:
  result: PASS
  artifacts: 16
  chunks: 3494
  source_fingerprints: 1
  map_sha256: 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  assets_sha256: 4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7
  atlas_version: 3
  chunk_size: 128
  all_verification_ok: true
  all_missing_sprites_empty: true
unknown:
  - terminal repository aggregate job result
  - terminal overall workflow result
next_action: wait for aggregate job 94839712570; if it passes and run 31813869825 concludes success, archive this task and complete the documentation-only PR closeout
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 3
  session_id: chatgpt-20260814T1849+0200
  session_started_at: 2026-08-14T18:49:00+02:00
  checkpointed_at: 2026-08-14T19:11:32+02:00
  last_progress_at: 2026-08-14T19:11:32+02:00
  phase: aggregate-certification
  exact_head: 1021d08978f078ff845e6f3f82fbbbc482cbf543
  pull_request: none
  active_operation: GitHub Actions aggregate job 94839712570 for release run 31813869825
  external_run_ids: [31813766316, 31813869825]
  operation_started_at: 2026-08-14T17:19:01+02:00
  wait_deadline_at: 2026-08-14T19:34:00+02:00
  check_generation: full-world-release-aggregate-94839712570
  checks_used: 8
  status: active
  safe_to_resume: true
  resume_condition: aggregate job 94839712570 reaches a terminal state
  next_action: after at least three minutes, inspect aggregate job 94839712570 and overall run 31813869825; on success archive the task and complete PR/CI/merge closeout
```
