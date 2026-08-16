---
task_id: OTH-20260816-atlas-incremental-build-ci
status: validating
owner: chat-github-atlas-incremental
branch: perf/OTH-20260816-atlas-incremental-build
base_branch: main
created: "2026-08-16T10:04:00+02:00"
updated: "2026-08-16T10:39:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "421"
ownership_released: false
owned_paths:
  - tools/otbm_atlas/incremental.py
  - tools/otbm_atlas/incremental_core.py
  - tools/otbm_atlas/incremental_state.py
  - tools/otbm_atlas/incremental_cached.py
  - tools/otbm_atlas/domain_probe.py
  - tools/otbm_atlas/chunk_benchmark.py
  - tools/otbm_atlas/tests/test_incremental.py
  - tools/otbm_atlas/tests/test_incremental_state.py
  - tools/otbm_atlas/tests/test_domain_probe.py
  - tools/otbm_atlas/tests/test_chunk_benchmark.py
  - .github/workflows/otbm-atlas-incremental.yml
  - docs/maps/otbm-atlas-incremental-build.md
  - docs/agents/reports/OTH-20260816-atlas-incremental-build-audit.md
  - docs/agents/tasks/active/OTH-20260816-atlas-incremental-build-ci.md
  - docs/agents/tasks/archive/OTH-20260816-atlas-incremental-build-ci.md
---

# OTBM Atlas incremental build and GitHub CI

## Goal

Move ordinary Atlas build/test CPU work to GitHub-hosted Actions while making full-world rebuilds exceptional. A normal change must produce a deterministic change-impact plan and rebuild only affected map/render/data/frontend domains. Full rebuilds must be explicit, justified and independently verifiable against incremental output.

## Delivery classification

```yaml
feature_scope:
  type: infrastructure
  user_facing: false
  backend_required: false
  frontend_required: false
  integration_required: true
  e2e_required: true
```

E2E here means a real incremental builder journey on deterministic fixtures/canonical representative data: unchanged inputs reuse outputs, one map chunk change rebuilds only that chunk, one used asset change invalidates only dependent chunks, unrelated data/frontend/docs changes do not render the world, and clean/incremental manifests remain equivalent for the same inputs.

## Verified constraints at task start

- `main` was `39cb2ce4ff427e7c3760eb6112b45efc0c1f73b8`; exact main must be re-read before merge/integration.
- Current Atlas v3 uses 128x128 chunks and has 3,494 certified detail chunks.
- Existing canonical detail PNG output is 10,995,096,999 bytes before other publication data, so GitHub Pages is not a valid current full-Atlas hosting target.
- Current legacy `atlas.py` cache fingerprint includes whole-map and whole-asset-tree SHA-256 values, so a single source change can invalidate all detail chunks.
- Current legacy `spool_map` recreates the complete spool when its global source state changes.
- Open PR #418 owns `tools/otbm_atlas/atlas.py` for resumable environment-animation export.
- Open PR #419 also owns `tools/otbm_atlas/atlas.py` for product-completion/tile-inspector work.
- Open PR #417 owns existing specialized Atlas workflow files; PR #420 owns `required.yml`.
- This task therefore implements new non-overlapping incremental paths first and must not overwrite those active owners.

## Acceptance inventory

- [x] Map source is spatially fingerprinted per chunk; a monolithic OTBM SHA change alone never forces all detail renders.
- [x] Stable spool state has per-chunk reconciliation; unchanged spool bytes are reused and deleted chunks are removed explicitly.
- [x] Dependency index records chunk -> appearance/sprite dependencies and reverse dependency maps.
- [x] Appearance metadata changes invalidate only chunks using changed appearances unless a global render-bound profile changes.
- [x] Sprite-sheet changes invalidate only chunks using sprites from changed sheet ranges.
- [x] Detail fingerprints depend only on local spool bytes, local render dependencies, render contract and required global gutter profile.
- [x] Overview invalidation is separate from detail invalidation.
- [x] Change-impact planning separates map, assets, spawn/NPC/monster, houses, mechanics, factual data, frontend and documentation domains.
- [x] Non-render-only changes skip map spool/dependency scanning in the incremental planner.
- [x] Full-build-required decisions are fail-closed, carry machine-readable reasons and require an explicit allow flag.
- [x] Render-sensitive incremental-core changes require an explicit render-core version transition; unversioned semantic drift fails closed.
- [x] Content-addressed publication metadata maps logical output paths to SHA-256 objects and supports deterministic patch manifests.
- [x] Incremental publication manifest promotion is atomic; immutable changed objects are written before manifest selection.
- [x] Persistent GitHub cache is source-derived spool/dependency state only; it contains no rendered map imagery and is self-validating by exact map/appearance identity.
- [x] 32/64/128 chunk-size benchmark tooling exists; final measured result is pending exact-head workflow completion.
- [x] GitHub-hosted workflow contains focused tests, impact planning, proportional domain probes, exact dirty-detail execution, representative pixel-equivalence E2E and bounded chunk benchmark.
- [x] PR path changes do not automatically trigger canonical full-world build.
- [x] No generated Tibia/CipSoft-derived render corpus is uploaded by the incremental workflow.
- [x] Existing Game -> Atlas v1 remains complete-snapshot artifact-first; this work is Atlas-side consumption/build invalidation, not a delta protocol.
- [ ] Final exact-head CI for the persistent-state generation is green and benchmark results are recorded.
- [ ] Fresh post-implementation audit is closed with no unresolved material finding inside owned paths.
- [ ] Main `tools/otbm_atlas/atlas.py` entry-point integration is complete after PRs #418/#419 release overlapping ownership.

## Scope guard

Do not enable GitHub Pages or publish Atlas render assets from this public repository. Current output size exceeds Pages suitability and public redistribution of generated third-party-derived assets is not authorized by this task. GitHub-hosted CI may generate bounded ephemeral outputs for validation but must not upload the render corpus.

Do not edit paths currently owned by PRs #417, #418, #419 or #420 while those tasks remain live. Integrating the new builder into `atlas.py` or replacing their workflow paths is a later phase of this same task only after ownership is terminal and exact-base reconciliation is safe.

## Context checkpoint

```yaml
checkpoint_version: 2
updated_at: 2026-08-16T10:39:00+02:00
phase: exact-head-validation
session_id: chat-github-atlas-incremental-20260816
session_role: implementer
execution_mode: chat-github
project_lane: otheryn-content
context_pressure: medium
context_growth: stable
decomposition_decision: phased
validation_level: focused-plus-live-ci
branch: perf/OTH-20260816-atlas-incremental-build
pr: 421
status: validating
head_before_checkpoint: 820bb6dea53a4312fa17bded0cde19c711207392
proven:
  - current global map/assets fingerprint can invalidate every legacy detail chunk
  - current Atlas output exceeds GitHub Pages practical/declared site-size target
  - Atlas-side incremental build does not require changing Game -> Atlas v1 snapshot semantics
  - local/reverse dependency invalidation and content-addressed publication primitives exist
  - non-render changes can skip render-source scanning entirely
  - persistent state stores only source-derived spool/dependency metadata and validates exact source identity
  - earlier focused generation passed 23 tests on a GitHub-hosted runner; new persistent-state tests are pending exact-head CI
  - exact-head checkout defect found during audit was repaired
blockers:
  - final integration into tools/otbm_atlas/atlas.py remains ownership-blocked by active PRs 418 and 419
  - PR 419 exact-head workflows currently require action, so it cannot be merged as verified
  - PR 418 CI is green but its own task still requires canonical full-world/deployed-browser acceptance before terminal closeout
next_action: obtain terminal exact-head PR 421 CI including persistent-state tests and benchmark, record fresh audit evidence, then merge the independent incremental infrastructure if clean while preserving the atlas.py integration blocker
```
