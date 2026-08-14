---
task_id: OTH-20260814-otbm-atlas-runtime-animations
status: implementing
agent: ChatGPT
project_lane: otheryn-content
task_kind: implementation
phase: implement
branch: agent/otbm-atlas-runtime-animations
base_branch: main
start_sha: 3bc97a36e3d9ec0ffc35eb3fc2e1908920c2c123
created: 2026-08-14T17:08:55+02:00
updated: 2026-08-14T17:08:55+02:00
risk: medium
related_pr: null
execution_mode: chat-github
execution_reason: GitHub-only multi-file atlas change with repository-owned Actions validation; owner-funded AI quota is not authorized
policy_version: 2
decomposition_decision: single
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: medium
invocation_started_at: 2026-08-14T16:49:00+02:00
last_progress_at: 2026-08-14T17:08:55+02:00
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 0
stall_warnings: 0
owned_paths:
  - tools/otbm_atlas/environment_animation.py
  - tools/otbm_atlas/viewer_runtime.js
  - tools/otbm_atlas/tests/test_environment_animation.py
  - tools/otbm_atlas/tests/test_viewer_runtime.py
  - tools/otbm_atlas/README.md
  - docs/agents/tasks/active/OTH-20260814-otbm-atlas-runtime-animations.md
---

# OTBM Atlas runtime object animations

## Objective

Extend the existing no-GIF cyclic object animation pipeline so canonical animated map items can use their pinned Tibia appearance phases at runtime beyond the current topmost 32x32 non-displaced subset, while preserving deterministic static fallback whenever exact compositing cannot be proven.

## Delivery classification

```yaml
feature_scope:
  type: full_stack
  user_facing: true
  backend_required: true
  frontend_required: true
  integration_required: true
  e2e_required: true
```

## Acceptance

- [ ] Runtime animation remains derived from canonical OTBM item identity and pinned Tibia appearance/sprite assets; no GIF generation.
- [ ] Identical animation frames are deduplicated and reused across instances.
- [ ] 32x64, 64x32 and 64x64 sprite layouts can be exported when their local replacement region is composition-safe.
- [ ] Appearance shift/height offsets are represented correctly when their replacement region is composition-safe.
- [ ] Browser drawing uses exported frame dimensions/offsets instead of assuming 32x32.
- [ ] Static canonical fallback remains explicit for unsafe edge, transparency, occlusion or state-driven cases.
- [ ] Existing animation timing semantics remain covered.
- [ ] Focused unit/runtime tests pass.
- [ ] Real canonical browser E2E passes on the exact final head.
- [ ] Independent audit reports no material finding before completion.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-14T17:08:55+02:00
head: UNKNOWN
branch: agent/otbm-atlas-runtime-animations
pr: none
status: implementing
phase: implement
execution_mode: chat-github
context_routes:
  - tools/otbm_atlas/environment_animation.py
  - tools/otbm_atlas/viewer_runtime.js
owned_paths:
  - tools/otbm_atlas/environment_animation.py
  - tools/otbm_atlas/viewer_runtime.js
  - tools/otbm_atlas/tests/test_environment_animation.py
  - tools/otbm_atlas/tests/test_viewer_runtime.py
  - tools/otbm_atlas/README.md
  - docs/agents/tasks/active/OTH-20260814-otbm-atlas-runtime-animations.md
proven:
  - main 3bc97a36e3d9ec0ffc35eb3fc2e1908920c2c123 contains the merged PR #381 bounded no-GIF environment animation pipeline.
  - Current exporter only accepts the top tile item, rejects non-32x32 sprite sheets and rejects nonzero appearance shift/height.
  - Current browser runtime draws every exported environment frame and underlay as a 32x32 tile-sized image.
derived:
  - Larger/displaced phases require exported draw geometry plus a replacement background region; unsupported transparency/occlusion must stay static rather than leak the default phase through the animation canvas.
unknown:
  - Exact canonical coverage gain until branch validation scans pinned world/assets.
conflicts: []
first_failure:
  marker: create_branch by explicit SHA returned 422
  evidence: GitHub connector create_branch; retry by trusted base_ref main succeeded
rejected_hypotheses:
  - local terminal required: repository GITHUB_ONLY_EXECUTION contract authorizes GitHub connector plus Actions
changed_paths:
  - docs/agents/tasks/active/OTH-20260814-otbm-atlas-runtime-animations.md
validation:
  - command: focused atlas tests
    result: NOT_RUN
    evidence: implementation not yet persisted
blockers: []
next_action: implement geometry-aware conservative environment animation export and browser drawing with focused tests
```
