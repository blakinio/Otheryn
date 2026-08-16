---
task_id: OTH-20260815-otbm-atlas-product-readiness
status: validating
owner: atlas-preview-coordinator
branch: blakinio/atlas-synology-browser-preview
base_branch: main
created: "2026-08-15T14:09:00+02:00"
updated: "2026-08-16T08:33:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "415"
ownership_released: false
owned_paths:
  - deploy/otbm-atlas-synology/**
  - tools/otbm_atlas/deploy_preflight.py
  - tools/otbm_atlas/deployed_browser_probe.py
  - tools/otbm_atlas/tests/test_deploy_preflight.py
  - .github/workflows/otbm-atlas-synology-preview.yml
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md
---

# OTBM Atlas product-readiness continuation

## Goal

Move the technically certified OTBM Atlas to a real private Synology Container Manager preview reachable through DSM Reverse Proxy in a normal browser, then collect real Chromium E2E and production-like performance evidence.

Canonical backlog: `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md`.
Preview/codec handover: `docs/maps/otbm-atlas-preview-codec-handover-20260815.md`.

## Owner architecture — authoritative

```text
generated static Atlas
→ Synology NAS persistent folder
→ Synology Container Manager container
→ local container HTTP port
→ DSM Reverse Proxy
→ normal browser
```

Hard boundaries remain: no SSH, SSH tunnel, `docker exec`, NAS shell prerequisite, Oteryn Platform integration, Cloudflare/public route, public Internet exposure, privileged container, Docker socket, or full-world build on Synology. Generated Atlas data is copied by DSM File Station, SMB or Synology Drive and mounted read-only.

## Verified baseline

- Entry `main` for this continuation was `475196ddba675e2f7f0dadcdb3fdb445db79bba2`.
- Atlas PRs #410, #412, #413 and #414 are merged; no Atlas PR was open at continuation entry.
- Technical Atlas implementation/full-world certification remains DONE/VERIFIED: schema/Atlas v3, chunk size 128, populated Z0..Z15, exactly 3494 detail chunks, zero certified missing sprites.
- Canonical map SHA-256 is `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`.
- Canonical Git asset corpus SHA-256 is `4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7`; the previously generated Windows-v3 corpus records `4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2`, whose sole byte difference was proven to be CRLF materialization of one NON_RENDER_INPUT file.
- The current-v3 benchmark covers 240 deterministic chunks across Z0..Z15: PNG `629930622` bytes, lossless WebP `320113728` bytes, saving `309816894` bytes / `49.18270094829586%`; 240/240 decode RGBA-identically.
- Complete current-v3 detail PNG storage is `10995096999` bytes. The `5587411323`-byte complete WebP figure remains ESTIMATED rather than measured.
- ATLAS-PR-010 is VERIFIED. ATLAS-PR-011 remains an owner decision; PNG→WebP migration is NOT_AUTHORIZED.
- Environment-animation full-world export performance/resume remains the separate READY task `OTH-20260815-atlas-environment-animation-export-performance`; earlier canonical attempts were interrupted after measurable progress and no final artifact may be assumed.

## Synology preview implementation

PR #415 implements the deployment layer without committing generated Atlas data:

- `deploy/otbm-atlas-synology/compose.yaml` uses a pinned official unprivileged nginx image, read-only root filesystem, `no-new-privileges`, all capabilities dropped, bounded PID count, loopback-only host bind, read-only Atlas bind mount, restart policy, log rotation and a deterministic health check.
- `deploy/otbm-atlas-synology/nginx.conf` serves static HTML/JS/CSS/JSON/PNG/WebP, returns deterministic 404s, exposes `/healthz`, keeps generated files immutable and adds conservative private-preview security headers.
- `deploy/otbm-atlas-synology/README.md` defines non-SSH DSM Container Manager Project/import, file-copy and reverse-proxy steps.
- `tools/otbm_atlas/deploy_preflight.py` checks current viewer bytes, canonical v3 identity, full independent chunk verification, creature references and final environment-animation readiness without regenerating the world.
- `tools/otbm_atlas/deployed_browser_probe.py` is the real deployed-URL Chromium harness for ATLAS-PR-003/004; it records screenshots, console/network failures, required interactions, animation evidence and cold/warm/navigation metrics.
- `.github/workflows/otbm-atlas-synology-preview.yml` independently validates the local container contract, MIME types, health/404 behavior, non-root/read-only/capability constraints, loopback binding, logs and source-data immutability without `docker exec`.

Recommended values are deliberately not presented as live NAS facts:

```text
RECOMMENDED_DATA_PATH: /volume1/docker/otheryn/atlas/current
RECOMMENDED_PROJECT_PATH: /volume1/docker/otheryn/atlas/project
RECOMMENDED_HOST_BIND: 127.0.0.1
RECOMMENDED_HOST_PORT: 8095
VERIFIED_EXISTING_NAS_PATH: UNKNOWN
VERIFIED_LIVE_NAS_PORT_AVAILABILITY: UNKNOWN
DSM_PROXY_DESTINATION: HTTP / 127.0.0.1 / 8095 / /
```

Repository port inventory found existing allocations at 7171–7175, 8080, 8088 and 9090 and no repository allocation at 8095. This does not prove live NAS availability.

## Product-readiness status

| Requirement | State | Evidence / remaining gate |
|---|---|---|
| ATLAS-PR-002 | PARTIAL | Deployment package exists in PR #415; cannot be VERIFIED until the container actually runs on Synology, the corpus mount is read-only/restart-capable, and the DSM reverse-proxy URL works in a normal browser. |
| ATLAS-PR-003 | NOT_RUN | Real Chromium must run against the actual owner DSM URL. Environment animation must pass or the requirement remains partial. |
| ATLAS-PR-004 | NOT_RUN | Cold/warm/navigation measurements must come from the actual deployed browser URL. |
| ATLAS-PR-011 | WAITING | Owner format decision only after real browser evidence; no migration authorized. |
| ATLAS-PR-001 | PENDING | Only the owner may accept the real viewer or record exact defects. |

## Feature scope

```yaml
feature_scope:
  type: infrastructure
  user_facing: true
  backend_required: false
  frontend_required: true
  integration_required: true
  e2e_required: true
  completion_claim: complete_feature
```

## Unknowns that must remain explicit

- Whether the preserved desktop `build/full-map-atlas` currently contains the final current viewer files; `build_atlas()` writes them after environment-animation enrichment, so an interrupted final enrichment run cannot be assumed to have refreshed them.
- Whether `data/environment-animations/index.json` exists and is complete in the deployable desktop corpus.
- Actual Synology volume/path and whether host TCP 8095 is free.
- Final private DSM reverse-proxy source URL.
- Real browser cold/warm/navigation measurements.

`deploy_preflight.py` deterministically resolves the first two from the actual generated directory without another full-world render.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-16T08:33:00+02:00
head: 6784bd2412102fa4643a357177a633b0e8baadc1
head_scope: implementation commit before durable task-checkpoint commit
branch: blakinio/atlas-synology-browser-preview
pr: 415
status: validating
phase: validate
execution_mode: chat-github
project_lane: otheryn-content
base_main_at_verification: 475196ddba675e2f7f0dadcdb3fdb445db79bba2
context_routes:
  - deploy/otbm-atlas-synology/README.md
  - docs/maps/otbm-atlas-product-readiness-backlog-20260815.md
  - docs/maps/otbm-atlas-preview-codec-handover-20260815.md
owned_paths:
  - deploy/otbm-atlas-synology/**
  - tools/otbm_atlas/deploy_preflight.py
  - tools/otbm_atlas/deployed_browser_probe.py
  - tools/otbm_atlas/tests/test_deploy_preflight.py
  - .github/workflows/otbm-atlas-synology-preview.yml
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md
proven:
  - technical Atlas and 3494-chunk canonical world remain certified
  - PR 410, 412, 413 and 414 are merged
  - PR 415 contains the smallest static-serving Synology deployment package and runtime validation tooling
  - deployment does not bake or commit the Atlas corpus
  - host path and 8095 are recommendations rather than claimed live NAS facts
unknown:
  - exact current desktop deployment-preflight result
  - final environment-animation artifact presence
  - live NAS port availability
  - actual private browser URL
  - deployed browser E2E and performance
conflicts: []
first_failure:
  marker: none
  evidence: none
changed_paths:
  - deploy/otbm-atlas-synology/compose.yaml
  - deploy/otbm-atlas-synology/nginx.conf
  - deploy/otbm-atlas-synology/.env.example
  - deploy/otbm-atlas-synology/README.md
  - tools/otbm_atlas/deploy_preflight.py
  - tools/otbm_atlas/deployed_browser_probe.py
  - tools/otbm_atlas/tests/test_deploy_preflight.py
  - .github/workflows/otbm-atlas-synology-preview.yml
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md
blockers: []
next_action: validate PR 415 exact head with repository CI and a fresh exact-diff/container-security audit, repair material findings, and merge the deployment package before requesting the minimal owner DSM action
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 1
  session_id: atlas-preview-20260816T0833+0200
  session_started_at: 2026-08-16T08:18:00+02:00
  checkpointed_at: 2026-08-16T08:33:00+02:00
  last_progress_at: 2026-08-16T08:33:00+02:00
  phase: validate
  exact_head: 6784bd2412102fa4643a357177a633b0e8baadc1
  pull_request: 415
  active_operation: exact-head PR validation
  external_run_ids: []
  operation_started_at: 2026-08-16T08:33:00+02:00
  wait_deadline_at: 2026-08-16T09:18:00+02:00
  check_generation: pr-415-initial
  checks_used: 0
  status: active
  safe_to_resume: true
  resume_condition: PR 415 checks or audit provide new evidence
  next_action: inspect the aggregate required-check state for PR 415 exact head, then audit the complete changed-file set against ATLAS-PR-002 security and deployment acceptance
```

## Closeout rule

Do not mark the task completed merely because PR #415 is merged. Runtime completion requires observable Synology/DSM/browser evidence. While incomplete, keep exactly one executable `next_action`.
