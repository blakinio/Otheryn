---
task_id: OTH-20260815-otbm-atlas-product-readiness
status: waiting
owner: none
branch: none
base_branch: main
created: 2026-08-15T14:09:00+02:00
updated: 2026-08-15T14:09:00+02:00
project_lane: otheryn-content
execution_mode: chat-github
related_pr: null
ownership_released: true
---

# OTBM Atlas product-readiness continuation

## Goal

Continue the OTBM Atlas from technical DONE/VERIFIED to owner-facing product readiness without reopening already-proven parser/render/full-world work.

The canonical product backlog is:

`docs/maps/otbm-atlas-product-readiness-backlog-20260815.md`

The durable continuation handover is:

`docs/maps/otbm-atlas-continuation-handover-20260815.md`

## Current state

- Technical Atlas closeout remains DONE/VERIFIED.
- Full canonical world certification remains Z0..Z15 / 3494 chunks / zero certified missing sprites.
- PR #401 preserved local-preview/storage/codec evidence and the real-chunk benchmark prompt.
- PR #402 preserved the complete product-readiness backlog and owner requirement `ATLAS-PR-013` for a Tile ID hover inspector.
- Current preview boundary remains local Synology/Container Manager + DSM reverse proxy, outside Oteryn Platform and without an SSH tunnel.
- Static bounded chunking remains the default architecture; a single giant per-floor image is not the selected direction.
- Server-side lazy detail rendering remains optional and is not authorized merely to avoid copying a multi-gigabyte static artifact.
- The bounded 24-image codec-direction experiment made WebP lossless promising, but it is not full-atlas evidence.
- The owner reports that a local Codex worker is currently finishing the read-only real generated-detail-chunk PNG-vs-WebP benchmark defined by `docs/maps/otbm-atlas-real-chunk-codec-benchmark-prompt-20260815.md`.
- The local Codex result has not yet been received or verified in the repository. Therefore `ATLAS-PR-010` and `ATLAS-PR-011` remain unresolved decision gates.

## Waiting reason

The next decision depends on external local benchmark evidence that is still being produced on the owner's desktop checkout. Do not infer the result from the earlier 24-image experiment and do not migrate the Atlas image format before the real generated-chunk evidence is reviewed.

No worker/branch ownership is held while waiting.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T14:09:00+02:00
status: waiting
project_lane: otheryn-content
execution_mode: chat-github
base_main_at_handover_start: b325dc8f713dd7412e38cd27e8fb353020541c4f
proven:
  - technical Atlas implementation and full-world certification are already DONE/VERIFIED
  - PR 401 merged the preview/storage/codec handover and bounded codec evidence
  - PR 402 merged the canonical product-readiness backlog ATLAS-PR-001..013
  - local preview must remain outside Oteryn Platform for the current phase
  - owner requires Tile ID hover inspector/filter with factual ground and visible stack server IDs
  - current browser architecture is bounded viewport/chunk loading rather than whole-world loading
  - WebP lossless showed 42.77% aggregate savings with exact RGBA on the bounded 24-image direction corpus only
unknown:
  - exact PNG-vs-WebP lossless saving on real generated build/full-map-atlas/tiles/**
  - browser/runtime impact of any future WebP migration
  - final owner format decision
  - final DSM preview hostname/path and live Synology configuration
constraints:
  - do not treat the 24-image codec result as full-atlas proof
  - do not implement WebP migration until the real generated-chunk result is reviewed and owner authorizes the migration
  - do not integrate the current preview with Oteryn Platform
  - do not require SSH tunnels for the Synology preview
  - do not invent tile IDs from rendered pixels or sprite appearance
  - preserve UNKNOWN/UNRESOLVED evidence rather than guessing
blockers:
  - waiting for owner-supplied local Codex benchmark report/artifacts
next_action: receive the local Codex real-chunk benchmark report and visual samples from the owner, verify them against the recorded benchmark contract, update ATLAS-PR-010/011 evidence, and present the measured format recommendation before any migration
```

## Closeout rule

This task is not complete merely when the codec decision is made. Continue through the applicable REQUIRED product-readiness inventory unless the owner explicitly narrows or supersedes scope. Preserve one exact `next_action` whenever the task remains incomplete.
