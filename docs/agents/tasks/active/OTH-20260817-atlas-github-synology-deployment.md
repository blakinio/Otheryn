---
task_id: OTH-20260817-atlas-github-synology-deployment
status: in_progress
owner: chat-github-atlas-deployment
branch: feat/OTH-20260817-atlas-github-synology-deployment
base_branch: main
created: "2026-08-17T11:02:00+02:00"
updated: "2026-08-17T11:49:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "435"
ownership_released: false
owned_paths:
  - .github/workflows/otbm-atlas-full-world-16.yml
  - .github/workflows/otbm-atlas-ci-ingest-tests.yml
  - .github/workflows/otbm-atlas-deploy-request.yml
  - deploy/otbm-atlas-ci-ingest/**
  - tools/otbm_atlas/world_publish.py
  - tools/otbm_atlas/production_data.py
  - tools/otbm_atlas/tests/test_world_publish.py
  - tools/otbm_atlas/tests/test_product_rebase_contract.py
  - docs/agents/tasks/active/OTH-20260817-atlas-github-synology-deployment.md
---

# OTBM Atlas GitHub-hosted render -> Synology deployment

## Goal

Close the missing production boundary after full-world certification: GitHub-hosted Linux runners remain the only render compute, while verified generated shard/global bundles are streamed directly to a temporary authenticated receiver on the owner's Synology, assembled there, fully deployment-preflighted, atomically promoted to `current`, and served by the existing private Atlas container.

## Admission / live evidence

- main at admission: `bb705a62ac67b04d524720ec682e1f2c31105dd9`;
- no duplicate open Atlas GitHub->Synology deployment PR/branch found;
- canonical full-world workflow previously built 32 weighted chunk shards on `ubuntu-latest` and uploaded only compact evidence, explicitly leaving generated corpus runner-local;
- Otheryn has repository runner `synology-ots-01` with labels `[ots, synology]` and Docker access, physically proven by historical workflow run `31934035062` / job `95133102010`;
- historical Synology render work is prohibited; the runner is receiver/assembly/deployment only;
- existing private Atlas project path remains `/volume1/docker/otheryn/atlas/project` and data path `/volume1/docker/otheryn/atlas/current`;
- full generated corpus must not be published through GitHub Actions artifacts, GitHub Pages, R2/CDN, or other object storage by this task;
- no owner-funded Codex/OpenAI/paid AI quota.

## Implemented architecture

```text
exact main deployment request
        |
        v
canonical full-world workflow_dispatch(expected_producer_sha, deploy=true)
        |
        +--> Synology receiver prepare (synology-ots-01)
        |      - >=20 GiB free-space gate
        |      - isolated generation directory
        |      - current manifest fingerprint capture
        |      - random bearer capability
        |      - write-only receiver container
        |      - outbound-only temporary Cloudflare Quick Tunnel
        |
        +--> plan on ubuntu-latest
        |
        +--> 32 render shards on ubuntu-latest
        |      render -> verify_world_shard -> direct chunked HTTPS upload
        |
        +--> global product-data bundle on ubuntu-latest
        |      full spool/factual/viewer/tile-inspector only
        |      no detail/environment rendering
        |      -> direct chunked HTTPS upload
        |
        +--> exact 3494-chunk compact certification
        |
        +--> Synology finalize
               validate exact 33 receiver receipts
               independently verify all 32 physical shard corpora
               assemble global + render/environment data using hardlinks when available
               reconstruct final environment index
               FULL_RUNTIME_READY publication gate
               current-state drift guard
               atomic previous/current promotion
               recreate only Atlas container
               Docker health + HTTP health + served 3494-chunk manifest verification
               ACTIVE deployment receipt or exact-generation rollback
               remove receiver/tunnel/token
```

PR/labeled full-world certification remains non-deploying and ephemeral. Synology deployment requires an explicit main-only dispatch bound to the exact authorized main SHA. Because the current GitHub connector cannot invoke `workflow_dispatch` directly, `.github/workflows/otbm-atlas-deploy-request.yml` provides a code-reviewed main-only deployment-request path whose merge dispatches the exact request commit SHA.

## Transport contract

- receiver API is bearer-authenticated and write-only: health, part PUT, bundle complete;
- no file-read/list/shell/arbitrary-path API;
- 64 MiB maximum request part;
- 48 MiB production uploader parts;
- maximum 128 parts / 4 GiB per bundle;
- per-part and complete-archive SHA-256 binding;
- exact idempotent retries only for identical part bytes;
- unsafe tar paths, symlinks, hardlinks, devices, FIFOs and duplicate members fail closed;
- same-repo admission only before any PR code may touch the self-hosted Synology runner;
- temporary tunnel exposes the ingest receiver only, never the Atlas viewer;
- receiver/tunnel/token are removed after deployment attempt; failed incoming data may remain tokenless for inspection.

## Live transport evidence so far

- focused publication unit contracts have repeatedly passed on hosted Linux;
- real `synology-ots-01` receiver preparation job `95343038174` succeeded: receiver container, temporary outbound tunnel and authenticated health were physically proven;
- the first tiny hosted upload experiment used an intentionally tiny 7-byte split, which created an unrepresentative number of requests; it was superseded rather than treated as transport failure;
- the final fixture uses 4096-byte parts to exercise multipart behavior without pathological request count;
- bounded stale pre-production endpoint cleanup run `32016201025` / job `95346081941` succeeded; the temporary cleanup workflow was removed immediately afterward and is not part of the production diff.

## Audit/remediation already performed

- self-hosted PR path hardened so fork PR code cannot execute on `synology-ots-01`;
- cross-job bearer handling changed so downstream consumers mask it immediately instead of depending on masked-output propagation;
- receiver completion serialized per bundle and total part/bundle limits added;
- full-world deploy admission now requires exact `expected_producer_sha == GITHUB_SHA` on `main`;
- receiver prepare now fail-cleans partial endpoints and checks Synology free space;
- runtime activation now verifies Docker health plus parsed served `manifest.json` with 3494 chunks;
- assembly uses hardlinks under the same Atlas filesystem when supported, avoiding a second full ~11 GiB physical copy;
- old product-rebase contract test updated to assert semantic default use of the resumable environment exporter rather than a brittle literal assignment;
- synthetic world-publication fixture corrected to use the real canonical map identity after assembler hardening.

## Acceptance

- [x] receiver unit contracts cover authorization, oversized requests, path traversal/symlink rejection, SHA binding, changed-part rejection and total bundle bound;
- [x] uploader splits bounded requests, validates SHA-256 and retries only bounded transient failures;
- [x] self-hosted runner admission excludes fork PR code;
- [x] Synology receiver/tunnel/authenticated health physically started successfully;
- [x] stale test endpoints physically cleaned after superseded run;
- [ ] final exact-head hosted multipart upload -> Synology byte verification PASS;
- [ ] 32 shard bundles remain render-computed only on `ubuntu-latest` under final PR full-world certification;
- [ ] PR full-world certification proves receiver/global/finalize deployment jobs remain skipped;
- [ ] full generated corpus is never uploaded as Actions artifacts;
- [ ] one hosted global-data bundle supplies factual/viewer/tile-inspector data without re-rendering detail/environment chunks;
- [ ] Synology assembler verifies all 32 shard corpora before merge;
- [ ] assembled corpus passes full publication gate in real post-merge deployment;
- [ ] promotion is atomic and refuses current-state drift;
- [ ] targeted Atlas runtime health failure rollback path remains regression-tested;
- [ ] exact-head repository/specialized CI PASS;
- [ ] fresh audit has zero open material findings;
- [ ] implementation merge and post-merge reread;
- [ ] real main deployment request produces ACTIVE receipt on Synology;
- [ ] broader product-readiness checkpoint updated to real-browser E2E/performance.

## Context checkpoint

```yaml
checkpoint_version: 2
updated_at: 2026-08-17T11:49:00+02:00
head: 3e21ffda9e2deb9ddd3f0d12a50c40ef079bd149
base: bb705a62ac67b04d524720ec682e1f2c31105dd9
status: in_progress
phase: exact-head-transport-and-ci
proven:
  - current full-world workflow used to discard generated shard corpora after certification
  - Otheryn repository runner synology-ots-01 exists with labels ots,synology and Docker access
  - authenticated receiver plus outbound temporary tunnel physically started on synology-ots-01
  - stale superseded pre-production endpoints were removed by bounded cleanup
  - hosted publication unit contracts pass
  - ordinary resumable environment exporter remains the default production path
blockers: []
next_action: wait for the newest exact-head focused/live transport and specialized CI, remediate any real failures, then run final PR full-world 3494-chunk certification with deployment jobs physically skipped
```
