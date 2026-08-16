---
task_id: OTH-20260816-required-concurrency
status: completed
owner: none
created: "2026-08-16T09:50:00+02:00"
completed: "2026-08-16T11:10:00+02:00"
updated: "2026-08-16T11:12:00+02:00"
project_lane: infrastructure
related_pr: "420"
ownership_released: true
modules_touched:
  - required-ci
---

# Required workflow stale-run cancellation — completed

PR #420 merged as `13ad8f6d5e889b62d63f39b2e34fe07ef241e37e` and adds same-PR stale-run cancellation to the repository `Required` workflow without changing its exact-head gate semantics.

## Delivered

- `Required` uses a per-PR/ref concurrency group;
- `cancel-in-progress: true` removes obsolete pollers after a newer head supersedes them;
- changed-path classification, applicable workflow names, exact-head matching, 35-minute deadline, 10-second polling interval, and pass/fail semantics remain unchanged.

## Verified acceptance

Implementation head `a0132142a2e10f2ba9302739e603383c37a88ddc` emitted Required run `31934841782`; the newer head `12b3a229af143b45206ebd659a847d812e299a17` emitted Required run `31934859066`, and the older run became `completed/cancelled`.

The final ready-for-review validation on head `12b3a229af143b45206ebd659a847d812e299a17` passed `CI` run `31938183396` and `Required` run `31938183391`. No OTBM Atlas/creature/environment specialized workflow was emitted solely by this task. Review closeout had zero submitted reviews and zero unresolved review threads before merge.

## Closeout

Documentation-only closeout PR #423 initially ran on head `55f07b2be64682abfcc2969a209d6e12a572da91`. GitHub emitted only `Required` run `31938361840`, which completed `success`; no OTBM Atlas/creature/environment specialized workflow was emitted. This validates both the task-only routing fix and the final archival path.

```yaml
closeout:
  implementation_pr: 420
  implementation_merge: 13ad8f6d5e889b62d63f39b2e34fe07ef241e37e
  stale_required_cancellation: PASS
  exact_head_ci: PASS
  exact_head_required: PASS
  specialized_otbm_fanout: NONE
  closeout_pr: 423
  closeout_proof_head: 55f07b2be64682abfcc2969a209d6e12a572da91
  closeout_required_run: 31938361840
  docs_only_trigger_proof: PASS
  heavy_otbm_workflows_emitted: 0
  task_status: completed
  task_archived: true
  ownership_released: true
```
