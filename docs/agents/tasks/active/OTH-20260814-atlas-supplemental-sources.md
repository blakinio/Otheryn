---
task_id: OTH-20260814-atlas-supplemental-sources
status: validating
owner: openai
branch: agent/oth-20260814-atlas-supplemental-sources
base_branch: main
created: 2026-08-14
updated: 2026-08-14
owned_paths:
  - vendor/map-analysis/crystalserver/data-global/scripts/**
  - vendor/map-analysis/crystalserver/data-global/raids/**
  - vendor/map-analysis/crystalserver/data/npclib/npc_system/**
  - vendor/map-analysis/crystalserver/SUPPLEMENTAL_SOURCES.md
  - vendor/map-analysis/crystalserver/supplemental-sources-manifest.json
  - docs/agents/tasks/active/OTH-20260814-atlas-supplemental-sources.md
required_reads:
  - AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
---

# CrystalServer atlas supplemental sources

## Goal

Vendor the exact pinned CrystalServer source trees needed to prove scripted map mechanics, raids/events, and shared NPC service semantics without changing `tools/otbm_atlas/**`.

## Pinned provenance

- repository: `zimbadev/crystalserver`
- commit: `5e89bf8329ea406cb4ea8f4a18f32954f13e5418`
- `data-global/scripts/**`: `0e3b0102c7d841345dc5b9d4a3b81631930dc362`
- `data-global/raids/**`: `95da7008cf26e5b41ad9f6ef6b5666707feb295c`
- `data/npclib/npc_system/**`: `8c95fc6faf1dc2c6c573cb57973838897a458a28`

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-14T17:09:00+02:00
branch: agent/oth-20260814-atlas-supplemental-sources
status: validating
reconciled_with_main: 1021d08978f078ff845e6f3f82fbbbc482cbf543
reconcile_commit: 0b5a4f5888d303ba2159202a6af7f5b19c5277f1
validated_source_manifest_blob: 89f4cf958c6f4d27c8664997d65ad5b2adb7c1e4
proven:
  - one-shot import workflow 31780269499 completed SUCCESS
  - data-global/scripts has exact upstream tree 0e3b0102c7d841345dc5b9d4a3b81631930dc362
  - data-global/raids has exact upstream tree 95da7008cf26e5b41ad9f6ef6b5666707feb295c
  - data/npclib/npc_system has exact upstream tree 8c95fc6faf1dc2c6c573cb57973838897a458a28
  - deterministic manifest contains 2054 files totaling 3285973 bytes
  - manifest content fingerprint is c599e44454b3cd2ec0378f2b1ba296f0858db2f9c683d60ec1da19ffdc672f92
  - scope counts are scripts=1897, raids=152, npc_system=5
  - one-shot importer workflow was removed after successful import
  - PR 381 is merged and this branch is reconciled with its merge commit
  - full per-file manifest was reverified after reconcile and remains exact blob 89f4cf958c6f4d27c8664997d65ad5b2adb7c1e4
unknown:
  - exact-head Required conclusion for this checkpoint commit
blockers: []
next_action: require exact-head Required, audit PR diff/review threads, then merge PR 383 if green
```
