---
task_id: OTH-20260817-atlas-controlled-distribution-prep
status: in_progress
owner: chat-github-atlas-distribution-prep
branch: feat/OTH-20260817-atlas-controlled-distribution-prep
base_branch: main
created: "2026-08-17T10:23:00+02:00"
updated: "2026-08-17T10:23:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: none
ownership_released: false
owned_paths:
  - deploy/otbm-atlas-controlled-beta/**
  - .github/workflows/otbm-atlas-controlled-beta.yml
  - docs/agents/tasks/active/OTH-20260817-atlas-controlled-distribution-prep.md
---

# OTBM Atlas controlled distribution preparation

## Goal

Prepare a fail-closed path from the existing private Synology Atlas origin toward controlled user access without publishing or uploading the generated Atlas corpus and without bypassing the existing redistribution-review requirement.

This is a bounded implementation subtask of `OTH-20260815-otbm-atlas-product-readiness`; it does not replace or duplicate that broader product-readiness task.

## Admission and boundaries

- live base at admission: `e1d83cd74496ebc09587a46243673b437968c807`;
- no open Atlas Cloudflare/Internet-distribution PR existed at admission;
- canonical Atlas remains v3, chunk size 128, 3494 chunks, map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`;
- existing private Synology runtime package remains canonical origin baseline;
- existing desktop corpus transfer blocker remains unchanged;
- no Synology full-world build is authorized;
- no generated Atlas corpus may be committed or uploaded as a GitHub Actions artifact;
- no GitHub Pages, R2/CDN/object-storage publication is authorized by this task;
- no public hostname, Cloudflare route or Internet port-forward may be activated by this task;
- ATLAS-PR-009 remains mandatory before any Internet-facing mode, including authenticated beta access;
- no owner-funded Codex/OpenAI/paid AI quota is used.

## Implementation

- add `deploy/otbm-atlas-controlled-beta/publication_gate.py`;
- require `FULL_RUNTIME_READY` plus canonical identity/current viewer/READY spatial, inspector, creature and environment state and successful independent verification;
- model `private-local`, `internet-authenticated` and `internet-public` explicitly;
- fail closed for both Internet-facing modes unless an exact-scope ATLAS-PR-009 approval record is supplied;
- ship only an `approved: false` approval schema template;
- document the intended post-approval Cloudflare Access + Tunnel beta topology while preserving origin `Cache-Control: private` and no edge/object-storage caching;
- add focused publication-gate tests and a dedicated lightweight workflow.

## Acceptance

- [x] private-local full-runtime report can pass without redistribution approval;
- [x] authenticated Internet mode fails without ATLAS-PR-009;
- [x] public Internet mode fails without ATLAS-PR-009;
- [x] false approval template cannot authorize release;
- [x] approval scope must match the requested Internet mode exactly;
- [x] non-canonical world identity blocks publication;
- [x] CORE_PREVIEW_READY is insufficient for controlled user distribution;
- [ ] exact-head focused workflow PASS;
- [ ] repository Required/CI applicable gate PASS;
- [ ] fresh diff audit has zero material findings;
- [ ] merge to main and post-merge reread;
- [ ] task archived and ownership released.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-17T10:23:00+02:00
head: 81f169f889358a932e96d19c4a2b31291b811838
base: e1d83cd74496ebc09587a46243673b437968c807
status: in_progress
phase: exact-head-validation
proven:
  - existing product-readiness backlog requires ATLAS-PR-009 before any Internet-facing release
  - existing Synology origin package is read-only/non-root and private
  - Cloudflare current documentation supports Access-protected self-hosted apps and outbound Tunnel connectivity
  - publication gate unit tests pass locally: 7/7
blockers:
  - broader product readiness still needs desktop build/full-map-atlas transfer to Synology
  - real Internet-facing activation remains blocked on ATLAS-PR-009 review
next_action: open the bounded PR, run focused workflow plus applicable repository gates, audit exact diff, merge if green, then archive this prep task without activating Internet exposure
```
