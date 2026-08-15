---
task_id: OTH-20260815-otbm-atlas-creature-animation
status: in_progress
owner: openai
branch: feat/otbm-atlas-creature-animation
base_branch: main
created: 2026-08-15T10:47:00+02:00
updated: 2026-08-15T10:47:00+02:00
project_lane: otheryn-content
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-creature-animation-tests.yml
  - docs/maps/otbm-atlas-completion-audit-20260814.md
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-creature-animation.md
required_reads:
  - AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
---

# Canonical OTBM Atlas creature animation

## Goal

Close the remaining verified runtime gap in the OTBM Atlas by extending the existing canonical NPC/monster sprite pipeline with bounded, time-based creature animation derived only from the pinned Tibia appearance data already vendored under `vendor/map-analysis/**`.

This task does not simulate world movement or invent server state. Static spawn positions remain factual. Creature animation is a presentation of canonical appearance frame groups and directions at those factual positions.

## Delivery classification

```yaml
feature_scope:
  type: full_stack
  user_facing: true
  backend_required: false
  frontend_required: true
  integration_required: true
  e2e_required: true
```

## Acceptance criteria

- Preserve creature frame-group semantics from pinned appearance protobuf metadata instead of flattening all groups into one static frame.
- Export canonical renderable phases for NPCs and monsters, retaining outfit recolouring and addons for every rendered phase.
- Support the canonical cardinal direction patterns without inventing diagonal source frames.
- Use canonical animation timing metadata (`default_start_phase`, phase durations, synchronization, loop semantics) with deterministic conservative fallback where metadata is unsafe or incomplete.
- Keep spawn position/provenance unchanged and do not simulate creature pathing.
- Keep browser work viewport/zoom bounded; no world-wide animation payload at startup.
- Reuse bounded image/runtime timing concepts instead of generating GIF/WebP/video assets for production.
- Preserve the current static sprite/dot fallback for unresolved or unsupported records.
- Unit tests must cover frame-group decoding, direction selection, phase rendering, recolouring/addons, timing and fallbacks.
- Real pinned-data integration must cover at least one NPC and one monster with more than one canonical animation phase.
- Real Chromium E2E must prove that the same NPC and same monster change canonical rendered phase over time in the production viewer.
- The E2E workflow must upload human-viewable production evidence plus machine-readable source/timing evidence.
- Existing OTBM Atlas, factual-layer, environment-animation and creature static-sprite behavior must remain green.
- Final exact-head CI and independent post-implementation audit must pass before completion.

## Forbidden shortcuts

- no AI/generated/mock creature frames;
- no network or `data-otservbr-global` fallback for canonical creature visuals;
- no fabricated direction or movement route;
- no whole-world creature animation preload;
- no per-spawn prebuilt GIF/animated WebP production model;
- no promotion of unresolved appearance data to certain truth.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T10:47:00+02:00
base_main: 75e121478beadbe12d4c77343f693f74887f489d
branch: feat/otbm-atlas-creature-animation
status: in_progress
proven:
  - completion audit classifies original full OTBM atlas core as DONE
  - canonical static NPC and monster sprite parity is merged and archived
  - current CreatureSpriteRenderer is intentionally static and selects one frame group, one direction pattern and one default phase
  - assets.py already decodes animation phase durations, synchronization, start and loop metadata but does not retain frame-group type
  - existing environment runtime already provides bounded animation timing/cache concepts suitable for reuse
  - current main has no competing creature-animation PR
constraints:
  - canonical vendored sources only
  - do not simulate server/world movement
  - do not consume owner-funded AI/Codex quota
blockers: []
next_action: extend appearance decoding with frame-group identity and implement canonical multi-phase creature animation export/runtime with focused tests
```
