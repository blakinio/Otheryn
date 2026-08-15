---
task_id: OTH-20260815-otbm-atlas-product-readiness
status: waiting
owner: none
branch: none
base_branch: main
created: "2026-08-15T14:09:00+02:00"
updated: "2026-08-15T22:24:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "413"
ownership_released: true
owned_paths: []
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
- PR #404 merged the historical deterministic 240-chunk PNG-versus-lossless-WebP benchmark. That historical sample measured PNG `626957721` bytes versus WebP `318561438` bytes, saving `308396283` bytes (`49.18932691475698%`), with decoded RGBA equality for all `240/240` tested chunks.
- PR #405 corrected benchmark repository-root handling and made the historical corpus identity explicit; that earlier measured manifest was Atlas version 2.
- PR #412 merged the canonical asset-provenance repair. Canonical 6,031-file asset bytes fingerprint as `4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7`; the desktop build's `4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2` value was proven to come only from Windows CRLF materialization of one `NON_RENDER_INPUT` proficiencies JSON.
- The preserved current Atlas v3 desktop corpus contains exactly 3494 detail PNG chunks and all 3494 manifest paths/checksums validate. Renderer inputs were canonical, so no detail rerender is required.
- The verified current-v3 benchmark tested a deterministic 240-chunk sample spanning Z0..Z15. PNG files totalled `629930622` bytes and lossless WebP totalled `320113728` bytes, saving `309816894` bytes (`49.18270094829586%`), with decoded RGBA equality for all `240/240` chunks.
- The complete current-v3 detail PNG corpus totals `10995096999` bytes. Applying the measured sample ratio estimates `5587411323` WebP bytes and `5407685676` bytes saved (`49.1827009483575%`); this full-corpus WebP value remains `ESTIMATED`, not measured.
- `ATLAS-PR-010` is VERIFIED on current-v3 detail evidence.
- `ATLAS-PR-011` remains an owner product decision. PNG-to-WebP migration is not authorized yet because owner visual acceptance and browser/runtime impact remain unresolved.
- The 24 PNG/WebP A/B pairs and `comparison.html` passed local artifact-consistency validation; owner visual review remains pending.

## Waiting reason

`ATLAS-PR-010` is complete and VERIFIED. The task remains `waiting` because `ATLAS-PR-011` requires the owner's product-format decision after reviewing the local A/B comparison, and browser/runtime impact of a future WebP migration remains UNKNOWN. No PNG-to-WebP migration is authorized before that decision.

PR #412 is merged and the provenance correction is terminal. No worker/branch ownership is held while the owner-facing codec decision waits.

## Current-v3 desktop generation finding

The canonical 6,031-file Git/corpus bytes fingerprint as `4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7`. The desktop build observed `4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2` because Windows `core.autocrlf=true` converted only `vendor/map-analysis/tibia-client/15.25.bd5a04/assets/proficiencies-1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22.json` from LF to 27,089 CRLF sequences while Git still reported a clean worktree. The local representation was 489,542 bytes with SHA-256 `ee7b88c09fb8db21405bfd5cc69249e6f513f1b6da7a4553832ed958d941a379`; CRLF-to-LF normalization restores the 462,453-byte Git blob and SHA-256 `1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22`, and restores the complete tree fingerprint to `4c78aa44...`. The other 6,030 paths and bytes match the clean canonical corpus.

That file is `NON_RENDER_INPUT`: `AssetRenderer`, appearance decoding and sprite-sheet lookup do not consume it. Every renderer input therefore matched canonical bytes. The schema/Atlas-v3 manifest truthfully retains the worktree fingerprint observed during generation (`4d11c5be...`); it must not be rewritten to imply that the run observed `4c78aa44...`. Proven renderer-input equivalence plus 3,494/3,494 manifest-path and PNG-checksum validation preserves the generated detail corpus as valid v3 codec-benchmark evidence without rerendering.

The vendored corpus now has a narrow `-text` rule so new checkouts retain raw Git bytes. Existing Windows checkouts are not silently rewritten by an attribute-only update, so `python -m tools.otbm_atlas.repair_asset_checkout` provides an idempotent upgrade path: it replaces the known file atomically only when its complete delta from the Git blob is CRLF-to-LF and refuses every other content difference.

The desktop canonical-v3 build produced all 3,494 detail chunks, both overview levels and a schema/Atlas-v3 manifest before spending more than the bounded execution budget in environment-animation enrichment. That phase created hundreds of thousands of small files, remained CPU-active, and did not resume efficiently after interruption. The performance/resume defect is preserved separately in `OTH-20260815-atlas-environment-animation-export-performance`; it does not block benchmarking the already-complete detail PNG corpus because environment-animation assets are excluded from `ATLAS-PR-010`.

The verified current-v3 benchmark tested a deterministic 240-chunk sample spanning Z0..Z15. Original generated PNG files totalled `629930622` bytes and genuine lossless WebP totalled `320113728` bytes, saving `309816894` bytes (`49.18270094829586%`) with decoded RGBA equality for all `240/240` chunks. The complete 3,494-detail-PNG corpus totals `10995096999` bytes; applying the measured aggregate sample ratio estimates `5587411323` WebP bytes and `5407685676` bytes saved (`49.1827009483575%`). This full-corpus WebP value remains `ESTIMATED`, not measured. Browser performance remains `UNKNOWN`; local median decode time was `18.05625 ms` for PNG and `46.60915 ms` for WebP. The required report, JSON, CSV, local comparison page and 24 A/B pairs were generated under `build/otbm-codec-benchmark/`, validated for totals, hashes, RGBA equality and HTML references, and remain intentionally uncommitted local artifacts.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T22:24:00+02:00
head: d231cac122ff40a5c1c7f0e2d176327df7e05105
head_scope: latest committed checkpoint evidence before the PR-link update on the documentation-only follow-up
branch: none
pr: 413
status: waiting
project_lane: otheryn-content
execution_mode: chat-github
base_main_at_verification: 28a33496f33b252556ac0efdcde97ba9e22da215
context_routes:
  - docs/maps/otbm-atlas-product-readiness-backlog-20260815.md
owned_paths: []
proven:
  - technical Atlas implementation and full-world certification are already DONE/VERIFIED
  - PR 412 is merged as 28a33496f33b252556ac0efdcde97ba9e22da215
  - canonical Git and clean-corpus bytes contain 6031 assets and fingerprint as 4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7
  - 4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2 is the observed Windows worktree-byte fingerprint caused only by core.autocrlf converting the proficiencies JSON to CRLF
  - CRLF-to-LF restores the canonical proficiencies file SHA and complete asset-tree SHA; all other 6030 assets match canonical bytes
  - the proficiencies JSON is NON_RENDER_INPUT and every AssetRenderer appearance and sprite input is canonical
  - the current-v3 desktop corpus manifest is schema and Atlas version 3 with chunk size 128, 3494 detail chunks, map SHA 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034 and observed worktree assets SHA 4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2
  - every current-v3 detail path and original PNG checksum matches the manifest
  - the verified current-v3 sample contains 240 deterministic chunks spanning Z0 through Z15
  - current-v3 sample PNG/WebP bytes are 629930622 / 320113728, saving 309816894 bytes / 49.18270094829586 percent
  - WebP used lossless=True, method=6 and exact=True; all 240 decodes are RGBA byte-identical to the original PNG decodes
  - the complete current-v3 detail PNG corpus contains 3494 chunks totalling 10995096999 bytes
  - estimated complete current-v3 detail WebP size is 5587411323 bytes; it is ESTIMATED rather than measured
  - 24 local PNG/WebP A/B pairs and comparison.html passed file, hash, metadata and reference validation
  - ATLAS-PR-010 has verified current-v3 evidence
  - the environment-animation exporter performance and resume defect is preserved in OTH-20260815-atlas-environment-animation-export-performance
derived:
  - WebP lossless is strongly promising for Atlas v3 detail storage, subject to owner review and a separate implementation decision
  - ATLAS-PR-011 remains an owner product decision; no WebP migration is authorized yet
unknown:
  - exact measured WebP size for all 3494 current-v3 detail chunks
  - owner visual acceptance of the locally generated 24 PNG/WebP A/B pairs and comparison.html
  - browser/runtime impact of any future WebP migration
  - final owner format decision
  - final DSM preview hostname/path and live Synology configuration
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - the historical v2 codec result can close the current-v3 evidence gap
  - current Git/canonical asset bytes fingerprint as 4d11c5be; that value came from Windows worktree line-ending conversion
changed_paths:
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md
validation:
  - command: python tools/otbm_atlas/codec_benchmark.py
    result: PASS
    evidence: previously verified current-v3 run; 240 deterministic chunks across Z0-Z15 and 240/240 RGBA exact
  - command: independent artifact consistency checks
    result: PASS
    evidence: 3494/3494 manifest paths and PNG checksums; 240 CSV rows across Z0-Z15 all record RGBA equality; JSON, CSV and Markdown totals agree; 24 retained A/B pairs decode RGBA-identically and their metadata, hashes and 48 HTML references agree
  - command: PR 412 focused tests and exact-diff audit
    result: PASS
    evidence: canonical asset provenance repair, regression coverage and independent audit completed before merge
  - command: focused task-record consistency review
    result: PASS
    evidence: Current state, Waiting reason and Context checkpoint now agree that ATLAS-PR-010 is VERIFIED and ATLAS-PR-011 is the remaining owner decision
blockers:
  - owner review of the local visual A/B artifacts and product format decision remains pending
next_action: present the verified current-v3 benchmark and local comparison.html to the owner for visual review without implementing WebP migration
```

## Closeout rule

This task is not complete merely when the codec decision is made. Continue through the applicable REQUIRED product-readiness inventory unless the owner explicitly narrows or supersedes scope. Preserve one exact `next_action` whenever the task remains incomplete.
