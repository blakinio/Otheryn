---
task_id: OTH-20260815-otbm-atlas-product-readiness
status: validating
owner: atlas-preview-coordinator
branch: blakinio/atlas-synology-browser-preview
base_branch: main
created: "2026-08-15T14:09:00+02:00"
updated: "2026-08-16T08:49:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "415"
ownership_released: false
owned_paths:
  - deploy/otbm-atlas-synology/**
  - tools/otbm_atlas/deploy_preflight.py
  - tools/otbm_atlas/deployed_browser_probe.py
  - tools/otbm_atlas/_deployed_browser_probe_core.py
  - tools/otbm_atlas/tests/test_deploy_preflight.py
  - .github/workflows/otbm-atlas-synology-preview.yml
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md
---

# OTBM Atlas product-readiness continuation

## Goal

Move the technically certified OTBM Atlas to a real private Synology Container Manager preview reachable through DSM Reverse Proxy in a normal browser, then collect real Chromium E2E and production-like performance evidence.

Canonical backlog: `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md`.
Preview/codec handover: `docs/maps/otbm-atlas-preview-codec-handover-20260815.md`.

## Authoritative preview architecture

```text
generated static Atlas
→ Synology NAS persistent folder
→ read-only mount into Synology Container Manager container
→ local container HTTP port
→ DSM Reverse Proxy
→ normal browser
```

No SSH, SSH tunnel, `docker exec`, NAS shell prerequisite, Oteryn Platform integration, Cloudflare/public route, Internet exposure, privileged container, Docker socket, or full-world build on Synology is authorized. File transfer is by DSM File Station, SMB or Synology Drive.

## Verified baseline

- Continuation entry `main`: `475196ddba675e2f7f0dadcdb3fdb445db79bba2`.
- Atlas PRs #410, #412, #413 and #414 are merged; no Atlas PR was open at continuation entry.
- Technical Atlas remains DONE/VERIFIED: schema/Atlas v3, chunk size 128, Z0..Z15, exactly 3494 detail chunks, zero certified missing sprites.
- Canonical map SHA-256: `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`.
- Canonical Git asset SHA-256: `4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7`; the preserved Windows-v3 corpus records `4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2`, whose sole byte delta was proven CRLF materialization of one NON_RENDER_INPUT file.
- Current-v3 benchmark: 240 deterministic Z0..Z15 chunks, PNG `629930622` bytes vs lossless WebP `320113728`, saving `49.18270094829586%`; 240/240 RGBA exact.
- Complete current-v3 detail PNG storage: `10995096999` bytes. Complete WebP size remains ESTIMATED, not measured.
- ATLAS-PR-010 is VERIFIED. ATLAS-PR-011 is an owner decision and PNG→WebP migration remains NOT_AUTHORIZED.
- Environment-animation export performance/resume remains the separate READY task `OTH-20260815-atlas-environment-animation-export-performance`; no completed final environment artifact may be assumed from the interrupted runs.

## PR #415 implementation

PR #415 adds only the preview/deployment layer and validation tooling; no generated Atlas corpus is committed.

- `deploy/otbm-atlas-synology/compose.yaml`: pinned official unprivileged nginx image; read-only root filesystem; `no-new-privileges`; all capabilities dropped; PID bound; read-only Atlas mount; loopback-only host bind by default; restart policy; health check; bounded logs.
- `deploy/otbm-atlas-synology/nginx.conf`: static HTML/JS/CSS/JSON/PNG/WebP, `/healthz`, deterministic 404 behavior, favicon 204 to avoid browser-noise 404s, private-preview security/cache headers.
- `deploy/otbm-atlas-synology/README.md`: non-SSH DSM Container Manager Project/import, transfer, reverse-proxy, validation and rollback contract.
- `tools/otbm_atlas/deploy_preflight.py`: current viewer-byte identity; canonical v3 manifest identity; independent chunk/overview verification; spatial shard/search consistency; creature sprite/animation descriptor/frame references; complete environment-animation shard/index/reference consistency.
- `tools/otbm_atlas/deployed_browser_probe.py`: public deployed-URL Chromium coordinator. Environment-animation acceptance now performs a bounded exhaustive discovery across the complete 3494-entry manifest when the fast core journey cannot locate a record, eliminating the prior arbitrary-prefix false-PARTIAL risk.
- `tools/otbm_atlas/_deployed_browser_probe_core.py`: preserved core browser journey used by the public coordinator; its quick environment probe is diagnostic-only and cannot decide final environment acceptance.
- `.github/workflows/otbm-atlas-synology-preview.yml`: Compose and real container-contract test without `docker exec`, including MIME/404/health, non-root/read-only/capability/loopback checks, logs and source-data immutability.

Recommended values remain recommendations, not fabricated NAS facts:

```text
RECOMMENDED_DATA_PATH: /volume1/docker/otheryn/atlas/current
RECOMMENDED_PROJECT_PATH: /volume1/docker/otheryn/atlas/project
RECOMMENDED_HOST_BIND: 127.0.0.1
RECOMMENDED_HOST_PORT: 8095
VERIFIED_EXISTING_NAS_PATH: UNKNOWN
VERIFIED_LIVE_NAS_PORT_AVAILABILITY: UNKNOWN
DSM_PROXY_DESTINATION: HTTP / 127.0.0.1 / 8095 / /
```

Repository port inventory contains 7171–7175, 8080, 8088 and 9090 and no repository allocation at 8095. Live NAS availability is still UNKNOWN until Container Manager binds the port.

## Product-readiness state

| Requirement | State | Remaining gate |
|---|---|---|
| ATLAS-PR-002 | PARTIAL | Container must actually run on Synology with read-only generated data and be reachable through DSM Reverse Proxy from a normal browser. |
| ATLAS-PR-003 | NOT_RUN | Real Chromium must pass against the actual owner DSM URL; required environment animation must pass or remain explicitly partial. |
| ATLAS-PR-004 | NOT_RUN | Real cold/warm/navigation measurements must be collected from that deployed browser URL. |
| ATLAS-PR-011 | WAITING | Owner format decision only after browser evidence; no WebP migration authorized. |
| ATLAS-PR-001 | PENDING | Only owner visual/interaction acceptance can close this requirement. |

## Fresh audit findings and remediation

A fresh exact-diff/security audit used the acceptance contract rather than the implementer narrative.

- `ATLAS-AUDIT-415-001` — MEDIUM — deployed-browser probe could false-fail zoom and manual corpus probes polluted page-network evidence. Fixed in `d3c14389991ea9637fad5ae1a9e75a8a708fd514`.
- `ATLAS-AUDIT-415-002` — MEDIUM — preflight did not initially prove complete spatial/creature/environment payload presence. Fixed in `9f5d3b3d6e5a71f5251ffc088011efe79b7a1890` with tests in `6f76daf82286a41dc16ac9e72648681354ef192e`.
- `ATLAS-AUDIT-415-003` — LOW — normal browser favicon could create irrelevant network 404 evidence. Fixed in `e00da2e27dfc57a9f5b7185e37e3a17b2641d9ee`.
- `ATLAS-AUDIT-415-004` — MEDIUM review-hygiene finding (reviewer labelled P2) — environment-animation acceptance previously searched only a 512-chunk prefix and could false-report `PARTIAL` for a valid animation record later in the manifest. Fixed in implementation commit `1d9bd8b0cdb157c4e2e8e92661b2f16ee4ce1b4a`: public probe exhaustively scans at most the fixed 3494 manifest chunks and recomputes final acceptance; the legacy fast scan is core diagnostic evidence only.

Open material audit findings: `0`, pending exact-head CI and thread-resolution verification.

## Explicit unknowns

- Exact current desktop `build/full-map-atlas` deployment-preflight result, including final current viewer bytes and final environment-animation artifact presence.
- Actual Synology volume/path and whether TCP 8095 is free on the NAS.
- Final private DSM reverse-proxy source URL.
- Real deployed browser E2E and cold/warm/navigation measurements.

`deploy_preflight.py` resolves desktop-corpus unknowns without another full-world render. Runtime unknowns require the owner DSM action and resulting private URL.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-16T08:49:00+02:00
head: 1d9bd8b0cdb157c4e2e8e92661b2f16ee4ce1b4a
head_scope: review-hygiene remediation before this documentation checkpoint
branch: blakinio/atlas-synology-browser-preview
pr: 415
status: validating
phase: exact-head-ci
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
  - tools/otbm_atlas/_deployed_browser_probe_core.py
  - tools/otbm_atlas/tests/test_deploy_preflight.py
  - .github/workflows/otbm-atlas-synology-preview.yml
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md
proven:
  - technical Atlas and 3494-chunk canonical world remain certified
  - PR 410, 412, 413 and 414 are merged
  - PR 415 contains the static Synology project plus deterministic desktop/deployed-browser validation tooling
  - generated Atlas data is neither committed nor baked into the image
  - deployment defaults are clearly separated from unknown live NAS state
  - fresh audit findings 001 through 004 have implementation remediations
unknown:
  - final exact-head CI result after this checkpoint commit
  - actual desktop deployment-preflight result
  - final environment-animation artifact presence
  - live NAS path/port and private browser URL
  - deployed Chromium E2E and performance
conflicts: []
first_failure:
  marker: audit/review findings ATLAS-AUDIT-415-001 through 004
  evidence: exact changed-file and live review-thread inspection
rejected_hypotheses:
  - config commit alone can verify ATLAS-PR-002
  - final environment animations can be inferred from interrupted exporter runs
  - an arbitrary environment-shard prefix is sufficient for real deployed acceptance
changed_paths:
  - deploy/otbm-atlas-synology/compose.yaml
  - deploy/otbm-atlas-synology/nginx.conf
  - deploy/otbm-atlas-synology/.env.example
  - deploy/otbm-atlas-synology/README.md
  - tools/otbm_atlas/deploy_preflight.py
  - tools/otbm_atlas/deployed_browser_probe.py
  - tools/otbm_atlas/_deployed_browser_probe_core.py
  - tools/otbm_atlas/tests/test_deploy_preflight.py
  - .github/workflows/otbm-atlas-synology-preview.yml
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md
validation:
  - command: earlier focused Synology preview workflow generation
    result: PASS
    evidence: unit, py_compile and real pinned-container contract passed before later review remediation
  - command: fresh exact-diff and live review-thread audit
    result: PASS_AFTER_REMEDIATION
    evidence: zero open material implementation findings; final thread cleanup awaits exact-head verification
blockers: []
next_action: move the branch to the review-hygiene remediation head, resolve all three outdated review threads after verifying their fixes, then require exact-head repository checks and merge before the minimal owner DSM action
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 3
  session_id: atlas-preview-20260816T0818+0200
  session_started_at: 2026-08-16T08:18:00+02:00
  checkpointed_at: 2026-08-16T08:49:00+02:00
  last_progress_at: 2026-08-16T08:49:00+02:00
  phase: exact-head-ci
  exact_head: 1d9bd8b0cdb157c4e2e8e92661b2f16ee4ce1b4a
  pull_request: 415
  active_operation: publish final review-hygiene remediation and validate exact head
  external_run_ids: []
  operation_started_at: 2026-08-16T08:49:00+02:00
  wait_deadline_at: 2026-08-16T09:18:00+02:00
  check_generation: pr-415-review-clean
  checks_used: 0
  status: active
  safe_to_resume: true
  resume_condition: branch head is published and exact-head checks/review hygiene are observable
  next_action: publish exact head, resolve verified outdated threads, then inspect one aggregate CI snapshot
```

## Closeout rule

Do not mark this task completed when PR #415 merges. ATLAS-PR-002/003/004 are runtime requirements and need observable Synology/DSM/browser evidence. Preserve exactly one executable `next_action` while incomplete.
