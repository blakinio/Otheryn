---
task_id: OTH-20260813-full-otbm-atlas
status: validating
owner: chatgpt-github-20260813
created: 2026-08-13
updated: 2026-08-13T19:45:00+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: false
execution_budget_minutes: 120
execution_budget_reason: fresh full-world validation is required after renderer and NPC sprite corrections
modules_touched:
  - otbm-atlas
---

# Full OTBM atlas continuation

PR #381 supersedes stale PR #377 after `main` advanced through merged PRs #378-#380. Trusted base: `3f34291e506f5349f5d03d084ccce3307ea861b4`.

The current implementation repairs detailed item visibility and subtype pattern semantics, conservative mechanics resolution, canonical NPC outfit rendering, and base/supplemental creature provenance while retaining bounded viewport/floor chunk loading, bounded caches, exact detailed pixels, `Auto | Detailed | Performance`, factual toggleable layers, and shareable X/Y/raw-Z/zoom/mode/layers.

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-13T19:45:00+02:00
head: 777d8ec364a326bca909de371863ef176d313b4d
branch: agent/oth-20260813-full-otbm-atlas-current-main
pr: 381
status: validating
phase: validate
session_id: chatgpt-github-20260813-003
session_role: implementer
execution_mode: chat-github
project_lane: otheryn-content
invocation_started_at: 2026-08-13T19:41:00+02:00
last_progress_at: 2026-08-13T19:45:00+02:00
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 1
stall_warnings: 0
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-atlas-tests.yml
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
proven:
  - canonical world SHA-256 is 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - historical v2 build covered 3494 chunks over raw Z0..15 but cannot certify corrected v3 detail pixels
  - exact head 168a8f496069e347cbb5cade1e8a7b0facbacf34 passed CI, Required, autofix.ci and OTBM Atlas Tests
  - PR #381 contains current-main-compatible fixes for nested container visibility, stack/fluid subtype patterns, conservative literal mechanics resolution, NPC mask/addon semantics and duplicate visual outfit handling
  - final-gate label is applied to PR #381
  - repository-owned final gate now includes a real Chromium journey built from a canonical Thais render and a factual base-map NPC selected from canonical spawn XML
unknown:
  - exact-head 777d8ec364a326bca909de371863ef176d313b4d focused/canonical/browser/full-world results
  - fresh v3 full-world statistics and verifier result
  - independent post-implementation audit result
  - terminal disposition of superseded PR #377
blockers: []
next_action: collect exact-head OTBM Atlas Tests including Chromium E2E and 3494-chunk v3 verification, then perform fresh exact-head audit and PR hygiene
```
