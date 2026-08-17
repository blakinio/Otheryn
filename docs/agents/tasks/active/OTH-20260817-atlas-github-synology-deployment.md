---
task_id: OTH-20260817-atlas-github-synology-deployment
status: implementing
owner: chat-github-atlas-deployment
branch: fix/OTH-20260817-atlas-durable-shard-transfer
base_branch: main
created: "2026-08-17T11:02:00+02:00"
updated: "2026-08-17T17:14:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "pending"
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

The current continuation is deliberately bounded: record the recovery decision, prove exactly one fresh real shard end-to-end, and do not authorize a new 32-shard production render until that proof is understood.

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
4. Do not start another full 32-shard production render yet.
5. First run exactly one real shard in a fresh test generation.
6. Keep approximately 48 MiB transfer parts; smaller parts are not the primary fix.
7. A source GitHub-hosted runner must not be considered safely releasable until Synology has independently confirmed the complete shard is durably present and content-equivalent.

## Target per-shard contract

The production contract to prove before a clean 32-shard rebuild is:

```text
BUILD
-> VERIFY BUILD
-> deterministic shard-XX.tar
-> split ~48 MiB parts
-> upload + per-part SHA ACK
-> durable Synology persistence
-> reconstruct complete archive
-> independent full archive SHA-256 match
-> TRANSFERRED_VERIFIED
-> source runner may finish
-> later extraction/assembly
-> ASSEMBLED
```

State meanings:

- `BUILT_VERIFIED`: generated corpus passed source-side independent verification;
- `TRANSFERRED_VERIFIED`: Synology durably holds the complete shard and independently matches the source archive identity;
- `ASSEMBLED`: persisted shard has been safely materialized into the world corpus.

A retry after `TRANSFERRED_VERIFIED` must never imply rerender. Extraction/assembly failure must not destroy the persisted rendered result.

## Bounded one-shard proof

The first proof uses exactly one real shard and a fresh generation under `/volume1/docker/otheryn/atlas/ci-ingest-tests/`.

Proof requirements:

- no old failed-run staging is read or reused;
- plan the canonical 32-way assignment, but build only shard `0`;
- run `verify_world_shard` before transfer;
- use the existing 48 MiB uploader parts;
- source hosted job must wait for a positive Synology completion receipt;
- after the hosted source job has ended, a separate `synology-ots-01` job independently verifies the received physical corpus and receipt;
- record exact producer SHA, bytes, part count and SHA evidence in workflow logs;
- clean only the exact disposable test generation after post-source verification;
- this proof does not publish, promote `current`, restart Atlas, or run a full-world build.

The first proof may use the currently available authenticated Quick Tunnel only as a bounded transport baseline. A pass validates one-shard transfer/reverification behavior; it does **not** approve Quick Tunnel as the final 16-19 GiB production bulk transport. The production transport decision remains gated on this evidence and must remain resumable/idempotent/SHA-verified.

## Prior implementation history

PR `#435` (`feat(atlas): deploy certified world to Synology`) merged the original receiver/uploader/full-world deployment architecture. PR `#441` (`fix(atlas): stage receiver repo without namespace initializer`) fixed the concrete receiver staging failure and produced the failed transport-heavy production run above.

The previous task checkpoint predates those post-merge production attempts and is superseded by this continuation checkpoint.

## Acceptance for this continuation phase

- [x] failed-run cause boundary rechecked against run `32032770809` and current receiver/uploader code;
- [x] owner decision recorded: old failed-run NAS staging is non-canonical and will not be reused;
- [x] clean rebuild is blocked behind a one-real-shard proof;
- [ ] dedicated branch + draft PR exists for the proof;
- [ ] exactly one real shard builds and passes source-side independent verification;
- [ ] hosted runner receives positive Synology completion evidence before it exits;
- [ ] separate post-source Synology job independently verifies the physical shard corpus/receipt;
- [ ] exact one-shard proof evidence is recorded here;
- [ ] production `TRANSFERRED_VERIFIED` implementation/transport design is updated from proof evidence;
- [ ] only after that, decide whether a clean 32/32 production render may start.

## Context checkpoint

```yaml
checkpoint_version: 2
policy_version: 2
updated_at: 2026-08-17T17:14:00+02:00
head: pending
base: ef9bb701904720004fef745462da14eeac0c4896
status: implementing
phase: validate
task_kind: e2e
execution_mode: chat-github
project_lane: otheryn-content
session_role: implementer-validator
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: medium
decomposition_decision: phased
decomposition_reason: one cohesive deployment task; gather one-shard physical evidence before changing the production transport contract
validation_level: focused
heavy_validation_runs: 0
proven:
  - run 32032770809 used exact producer 0be8c1d88767d58dc08676525c8dbfd77b016d99
  - hosted shard build and independent verification succeeded before representative HTTP 524 transport failures
  - hosted runner to synology-ots-01 reachability is physically proven by successful shards
  - current receiver stores 48 MiB parts durably and serializes reconstruction plus extraction under a global completion lock
  - owner explicitly rejects old failed-run staging as an input to the next production generation
blockers: []
next_action: open a draft PR and run exactly one fresh real shard through the bounded hosted-to-Synology transfer proof
```
