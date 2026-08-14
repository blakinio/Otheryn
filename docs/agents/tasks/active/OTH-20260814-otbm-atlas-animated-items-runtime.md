---
task_id: OTH-20260814-otbm-atlas-animated-items-runtime
status: in_progress
owner: agent
created: 2026-08-14
updated: 2026-08-14T18:55:00+02:00
project_lane: otheryn-content
related_pr: null
ownership_released: false
modules_touched:
  - otbm-atlas
---

# OTBM atlas animated item runtime

Extend the existing `tools/otbm_atlas/environment_animation.py` runtime animation pipeline instead of introducing GIF assets or a parallel renderer.

## Scope

- retain canonical static chunk pixels as the fallback;
- animate cyclic object appearances directly from pinned Tibia appearance/sprite phases;
- support 32x64, 64x32 and 64x64 sprite layouts in addition to 32x32;
- support appearance shift/height geometry;
- support safe non-topmost stack entries and animated ground entries with canonical underlay/overdraw composition;
- deduplicate phase sprites by appearance/pattern while keeping per-instance composition bounded;
- refuse ambiguous overlap/edge/coverage cases instead of inventing pixels;
- preserve bounded browser caches and close-zoom activation;
- validate with unit tests, pinned-asset integration and real Chromium E2E.

## Non-goals

- no GIF/WebP animation generation;
- no inference of server-driven/stateful appearance changes;
- no modification of canonical OTBM geometry or source assets;
- no owner-funded AI/Codex/API use.

## Context checkpoint

```yaml
checkpoint_version: 1
status: in_progress
phase: implementation
base_main: 1021d08978f078ff845e6f3f82fbbbc482cbf543
branch: agent/oth-20260814-animated-items-runtime
current_contract: cyclic pinned-appearance animation with conservative static fallback
next_action: generalize exporter geometry/composition, update browser runtime, then validate focused and Chromium gates
```
