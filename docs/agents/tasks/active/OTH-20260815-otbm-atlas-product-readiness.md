---
task_id: OTH-20260815-otbm-atlas-product-readiness
status: waiting
owner: none
branch: none
base_branch: main
created: "2026-08-15T14:09:00+02:00"
updated: "2026-08-16T09:03:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "415"
ownership_released: true
owned_paths: []
---

# OTBM Atlas product-readiness continuation

## Goal

Move the technically certified OTBM Atlas to a real private Synology Container Manager preview reachable through DSM Reverse Proxy in a normal browser, then collect real Chromium E2E and production-like browser performance evidence.

Canonical backlog: `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md`.
Deployment runbook: `deploy/otbm-atlas-synology/README.md`.

## Current verified repository state

- `main`: `b9f51b01352abcda4db8df54f3b575ddc7b2532b`.
- PR #415 `feat(atlas): add private Synology browser preview` is MERGED as `b9f51b01352abcda4db8df54f3b575ddc7b2532b`.
- Final PR head: `29ad7835e4c8e9cd98e48058a840e519afb02bc9`.
- Exact-head CI run `31932432026`: SUCCESS.
- Exact-head Required run `31932431889`: SUCCESS.
- All three live PR review threads are resolved.
- Fresh audit findings `ATLAS-AUDIT-415-001` through `004` were remediated; open material findings: `0`.
- Earlier focused Synology-preview job `31931712166 / 95127448119`: SUCCESS, including real pinned-image pull, Compose start, health, MIME, deterministic 404, security headers, non-root user, read-only root filesystem, dropped capabilities, `no-new-privileges`, read-only Atlas/config mounts, loopback port binding, restart policy, PID bound, visible logs and unchanged mounted fixture bytes.

## Technical Atlas baseline

- Atlas schema/version: `3`.
- Chunk size: `128` map tiles.
- Certified world: populated `Z0..Z15`, exactly `3494` detail chunks, zero certified missing sprites.
- Canonical map SHA-256: `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`.
- Accepted asset provenance:
  - canonical Git bytes `4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7`;
  - validated Windows worktree representation `4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2`, whose only byte delta was one CRLF-materialized NON_RENDER_INPUT file.
- ATLAS-PR-010 is VERIFIED: 240 deterministic current-v3 chunks, PNG `629930622` bytes vs lossless WebP `320113728` bytes, saving `49.18270094829586%`; `240/240` decode RGBA-identically.
- PNG→WebP migration remains NOT_AUTHORIZED. ATLAS-PR-011 is an owner decision after real browser evidence.

## Merged Synology deployment contract

```text
project: otheryn-atlas-preview
image: ghcr.io/nginx/nginx-unprivileged:1.31.3-alpine3.24-slim@sha256:22f839c5fb4007dc24d203a170a9e03fc185d660bfefc34ac6823a7aef085cbc
container HTTP: 8080
recommended host bind: 127.0.0.1
recommended host port: 8095
recommended data path: /volume1/docker/otheryn/atlas/current
recommended project path: /volume1/docker/otheryn/atlas/project
DSM destination: HTTP / 127.0.0.1 / 8095 / /
health: /healthz and container healthcheck
```

The path and port values above are RECOMMENDED, not verified live NAS facts. Repository inventory proves only that Otheryn's tracked Docker configuration does not allocate `8095`; live NAS availability remains UNKNOWN until DSM starts the project.

## Runtime requirements

| Requirement | State | Completion gate |
|---|---|---|
| ATLAS-PR-002 | PARTIAL | The merged project must actually run on Synology with the Atlas mounted read-only and be reachable through DSM Reverse Proxy from a normal browser without any SSH tunnel. |
| ATLAS-PR-003 | NOT_RUN | Real Chromium must pass against the exact DSM URL used by the owner; required creature/environment animation evidence must pass or remain explicitly unverified. |
| ATLAS-PR-004 | NOT_RUN | Real cold/warm/navigation measurements must exist from that same deployed URL. |
| ATLAS-PR-011 | WAITING | Owner decides PNG vs WebP lossless only after browser evidence; no migration is authorized before that. |
| ATLAS-PR-001 | PENDING | Only the owner may accept the real viewer or record exact UI/UX defects. |

## Explicit remaining unknowns

- The current desktop `build/full-map-atlas` deployment-preflight result is not observable from the GitHub-only coordinator. In particular, final current viewer bytes and the final `data/environment-animations/` artifact must not be inferred from the earlier interrupted exporter attempts.
- The live Synology volume/path and TCP `8095` availability are not observable from repository state.
- The DSM reverse-proxy source hostname/port and resulting private browser URL are owner DSM state.
- Real deployed Chromium E2E and browser performance remain UNKNOWN until that URL exists.

Do not rerender the full Atlas merely to deploy it. Use the existing desktop generated corpus. If the final environment-animation artifact is absent, keep ATLAS-PR-003 partial and route that exact dependency to `OTH-20260815-atlas-environment-animation-export-performance`; do not launch an unbounded exporter automatically.

## Minimal unavoidable owner DSM action

1. Copy the existing desktop generated Atlas directory contents from `build/full-map-atlas/` to the chosen Synology persistent folder using SMB, DSM File Station or Synology Drive. Recommended destination: `/volume1/docker/otheryn/atlas/current`.
2. Copy the merged project files from `deploy/otbm-atlas-synology/` to the Synology project folder. Recommended: `/volume1/docker/otheryn/atlas/project`. If DSM expects `docker-compose.yml`, use the contents of repository `compose.yaml` under that filename; keep `nginx.conf` in the same project folder.
3. In DSM Container Manager create/import Project `otheryn-atlas-preview` from that project folder and start it. Expected host binding is `127.0.0.1:8095 → container 8080`. If DSM reports a real port conflict, choose another unused high TCP port and use the same actual port in the reverse-proxy destination.
4. In DSM Reverse Proxy create a private/local rule whose destination is protocol `HTTP`, hostname `127.0.0.1`, port `8095` (or the actual conflict-free replacement), root path `/` where the UI exposes a path field. Do not add public DNS, Cloudflare or Internet port-forwarding.
5. Confirm the resulting private browser URL. No credentials, tokens or DSM secrets are required in chat.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-16T09:03:00+02:00
head: b9f51b01352abcda4db8df54f3b575ddc7b2532b
head_scope: merged main after PR 415
branch: none
pr: 415
pr_state: merged
status: waiting
phase: runtime-deploy
execution_mode: chat-github
project_lane: otheryn-content
proven:
  - PR 415 merged to main as b9f51b01352abcda4db8df54f3b575ddc7b2532b
  - exact PR head 29ad7835e4c8e9cd98e48058a840e519afb02bc9 passed CI 31932432026 and Required 31932431889
  - all PR review threads are resolved
  - open material audit findings are zero
  - static container contract was exercised successfully in focused workflow 31931712166 job 95127448119
  - technical Atlas remains certified as v3 / Z0..Z15 / 3494 chunks
unknown:
  - actual desktop deployment-preflight outcome for final viewer/environment payloads
  - live NAS path and 8095 availability
  - private DSM browser URL
  - deployed Chromium E2E and performance
blockers:
  - owner DSM UI/file-copy action is required; no Synology/DSM connector is available to the coordinator and private NAS UI is not reachable from this execution environment
next_action: owner copies the existing generated Atlas and merged project into Synology, starts Project otheryn-atlas-preview, creates the private DSM reverse-proxy destination HTTP 127.0.0.1:8095, and returns the resulting private browser URL for immediate ATLAS-PR-003/004 continuation
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 5
  session_id: atlas-preview-20260816T0903+0200
  session_started_at: 2026-08-16T09:03:00+02:00
  checkpointed_at: 2026-08-16T09:03:00+02:00
  last_progress_at: 2026-08-16T09:03:00+02:00
  phase: runtime-deploy
  exact_head: b9f51b01352abcda4db8df54f3b575ddc7b2532b
  pull_request: 415
  active_operation: none
  external_run_ids: [31932432026, 31932431889, 31931712166]
  operation_started_at: null
  wait_deadline_at: null
  check_generation: null
  checks_used: 0
  status: waiting
  safe_to_resume: true
  resume_condition: owner supplies the private DSM Atlas browser URL after project start and reverse-proxy creation
  next_action: attempt real Chromium E2E and performance measurement against the supplied DSM URL; if private-network reachability is unavailable, record that exact environment blocker and use the repository probe evidence produced on the owner's desktop rather than estimating results
```

## Closeout rule

The product-readiness task is not complete at repository merge. Runtime completion requires observable Synology/DSM/browser evidence. Preserve exactly one executable `next_action` while incomplete.
