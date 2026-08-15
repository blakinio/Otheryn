---
task_id: OTH-20260815-otbm-atlas-product-readiness
status: in_progress
owner: chat-github
branch: blakinio/atlas-synology-preview
base_branch: main
created: "2026-08-15T14:09:00+02:00"
updated: "2026-08-15T23:35:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: ""
ownership_released: false
owned_paths:
  - docker/otbm-atlas-synology/
  - .github/workflows/otbm-atlas-synology-preview.yml
  - tools/otbm_atlas/preview_corpus_check.py
  - tools/otbm_atlas/tests/test_preview_corpus_check.py
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md
---

# OTBM Atlas product-readiness continuation

## Goal

Move the technically verified canonical OTBM Atlas to a real private browser preview served by a Synology Container Manager container through DSM Reverse Proxy, then collect real browser E2E and performance evidence before any PNG-to-WebP product decision.

The canonical product backlog remains `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md`.

## Owner decision for this continuation

The owner superseded the previous codec-first waiting state for this invocation. The required preview architecture is now:

```text
generated static Atlas
-> Synology persistent folder
-> Synology Container Manager static HTTP container
-> local host TCP port
-> DSM Reverse Proxy
-> normal browser
```

Constraints: private/local preview; no Oteryn Platform integration; no SSH, SSH tunnel, SCP, `docker exec`, privileged container, Docker socket, public DNS/Cloudflare exposure or full-world rebuild on Synology. Atlas generation remains a desktop responsibility. The owner creates the DSM reverse-proxy rule in DSM UI.

## Verified baseline

- Live base for this branch was `main` at `475196ddba675e2f7f0dadcdb3fdb445db79bba2`, the merge of PR #414.
- Atlas PRs #410, #412, #413 and #414 are merged.
- No currently open PR owns the Atlas preview/product-readiness paths; open PRs observed at startup were #369, #339, #341 and #347 in unrelated lanes.
- Technical Atlas rendering remains DONE/VERIFIED.
- Canonical current-v3 detail corpus identity remains schema/Atlas v3, chunk size 128, map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`, Z0..Z15 and 3494 chunks.
- The preserved desktop-v3 manifest observed asset worktree SHA-256 `4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2`; PR #412 proved the only difference from canonical Git asset SHA-256 `4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7` is CRLF materialization of one NON_RENDER_INPUT proficiencies JSON. Renderer inputs are canonical and no detail rerender is required.
- All 3494 current-v3 detail manifest paths/checksums were previously verified.
- `ATLAS-PR-010` remains VERIFIED: deterministic 240-chunk sample across Z0..Z15 measured PNG `629930622` bytes versus lossless WebP `320113728` bytes, saving `49.18270094829586%`, with decoded RGBA equality for 240/240.
- Complete current-v3 detail PNG bytes remain `10995096999`; full-corpus WebP size remains estimated rather than measured.
- PNG-to-WebP migration is not authorized. Browser/runtime impact remains UNKNOWN until the real preview exists.

## Environment-animation dependency

The preserved desktop canonical-v3 run completed all 3494 detail chunks, both overview levels and the v3 manifest, then was interrupted during `enrich_environment_animations` after bounded long-running attempts. The active dependency is `docs/agents/tasks/active/OTH-20260815-atlas-environment-animation-export-performance.md`.

The current builder writes final factual enrichment and `write_viewer(output)` only after environment-animation enrichment. The environment exporter writes `data/environment-animations/index.json` only after processing all shards/assets and currently rebuilds its output tree from scratch. Therefore the exact browser-completeness state of the preserved desktop directory must be measured rather than inferred. Do not call `ATLAS-PR-003` complete while the environment-animation final artifact is absent.

## Current implementation

Branch `blakinio/atlas-synology-preview` adds a small static deployment package under `docker/otbm-atlas-synology/`:

- pinned unprivileged nginx static-server image;
- read-only generated Atlas bind mount;
- read-only container root filesystem;
- all Linux capabilities dropped and `no-new-privileges` enabled;
- no database/backend/renderer/source assets/Docker socket/privileged mode;
- loopback-only host publication by default;
- deterministic `/__health` endpoint;
- useful nginx stdout/stderr logs;
- explicit MIME handling through nginx's standard MIME table, including HTML/JS/CSS/JSON/PNG/WebP;
- `unless-stopped` restart policy;
- DSM Project/Reverse Proxy runbook with recommended, explicitly unverified NAS path/port values.

The branch also adds `tools/otbm_atlas/preview_corpus_check.py`, a read-only preflight which separates `browserCoreReady` from `environmentAnimations.ready`/`fullBrowserReady`. The final checksum pass hashes the manifest-referenced detail, overview and low-overview images; it also verifies viewer/factual/spatial files, creature sprite/animation references and environment-animation shard/assets references without rebuilding the Atlas.

## Product requirement state

### ATLAS-PR-002 — Synology container preview

`PARTIAL`

Repository deployment artifacts are being implemented. Completion still requires observable evidence that the container is running on the owner's Synology, serving the verified corpus read-only, survives restart and is reachable through DSM Reverse Proxy from a normal browser without an SSH tunnel.

### ATLAS-PR-003 — real browser E2E

`NOT_RUN`

No real DSM preview URL is available in this execution environment. Chromium E2E must use the same private DSM URL as the owner. Environment animation remains an explicit dependency until the desktop corpus preflight proves `environmentAnimations.ready: true`.

### ATLAS-PR-004 — production-like browser performance

`NOT_RUN`

Cold/warm/navigation browser measurements remain UNKNOWN until the real DSM URL exists. No targets will be invented.

### ATLAS-PR-011 — PNG/WebP decision

`WAITING`

No migration is authorized. The existing storage/decode benchmark is evidence only; the owner decision waits for real browser cold/warm/interaction measurements.

### ATLAS-PR-001 — owner visual review

`PENDING`

Only the owner can accept the resulting browser UI or record exact UX defects.

## Synology recommendations requiring runtime confirmation

Repository Docker quickstart conventions already use host ports 8080 and 8088, so the Atlas project recommends host port `18088`. Repository history also contains a Synology operational path below `/volume1/docker/oteryn/`, so the preview recommends:

```text
project: /volume1/docker/oteryn/atlas-project
atlas data: /volume1/docker/oteryn/atlas/current
host bind: 127.0.0.1:18088 -> container 8080
DSM reverse-proxy destination: HTTP / 127.0.0.1 / 18088 / /
```

These are `RECOMMENDED`, not `VERIFIED_EXISTING`. Actual volume/path existence, port availability, DSM version/menu wording and final private source URL remain UNKNOWN until owner DSM interaction.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T23:35:00+02:00
base_main: 475196ddba675e2f7f0dadcdb3fdb445db79bba2
branch: blakinio/atlas-synology-preview
pr: pending
status: in_progress
project_lane: otheryn-content
execution_mode: chat-github
owned_paths:
  - docker/otbm-atlas-synology/
  - .github/workflows/otbm-atlas-synology-preview.yml
  - tools/otbm_atlas/preview_corpus_check.py
  - tools/otbm_atlas/tests/test_preview_corpus_check.py
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md
proven:
  - technical Atlas rendering and canonical full-world certification remain DONE/VERIFIED
  - current-v3 detail corpus is 3494 chunks across Z0-Z15 with previously verified manifest paths/checksums
  - map SHA is 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - ATLAS-PR-010 is VERIFIED and WebP migration is not authorized
  - preserved desktop run was interrupted during environment-animation enrichment after detail/overview/manifest generation
  - build_atlas writes final factual enrichment and viewer files after environment-animation enrichment
  - final environment-animation runtime index is data/environment-animations/index.json
  - deployment branch is based on main 475196ddba675e2f7f0dadcdb3fdb445db79bba2
  - deployment design uses a small server image plus read-only persistent Atlas mount rather than baking Atlas data into the image
derived:
  - the preserved desktop corpus may support a useful partial preview but cannot be called full-browser-ready until read-only preflight proves final viewer/factual/creature/environment artifacts
unknown:
  - current desktop corpus preflight result for browserCoreReady and environmentAnimations.ready
  - owner NAS existence of the recommended Atlas paths
  - availability of recommended host port 18088 on the NAS
  - exact DSM version/menu path
  - final private DSM browser URL
  - real Chromium E2E and production-like browser performance
conflicts: []
validation:
  - focused/component CI: pending PR execution
blockers: []
next_action: open the Synology preview PR from blakinio/atlas-synology-preview and run/fix all exact-head focused and repository CI before any owner DSM action
```

## Closeout rule

Do not mark runtime requirements complete from committed configuration or CI alone. `ATLAS-PR-002` requires real Synology + DSM browser reachability, `ATLAS-PR-003` requires real Chromium against that DSM URL, `ATLAS-PR-004` requires measured browser evidence, and `ATLAS-PR-011` remains an explicit owner format decision.
