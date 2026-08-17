---
task_id: OTH-20260817-atlas-production-4-deployment
status: implementing
owner: chat-github-atlas-deployment
branch: ops/OTH-20260817-atlas-production-4
base_branch: main
created: "2026-08-17T21:57:49+02:00"
updated: "2026-08-17T21:57:49+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "pending"
ownership_released: false
owned_paths:
  - deploy/otbm-atlas-ci-ingest/deployment-request.json
  - docs/agents/tasks/active/OTH-20260817-atlas-production-4-deployment.md
---

# Atlas production deployment request 4

## Goal

Admit one fresh exact-main 32-shard Atlas production generation through the hardened `TRANSFERRED_VERIFIED` GitHub-hosted -> Synology contract merged in PR `#442`.

## Admission boundary

- base main SHA before this request: `4cc2b9189f2fb6264a469a1cf944119c2ad9c8aa`;
- request id: `oth-20260817-atlas-production-4`;
- target: private Synology only;
- full-world certification is mandatory;
- generated corpus is not uploaded as GitHub artifacts;
- merge of the request PR is the audited signal that triggers `.github/workflows/otbm-atlas-deploy-request.yml`;
- that workflow must dispatch `.github/workflows/otbm-atlas-full-world-16.yml` with `deploy_to_synology=true` and `expected_producer_sha` equal to the exact request merge SHA;
- do not reuse failed production run `32032770809` staging;
- public Atlas remains out of scope.

## Required production contract

`BUILD -> VERIFY BUILD -> durable upload -> receiver COMPLETE -> independent Synology archive/corpus re-verification -> TRANSFERRED_VERIFIED -> full-world certification -> ASSEMBLED -> private promotion/runtime health`.

A same-producer retry may reuse only physically re-verified `TRANSFERRED_VERIFIED` shards. Invalid active shard state must remain quarantined and only that shard may rerender.

## Acceptance

- [ ] request PR passes exact-head repository gates;
- [ ] request PR merges through normal governance;
- [ ] deployment-request workflow validates the new request and dispatches the exact merge SHA;
- [ ] canonical plan certifies exactly 3494 chunks / 32 shards;
- [ ] all 32 shard jobs reach successful durable transfer or reuse a physically verified same-producer shard;
- [ ] Synology independently reports all 32 shards `TRANSFERRED_VERIFIED`;
- [ ] full-world certification passes;
- [ ] global publication bundle passes;
- [ ] Synology assembly/publication gate passes;
- [ ] private `current` promotion and Atlas runtime health pass, or exact rollback succeeds;
- [ ] task records final run/generation evidence and releases ownership.

## Context checkpoint

```yaml
checkpoint_version: 2
policy_version: 2
updated_at: 2026-08-17T21:57:49+02:00
head: c4756f4f6a7b6964dfcb0e0e44b6f4b516a469e0
base: 4cc2b9189f2fb6264a469a1cf944119c2ad9c8aa
status: implementing
phase: admit-production
task_kind: e2e
execution_mode: chat-github
project_lane: otheryn-content
session_role: implementer-validator
context_pressure: low
context_growth: stable
context_score: 8
estimate_confidence: high
decomposition_decision: phased
decomposition_reason: use a small audited request PR to trigger the exact-main production workflow; monitor production separately after merge
validation_level: focused
heavy_validation_runs: 0
proven:
  - PR 442 merged hardened producer-fenced TRANSFERRED_VERIFIED production logic to main as 4cc2b9189f2fb6264a469a1cf944119c2ad9c8aa
  - one-real-shard proof run 32054847514 passed build, source verify, OIDC transfer, Synology physical reverify and deterministic archive identity
blockers: []
next_action: open the production request PR, pass required gates, merge it, then verify exact-main deployment dispatch
```
