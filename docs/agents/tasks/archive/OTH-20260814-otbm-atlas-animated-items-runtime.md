---
task_id: OTH-20260814-otbm-atlas-animated-items-runtime
status: completed
branch: agent/oth-20260814-animated-items-runtime
base_branch: main
created: 2026-08-14
updated: 2026-08-14T17:35:00Z
related_pr: "387"
owned_paths:
  - tools/otbm_atlas/environment_animation.py
  - tools/otbm_atlas/viewer_runtime.js
  - tools/otbm_atlas/tests/test_environment_animation.py
  - tools/otbm_atlas/tests/test_viewer_runtime.py
  - .github/workflows/otbm-environment-animation-tests.yml
  - tools/otbm_atlas/ANIMATION.md
  - tools/otbm_atlas/README.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - tools/otbm_atlas/README.md
  - tools/otbm_atlas/ANIMATION.md
search_first: []
optional_reads: []
---

# OTBM atlas animated item runtime

## Outcome

Extended the existing OTBM Atlas environment-animation pipeline instead of introducing GIF/WebP assets or a parallel renderer. Cyclic object phases now support pinned 32x32, 32x64, 64x32 and 64x64 sprite geometry, canonical `shift`/`height`, safe animated ground and non-topmost stack entries, and per-instance `underlay -> phase -> overdraw` composition. Shared phase images remain deduplicated by canonical appearance/pattern and are selected by the browser at runtime.

Correctness remains conservative: undecodable geometry, overlapping animated rectangles, chunk-edge risk, non-opaque replacement patches and server-driven/stateful variants retain deterministic canonical static pixels. Browser animation remains close-zoom-only with bounded image and shard caches.

The automated review's dense-chunk P1 was fixed by replacing all-pairs overlap detection with a 32-pixel spatial hash. A regression test covers a dense 128x128 grid (16,384 candidate rectangles) and proves that aligned non-overlapping tiles require zero `_intersects` calls while genuine overlaps are still detected.

The durable no-GIF extension contract is documented in `tools/otbm_atlas/ANIMATION.md`; the main `tools/otbm_atlas/README.md` now describes the generalized runtime rather than the obsolete topmost-32x32-only policy.

Full 3494-chunk world release certification is governed by the separate `OTH-20260814-otbm-atlas-full-world-release-validation` task/history and is not weakened or redefined here.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-14T17:35:00Z
head: e852748a0a4be8e6df9048f125c7c890bdc457fe
branch: agent/oth-20260814-animated-items-runtime
pr: 387
status: completed
context_routes:
  - tools/otbm_atlas/ANIMATION.md
  - tools/otbm_atlas/README.md
  - tools/otbm_atlas/environment_animation.py
  - .github/workflows/otbm-environment-animation-tests.yml
owned_paths:
  - tools/otbm_atlas/environment_animation.py
  - tools/otbm_atlas/viewer_runtime.js
  - tools/otbm_atlas/tests/test_environment_animation.py
  - tools/otbm_atlas/tests/test_viewer_runtime.py
  - .github/workflows/otbm-environment-animation-tests.yml
  - tools/otbm_atlas/ANIMATION.md
  - tools/otbm_atlas/README.md
  - docs/agents/tasks/archive/OTH-20260814-otbm-atlas-animated-items-runtime.md
proven:
  - Runtime item animation uses pinned appearance phases with schema-v2 geometry, stack metadata and canonical static fallback rather than per-item GIF/WebP assets.
  - Dense 128x128 aligned animation rectangles are indexed by 32-pixel spatial buckets and the regression test observes zero _intersects calls for 16384 non-overlapping candidates.
  - Pinned-asset Chromium E2E selected serverId 114 with spriteSize 32x64 and drawOffsetPixels -8,-40 and observed six distinct runtime frames.
  - Canonical production export selected serverId 4643 at 32590,31926,0 and exported 190 instances across 49 unique animations with zero static fallbacks in the fixture chunk.
  - ef099cfccdb107e1e264c8cfab6b049aef60adbd passed atlas unit/runtime, canonical Thais scan/render, real browser Thais, canonical animation export and extended Chromium E2E.
  - e852748a0a4be8e6df9048f125c7c890bdc457fe differs from ef099cfccdb107e1e264c8cfab6b049aef60adbd only by the generalized animation README update.
derived:
  - Shared phase images plus runtime phase selection make prebuilt per-instance animated image files unnecessary for cyclic map-item appearances.
unknown: []
conflicts: []
first_failure:
  marker: automated-review-p1-dense-overlap-scan
  evidence: Review found an all-pairs candidate scan capable of roughly 134 million checks in a dense 128x128 chunk; commit 80868fc6f149fb80f8b01ea0b2be9bfd2ef320a0 replaced it with spatial buckets and ef099cfccdb107e1e264c8cfab6b049aef60adbd added the dense-grid regression.
rejected_hypotheses:
  - Prebuilding one GIF or animated WebP per torch, lamp, water tile or other cyclic object is required for browser animation.
  - Unsafe or server-driven appearance changes should be guessed when cyclic pinned metadata is insufficient.
changed_paths:
  - tools/otbm_atlas/environment_animation.py
  - tools/otbm_atlas/viewer_runtime.js
  - tools/otbm_atlas/tests/test_environment_animation.py
  - tools/otbm_atlas/tests/test_viewer_runtime.py
  - .github/workflows/otbm-environment-animation-tests.yml
  - tools/otbm_atlas/ANIMATION.md
  - tools/otbm_atlas/README.md
  - docs/agents/tasks/archive/OTH-20260814-otbm-atlas-animated-items-runtime.md
validation:
  - command: GitHub Actions OTBM Atlas Tests run 31823415498
    result: PASS
    evidence: Atlas unit/runtime, canonical Thais scan/render and real browser Thais E2E all succeeded on implementation head ef099cfccdb107e1e264c8cfab6b049aef60adbd.
  - command: GitHub Actions OTBM Environment Animation E2E run 31823415553
    result: PASS
    evidence: Canonical production export and extended pinned-asset Chromium animation both succeeded on implementation head ef099cfccdb107e1e264c8cfab6b049aef60adbd.
  - command: GitHub Actions CI run 31823666240
    result: PASS
    evidence: General repository CI succeeded on e852748a0a4be8e6df9048f125c7c890bdc457fe.
  - command: GitHub Actions Required run 31823665896
    result: PASS
    evidence: Required gate succeeded on e852748a0a4be8e6df9048f125c7c890bdc457fe.
  - command: GitHub Actions autofix.ci run 31823666038
    result: PASS
    evidence: Autofix gate succeeded without changes on e852748a0a4be8e6df9048f125c7c890bdc457fe.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/archive/OTH-20260814-otbm-atlas-animated-items-runtime.md --require-checkpoint
    result: PASS
    evidence: Exact proposed archive task was validated locally against repository checkpoint.py and GOVERNANCE_CONTRACT.json before upload.
blockers: []
next_action: Reopen this archived task only if a regression is reproduced against the runtime item animation contract.
```
