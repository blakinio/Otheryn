---
task_id: OTH-20260815-atlas-environment-animation-export-performance
status: validating
owner: atlas-environment-resume
branch: blakinio/atlas-environment-animation-resume
base_branch: main
created: 2026-08-15
updated: 2026-08-16
project_lane: otheryn-content
related_pr: "418"
owned_paths:
  - tools/otbm_atlas/atlas.py
  - tools/otbm_atlas/environment_animation_resume.py
  - tools/otbm_atlas/tests/test_environment_animation_resume.py
  - docs/maps/otbm-atlas-environment-resume-evidence-20260816.md
  - docs/agents/tasks/active/OTH-20260815-atlas-environment-animation-export-performance.md
required_reads:
  - AGENTS.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/SESSION_RECOVERY_AND_ORPHANED_EXECUTION.md
  - docs/maps/atlas-environment-animation.md
---

# Make full-world environment-animation export bounded and resumable

## Goal

Prevent canonical Atlas builds from losing hours of completed environment-animation work after interruption while preserving the schema-2 browser/runtime and exact pixel-composition rules.

## Prior reproduction evidence

- Historical failing source: `a4878325b892b2044f514d27a1a3104e5ce843f7`.
- Two bounded Windows attempts remained in legacy `enrich_environment_animations` after about 82 and 120 minutes.
- All 3,494 detail chunks and both overview levels completed before that phase.
- The legacy exporter was making progress, not deadlocked, but created hundreds of thousands of small files and deleted/rebuilt its output tree on restart.

## Implementation in PR #418

The Atlas build now routes environment animation through `environment_animation_resume.py`:

- one deterministic checkpoint per manifest chunk;
- chunk fingerprint = exporter/source contract + exact spool bytes;
- checkpoint reuse only when the fingerprint, shard and every referenced asset remain valid;
- atomic frame/shard/checkpoint/index/state writes;
- content-addressed underlay/overdraw assets to deduplicate identical occurrence composites;
- existing stable frame paths/animation keys and schema-2 browser records preserved;
- deterministic `completed/total` progress emitted without external directory counting;
- final `completedChunks`, `reusedChunks`, `outputFiles` and `outputBytes` statistics;
- global invalidation when source/export contract changes, per-chunk invalidation when only one spool changes.

`--workers` remains a detail-rendering control. This implementation deliberately does not invent unsafe environment-export parallelism; resumability/deduplication addresses the measured failure mode first.

## Acceptance inventory

1. deterministic progress totals/current position — IMPLEMENTED, awaiting exact-head CI and canonical run;
2. durable restart checkpoint — focused tests PASS after repair, awaiting final exact-head generation;
3. unchanged verified payloads reused — focused test compares reusable frames/underlays/overdraws/shards/checkpoints while allowing progress metadata to record `reusedChunks`;
4. file/byte totals and occurrence deduplication — IMPLEMENTED;
5. workers behavior explicit/no unsafe parallelism — IMPLEMENTED;
6. clean/interrupted/resume/stale/equivalence tests — IMPLEMENTED;
7. real canonical full-world run — PENDING on the persisted Synology 3,494-chunk spool;
8. browser/runtime behavior and pixel correctness — PENDING exact-head environment E2E plus deployed Chromium.

## Validation history

- Initial PR generation failed because the new module imported `AssetRenderer` from the wrong module. Fixed to import it from `tools.otbm_atlas.render`.
- A subsequent full focused suite found one test-contract mistake: it compared `index.json`/`export-state.json`, whose progress metadata correctly changes `reusedChunks` on restart. The implementation already preserved reusable payloads. The test was corrected at head `def0a76ef45615bd5353ff437b28252df37448fc` to compare reusable payload files separately and assert updated progress metadata.
- Before that correction, all other environment resume tests passed, as did canonical item/creature integration, factual layers, CI and Required gates on the prior generation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-16T09:45:00+02:00
head: def0a76ef45615bd5353ff437b28252df37448fc
branch: blakinio/atlas-environment-animation-resume
pr: 418
status: validating
phase: exact-head-ci
execution_mode: chat-github
project_lane: otheryn-content
proven:
  - legacy exporter failure mode was non-resumable small-file-heavy progress, not deadlock
  - resumable exporter implementation is present on PR 418
  - wrong AssetRenderer import was found from real CI and repaired
  - focused clean/interrupted/stale/deterministic tests run through the real Atlas test suite; only progress-metadata comparison required correction on the previous generation
  - CI and Required passed on the previous repaired-import generation
unknown:
  - exact-head def0a76 final CI/E2E result
  - canonical full-world resumable-export runtime and final file/byte cardinality
  - deployed browser environment-animation result after final release
conflicts: []
first_failure:
  marker: test compared mutable progress metadata while asserting payload immutability
  evidence: prior Atlas suite showed reusable payload generation/reuse PASS but index reusedChunks changed 0 -> 1
rejected_hypotheses:
  - payload assets were rewritten on identical restart
  - exporter deadlocks
  - detail rendering is the environment phase bottleneck
changed_paths:
  - tools/otbm_atlas/atlas.py
  - tools/otbm_atlas/environment_animation_resume.py
  - tools/otbm_atlas/tests/test_environment_animation_resume.py
  - docs/maps/otbm-atlas-environment-resume-evidence-20260816.md
  - docs/agents/tasks/active/OTH-20260815-atlas-environment-animation-export-performance.md
blockers: []
next_action: verify exact-head PR 418 CI and environment E2E; remediate any material failure, merge, then execute the full resumable exporter against the persistent Synology 3,494-chunk Atlas spool
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 2
  session_id: atlas-env-resume-20260816
  checkpointed_at: 2026-08-16T09:45:00+02:00
  phase: exact-head-ci
  exact_head: def0a76ef45615bd5353ff437b28252df37448fc
  pull_request: 418
  active_operation: exact-head CI and E2E
  external_run_ids: [31934745639, 31934745394, 31934745395, 31934745418]
  status: active
  safe_to_resume: true
  resume_condition: exact-head checks become terminal
  next_action: inspect aggregate exact-head checks; if green, perform fresh PR audit/review hygiene and merge before the full Synology export
```
