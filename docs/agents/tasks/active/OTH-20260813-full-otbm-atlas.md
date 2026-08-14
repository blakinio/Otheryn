---
task_id: OTH-20260813-full-otbm-atlas
status: implementing
owner: chatgpt-github-20260814-atlas-completion
created: 2026-08-13
updated: 2026-08-14T09:36:00+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: false
execution_budget_minutes: 120
execution_budget_reason: finish atlas functionality and focused validation before one final full-world acceptance build
modules_touched:
  - otbm-atlas
---

# Full OTBM atlas continuation

PR #381 remains the active atlas integration branch. Owner decision on 2026-08-14: do not repeatedly run the expensive 3494-chunk `Full canonical world v3` job during active atlas development. Finish the atlas first using focused/unit/canonical-region/browser validation, freeze the final code SHA, then perform one full canonical-world build and verifier pass as the final release/merge acceptance gate.

The `ci:final-gate` label was removed from PR #381 so normal `synchronize` events no longer start the expensive full-world job. Re-apply `ci:final-gate` only after code freeze when the atlas is functionally complete and the exact final SHA is ready for acceptance. Any already-running historical full-world jobs are non-authoritative for later changed heads.

Current implemented scope preserves the chunked/bounded architecture. It includes canonical item rendering semantics, conservative factual mechanics indexing, separated base/supplemental spawn provenance, canonical NPC outfit rendering, persistent URL/view state, `Auto | Detailed | Performance`, factual toggleable layers, bounded viewport/chunk/image caches, exact detailed pixels, and the owner-approved browser-side cyclic environment animation expansion. Stateful variants such as doors, switches, quest objects or on/off state remain separate and are not inferred as cyclic animation.

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-14T09:36:00+02:00
code_head_before_checkpoint: 8f429ab8dc8612012809f051d029d43634414875
branch: agent/oth-20260813-full-otbm-atlas-current-main
pr: 381
status: implementing
phase: atlas-completion-before-final-full-world
session_id: chatgpt-github-20260814-atlas-completion
session_role: implementer
execution_mode: chat-github
project_lane: otheryn-content
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-atlas-tests.yml
  - .github/workflows/otbm-environment-animation-tests.yml
  - docs/maps/**
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
proven:
  - canonical world SHA-256 is 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - focused atlas unit/runtime tests, canonical Thais render and real Chromium journeys are the development-time validation gates
  - full-world generation is expensive enough to exceed the owner's 45-minute local target and has repeatedly consumed long GitHub runner time
  - repeated full-world runs are not required while the implementation is still changing
  - full-world verification remains required once, on the frozen final SHA, before final merge/release certification
  - `ci:final-gate` is intentionally absent during active development
unknown:
  - final frozen SHA
  - final canonical full-world statistics and verifier result
  - final independent audit result after implementation is complete
blockers: []
next_action: finish remaining atlas functionality and UI using focused tests; when code and docs are complete, freeze the SHA, re-apply ci:final-gate once, run the 3494-chunk full-world build plus verifier, audit the unchanged head, then merge/archive
```
