---
task_id: OTH-20260817-atlas-github-synology-deployment
status: review
owner: chat-github-atlas-deployment
branch: fix/OTH-20260817-atlas-durable-shard-transfer
base_branch: main
created: "2026-08-17T11:02:00+02:00"
updated: "2026-08-17T21:47:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "#442"
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

Finish the private Synology Atlas deployment without repeating expensive render work blindly. GitHub-hosted Linux remains the render compute; Synology remains receiver/verification/assembly/deployment only.

The bounded one-real-shard proof and the production `TRANSFERRED_VERIFIED` hardening are now implemented and focused-validated in PR `#442`. A new 32-shard production render remains blocked until this PR is reviewed/merged under normal governance and a subsequent exact-main production decision is made.

## Canonical production identity

- Atlas schema/version: `3`;
- populated chunks: `3494`;
- floors: `Z0..15`;
- canonical map SHA-256: `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`;
- deterministic plan: 32 weighted shards, about 109 chunks/shard;
- production target root: `/volume1/docker/otheryn/atlas`;
- active Atlas target: `/volume1/docker/otheryn/atlas/current`;
- preview remains private/loopback only; public Atlas remains blocked by `ATLAS-PR-009`.

## Verified failed-run evidence

Production run `32032770809` used producer/main SHA `0be8c1d88767d58dc08676525c8dbfd77b016d99`.

Verified facts from that run:

- all inspected shard jobs reached `BUILD` and independent shard verification before transport completion;
- hosted render jobs ran on `ubuntu-latest`;
- receiver preparation ran on `synology-ots-01` with labels `[ots, synology]`;
- shard `0` completed transport with `archiveBytes=514170880`, 11 parts and receipt `COMPLETE`;
- shards `26` and `29` also completed the transport step;
- representative failed shard `1` built 109 chunks and passed independent verification, then failed at final `/complete` with HTTP `524`;
- uploader uses 48 MiB parts and persists per-part SHA-256 acknowledgements;
- receiver fsyncs each part before atomic rename;
- receiver serializes reconstruction plus safe extraction under one global `_completion_lock`;
- uploader retry set at the failed producer SHA did not include HTTP `524`;
- full-world certification and final assembly were skipped after shard-matrix failure.

This proves network reachability. It does **not** make old failed-run staging canonical or reusable.

## Owner recovery decision — 2026-08-17

The old failed-run NAS staging is **not an input** to the next production generation.

Rules:

1. Do not recover, reuse, or mix old run `32032770809` staging into the next production corpus.
2. Do not delete old staging merely to make the next run work; it may remain quarantined/non-canonical evidence until deliberate cleanup.
3. The next production generation must be fresh and fenced to one exact producer SHA.
4. Do not start another full 32-shard production render until this hardening is merged and a new exact-main production execution is deliberately admitted.
5. Keep approximately 48 MiB transfer parts; smaller parts are not the primary fix.
6. A source GitHub-hosted runner may finish after the receiver returns exact durable `COMPLETE` identity; independent Synology re-verification then promotes persisted data to durable `TRANSFERRED_VERIFIED` state before world assembly.
7. A retry after `TRANSFERRED_VERIFIED` must not rerender that shard unless later physical verification invalidates the active copy.

## Target per-shard contract

```text
BUILD
-> VERIFY BUILD
-> deterministic shard-XX.tar
-> split ~48 MiB parts
-> upload + per-part SHA ACK
-> durable Synology persistence
-> reconstruct complete archive
-> receiver COMPLETE with exact source archive bytes/SHA-256
-> independent Synology physical corpus verification
-> independent deterministic full archive bytes/SHA-256 match
-> TRANSFERRED_VERIFIED
-> later extraction/assembly
-> ASSEMBLED
```

State meanings:

- `BUILT_VERIFIED`: generated corpus passed source-side independent verification;
- `TRANSFERRED_VERIFIED`: Synology durably holds the complete shard and independently matches the source archive identity;
- `ASSEMBLED`: persisted shard has been safely materialized into the world corpus.

A retry after `TRANSFERRED_VERIFIED` must never imply rerender. Extraction/assembly failure must not destroy the persisted rendered result.

## Successful bounded one-shard proof — run 32054847514

The bounded proof executed on exact producer/PR head `f88d0e2d7d4860e1f0f2ea2b2a456de81ceb736e` and completed `SUCCESS`.

Verified evidence:

- canonical 32-way plan: `3494` chunks, shard `0` assignment `109` chunks;
- `worldPlanDigest`: `8d1d2975292b1e67410239cdee330e5a7728a4a4085f537bf611266855f59265`;
- shard `0` build: PASS, four hosted workers;
- source `verify_world_shard`: PASS, `missingSprites={}`;
- transfer auth: job-scoped GitHub OIDC, no cross-job bearer;
- Synology receiver receipt: `COMPLETE`;
- archive bytes: `514170880`;
- archive SHA-256: `7edfda86139460bc17b1b07037f2b404cc8ec5212c2999dcd39ff5ee60d650c1`;
- transfer parts: `11` at the existing ~48 MiB part contract;
- separate post-source job ran on `synology-ots-01` after the hosted source job exited;
- physical shard verification: PASS, `109` chunks;
- deterministic archive rebuild matched the same `514170880` bytes and SHA-256 exactly;
- disposable proof generation cleanup ran only after successful physical re-verification;
- workflow `Temporary Atlas One-Shard Transfer Proof` run `32054847514`: `completed/success`.

The temporary automatic proof workflow was removed after the evidence was captured so unrelated PR synchronizations cannot repeat the expensive one-shard render. The proof result remains recorded here.

## Validated production TRANSFERRED_VERIFIED hardening

PR `#442` now implements the following production design:

1. Production ingest generation identity is producer-fenced (`producer-<40-hex SHA>`) rather than run-attempt-fenced, so a failed same-producer generation can be resumed without mixing producers.
2. Existing producer generation control state is preserved; the control repo is refreshed from the exact producer while the original captured `current-state.json` remains the promotion fence.
3. At the start of a retry, any previously `COMPLETE` shard is physically re-verified on Synology. This can promote a shard from an interrupted earlier attempt to `TRANSFERRED_VERIFIED` without rerendering it.
4. `transfer_state.py` independently rebuilds the deterministic TAR from each physical Synology shard, compares full archive bytes/SHA-256 with the receiver receipt, runs physical `verify_world_shard`, and only then writes `TRANSFERRED_VERIFIED` marker/evidence.
5. Resume state exports only producer-matching markers with an existing physical bundle, receipt and compact evidence.
6. Matrix shard jobs with durable `TRANSFERRED_VERIFIED` state skip expensive free-disk/build/verify/upload/evidence generation and use preserved Synology evidence instead.
7. Newly transferred and reused shards are physically re-verified on `synology-ots-01` before full-world certification/global bundle/final assembly can proceed.
8. If active persisted state is physically invalid or receipt/bundle state is inconsistent, its reusable marker is removed and the active bundle/receipt/parts are moved under `control/quarantine/`. Evidence is retained for inspection while a later retry may rerender only that invalidated shard.
9. Failed/incomplete producer generation is preserved for safe retry/inspection; successful final deployment cleanup may remove duplicate ingest staging.
10. The workflow still requires explicit `workflow_dispatch`, `deploy_to_synology=true`, exact `main`, and exact `expected_producer_sha` before production deployment admission.

## Focused exact-head validation

Code head validated: `5f508f800d396b1e16701ec7a74a311f3151610e`.

Exact-head checks:

- `CI` run `32061490421`: `completed/success`;
- `Required` run `32061490164`: `completed/success`;
- `OTBM Atlas CI Ingest Tests` run `32061490146`: `completed/success`;
  - publication/helper compile: PASS;
  - focused world publication + OIDC + transfer-state unit tests: PASS;
  - temporary receiver on `synology-ots-01`: PASS;
  - hosted fixture upload with job-scoped GitHub OIDC: PASS;
  - physical received-byte verification on Synology: PASS;
  - exact temporary generation cleanup: PASS.

The production 32-shard workflow was **not** triggered during this validation. No `current` promotion, Atlas restart, public route or production deployment was performed.

## Prior implementation history

PR `#435` (`feat(atlas): deploy certified world to Synology`) merged the original receiver/uploader/full-world deployment architecture. PR `#441` (`fix(atlas): stage receiver repo without namespace initializer`) fixed the concrete receiver staging failure and produced the failed transport-heavy production run above.

## Acceptance for this continuation phase

- [x] failed-run cause boundary rechecked against run `32032770809` and current receiver/uploader code;
- [x] owner decision recorded: old failed-run NAS staging is non-canonical and will not be reused;
- [x] clean rebuild was blocked behind a one-real-shard proof;
- [x] dedicated branch + draft PR `#442` exists for the proof/hardening;
- [x] exactly one real shard builds and passes source-side independent verification;
- [x] hosted runner receives positive Synology completion evidence before it exits;
- [x] separate post-source Synology job independently verifies the physical shard corpus/receipt;
- [x] exact one-shard proof evidence is recorded here;
- [x] production `TRANSFERRED_VERIFIED` implementation/transport design is updated from proof evidence;
- [x] focused unit/exact-head CI and hosted->Synology fixture E2E pass for the hardened implementation;
- [ ] only after normal review/merge governance, decide whether a clean 32/32 production render may start.

## Context checkpoint

```yaml
checkpoint_version: 2
policy_version: 2
updated_at: 2026-08-17T21:47:00+02:00
head: 5f508f800d396b1e16701ec7a74a311f3151610e
base: ef9bb701904720004fef745462da14eeac0c4896
status: review
phase: review
task_kind: e2e
execution_mode: chat-github
project_lane: otheryn-content
session_role: implementer-validator
context_pressure: low
context_growth: stable
context_score: 8
estimate_confidence: high
decomposition_decision: phased
decomposition_reason: one-shard proof and production transfer hardening are complete; keep expensive 32/32 production execution behind normal merge governance and an exact-main admission decision
validation_level: focused
heavy_validation_runs: 1
proven:
  - one-shard proof run 32054847514 completed success on exact head f88d0e2d7d4860e1f0f2ea2b2a456de81ceb736e
  - shard 0 source verify passed for 109 chunks with no missing sprites
  - receiver COMPLETE matched 514170880 bytes and 7edfda86139460bc17b1b07037f2b404cc8ec5212c2999dcd39ff5ee60d650c1
  - post-source synology-ots-01 physical verification and deterministic archive identity passed
  - job-scoped GitHub OIDC removes the prior cross-job bearer secret path
  - code head 5f508f800d396b1e16701ec7a74a311f3151610e passed CI 32061490421 and Required 32061490164
  - code head 5f508f800d396b1e16701ec7a74a311f3151610e passed OTBM Atlas CI Ingest Tests 32061490146 including hosted-to-Synology fixture transport and physical byte verification
blockers: []
next_action: move PR #442 through normal review/merge governance; do not run 32/32 production until merged exact-main state is deliberately admitted
```
