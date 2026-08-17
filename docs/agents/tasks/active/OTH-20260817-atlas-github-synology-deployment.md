---
task_id: OTH-20260817-atlas-github-synology-deployment
status: validating
owner: chat-github-atlas-deployment
branch: fix/OTH-20260817-atlas-durable-shard-transfer
base_branch: main
created: "2026-08-17T11:02:00+02:00"
updated: "2026-08-17T21:17:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "#442"
ownership_released: false
owned_paths:
  - .github/workflows/otbm-atlas-full-world-16.yml
  - .github/workflows/otbm-atlas-ci-ingest-tests.yml
  - .github/workflows/otbm-atlas-deploy-request.yml
  - .github/workflows/tmp-atlas-one-shard-transfer-proof.yml
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

The bounded one-real-shard proof is now complete. The current continuation hardens the production 32-shard path with durable `TRANSFERRED_VERIFIED` state and safe same-producer retry. A new 32-shard production render remains blocked until this exact-head hardening passes focused validation and is reviewed/merged under normal governance.

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

This proves network reachability. It does **not** prove that every failed-run shard is safely reusable.

## Owner recovery decision — 2026-08-17

The old failed-run NAS staging is **not an input** to the next production generation.

Rules:

1. Do not recover, reuse, or mix old run `32032770809` staging into the next production corpus.
2. Do not delete old staging merely to make the next run work; it may remain quarantined/non-canonical evidence until deliberate cleanup.
3. The next production generation must be fresh and fenced to one exact producer SHA.
4. Do not start another full 32-shard production render until the hardened production transfer contract is validated on the exact PR head and merged.
5. Keep approximately 48 MiB transfer parts; smaller parts are not the primary fix.
6. A source GitHub-hosted runner may finish after the receiver returns exact durable `COMPLETE` identity; independent Synology re-verification then promotes that persisted shard to durable `TRANSFERRED_VERIFIED` state before world assembly.
7. A retry after `TRANSFERRED_VERIFIED` must not rerender that shard unless later physical verification invalidates and removes the marker.

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

This validates the bounded transport/reverification mechanism. It does **not** by itself authorize Quick Tunnel as the final high-volume production transport or authorize a 32/32 production render before the production contract below is validated and merged.

## Production TRANSFERRED_VERIFIED hardening derived from the proof

PR `#442` now stages the following production design for exact-head validation:

1. Production ingest generation identity is producer-fenced (`producer-<40-hex SHA>`) rather than run-attempt-fenced, so a failed same-producer generation can be resumed without mixing producers.
2. Existing producer generation control state is preserved; control repo is refreshed from the exact producer while the original captured `current-state.json` remains the promotion fence.
3. `transfer_state.py` independently rebuilds the deterministic TAR from each physical Synology shard, compares full archive bytes/SHA-256 with the receiver receipt, runs physical `verify_world_shard`, and only then writes `TRANSFERRED_VERIFIED` marker/evidence.
4. Resume state exports only producer-matching markers with an existing physical bundle, receipt and compact evidence.
5. Matrix shard jobs with durable `TRANSFERRED_VERIFIED` state skip expensive free-disk/build/verify/upload/evidence generation and use preserved Synology evidence instead.
6. Newly transferred and reused shards are physically re-verified on `synology-ots-01` before full-world certification/global bundle/final assembly can proceed.
7. If a physical verification fails, its marker/evidence is removed fail-closed; a later retry is then allowed to rerender only that invalidated shard.
8. Failed/incomplete producer generation is preserved for retry/inspection; successful final deployment cleanup may remove duplicate ingest staging.
9. The workflow still requires explicit `workflow_dispatch`, `deploy_to_synology=true`, exact `main`, and exact `expected_producer_sha` before production deployment admission.

Hard boundaries remain unchanged during PR validation: do not run full 32-shard production render, do not promote `current`, do not restart Atlas, and do not open a public route.

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
- [ ] focused unit/syntax/exact-head CI passes for the hardened production workflow;
- [ ] only after green exact-head validation and normal merge governance, decide whether a clean 32/32 production render may start.

## Context checkpoint

```yaml
checkpoint_version: 2
policy_version: 2
updated_at: 2026-08-17T21:17:00+02:00
head: pending-production-hardening-commit
base: ef9bb701904720004fef745462da14eeac0c4896
status: validating
phase: validate
task_kind: e2e
execution_mode: chat-github
project_lane: otheryn-content
session_role: implementer-validator
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: high
decomposition_decision: phased
decomposition_reason: one-shard proof is complete; validate resumable producer-fenced TRANSFERRED_VERIFIED production contract before any expensive 32/32 production execution
validation_level: focused
heavy_validation_runs: 1
proven:
  - one-shard proof run 32054847514 completed success on exact head f88d0e2d7d4860e1f0f2ea2b2a456de81ceb736e
  - shard 0 source verify passed for 109 chunks with no missing sprites
  - receiver COMPLETE matched 514170880 bytes and 7edfda86139460bc17b1b07037f2b404cc8ec5212c2999dcd39ff5ee60d650c1
  - post-source synology-ots-01 physical verification and deterministic archive identity passed
  - job-scoped GitHub OIDC removes the prior cross-job bearer secret path
blockers: []
next_action: commit production TRANSFERRED_VERIFIED hardening, run focused exact-head CI, and keep 32/32 production execution blocked until those checks and normal merge governance pass
```
