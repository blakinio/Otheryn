---
task_id: OTH-20260813-full-otbm-atlas
status: validating
owner: chatgpt-github-20260813
created: 2026-08-13
updated: 2026-08-13T20:08:00+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: false
execution_budget_minutes: 120
execution_budget_reason: fresh full-world validation is required after canonical renderer corrections
modules_touched:
  - otbm-atlas
---

# Full OTBM atlas continuation

PR #381 supersedes stale PR #377 after `main` advanced through merged PRs #378-#380. Trusted base: `3f34291e506f5349f5d03d084ccce3307ea861b4`.

The implementation keeps the complete OTBM browser path viewport/floor chunked with bounded image and overlay caches. It preserves `Auto | Detailed | Performance`, shareable X/Y/raw-Z/zoom/mode/layers, factual base/supplemental creature layers, mechanics/houses/teleports/towns/waypoints, and canonical detailed pixels without guessing unresolved data.

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-13T20:08:00+02:00
code_head: 5232fb91b6aa3ea5530c652ebaa2d2675c6f7b9c
branch: agent/oth-20260813-full-otbm-atlas-current-main
pr: 381
status: validating
phase: final-gate
session_id: chatgpt-github-20260813-004
session_role: implementer
execution_mode: chat-github
project_lane: otheryn-content
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-atlas-tests.yml
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
proven:
  - canonical world SHA-256 is 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - historical v2 build covered 3494 chunks over raw Z0..15 but does not certify corrected v3 pixels
  - v3 renderer excludes nested container contents from the visible stack and follows pinned OTClient stack-count and new-fluid subtype patterns
  - v3 renderer now also follows pinned OTClient hangable pattern selection using appearance hang/hook metadata and tile hook orientation
  - dynamic UID dispatch tables are not guessed; literal registrations remain factual
  - pinned OTClient NPC mask behavior was revalidated against ThingType::loadTexture and Image::overwriteMask; mixed non-primary mask colors are intentionally not selected
  - base-map and supplemental NPC/monster records are emitted as separate spatial viewer kinds
  - detailed canvas disables image smoothing and marker hit-testing is bounded to current visible shards
  - final-gate label is applied and repository-owned validation includes unit/runtime, canonical Thais, real Chromium E2E and 3494-chunk full-world verification
  - one-shot hangable repair ran the complete tools/otbm_atlas test suite plus git diff --check successfully before committing
unknown:
  - final-head CI/Required/autofix terminal results after this checkpoint commit
  - final-head canonical Thais, Chromium E2E and fresh v3 3494-chunk verifier result
  - fresh v3 full-world statistics
blockers: []
next_action: collect terminal final-head gates; merge PR #381 only if all required checks and independent generated-output verification pass, then archive this task and release ownership
```
