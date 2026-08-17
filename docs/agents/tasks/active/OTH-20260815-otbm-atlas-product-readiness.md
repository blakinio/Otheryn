---
task_id: OTH-20260815-otbm-atlas-product-readiness
status: waiting
owner: none
branch: none
base_branch: main
created: "2026-08-15T14:09:00+02:00"
updated: "2026-08-17T10:45:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "415,416,431,433"
ownership_released: true
owned_paths: []
---

# OTBM Atlas product-readiness continuation

## Goal

Move the technically certified OTBM Atlas to a real private Synology Container Manager preview reachable through DSM Reverse Proxy in a normal browser, then collect real Chromium E2E and production-like browser performance evidence.

Canonical backlog: `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md`.
Private Synology runbook: `deploy/otbm-atlas-synology/README.md`.
Verified SMB publication helper: `deploy/otbm-atlas-smb-transfer/README.md`.
Controlled-distribution guardrail: `deploy/otbm-atlas-controlled-beta/README.md`.

## Current repository state

- current implementation baseline: `845510abdc8ad0291e559586efd03addd17e13ea` (`feat(atlas): add verified Synology SMB promotion (#433)`);
- PR #415 — MERGED — private Synology preview implementation;
- PR #416 — MERGED — DSM runtime handoff;
- PR #431 — MERGED as `76da15d02598d38fb00852df866a14ce094c37b9` — fail-closed controlled-distribution/publication gate;
- PR #433 — MERGED as `845510abdc8ad0291e559586efd03addd17e13ea` — verified Windows-to-Synology SMB staging/promotion helper;
- no Windows/macOS platform builds are part of canonical CI; PowerShell deployment-contract validation runs on `ubuntu-latest`;
- no Internet-facing Atlas route has been activated;
- no generated Atlas corpus has been committed or uploaded as a repository/Actions/object-storage publication artifact.

## Technical Atlas baseline

- Atlas/schema version `3`;
- chunk size `128`;
- certified Z0..Z15;
- exactly `3494` populated detail chunks;
- zero certified missing sprites;
- canonical map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`;
- full-world certification and incremental production entry are already complete;
- PNG→WebP migration remains `NOT_AUTHORIZED` pending browser evidence/owner decision.

## Synology deployment contract — already established

```text
project: otheryn-atlas-preview
image: ghcr.io/nginx/nginx-unprivileged:1.31.3-alpine3.24-slim@sha256:22f839c5fb4007dc24d203a170a9e03fc185d660bfefc34ac6823a7aef085cbc
container HTTP: 8080
host bind: 127.0.0.1
host port: 8095
data path: /volume1/docker/otheryn/atlas/current
project path: /volume1/docker/otheryn/atlas/project
DSM reverse-proxy destination: HTTP 127.0.0.1:8095 /
health: /healthz plus container healthcheck
```

The project files are already staged on the NAS under `/volume1/docker/otheryn/atlas/project` and were previously hash-verified. The verified Synology SMB share is:

```text
host: Synology
share: docker
share path: /volume1/docker
Windows Atlas root: \\Synology\docker\otheryn\atlas
Windows current target: \\Synology\docker\otheryn\atlas\current
```

The share is not browseable in Windows Network discovery, so use the direct UNC path.

## Recovered policy violation remains closed

A historical attempt to build a new full Atlas on Synology was canceled before verification/promotion/runtime start. Its partial `/work/_atlas_build` residue was removed. No partial output was promoted to `current`.

**Do not start another full-world build on Synology.** Deployment must reuse the already-generated desktop corpus.

## New fail-closed publication boundary — merged

PR #431 added a publication gate that accepts the real generated Atlas directory and recomputes a fresh full `deployment_preflight` in-process with:

```text
verify_chunks=true
require_environment_animations=true
```

The gate requires `FULL_RUNTIME_READY`, canonical Atlas identity, current viewer/runtime layers and successful independent verification.

Publication modes are explicit:

- `private-local` — allowed without ATLAS-PR-009 only after the real corpus passes the full gate;
- `internet-authenticated` — blocked without exact-scope ATLAS-PR-009 approval;
- `internet-public` — independently blocked without exact-scope ATLAS-PR-009 approval.

The committed approval template is intentionally `approved: false`.

No public DNS, Cloudflare route, Internet port-forward, GitHub Pages, R2/CDN or object-storage publication is authorized by this task state.

## New verified SMB transfer boundary — merged

PR #433 added `deploy/otbm-atlas-smb-transfer/publish.ps1`.

For the first physical publication it performs, in order:

1. fresh full publication gate against the existing desktop `build/full-map-atlas`;
2. copy over SMB only into a unique `incoming-<timestamp>-<id>` directory;
3. bounded `robocopy` with `/MIR` restricted to disposable staging, never directly against `current`;
4. fresh full publication gate again against the copied UNC staging corpus;
5. current-state drift check immediately before promotion;
6. same-share rename to `current` only after all verification passes;
7. local evidence receipt outside the Atlas corpus.

An existing `current` is fail-closed by default. Replacement requires explicit `-AllowReplaceCurrent`; even then, initial presence plus `manifest.json` SHA-256 must remain stable for the duration of the long transfer. A newly appearing/disappearing/changed `current` blocks promotion.

Final #433 validation on head `e0d848235469b45e3f8a361d76348f9983bf44fa`:

- `OTBM Atlas SMB Transfer` run `32011599746` — SUCCESS;
- `CI` run `32011599883` — SUCCESS;
- `Required` run `32011599742` — SUCCESS;
- `autofix.ci` run `32011599756` — SUCCESS;
- fresh audit: 1 material race found, 1 remediated, 0 open material findings;
- implementation branch deleted after merge.

## Runtime requirements

| Requirement | State | Completion gate |
|---|---|---|
| ATLAS-PR-002 | PARTIAL | Execute the merged SMB helper from the Windows machine holding the existing desktop corpus, then import/start the already-staged DSM project and create the private DSM Reverse Proxy rule. |
| ATLAS-PR-003 | NOT_RUN | Real Chromium must run against the resulting actual private DSM URL. |
| ATLAS-PR-004 | NOT_RUN | Cold/warm/navigation measurements must be collected against the same deployed URL. |
| ATLAS-PR-011 | WAITING | Owner format decision only after browser evidence; WebP migration remains unauthorized. |
| ATLAS-PR-001 | PENDING | Only owner visual/interaction review may accept the viewer or record defects. |
| ATLAS-PR-009 | WAITING | Explicit review/record required before any Internet-facing release, including authenticated beta. |

## Exact next owner-side action

The GitHub connector cannot read the owner's Windows desktop filesystem or execute a 10+ GB transfer over the owner's LAN. Everything before that physical boundary is now merged and validated.

From the repository root on the Windows machine that already contains `build/full-map-atlas`, run exactly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File deploy\otbm-atlas-smb-transfer\publish.ps1
```

The command must finish with `Promotion complete` and report:

```text
Current Atlas: \\Synology\docker\otheryn\atlas\current
Manifest SHA-256: <value>
Evidence: <local build/atlas-deployment-evidence/... directory>
```

Do **not** use `-AllowReplaceCurrent` for the first publication. If the command refuses because `current` already exists, preserve that evidence and investigate rather than forcing replacement.

## After successful SMB publication — reserved DSM owner actions

Only after the helper succeeds:

1. DSM Container Manager → Project → import/start `otheryn-atlas-preview` from `/volume1/docker/otheryn/atlas/project/docker-compose.yml` and confirm `healthy`;
2. DSM Control Panel → Login Portal → Advanced → Reverse Proxy → create the **private** rule whose destination is `HTTP 127.0.0.1:8095 /`;
3. open the resulting private URL in a normal browser and provide only that URL, without credentials/tokens;
4. run `tools.otbm_atlas.deployed_browser_probe` against that exact URL to collect ATLAS-PR-003/004 evidence;
5. perform owner visual/interaction review for ATLAS-PR-001;
6. only after browser evidence revisit format/cache/storage decisions;
7. do not activate any Internet-facing route until ATLAS-PR-009 is explicitly reviewed and recorded.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-17T10:45:00+02:00
head: 845510abdc8ad0291e559586efd03addd17e13ea
status: waiting
phase: owner-windows-smb-transfer-then-dsm-runtime
execution_mode: chat-github
project_lane: otheryn-content
proven:
  - technical Atlas production pipeline and full-world 3494-chunk certification are complete
  - private Synology project files are already staged and verified
  - Synology SMB target is \\Synology\docker\otheryn\atlas\current
  - no reusable full Atlas corpus exists on Synology
  - forbidden NAS full-build attempt was canceled and residue removed
  - PR 431 fail-closed real-corpus publication gate is merged
  - PR 433 verified staged SMB publication helper is merged
  - PR 433 focused workflow, CI, Required and autofix all passed on exact final head
  - Windows/macOS platform builds remain disabled
  - no Internet exposure or public corpus publication has been activated
unknown:
  - actual result of the owner-side merged SMB publication helper against the existing desktop corpus
  - final DSM reverse-proxy source URL
  - deployed Chromium E2E/performance evidence
  - owner viewer acceptance
  - ATLAS-PR-009 Internet-facing redistribution decision
blockers:
  - coordinator cannot access the owner's Windows desktop/LAN to execute the physical 10+ GB SMB transfer
next_action: owner runs `powershell -NoProfile -ExecutionPolicy Bypass -File deploy\\otbm-atlas-smb-transfer\\publish.ps1` from the repository root on the Windows machine containing build/full-map-atlas and returns the terminal result; then verify DSM runtime and run real-browser E2E/performance
```

## Closeout rule

The product-readiness task remains incomplete until the real Synology/DSM/browser path is proven. Keep exactly one executable `next_action` while incomplete.
