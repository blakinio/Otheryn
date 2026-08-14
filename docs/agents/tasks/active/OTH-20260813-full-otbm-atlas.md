---
task_id: OTH-20260813-full-otbm-atlas
status: validating
owner: chatgpt-github-20260814-atlas-completion
created: 2026-08-13
updated: 2026-08-14T10:16:00+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: false
execution_budget_minutes: 120
execution_budget_reason: implementation is complete; one deliberately-triggered full-world validation remains before merge/release certification
modules_touched:
  - otbm-atlas
---

# Full OTBM atlas continuation

PR #381 is the active atlas integration branch. Owner decision on 2026-08-14: the expensive 3494-chunk `Full canonical world v3` job is not a synchronize-time development test. Atlas implementation is completed first with focused/unit/canonical-region/browser validation, then the frozen implementation is subjected to one full canonical-world build and verifier pass as the final release/merge acceptance gate.

## Frozen implementation

The implementation is frozen at code SHA `e638c96f41a7fd3ad6a4c0f81c8e757adaf779ea`.

The completed scope preserves the full chunked/bounded architecture and includes:

- canonical item sprite selection including stack-count, fluid/splash subtype, hangable hook and container-visibility semantics;
- canonical NPC outfit/addon rendering from pinned client appearances;
- conservative factual AID/UID/mechanics resolution without heuristic guessing;
- base-map versus supplemental NPC/monster provenance and separate layers;
- multi-resolution complete-world chunk manifests with exact canonical detail imagery;
- `Auto | Detailed | Performance` render modes with bounded viewport/chunk/image caches;
- raw canonical OTBM `X/Y/Z` (`Z=0..15`) consistently across UI, jump, copy, search and URL state;
- URL/local-storage persistence for position, zoom, render mode, layers and selected marker;
- factual layers for NPCs, monsters, supplemental creatures, teleports, houses, house doors, AID, UID, towns/temples, waypoints and mechanics;
- bosses kept explicitly disabled/`UNKNOWN` because no authoritative boss classification source is present;
- search that navigates to the factual record, enables/persists its layer, selects the exact shard record and opens details;
- hit testing restricted to current visible shards and currently enabled layers;
- exact detailed pixels with image smoothing disabled;
- bounded browser-side cyclic environment animation from pinned appearance metadata, while server-driven state variants remain separate and are not inferred;
- durable UI classification/behavior contract in `docs/maps/atlas-viewer-ui-contract.md`.

## CI policy

`.github/workflows/otbm-atlas-tests.yml` now intentionally separates development and final acceptance:

- unit/runtime tests run during normal PR development;
- canonical Thais scan/render runs during normal PR development;
- real Chromium Thais E2E runs during normal PR development;
- environment-animation Chromium E2E remains a focused development gate;
- `Full canonical world v3` runs only on explicit `workflow_dispatch` or the specific PR `labeled` event that adds `ci:final-gate`.

Keeping `ci:final-gate` on a PR no longer causes every later `synchronize` event to rebuild the full world. The label is currently absent and must be added only when the owner is ready for the single final acceptance build.

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-14T10:16:00+02:00
frozen_code_sha: e638c96f41a7fd3ad6a4c0f81c8e757adaf779ea
branch: agent/oth-20260813-full-otbm-atlas-current-main
pr: 381
status: validating
phase: ready-for-final-full-world-acceptance
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
  - full atlas unit/runtime suite PASS on frozen code SHA e638c96f41a7fd3ad6a4c0f81c8e757adaf779ea
  - canonical Thais scan and pinned-asset render PASS on frozen code SHA e638c96f41a7fd3ad6a4c0f81c8e757adaf779ea
  - real Chromium Thais navigation/search/layer/details journey PASS on frozen code SHA e638c96f41a7fd3ad6a4c0f81c8e757adaf779ea
  - environment-animation real Chromium E2E PASS on frozen code SHA e638c96f41a7fd3ad6a4c0f81c8e757adaf779ea
  - repository CI PASS, Required PASS and autofix.ci PASS on frozen code SHA e638c96f41a7fd3ad6a4c0f81c8e757adaf779ea
  - Full canonical world v3 was SKIPPED on that development validation as intended
  - PR #381 has zero unresolved review threads at implementation freeze
unknown:
  - final canonical full-world v3 statistics and verifier result for the frozen implementation
  - fresh independent post-full-world audit result
blockers:
  - one explicit final 3494-chunk full-world build plus independent verifier is still required before final merge/release certification
  - one fresh independent audit is still required after that full-world result and before merge
next_action: when the owner chooses to run final acceptance, ensure no product-code change exists after frozen_code_sha, add ci:final-gate once (or workflow_dispatch), collect the 3494-chunk Z0..15 verifier result, perform the fresh independent audit, then merge PR #381 and archive this task
```
