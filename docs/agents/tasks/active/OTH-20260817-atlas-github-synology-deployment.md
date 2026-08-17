---
task_id: OTH-20260817-atlas-github-synology-deployment
status: in_progress
owner: chat-github-atlas-deployment
branch: feat/OTH-20260817-atlas-github-synology-deployment
base_branch: main
created: "2026-08-17T11:02:00+02:00"
updated: "2026-08-17T11:02:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: none
ownership_released: false
owned_paths:
  - .github/workflows/otbm-atlas-full-world-16.yml
  - .github/workflows/otbm-atlas-ci-ingest-tests.yml
  - deploy/otbm-atlas-ci-ingest/**
  - tools/otbm_atlas/world_publish.py
  - tools/otbm_atlas/production_data.py
  - tools/otbm_atlas/tests/test_world_publish.py
  - docs/agents/tasks/active/OTH-20260817-atlas-github-synology-deployment.md
---

# OTBM Atlas GitHub-hosted render -> Synology deployment

## Goal

Close the missing production boundary after full-world certification: GitHub-hosted Linux runners remain the only render compute, while verified generated shard/global bundles are streamed directly to a temporary authenticated receiver on the owner's Synology, assembled there, fully deployment-preflighted, atomically promoted to `current`, and served by the existing private Atlas container.

## Admission / live evidence

- main at admission: `bb705a62ac67b04d524720ec682e1f2c31105dd9`;
- no duplicate open Atlas GitHub->Synology deployment PR/branch found;
- canonical full-world workflow builds 32 weighted chunk shards on `ubuntu-latest` and currently uploads only compact evidence, explicitly leaving generated corpus runner-local;
- Otheryn has a repository runner `synology-ots-01` with labels `[ots, synology]` and Docker access, physically proven by historical workflow run `31934035062` / job `95133102010`;
- historical Synology render work is prohibited; the runner is receiver/assembly/deployment only;
- existing private Atlas project path remains `/volume1/docker/otheryn/atlas/project` and data path `/volume1/docker/otheryn/atlas/current`;
- current generated corpus must not be published through GitHub Actions artifacts, GitHub Pages, R2/CDN, or other object storage by this task;
- Quick Tunnel is accepted only as an ephemeral authenticated CI transport, not a user-facing Atlas host; transport requests are bounded below Cloudflare's current per-request upload limit and retryable;
- no owner-funded Codex/OpenAI/paid AI quota.

## Architecture

```text
workflow_dispatch(main, deploy_to_synology=true)
        |
        +--> Synology receiver prepare (synology-ots-01)
        |      - isolated generation directory
        |      - ephemeral bearer capability
        |      - local receiver container
        |      - outbound-only temporary Cloudflare Quick Tunnel
        |
        +--> plan on ubuntu-latest
        |
        +--> 32 render shards on ubuntu-latest
        |      render -> verify_world_shard -> direct chunked HTTPS upload
        |
        +--> global product-data bundle on ubuntu-latest
        |      full spool/factual/viewer/tile-inspector only, no detail render
        |      -> direct chunked HTTPS upload
        |
        +--> full-world compact certification
        |
        +--> Synology finalize
               verify every received shard
               assemble global + render/environment data
               FULL_RUNTIME_READY deployment preflight
               current-state drift guard
               atomic previous/current promotion
               targeted Atlas container recreate + health check
               deployment receipt
               rollback on failed runtime health
               tear down temporary receiver/tunnel
```

PR/labeled certification remains non-deploying and ephemeral. Only explicit `workflow_dispatch` on `main` with `deploy_to_synology=true` may mutate Synology.

## Acceptance

- [ ] receiver rejects unauthorized, oversized, malformed and path-unsafe uploads;
- [ ] uploader splits requests below the transport limit, validates SHA-256 and retries bounded transient failures;
- [ ] 32 shard bundles remain render-computed only on `ubuntu-latest`;
- [ ] full generated corpus is never uploaded as Actions artifacts;
- [ ] one hosted global-data bundle supplies factual/viewer/tile-inspector data without re-rendering detail/environment chunks;
- [ ] Synology assembler verifies all 32 shard corpora before merge;
- [ ] assembled corpus passes full `deployment_preflight(... verify_chunks=True, require_environment_animations=True)`;
- [ ] promotion is atomic and refuses current-state drift;
- [ ] targeted Atlas runtime health failure rolls back the previous generation;
- [ ] receiver/tunnel is removed after success or failure;
- [ ] PR/labeled full-world certification cannot deploy;
- [ ] focused unit + live tiny transport contract PASS;
- [ ] exact-head repository CI / Required PASS;
- [ ] fresh audit 0 open material findings;
- [ ] merge and post-merge reread;
- [ ] broader product-readiness checkpoint updated to canonical automated deployment path.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-17T11:02:00+02:00
head: pending
base: bb705a62ac67b04d524720ec682e1f2c31105dd9
status: in_progress
phase: implementation
proven:
  - current full-world workflow is certification-only and discards generated shard corpora
  - Otheryn repository runner synology-ots-01 exists with labels ots,synology and Docker access
  - Quick Tunnel is outbound-origin, temporary and officially development/test only; this design uses it only as retryable internal CI transport
blockers: []
next_action: implement authenticated chunked direct ingest, global bundle generation, Synology assembly/preflight/promotion and workflow wiring, then run focused/live transport validation and exact-head CI
```
