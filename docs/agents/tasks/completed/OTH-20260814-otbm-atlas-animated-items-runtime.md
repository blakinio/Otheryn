---
task_id: OTH-20260814-otbm-atlas-animated-items-runtime
status: completed
owner: agent
created: 2026-08-14
updated: 2026-08-14T19:10:00+02:00
project_lane: otheryn-content
related_pr: 387
ownership_released: true
modules_touched:
  - otbm-atlas
---

# OTBM atlas animated item runtime

Extended the existing `tools/otbm_atlas/environment_animation.py` runtime animation pipeline rather than introducing GIF assets or a parallel renderer.

## Delivered

- canonical cyclic object phases are decoded from the pinned Tibia appearance/sprite assets;
- 32x32, 32x64, 64x32 and 64x64 sprite layouts are supported;
- canonical appearance `shift` and `height` displacement is preserved;
- safe animated ground and non-topmost stack entries use per-instance underlay/overdraw composition;
- phase images are deduplicated by canonical appearance/pattern while instance composition stays bounded;
- overlapping animated rectangles, chunk-edge risks, undecodable geometry and non-opaque replacement cases fall back to canonical static pixels;
- browser runtime consumes schema-v2 geometry/stack metadata while retaining schema-v1 32x32 defaults;
- the no-GIF extension contract is documented in `tools/otbm_atlas/ANIMATION.md`.

## Validation evidence

Validated on PR #387 head `da4aeed3058939e0ce5707fe24cab97603c0fd8e` merged virtually with current base `80e07b9afece08506c1fe401f20df073c93833f1` as GitHub PR merge ref `af4756df4212eb16090cdaf916950a732222b7b9`.

- `CI` run 31822053454: SUCCESS.
- `Required` run 31822053129: SUCCESS.
- `autofix.ci` run 31822053074: SUCCESS.
- `OTBM Atlas Tests` run 31822053037:
  - Atlas unit and runtime tests: SUCCESS.
  - Real browser Thais E2E: SUCCESS.
  - Canonical Thais scan and render: SUCCESS.
- `OTBM Environment Animation E2E` run 31822053045:
  - Canonical animation export integration: SUCCESS; canonical chunk exported 190 animated instances / 49 unique animations with zero static fallbacks in the selected fixture chunk.
  - Extended item animation browser E2E: SUCCESS; pinned asset `serverId=114`, sprite `32x64`, draw offset `[-8,-40]`, six distinct Chromium runtime frames observed.
- PR review threads: none at final code validation.

Full-world release certification remains the separate pre-existing task `OTH-20260814-otbm-atlas-full-world-release-validation`; it is not redefined by this bounded animation task.

## Context checkpoint

```yaml
checkpoint_version: 1
status: completed
phase: closeout
base_main: 80e07b9afece08506c1fe401f20df073c93833f1
branch: agent/oth-20260814-animated-items-runtime
related_pr: 387
validated_code_head: da4aeed3058939e0ce5707fe24cab97603c0fd8e
validated_merge_ref: af4756df4212eb16090cdaf916950a732222b7b9
current_contract: runtime cyclic pinned-appearance item animation with canonical static fallback and no GIF assets
next_action: none for this task; merge PR #387 after documentation-only closeout checks
```
