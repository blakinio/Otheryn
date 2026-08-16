---
task_id: OTH-20260815-otbm-atlas-product-readiness
status: waiting
owner: none
branch: none
base_branch: main
created: "2026-08-15T14:09:00+02:00"
updated: "2026-08-16T10:31:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "415,416"
ownership_released: true
owned_paths: []
---

# OTBM Atlas product-readiness continuation

## Goal

Move the technically certified OTBM Atlas to a real private Synology Container Manager preview reachable through DSM Reverse Proxy in a normal browser, then collect real Chromium E2E and production-like browser performance evidence.

Canonical backlog: `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md`.
Deployment runbook: `deploy/otbm-atlas-synology/README.md`.

## Repository state

- `main` at this checkpoint: `39cb2ce4ff427e7c3760eb6112b45efc0c1f73b8` (`docs(atlas): hand off merged preview to DSM runtime (#416)`).
- PR #415 is MERGED. Final implementation head: `29ad7835e4c8e9cd98e48058a840e519afb02bc9`; merge commit: `b9f51b01352abcda4db8df54f3b575ddc7b2532b`.
- Exact-head CI `31932432026`: SUCCESS. Required `31932431889`: SUCCESS.
- All PR #415 review threads are resolved and audit findings `ATLAS-AUDIT-415-001` through `004` are remediated; open material findings: `0`.
- Focused static-container contract `31931712166 / 95127448119`: SUCCESS.

## Technical Atlas baseline

- schema / Atlas version `3`;
- chunk size `128`;
- certified `Z0..Z15`, exactly `3494` detail chunks, zero certified missing sprites;
- canonical map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`;
- accepted asset fingerprints:
  - `4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7` canonical Git bytes;
  - `4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2` previously validated Windows worktree representation whose sole byte delta was a NON_RENDER_INPUT CRLF materialization;
- ATLAS-PR-010 VERIFIED: deterministic 240-chunk Z0..Z15 sample, PNG `629930622` bytes vs lossless WebP `320113728` bytes, `240/240` RGBA exact;
- PNG→WebP migration remains `NOT_AUTHORIZED`.

## Synology deployment contract

```text
project: otheryn-atlas-preview
image: ghcr.io/nginx/nginx-unprivileged:1.31.3-alpine3.24-slim@sha256:22f839c5fb4007dc24d203a170a9e03fc185d660bfefc34ac6823a7aef085cbc
container HTTP: 8080
host bind: 127.0.0.1
host port: 8095
data path: /volume1/docker/otheryn/atlas/current
project path: /volume1/docker/otheryn/atlas/project
DSM reverse-proxy destination: HTTP / 127.0.0.1 / 8095 / /
health: /healthz plus container healthcheck
```

## Synology effects now VERIFIED

### Project files are already staged on the NAS

One-shot non-SSH staging run `31936147519`, job `95138269934`, executed on dedicated runner `oteryn-synology-staging` and succeeded.

Before staging: `EXISTING_PROJECT=false`.

Persistent files now present on Synology:

```text
/volume1/docker/otheryn/atlas/project/docker-compose.yml
  sha256 64497eeaef5488a849e3a420ce2c3142d4659007fefec228d6224d14b3086d90
/volume1/docker/otheryn/atlas/project/nginx.conf
  sha256 e4ede6aeb53e07cd721578e85edee4038939e5531e5077cf5fff8327ff616ad2
/volume1/docker/otheryn/atlas/project/.env.example
  sha256 f38ac0693f693755d045d3fa3a4573e0d849f5a02ff74e739a4e65b374130bf9
/volume1/docker/otheryn/atlas/project/SOURCE.txt
  sha256 81d17743be8788b039b749c59a1c5524f0ce24e70d988bd28eeb94cb2e27a857
```

`CANONICAL_OTERYN_STAGING_UNCHANGED=true` and `ATLAS_PROJECT_HASH_VERIFICATION=PASS`.
The operational Oteryn-Platform carrier PR #1110 was closed without merge after the bounded run; no Platform product/runtime integration was created.

### SMB target is VERIFIED

Read-only Synology share inspection run `31936365237`, job `95138825588`, proved:

```text
host name: Synology
share name: docker
share path: /volume1/docker
WinShare: yes
ACL: yes
```

Therefore the direct Windows SMB destination for the generated corpus is:

```text
\\Synology\docker\otheryn\atlas\current
```

The share is not browseable in Network discovery (`fBrowseable=no`), so clients should use the direct UNC path.

### No usable Atlas corpus exists on the NAS

Read-only discovery established:

- `/volume1` exists but no matching `full-map-atlas/manifest.json`, no `full-map-atlas` directory and no likely Otheryn repository directory was found during the bounded searches;
- `/volume2` exists but has no top-level directories at all (`VOLUME2_TOPLEVEL` empty);
- the intended `/volume1/docker/otheryn/atlas/current` corpus was not present;
- port `8095` was previously observed free and no Atlas service was listening on it.

The generated 10+ GB corpus therefore cannot be sourced from Synology itself. The remaining source is the already-generated desktop `build/full-map-atlas`, which is outside the file/network channels available to this coordinator.

## Recovered policy violation: forbidden NAS build

An earlier one-shot runtime generation `31934035062 / 95133102010` was found building a new full Atlas on `synology-ots-01`, contrary to the owner contract that deployment must reuse the desktop build.

It was canceled before verification, promotion or Atlas-container start by concurrency replacement run `31936024989`.

Cleanup run `31936217515 / 95138445343` then proved the residue had no `manifest.json` and removed only `/work/_atlas_build`:

```text
partial_tile_png_count=1022
partial_bytes=1614629845
PARTIAL_BUILD_RESIDUE_REMOVED=true
```

No partial output was promoted to `/volume1/docker/otheryn/atlas/current`.

## Runtime requirements

| Requirement | State | Completion gate |
|---|---|---|
| ATLAS-PR-002 | PARTIAL | Desktop corpus must be transferred to the verified SMB destination, then the already-staged DSM project must be imported/started and exposed by the owner-created private DSM Reverse Proxy rule. |
| ATLAS-PR-003 | NOT_RUN | Real Chromium must run against the resulting actual DSM URL. |
| ATLAS-PR-004 | NOT_RUN | Cold/warm/navigation measurements must be collected against the same deployed URL. |
| ATLAS-PR-011 | WAITING | Owner format decision only after browser evidence; WebP migration remains unauthorized. |
| ATLAS-PR-001 | PENDING | Only owner visual/interaction review may accept the viewer or record defects. |

## Remaining owner boundary

The project-copy step no longer requires owner action: it is already complete on Synology.

The one data operation that cannot be executed from the available GitHub/Synology connectors is reading the existing `build/full-map-atlas` directory from the owner's Windows desktop. The verified transfer destination is `\\Synology\docker\otheryn\atlas\current`.

After that transfer, the owner task still reserves these lifecycle operations for DSM UI:

1. Container Manager → Project → import/start `otheryn-atlas-preview` from `/volume1/docker/otheryn/atlas/project/docker-compose.yml` and confirm `healthy`;
2. Control Panel → Login Portal → Advanced → Reverse Proxy → create the private rule whose destination is `HTTP 127.0.0.1:8095 /`;
3. open the resulting private URL in a normal browser and provide only that URL (no credentials/tokens).

Do not use SSH, SSH tunnels, `docker exec`, public DNS, Cloudflare, Internet port forwarding or another full-world build to bridge this boundary.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-16T10:31:00+02:00
head: 39cb2ce4ff427e7c3760eb6112b45efc0c1f73b8
head_scope: protected main plus non-merged one-shot Synology evidence
status: waiting
phase: desktop-corpus-transfer-then-dsm-runtime
execution_mode: chat-github
project_lane: otheryn-content
proven:
  - PR 415 deployment implementation is merged and exact-head required CI passed
  - /volume1/docker/otheryn/atlas/project is already staged with exact expected hashes
  - canonical oteryn-staging services were unchanged by the staging operation
  - Synology SMB host/share is Synology/docker -> /volume1/docker
  - direct corpus target is \\Synology\docker\otheryn\atlas\current
  - no reusable full-map-atlas corpus exists on volume1 or volume2
  - forbidden NAS full-build generation was canceled before promotion/runtime start
  - 1022 partial PNG files / 1614629845 bytes from that canceled temp build were removed and no manifest was present
unknown:
  - actual desktop deployment_preflight result, especially final environment-animation readiness
  - final DSM reverse-proxy source URL
  - deployed Chromium E2E and performance
blockers:
  - the coordinator has no channel to read the owner's Windows desktop build/full-map-atlas directory; this external data transfer is the only remaining non-DSM deployment-data boundary
next_action: owner runs the validated SMB transfer of the existing desktop build/full-map-atlas to \\Synology\docker\otheryn\atlas\current, then imports/starts the already-staged DSM project and creates the private DSM reverse-proxy rule
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 6
  session_id: atlas-preview-20260816T1031+0200
  session_started_at: 2026-08-16T10:06:00+02:00
  checkpointed_at: 2026-08-16T10:31:00+02:00
  last_progress_at: 2026-08-16T10:31:00+02:00
  phase: desktop-corpus-transfer-then-dsm-runtime
  exact_head: 39cb2ce4ff427e7c3760eb6112b45efc0c1f73b8
  pull_request: 415
  active_operation: none
  external_run_ids: [31936147519, 31936365237, 31936024989, 31936217515, 31936583947]
  operation_started_at: null
  wait_deadline_at: null
  check_generation: null
  checks_used: 0
  status: waiting
  safe_to_resume: true
  resume_condition: desktop corpus has been copied to the verified SMB destination and DSM project/reverse-proxy actions have produced the private Atlas URL
  next_action: verify the copied NAS corpus and real Synology container/DSM URL, then run ATLAS-PR-003 Chromium E2E and ATLAS-PR-004 performance without estimating missing evidence
```

## Closeout rule

The product-readiness task remains incomplete until the real Synology/DSM/browser path is proven. Keep one executable `next_action` while incomplete.
