---
task_id: OTH-20260816-atlas-incremental-build-ci
status: validating
owner: chat-github-atlas-incremental
branch: perf/OTH-20260816-atlas-production-incremental-entry
base_branch: main
created: "2026-08-16T10:04:00+02:00"
updated: "2026-08-16T16:25:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "426"
ownership_released: false
owned_paths:
  - tools/otbm_atlas/incremental.py
  - tools/otbm_atlas/incremental_core.py
  - tools/otbm_atlas/incremental_state.py
  - tools/otbm_atlas/incremental_cached.py
  - tools/otbm_atlas/production_incremental.py
  - tools/otbm_atlas/environment_incremental.py
  - tools/otbm_atlas/environment_animation_resume.py
  - tools/otbm_atlas/atlas.py
  - tools/otbm_atlas/domain_probe.py
  - tools/otbm_atlas/chunk_benchmark.py
  - tools/otbm_atlas/tests/test_incremental.py
  - tools/otbm_atlas/tests/test_incremental_state.py
  - tools/otbm_atlas/tests/test_production_incremental.py
  - tools/otbm_atlas/tests/test_environment_incremental.py
  - tools/otbm_atlas/tests/test_environment_animation_resume.py
  - tools/otbm_atlas/tests/test_domain_probe.py
  - tools/otbm_atlas/tests/test_chunk_benchmark.py
  - .github/workflows/otbm-atlas-incremental.yml
  - docs/maps/otbm-atlas-incremental-build.md
  - docs/agents/tasks/active/OTH-20260816-atlas-incremental-build-ci.md
  - docs/agents/tasks/archive/OTH-20260816-atlas-incremental-build-ci.md
---

# OTBM Atlas incremental build and GitHub CI

## Goal

Move ordinary Atlas build/test CPU work to GitHub-hosted Actions while making full-world rebuilds exceptional. A normal change must rebuild only affected map/render/data/frontend domains. Production `atlas.py` must persist and verify local state instead of treating a new monolithic map or asset-tree SHA as permission to rerender the world.

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

E2E means real incremental builder journeys on deterministic and canonical representative data: unchanged inputs reuse outputs, a local change dirties only its dependency closure, unrelated asset/source SHA changes do not invalidate unrelated chunks, corrupted persisted state is repaired from canonical source, environment-animation checkpoints are local, and the fail-closed full-build guard remains explicit.

## Verified baseline

- Atlas v3 production chunk contract remains 128x128.
- Certified canonical world baseline contains 3,494 detail chunks across Z0..Z15.
- Existing canonical detail PNG output is 10,995,096,999 bytes before other publication data, so GitHub Pages is not the current full-Atlas hosting target.
- PR #417 runner-fanout optimization is merged.
- PR #418 resumable environment-animation exporter is merged.
- PR #420 stale Required-poller cancellation is merged.
- PR #421 spatial incremental planner/cache/publication pipeline is merged as `32f7d5c58a889b78de5637ff9fbea56686b79bcd`; its final implementation head passed incremental unit tests, real dirty-build planning, pixel equivalence, the bounded 32/64/128 benchmark, CI, Required, Atlas Tests and applicable creature/environment workflows.
- PR #419 product/tile-inspector branch was reconciled with current incremental `main` as merge head `3a151e95e0c285135bb8cf96414b731b8910deb7`; its exact-head incremental workflow, CI and Required are green while the remaining bounded product/browser workflows complete.
- PR #426 owns the final production-entry integration on top of the reconciled product stack.

## Acceptance inventory

- [x] Map source is spatially fingerprinted per chunk; a monolithic OTBM SHA change alone never forces all detail renders.
- [x] Stable spool state has per-chunk reconciliation; unchanged spool bytes are reused and deleted chunks are removed explicitly.
- [x] Persisted production spool bytes are bound to per-chunk hashes; corruption is repaired from canonical OTBM rather than trusted.
- [x] Dependency index records chunk -> appearance/sprite dependencies and reverse dependency maps.
- [x] Appearance metadata changes invalidate only chunks using changed appearances unless a global render-bound profile changes.
- [x] Sprite-sheet changes invalidate only chunks using sprites from changed sheet ranges for detail rendering.
- [x] Detail fingerprints depend only on local spool bytes, local render dependencies, render contract and required global gutter profile.
- [x] Production `atlas.py` consumes exact dirty/reused/deleted chunk sets rather than whole-map/tree SHA cache invalidation.
- [x] Existing certified detail corpus can be adopted without rerender when exact source identity matches; the migration binds the legacy spool to verified local hashes.
- [x] Reused detail/overview images are not re-hashed across the complete ~11 GB corpus on every ordinary build.
- [x] Overview invalidation remains separate from detail invalidation.
- [x] Environment-animation global fingerprint excludes monolithic map SHA, complete asset SHA and complete chunk inventory.
- [x] Environment-animation chunk fingerprint binds local spool, logical bounds, used appearance semantics and exact decoded sprite pixels.
- [x] Unrelated sprite changes do not invalidate unrelated environment-animation checkpoints.
- [x] Deleted environment chunks remove stale checkpoint/shard references and unreachable payloads.
- [x] Change-impact planning separates map, assets, spawn/NPC/monster, houses, mechanics, factual data, frontend and documentation domains.
- [x] Non-render-only changes skip map spool/dependency scanning in the PR incremental planner.
- [x] Full-build-required decisions are fail-closed, carry machine-readable reasons and require an explicit allow flag.
- [x] Production full-detail override is explicit `--allow-full-build`; there is no implicit fallback.
- [x] Render-sensitive incremental-core changes require an explicit render-core version transition; unversioned semantic drift fails closed.
- [x] Content-addressed publication metadata maps logical output paths to SHA-256 objects and supports deterministic patch manifests.
- [x] Incremental publication manifest promotion is atomic; immutable changed objects are written before manifest selection.
- [x] Persistent GitHub cache is source-derived spool/dependency state only; it contains no rendered map imagery and is self-validating.
- [x] 32/64/128 benchmark tooling and exact-head evidence exist; production chunk size remains 128 pending browser/deployment evidence for a change.
- [x] GitHub-hosted workflow contains focused tests, impact planning, proportional domain probes, exact dirty-detail execution, representative equivalence E2E and bounded benchmark.
- [x] PR path changes do not automatically trigger canonical full-world build.
- [x] No generated Tibia/CipSoft-derived render corpus is uploaded by the incremental workflow.
- [x] Existing Game -> Atlas v1 remains complete-snapshot artifact-first; this work is Atlas-side consumption/build invalidation, not a delta protocol.
- [x] GitHub Pages remains disabled for the full Atlas; CI/build compute is separated from hosting/storage.
- [ ] Final exact-head #426 CI/E2E generation is terminal green after production-contract documentation.
- [ ] Fresh final audit has zero unresolved material findings and clean review/thread state.
- [ ] PR #426 is merged and `main` is re-read to prove the production entry point and local environment invalidation are present.
- [ ] Task lifecycle is archived/released after post-merge verification.

## Scope guard

Do not enable GitHub Pages or publish the Atlas render corpus from this public repository. Build/test Actions may create bounded ephemeral derived data but must not upload the full generated map corpus.

Do not reintroduce complete-map or complete-asset SHA into a local detail/environment chunk fingerprint. If a real global dependency exists, encode it as a narrow contract/profile/version and fail closed with an explicit reason.

## Context checkpoint

```yaml
checkpoint_version: 3
updated_at: 2026-08-16T16:25:00+02:00
phase: final-production-validation
session_id: chat-github-atlas-incremental-20260816
session_role: implementer
execution_mode: chat-github
project_lane: otheryn-content
validation_level: exact-head-plus-post-merge
branch: perf/OTH-20260816-atlas-production-incremental-entry
pr: 426
status: validating
proven:
  - PR 421 incremental infrastructure merged with fully green exact-head validation
  - PR 418 resumable environment exporter merged
  - product branch 419 reconciled with incremental main without dropping either change set
  - production planner persists per-chunk detail and spool identities
  - production planner repairs corrupt spool from canonical source
  - production atlas entry renders exact dirty detail set and requires explicit --allow-full-build for global transitions
  - environment exporter v3 uses global semantic contract plus local appearance/sprite/spool dependencies
  - tests cover zero-dirty reuse, legacy adoption, one local dirty chunk, corruption repair, local environment sprite impact and deleted-chunk cleanup
  - final stack CI, Required, Atlas Incremental, Synology Preview and multiple factual/audit checks have already produced green evidence on pre-documentation exact heads
blockers: []
next_action: obtain one final terminal exact-head PR 426 generation after this checkpoint, perform fresh diff/review/source audit, merge, re-read main and archive the task
```
