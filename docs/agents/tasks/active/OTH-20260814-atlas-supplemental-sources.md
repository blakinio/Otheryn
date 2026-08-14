---
task_id: OTH-20260814-atlas-supplemental-sources
status: in_progress
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
  - .github/workflows/import-crystal-atlas-supplemental-sources.yml
  - docs/agents/tasks/active/OTH-20260814-atlas-supplemental-sources.md
required_reads:
  - AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
---

# CrystalServer atlas supplemental sources

## Goal

Vendor the exact pinned CrystalServer source trees needed to prove scripted map mechanics, raids/events, and shared NPC service semantics without changing `tools/otbm_atlas/**` while PR #381 owns the atlas implementation.

## Pinned provenance

- repository: `zimbadev/crystalserver`
- commit: `5e89bf8329ea406cb4ea8f4a18f32954f13e5418`
- `data-global/scripts/**`: `0e3b0102c7d841345dc5b9d4a3b81631930dc362`
- `data-global/raids/**`: `95da7008cf26e5b41ad9f6ef6b5666707feb295c`
- `data/npclib/npc_system/**`: `8c95fc6faf1dc2c6c573cb57973838897a458a28`

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-14T09:29:00+02:00
branch: agent/oth-20260814-atlas-supplemental-sources
status: in_progress
proven:
  - canonical world, monster and NPC source trees are already vendored
  - atlas mechanics resolver must ultimately use sources from the same pinned CrystalServer revision as the map
  - CrystalServer raids encode explicit event regions, single spawns, delays and monster identities
  - vendored NPC definitions already contain shop, bank and travel behavior; shared npclib is only needed to prove helper semantics
unknown:
  - final imported file count and byte total for the three supplemental trees
blockers: []
next_action: run a one-shot exact-tree import with deterministic manifest, verify tree SHAs, remove the importer workflow, then open a data-only PR
```
