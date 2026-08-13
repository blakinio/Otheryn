---
task_id: OTH-20260813-full-otbm-atlas
status: implementing
owner: chatgpt-github-20260814-environment-animation
created: 2026-08-13
updated: 2026-08-14T00:25:00+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: false
execution_budget_minutes: 120
execution_budget_reason: owner-expanded atlas scope adds deterministic animated environment appearances and requires renewed exact-head validation
modules_touched:
  - otbm-atlas
---

# Full OTBM atlas continuation

PR #381 remains the active atlas integration branch. The owner explicitly expanded its scope on 2026-08-14 to add browser-side animation for canonical environment appearances such as flames and lamps, while keeping server-driven state changes distinct from cyclic appearance animation.

The implementation must preserve the existing chunked/bounded architecture. Cyclic environment animation is generated from pinned object appearance frame metadata and sprite assets. The browser animates only viewport-visible records at close zoom. To avoid phase-zero ghosting, only conservative topmost 32x32 non-displaced object animations are promoted to the dynamic overlay; their high-zoom base chunk omits those exact objects and the browser redraws their canonical phases. Larger/displaced/occluded animations remain deterministic static pixels until a future full dynamic-stack renderer can preserve exact occlusion. Stateful objects such as open/closed doors, switches, or on/off variants are not inferred as animation.

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-14T00:25:00+02:00
code_head: 08cf740184778e159d0f57bb5fb0fa491e01472a
branch: agent/oth-20260813-full-otbm-atlas-current-main
pr: 381
status: implementing
phase: environment-animation
session_id: chatgpt-github-20260814-environment-animation
session_role: implementer
execution_mode: chat-github
execution_reason: GitHub-only multi-file atlas change; owner-funded Codex remains forbidden
project_lane: otheryn-content
context_pressure: medium
context_growth: stable
context_score: 7
decomposition_decision: phased
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-atlas-tests.yml
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
proven:
  - canonical world SHA-256 is 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - pinned appearances.proto defines SpriteAnimation default phase, synchronized/random flags, loop type/count and per-phase duration ranges
  - current atlas already keeps detailed pixels and spatial overlays chunked with bounded browser caches
  - current static renderer uses the pinned object appearance first frame group and declared default_start_phase
  - owner explicitly requested cyclic environment animation to be implemented in the atlas
  - dynamic server state must stay separate from cyclic appearance animation
unknown:
  - exact full-world count of conservatively promotable animated environment objects until regenerated validation completes
  - final exact-head CI, browser E2E and full-world verifier results after this scope expansion
blockers: []
recovery:
  policy_version: 1
  generation: 1
  session_id: chatgpt-github-20260814-environment-animation
  session_started_at: 2026-08-14T00:25:00+02:00
  checkpointed_at: 2026-08-14T00:25:00+02:00
  last_progress_at: 2026-08-14T00:25:00+02:00
  phase: environment-animation
  exact_head: 08cf740184778e159d0f57bb5fb0fa491e01472a
  pull_request: 381
  active_operation: none
  external_run_ids: []
  operation_started_at: null
  wait_deadline_at: null
  check_generation: null
  checks_used: 0
  status: active
  safe_to_resume: true
  resume_condition: branch remains owned by this task and PR 381 is open
  next_action: implement deterministic environment animation metadata, clean high-zoom chunk bases, browser culling/timing, tests and documentation
next_action: implement deterministic environment animation metadata, clean high-zoom chunk bases, browser culling/timing, tests and documentation
```
