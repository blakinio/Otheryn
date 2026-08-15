# OTBM Atlas product-readiness backlog — 2026-08-15

## Purpose

This document preserves the remaining product-readiness work for OTBM Atlas after the canonical technical atlas closeout.

It does **not** reopen or weaken `docs/maps/otbm-atlas-completion-audit-20260814.md`. The existing parser/render/chunk/factual-layer/creature-animation implementation remains technically DONE/VERIFIED. This backlog tracks owner-facing preview, UX acceptance, operational hardening, measured storage optimization and new inspection affordances required before the owner can reasonably call the Atlas a 10/10 product.

## Status model

- `REQUIRED` — needed before product-level 10/10 closeout.
- `INVESTIGATE` — measure or validate before deciding whether implementation is required.
- `OPTIONAL` — useful improvement that is not currently a product-completion blocker.
- `DONE` — already proven by repository evidence.

## Current baseline

- repository: `blakinio/Otheryn`
- project lane: `otheryn-content`
- technical Atlas closeout: DONE/VERIFIED
- certified canonical world: Z0..Z15, 3494 chunks
- current product review state: owner/human subjective UX parity review pending
- current preview direction: local Synology/Container Manager + DSM reverse proxy, outside Oteryn Platform

## Product-readiness inventory

| ID | Priority | Status | Work | Completion evidence |
|---|---|---|---|---|
| ATLAS-PR-001 | P0 | REQUIRED | Owner visual/interaction acceptance against the real browser viewer. | Owner accepts the resulting UI/interaction or records exact defects to fix. |
| ATLAS-PR-002 | P0 | REQUIRED | Temporary local Synology browser preview, without Oteryn Platform integration. | Reachable through the existing DSM reverse-proxy pattern from the intended local client; no unintended public/Platform exposure. |
| ATLAS-PR-003 | P0 | REQUIRED | Real deployed-preview E2E. | Deep-link X/Y/Z, pan/zoom, floors, search, details, factual layers, render-mode switching and creature/environment animation work through the actual served preview. |
| ATLAS-PR-004 | P1 | REQUIRED | Production-like performance measurement. | Measured cold/warm transfer, request counts, chunk-load timings, browser memory/cache behaviour and large navigation jumps; budgets are based on measurements rather than invented targets. |
| ATLAS-PR-005 | P1 | REQUIRED | Mobile/touch/responsive/accessibility acceptance. | Touch pan/zoom, small viewport, details surface, keyboard/focus behaviour, readable controls and relevant reduced-motion/accessibility checks are verified. |
| ATLAS-PR-006 | P1 | REQUIRED | Triage remaining unresolved/ambiguous canonical creature records. | Every unresolved record is classified as resolver defect, canonical-source gap or intentionally unresolved evidence state; no silent guessing. |
| ATLAS-PR-007 | P1 | REQUIRED | Repeatable Atlas release/update pipeline. | Source fingerprint change -> build/verify -> full-world certification when required -> preview/staging -> E2E -> atomic promotion/rollback path is documented and reproducible. |
| ATLAS-PR-008 | P1 | REQUIRED | Serving hardening and operator runbook. | Cache headers, compression policy, error/404 behaviour, health/availability checks, rollback and rebuild/publish instructions are documented and verified for the chosen hosting model. |
| ATLAS-PR-009 | P1 | REQUIRED | Public redistribution/legal review before any Internet-facing release of proprietary Tibia-derived imagery/assets. | Exact redistribution/hosting boundary is reviewed and recorded before public release. This does not block local private preview. |
| ATLAS-PR-010 | P1 | INVESTIGATE | Real generated-detail-chunk PNG vs WebP-lossless benchmark. | Existing `build/full-map-atlas/tiles/**` corpus is measured; at least 200 real chunks or preferably all available chunks; RGBA exactness and A/B samples proven before migration. |
| ATLAS-PR-011 | P1 | INVESTIGATE | Decide whether detail chunk format should remain PNG or migrate to WebP lossless. | Owner reviews measured storage/decode results and representative visual A/B samples; any migration becomes a separate implementation task. |
| ATLAS-PR-012 | P2 | OPTIONAL | Server-side lazy/on-demand detail rendering with persistent cache. | Implement only if measured storage/deployment/operational needs justify the added backend complexity; static full-build path remains supported. |
| ATLAS-PR-013 | P1 | REQUIRED | Tile ID hover inspector/filter. | See dedicated contract below. |

## Tile ID hover inspector — owner requirement

Owner request: add a first-class toggle/filter so that, when enabled, moving the pointer over a map tile shows the authoritative ID information for that tile position.

### Data-model clarification

OTBM map positions are not represented by one universal standalone "tile ID". A map position may contain a ground item plus zero or more visible stack items, each with a canonical server ID and possibly other factual metadata.

Therefore the UI must not invent a single opaque identifier when the canonical data contains several IDs.

### Required user behaviour

Add a first-class toggle in the Atlas controls, working name:

`Tile IDs` or `Tile inspector`

When disabled:

- no per-pointer tile-ID inspection work should be performed beyond existing coordinate handling;
- existing map interaction and tooltips remain unchanged.

When enabled and the pointer is over a valid map position:

- resolve the exact raw OTBM X/Y/Z map position under the pointer;
- show at minimum the canonical ground `serverId` when a ground item exists;
- expose canonical server IDs for visible top-level stack items on that position rather than collapsing them into an invented single ID;
- distinguish clearly between `ground serverId` and stack-item `serverId` values;
- retain X/Y/Z in the inspection tooltip/details;
- include ActionID/UniqueID only when those values actually exist and are already supported by factual evidence;
- never infer an ID from pixels, sprite appearance or external data;
- preserve explicit UNKNOWN/unavailable states when canonical data does not expose a value.

### Interaction constraints

- inspection must use the factual map/chunk data corresponding to the currently displayed canonical map position;
- it must remain viewport/chunk bounded and must not require loading the complete world into the browser;
- hovering must not mutate map state, selected marker, URL state or factual overlays;
- rapid pointer movement must not trigger unbounded network requests or memory growth;
- the feature must work at detail zoom; behaviour at distant overview zoom must be explicitly defined rather than returning misleading tile IDs for visually aggregated pixels;
- pointer-to-map coordinate conversion must remain correct across pan, zoom, floor switching, render mode and high-DPI displays;
- touch devices should receive a deliberate tap/inspect equivalent or the feature should be explicitly desktop-only until a later mobile interaction is accepted.

### Acceptance tests

At minimum verify on real canonical data:

1. toggle OFF -> no Tile ID tooltip/inspector result;
2. toggle ON -> hover a known ground tile -> exact expected X/Y/Z and ground server ID;
3. hover a position with multiple visible stack items -> ground and each top-level stack server ID remain distinguishable;
4. hover a position with AID/UID -> those factual values are shown only when present;
5. zoom/pan and hover the same logical position -> identical canonical IDs;
6. switch floors -> IDs come from the selected Z only;
7. switch Auto/Detailed/Performance -> logical tile identity does not change;
8. rapid hover across chunk boundaries -> bounded loading/cache behaviour, no stale ID from a prior tile;
9. unsupported/empty position -> explicit empty/unavailable state, not a guessed value;
10. real Chromium E2E against generated canonical Atlas data.

### Open product choice

The owner used the singular phrase "tile ID". For implementation, the recommended presentation is:

- primary line: `Ground ID: <serverId>`;
- secondary stack list: `Items: <serverId>, ...` when present.

If the owner later wants only the ground ID, that is a presentation narrowing; the underlying factual inspector should still avoid treating the whole OTBM map position as if it had one fabricated ID.

## Storage/codec decision gate

Do not migrate Atlas imagery formats based only on the bounded 24-image codec-direction experiment. The stored experiment showed WebP lossless as promising and RGBA-exact for that corpus, but final detail-map savings are still UNKNOWN until the real generated-chunk benchmark runs.

Use:

- `docs/maps/otbm-atlas-preview-codec-handover-20260815.md`
- `docs/maps/otbm-atlas-real-chunk-codec-benchmark-prompt-20260815.md`
- `docs/maps/evidence/otbm-atlas-codec-direction-20260815/`

as the durable context for that decision.

## Product closeout rule

Do not label the entire OTBM Atlas product "10/10 complete" solely because the technical rendering contract is DONE. Product closeout requires the applicable REQUIRED items above to be verified or explicitly superseded by an owner decision, with real preview/browser evidence for user-facing behaviour.
