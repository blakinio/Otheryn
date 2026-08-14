---
task_id: OTH-20260814-atlas-factual-source-index
status: in_progress
owner: openai
branch: agent/oth-20260814-atlas-factual-source-index
base_branch: agent/oth-20260814-atlas-supplemental-sources
created: 2026-08-14
updated: 2026-08-14
owned_paths:
  - tools/otbm_atlas_facts/**
  - docs/agents/tasks/active/OTH-20260814-atlas-factual-source-index.md
required_reads:
  - AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
---

# Factual CrystalServer source index for the atlas

## Goal

Build a conservative static-analysis package for the exact pinned CrystalServer corpus imported by #383. The package does not modify `tools/otbm_atlas/**` while #381 owns that path. It produces evidence-bearing facts that can later be wired into atlas spatial layers.

## Scope

- literal and simple numeric-table AID/UID registrations plus statically proven scripted teleport destinations;
- explicit monster `rewardBoss` metadata without treating directory names as boss truth;
- XML raids, static Lua `Raid`/`Zone` areas, and partial inventories for dynamic world events;
- NPC shop/bank/guild-bank/travel service metadata from already-vendored NPC scripts;
- `RESOLVED`, `AMBIGUOUS`, `UNRESOLVED` and `UNKNOWN` states with exact source paths.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-14T09:45:00+02:00
branch: agent/oth-20260814-atlas-factual-source-index
status: in_progress
base: e5b93971239806b20eb2a7510da0b69711f4322d
proven:
  - supplemental source trees are exact pinned CrystalServer trees on the stacked base
  - representative parser prototypes resolve Kazordoon elevator AIDs 50011/50012 and Fibula loop-registered AIDs 50390/50391 to exact destinations
  - representative NPC prototypes identify Ray shop, Naji bank/guild-bank and Captain Bluebear travel routes
  - raid prototype distinguishes XML spatial raids, static Lua Raid/Zone areas and dynamic events with UNKNOWN spatial status
constraints:
  - do not touch tools/otbm_atlas/** until #381 releases ownership
  - never classify a boss solely from path/name
  - never turn conditional scripted transitions into unconditional routing claims
blockers: []
next_action: commit the source-analysis package and validate it against exact vendored CrystalServer samples
```
