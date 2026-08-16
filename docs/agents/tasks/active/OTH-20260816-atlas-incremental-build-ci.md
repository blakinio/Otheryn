---
task_id: OTH-20260816-atlas-incremental-build-ci
status: implementing
owner: chat-github-atlas-incremental
branch: perf/OTH-20260816-atlas-incremental-build
base_branch: main
created: "2026-08-16T10:04:00+02:00"
updated: "2026-08-16T10:04:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: ""
ownership_released: false
owned_paths:
  - tools/otbm_atlas/incremental.py
  - tools/otbm_atlas/chunk_benchmark.py
  - tools/otbm_atlas/tests/test_incremental.py
  - tools/otbm_atlas/tests/test_chunk_benchmark.py
  - .github/workflows/otbm-atlas-incremental.yml
  - docs/maps/otbm-atlas-incremental-build.md
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

E2E here means a real incremental builder journey on deterministic fixtures/canonical representative data: unchanged inputs reuse outputs, one map chunk change rebuilds only that chunk, one used asset change invalidates only dependent chunks, unrelated frontend/docs changes do not render the world, and clean/incremental manifests remain equivalent for the same inputs.

## Verified constraints at task start

- `main` is `39cb2ce4ff427e7c3760eb6112b45efc0c1f73b8`.
- Current Atlas v3 uses 128x128 chunks and has 3,494 certified detail chunks.
- Existing canonical detail PNG output is 10,995,096,999 bytes before other publication data, so GitHub Pages is not a valid current full-Atlas hosting target.
- Current `atlas.py` cache fingerprint includes whole-map and whole-asset-tree SHA-256 values, so a single source change can invalidate all detail chunks.
- Current `spool_map` recreates the complete spool when its global source state changes.
- Open PR #418 owns `tools/otbm_atlas/atlas.py` for resumable environment-animation export.
- Open PR #419 also owns `tools/otbm_atlas/atlas.py` for product-completion/tile-inspector work.
- Open PR #417 owns the existing specialized Atlas workflow files; PR #420 owns `required.yml`.
- This task therefore starts with new non-overlapping incremental-builder/workflow paths and must not edit those actively owned files until their ownership becomes terminal.

## Acceptance inventory

- [ ] Map source is spatially fingerprinted per chunk; a monolithic OTBM SHA change alone never forces all detail renders.
- [ ] Stable spool state is updated per chunk; unchanged spool bytes are reused and deleted chunks are removed explicitly.
- [ ] Dependency index records chunk -> appearance/sprite dependencies and reverse dependency maps.
- [ ] Appearance metadata changes invalidate only chunks using changed appearances unless a global render-bound profile changes.
- [ ] Sprite-sheet changes invalidate only chunks using sprites from changed sheet ranges.
- [ ] Detail fingerprints depend only on local spool bytes, local render dependencies, render contract and required global gutter profile.
- [ ] Overview invalidation is separate from detail invalidation.
- [ ] Change-impact planning separates map, assets, spawn/NPC/monster, mechanics, factual data, frontend and documentation domains.
- [ ] Full-build-required decisions are fail-closed, carry machine-readable reasons and require an explicit allow flag.
- [ ] Content-addressed publication metadata maps logical output paths to SHA-256 objects and supports deterministic patch manifests.
- [ ] Incremental publication writes are atomic; failed candidate work does not replace the prior publication manifest.
- [ ] 32/64/128 chunk-size benchmark tooling exists and GitHub Actions runs a bounded representative benchmark before changing the default from 128.
- [ ] GitHub-hosted Actions run focused incremental tests/build probes without using Synology runners or owner-funded AI.
- [ ] PR path changes do not automatically trigger canonical full-world build.
- [ ] A clean-vs-incremental equivalence test runs on deterministic fixtures/representative scope; canonical full-world equivalence remains explicit/manual until a safe sharded GitHub-hosted execution path is proven.
- [ ] No generated Tibia/CipSoft-derived render corpus is uploaded as a public workflow artifact.
- [ ] Existing Game -> Atlas v1 remains complete-snapshot artifact-first; this work is Atlas-side consumption/build invalidation, not a delta protocol.

## Scope guard

Do not enable GitHub Pages or publish Atlas render assets from this public repository. Current output size exceeds Pages suitability and public redistribution of generated third-party-derived assets is not authorized by this task. GitHub-hosted CI may generate bounded ephemeral outputs for validation but must not upload the render corpus.

Do not edit paths currently owned by PRs #417, #418, #419 or #420 while those tasks remain live. Integrating the new builder into `atlas.py` or replacing existing workflow triggers is a later phase of this same task only after ownership is terminal and exact-base reconciliation is safe.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-16T10:04:00+02:00
phase: implement
session_id: chat-github-atlas-incremental-20260816
session_role: implementer
execution_mode: chat-github
project_lane: otheryn-content
context_pressure: medium
context_growth: stable
decomposition_decision: phased
validation_level: focused
branch: perf/OTH-20260816-atlas-incremental-build
pr: none
status: implementing
head: 39cb2ce4ff427e7c3760eb6112b45efc0c1f73b8
owned_paths:
  - tools/otbm_atlas/incremental.py
  - tools/otbm_atlas/chunk_benchmark.py
  - tools/otbm_atlas/tests/test_incremental.py
  - tools/otbm_atlas/tests/test_chunk_benchmark.py
  - .github/workflows/otbm-atlas-incremental.yml
  - docs/maps/otbm-atlas-incremental-build.md
proven:
  - current global map/assets fingerprint can invalidate every detail chunk
  - current Atlas output exceeds GitHub Pages practical/declared site-size target
  - current public repo has overlapping active Atlas PR ownership
  - Atlas-side incremental build does not require changing Game -> Atlas v1 snapshot semantics
blockers: []
next_action: implement deterministic per-chunk change-impact/dependency/publication primitives in new non-overlapping files with focused tests
```
