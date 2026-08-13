---
task_id: OTH-20260813-full-otbm-atlas
status: implementing
owner: chatgpt-github-20260813
created: 2026-08-13
updated: 2026-08-13T18:52:00+02:00
project_lane: otheryn-content
related_pr: null
ownership_released: false
execution_budget_minutes: 120
execution_budget_reason: fresh full-world validation is required after renderer and NPC sprite corrections
modules_touched:
  - otbm-atlas
---

# Full OTBM atlas continuation

This active record supersedes stale PR #377 after `main` advanced through merged PRs #378-#380. Branch base: `3f34291e506f5349f5d03d084ccce3307ea861b4`.

Verified gaps: current renderer still draws nested container descendants and ignores stack/fluid subtype patterns; atlas cache remains v2; broad UID table-key inference must not guess mechanics; base and supplemental creature origins require separate browser layers. Merged PR #378 also has unresolved review findings for outfit mask colors, addons, and duplicate visual outfits; PR #379 lacks real browser E2E and verifiable independent-audit evidence. PR #380's pinned creature sources are preserved.

Product constraints remain: viewport/floor chunk loading only, bounded caches, exact canonical detail render, `Auto | Detailed | Performance`, factual toggleable layers, shareable X/Y/raw-Z/zoom/mode/layers, and no guessed data.

```yaml
checkpoint_version: 1
updated_at: 2026-08-13T18:52:00+02:00
head: 3f34291e506f5349f5d03d084ccce3307ea861b4
branch: agent/oth-20260813-full-otbm-atlas-current-main
pr: none
status: implementing
phase: implement
session_id: chatgpt-github-20260813-002
session_role: implementer
execution_mode: chat-github
project_lane: otheryn-content
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-atlas-tests.yml
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
proven:
  - canonical world SHA-256 is 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - historical v2 build covered 3494 chunks over raw Z0..15 but cannot certify corrected detail pixels
  - no active atlas task exists on current main
  - PR #377 is the only open atlas PR and is stale against merged #378-#380
unknown:
  - corrected NPC sprite output counts
  - authoritative boss classification contract
  - fresh v3 full-world statistics
  - independent post-repair audit result
next_action: verify NPC mask/addon semantics against pinned OTClient source and apply current-main-compatible repairs with regression tests
```
