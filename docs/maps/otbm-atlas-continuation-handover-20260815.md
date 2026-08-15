# OTBM Atlas continuation handover — 2026-08-15

## Purpose

This document is the durable handover for continuing OTBM Atlas product-readiness work in a fresh agent window without relying on chat history.

It supplements, but does not supersede:

- `docs/maps/otbm-atlas-completion-audit-20260814.md` — technical completion truth;
- `docs/maps/otbm-atlas-preview-codec-handover-20260815.md` — local preview/storage/codec discussion and bounded codec experiment;
- `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md` — canonical remaining product-readiness inventory;
- `docs/maps/otbm-atlas-real-chunk-codec-benchmark-prompt-20260815.md` — read-only local benchmark contract.

The active continuation task is:

`docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md`

## Repository state at handover creation

Repository: `blakinio/Otheryn`

`main` at handover start:

`b325dc8f713dd7412e38cd27e8fb353020541c4f`

Recent canonical Atlas documentation merges:

- PR #400 — final technical Atlas closeout;
- PR #401 — local preview/storage/codec handover and benchmark evidence;
- PR #402 — complete product-readiness backlog including Tile ID inspector requirement.

Future agents must verify live `main`, open PRs, active tasks, ownership and CI before acting. Do not assume the SHA above is still current.

## What is already technically complete

Do not reopen these merely because product work remains:

- canonical pinned CrystalServer `world.otbm` and Tibia assets;
- full-world preprocessing and bounded 128x128 chunk architecture;
- all populated floors `Z=0..15`;
- certified 3494 chunks;
- zero certified missing sprites in full-world validation;
- detailed canonical rendering and lightweight overview rendering;
- `Auto | Detailed | Performance` render modes;
- URL/local state for coordinates, zoom, render mode and layers;
- factual layers and conservative uncertainty semantics;
- NPC/monster canonical sprites;
- environment/item cyclic animation;
- NPC/monster canonical phase animation;
- real Chromium technical E2E and independent audit recorded by the final closeout.

Technical DONE does not mean the owner-facing product is yet 10/10.

## Remaining product-readiness work

The canonical list is `ATLAS-PR-001..013` in:

`docs/maps/otbm-atlas-product-readiness-backlog-20260815.md`

Important remaining areas include:

- owner visual/interaction acceptance;
- temporary local Synology browser preview;
- real deployed-preview E2E;
- performance measurement;
- mobile/touch/responsive/accessibility acceptance;
- triage of unresolved/ambiguous canonical creature records;
- repeatable release/update process;
- serving hardening/operator runbook;
- redistribution/legal review before any Internet-facing proprietary Tibia-derived imagery release;
- real generated-detail-chunk PNG vs WebP-lossless benchmark;
- owner decision on final detail image format;
- optional lazy rendering only if later justified;
- Tile ID hover inspector/filter.

## Current owner decisions

### Preview scope

For the current preview phase:

- run on Synology / Container Manager;
- use the normal Synology DSM reverse-proxy pattern;
- no SSH tunnel;
- no Oteryn Platform integration;
- no public Oteryn Platform route;
- this is initially a local/private browser preview for owner UX review.

Exact Synology hostname, paths and live reverse-proxy configuration are not recorded as facts here and must be inspected before deployment mutation.

### Build location

For a heavy desktop build, the owner selected:

`--workers 8`

The desktop should perform heavy generation rather than making Synology render the entire world unnecessarily.

### Chunking

Keep bounded, independently addressable map chunks as the default architecture.

Do not replace the world with one giant high-resolution image per floor merely so the browser can crop it visually; fewer source files do not automatically mean lower network transfer, lower decoded memory or better viewport loading.

### Lazy rendering

Server-side on-demand detail rendering with persistent cache was discussed, but it is **not currently selected or pre-authorized** as the storage solution.

First finish the real generated-chunk codec benchmark. If static lossless optimization is sufficient, keep the simpler static architecture.

### Codec direction

A bounded ChatGPT-side experiment on 24 real images from the supplied Tibia asset corpus measured:

- current Atlas-style PNG: `351021` bytes total;
- WebP lossless: `200886` bytes total;
- aggregate saving: `42.770945328057294%`;
- decoded RGBA equality: exact for every tested WebP image;
- Pillow optimized PNG: larger than current Atlas-style PNG on that corpus;
- AVIF Q100 4:4:4: not pixel-exact and not storage-competitive in that experiment.

This evidence is only a **codec-direction result**, not a full generated Atlas result.

Do not claim that an owner-observed ~6 GB Atlas becomes any exact smaller size until final `build/full-map-atlas/tiles/**` measurements exist.

## Local Codex benchmark currently pending

The owner reports that a local Codex worker is finishing the read-only benchmark defined by:

`docs/maps/otbm-atlas-real-chunk-codec-benchmark-prompt-20260815.md`

Expected evidence includes:

- actual generated detail chunk count and exact PNG storage;
- at least 200 real detail chunks benchmarked, preferably all if cheap;
- genuine lossless WebP encoding;
- byte-for-byte RGBA equality after WebP decode;
- saving distribution/percentiles;
- encode/decode measurements;
- at least 24 representative PNG/WebP visual A/B pairs;
- local `comparison.html`;
- no implementation changes or commits from the benchmark worker.

Until those results are supplied and verified:

- `ATLAS-PR-010` remains unresolved;
- `ATLAS-PR-011` remains unresolved;
- no WebP migration is authorized;
- no storage extrapolation from the 24-image sample is release evidence.

## Tile ID hover inspector requirement

Owner requires a first-class toggle/filter such as:

`Tile IDs` or `Tile inspector`

When enabled, pointer hover over a valid map position must expose factual canonical identity for that exact raw OTBM X/Y/Z position.

Important semantic rule: a map position does not have one universal opaque tile ID. It can contain ground plus visible top-level stack items.

Recommended presentation:

```text
X: 32345
Y: 32218
Z: 7
Ground ID: <ground serverId>
Items:
- <visible stack serverId>
- ...
AID: <only if present>
UID: <only if present>
```

Requirements:

- ground and stack IDs remain distinguishable;
- use canonical OTBM data, never rendered-pixel/sprite inference;
- preserve explicit empty/UNKNOWN states;
- remain viewport/chunk bounded;
- no unbounded request growth during rapid hover;
- coordinate mapping remains correct across zoom/pan/floor/render-mode/high-DPI;
- detail-zoom behavior must be reliable; distant overview behavior must be explicitly defined;
- include real Chromium E2E on canonical generated data.

The complete contract and test inventory is under `ATLAS-PR-013` in the product-readiness backlog.

## Next action in the fresh window

1. Verify live repository state and read the active continuation task.
2. If the owner has supplied the completed local Codex benchmark, treat the artifacts/report as evidence to verify rather than narrative truth.
3. Compare the result with the benchmark contract and classify `MEASURED`, `ESTIMATED`, `UNKNOWN` and any inconsistencies.
4. Update durable evidence for `ATLAS-PR-010` and recommend the PNG/WebP decision for `ATLAS-PR-011`.
5. Do not implement a format migration until the owner accepts the measured recommendation.
6. Continue the highest-priority safe product-readiness work after the codec decision, preserving the local Synology/no-Platform boundary unless the owner explicitly changes it.
7. Keep `ATLAS-PR-013` in scope as a required product feature.

## Source-of-truth order

Use this order:

1. current repository governance and live `main` / PR / CI / task state;
2. active task `OTH-20260815-otbm-atlas-product-readiness`;
3. `otbm-atlas-product-readiness-backlog-20260815.md`;
4. final technical closeout audit;
5. preview/codec handover and stored benchmark evidence;
6. owner-supplied fresh local Codex benchmark artifacts;
7. this handover;
8. chat history only as non-durable context.

Do not fill missing evidence by inference.
