---
task_id: OTH-20260813-full-otbm-atlas
status: validating
owner: chatgpt-github-20260814-atlas-completion
created: 2026-08-13
updated: 2026-08-14T11:58:00+02:00
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

## Final-gate repair

Exact-head acceptance run `31783345069` on PR head `27454113b9b85a2a17d4b61717874167ba339bf1` proved unit/runtime, canonical Thais, real Chromium E2E, shard 0 and shard 1. Shards 2 and 3 were cancelled during `Build canonical atlas shard` at the configured 90-minute job timeout; their verifier/evidence steps were therefore skipped. The logs contain no functional renderer/verifier error before cancellation.

The material blocker was repaired in commit `e184a3604687b05b1c898f46ada02a71d8a59d9d` by changing only `.github/workflows/otbm-atlas-tests.yml`: `full-world-shards.timeout-minutes` was increased from 90 to 120. Canonical atlas code, rendering semantics, source fingerprints, shard definitions, verifier, and aggregate 3494-chunk acceptance assertions were not weakened or changed.

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-14T11:58:00+02:00
invocation_started_at: 2026-08-14T11:58:12+02:00
last_progress_at: 2026-08-14T11:58:00+02:00
frozen_code_sha: e638c96f41a7fd3ad6a4c0f81c8e757adaf779ea
acceptance_repair_sha: e184a3604687b05b1c898f46ada02a71d8a59d9d
branch: agent/oth-20260813-full-otbm-atlas-current-main
pr: 381
status: validating
phase: final-full-world-revalidation
session_id: chatgpt-github-20260814-atlas-completion
session_role: validator-repair
execution_mode: chat-github
project_lane: otheryn-content
context_pressure: medium
context_growth: stable
decomposition_decision: phased
validation_level: full
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 1
context_reconstruction_attempts: 0
stall_warnings: 0
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-atlas-tests.yml
  - .github/workflows/otbm-environment-animation-tests.yml
  - docs/maps/**
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
proven:
  - canonical world SHA-256 is 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - full atlas unit/runtime suite PASS on frozen implementation
  - canonical Thais scan and pinned-asset render PASS on frozen implementation
  - real Chromium Thais navigation/search/layer/details journey PASS on frozen implementation
  - environment-animation real Chromium E2E PASS on frozen implementation
  - repository CI PASS, Required PASS and autofix.ci PASS on the pre-repair acceptance head
  - PR #381 has zero unresolved review threads at implementation freeze
  - acceptance run 31783345069 shard 0 PASS and shard 1 PASS with independent verifier and missingSprites empty
  - acceptance run 31783345069 shard 2 and shard 3 cancellation signature is the 90-minute workflow timeout, not a reported functional failure
unknown:
  - final 3494-chunk aggregate verifier result on the repaired exact head
  - fresh independent post-full-world audit result
blockers:
  - repaired final full-world gate must pass on the new exact head before merge
  - one fresh independent audit is required after that full-world result and before merge
next_action: re-trigger ci:final-gate on the new exact head, require all four shards plus aggregate 3494-chunk Z0..15 evidence and exact-head CI/E2E PASS, then perform the fresh audit and merge/archive only if every gate passes
```
