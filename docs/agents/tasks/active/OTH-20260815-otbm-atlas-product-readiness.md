---
task_id: OTH-20260815-otbm-atlas-product-readiness
status: waiting
owner: none
branch: none
base_branch: main
created: 2026-08-15T14:09:00+02:00
updated: 2026-08-15T14:29:00+02:00
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "406"
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
- PR #404 merged the owner's local Codex benchmark report, machine-readable results and reproduction script.
- The reported 240-chunk sample spans Z0..Z15 and measures existing PNG `626957721` bytes versus lossless WebP `318561438` bytes: `308396283` bytes / `49.18932691475698%` aggregate saving, with decoded RGBA equality for all `240/240` tested chunks.
- The reported local detail directory contains 3494 PNG chunks totaling `10996609082` bytes. The reported `5587451091`-byte full-detail WebP value is explicitly ESTIMATED from the sample ratio, not measured by converting all chunks.
- Reported Pillow/libwebp decode timings are local codec measurements only, not browser benchmarks.
- PR #405 merged the benchmark repository-root correction and records the measured local corpus manifest identity.
- That manifest identifies the measured local corpus as schema/Atlas version 2 with assets SHA-256 `4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2`.
- The current canonical Atlas implementation is version 3, and the certified full-world release evidence is Atlas version 3 with assets SHA-256 `4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7` and the same canonical map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`.
- Therefore the supplied benchmark is useful codec-direction evidence on real generated Atlas detail chunks, but it is not yet a verified benchmark of the current certified Atlas v3 detail corpus.
- The 24 PNG/WebP A/B pairs and `comparison.html` are reported to exist locally but are not durable GitHub artifacts, so they have not been independently inspected in this coordinator session.

## Waiting reason

`ATLAS-PR-010` cannot be marked VERIFIED under the owner's benchmark contract because the measured corpus is Atlas v2 rather than the current certified Atlas v3 corpus. `ATLAS-PR-011` therefore remains INCONCLUSIVE and no PNG-to-WebP migration is authorized.

No worker/branch ownership is held while waiting.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T14:29:00+02:00
status: waiting
project_lane: otheryn-content
execution_mode: chat-github
base_main_at_verification: 596c37c832a75999f4049b4b16a79ed47b1dbf9b
related_prs:
  - 404
  - 405
  - 406
proven:
  - technical Atlas implementation and full-world certification are already DONE/VERIFIED
  - PR 404 merged a deterministic 240-detail-chunk benchmark spanning Z0..Z15
  - sample existing PNG bytes are 626957721
  - sample WebP-lossless bytes are 318561438
  - sample aggregate saving is 308396283 bytes / 49.18932691475698 percent
  - all 240 tested WebP decodes are reported RGBA byte-identical to the original PNG decode
  - WebP parameters are lossless=True, method=6, exact=True
  - per-floor sample counts sum to 240 and per-floor byte totals sum exactly to the aggregate PNG/WebP totals
  - the reported full-detail WebP size 5587451091 bytes is ESTIMATED, not measured
  - local PNG/WebP decode timings are not browser-performance evidence
  - PR 405 corrected the benchmark repository-root calculation
  - PR 405 records the measured local manifest as Atlas version 2 with map SHA 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034 and assets SHA 4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2
  - current canonical Atlas code uses ATLAS_VERSION 3
  - certified full-world evidence uses Atlas version 3 with assets SHA 4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7
inferences:
  - WebP lossless is strongly promising for Atlas detail imagery, but the exact current-v3 saving remains unproven
unknown:
  - exact PNG-vs-WebP lossless saving on the current certified Atlas v3 build/full-map-atlas/tiles/** corpus
  - independent visual inspection of the locally generated 24 PNG/WebP A/B pairs and comparison.html
  - browser/runtime impact of any future WebP migration
  - final owner format decision
  - final DSM preview hostname/path and live Synology configuration
constraints:
  - do not treat the v2 240-chunk result or the earlier 24-image result as full current-v3 Atlas proof
  - do not implement WebP migration until the current canonical generated-chunk result is reviewed and owner authorizes the migration
  - do not integrate the current preview with Oteryn Platform
  - do not require SSH tunnels for the Synology preview
  - do not invent tile IDs from rendered pixels or sprite appearance
  - preserve UNKNOWN/UNRESOLVED evidence rather than guessing
blockers:
  - measured local benchmark corpus is Atlas v2 while the current certified canonical Atlas is v3
  - visual comparison artifacts are not available as durable GitHub artifacts for independent inspection
next_action: verify or generate a current canonical Atlas v3 full-map output on the desktop using --workers 8 only if a current v3 output is absent, rerun the lossless PNG-vs-WebP benchmark against that v3 detail corpus, and provide the 24 A/B samples plus comparison.html for owner review
```

## Closeout rule

This task is not complete merely when the codec decision is made. Continue through the applicable REQUIRED product-readiness inventory unless the owner explicitly narrows or supersedes scope. Preserve one exact `next_action` whenever the task remains incomplete.
