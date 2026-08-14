---
task_id: OTH-20260814-atlas-factual-source-index
status: validating
owner: openai
branch: agent/oth-20260814-atlas-factual-source-index
base_branch: main
created: 2026-08-14
updated: 2026-08-14T18:50:00+02:00
related_pr: "385"
owned_paths:
  - tools/otbm_atlas_facts/**
  - .github/workflows/otbm-atlas-facts-tests.yml
  - docs/agents/tasks/active/OTH-20260814-atlas-factual-source-index.md
required_reads:
  - AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
---

# Factual CrystalServer source index for the atlas

## Goal

Build a conservative static-analysis package for the exact pinned CrystalServer corpus now present on `main`. It produces evidence-bearing facts for later atlas spatial/UI integration without executing Lua or guessing dynamic behavior.

## Scope

- literal and simple numeric-table AID/UID registrations plus statically proven scripted teleport destinations;
- explicit monster `rewardBoss` metadata kept separate from definition-path/category evidence;
- XML raids, static Lua raid/event evidence, exact single-spawn positions, bounded area-spawn rectangles, and UNKNOWN spatial status where dynamic behavior is not provable;
- NPC shop/bank/guild-bank/travel service metadata from already-vendored NPC scripts;
- pinned shared NPC-system semantics for travel/bank helpers;
- `RESOLVED`, `AMBIGUOUS`, `UNRESOLVED` and `UNKNOWN` states with exact source provenance.

## Context checkpoint

```yaml
checkpoint_version: 2
updated_at: 2026-08-14T18:50:00+02:00
branch: agent/oth-20260814-atlas-factual-source-index
pr: 385
status: validating
base_main: 80e07b9afece08506c1fe401f20df073c93833f1
proven:
  - PR 383 is merged and the supplemental source trees are canonical on main
  - Kazordoon elevator AIDs 50011/50012 and Fibula loop AIDs 50390/50391 resolve to exact static destinations
  - Pythius The Rotten has explicit rewardBoss=true while Rat resolves false; path/category is retained only as independent evidence
  - Thais Orc raid produces factual areas/single spawns and dynamic scripted events remain UNKNOWN when spatial truth cannot be proven
  - Ray shop, Naji bank/guild-bank and Captain Bluebear travel routes are extracted from pinned NPC definitions
  - pinned npclib proves StdModule travel/bank helper semantics used by those NPC definitions
constraints:
  - do not execute Lua
  - never classify a boss solely from path or name
  - never turn conditional scripted transitions into unconditional routing claims
  - do not touch tools/otbm_atlas/** while PR 386 owns overlapping atlas runtime paths
blockers: []
next_action: reconcile PR 385 onto current main without retaining already-merged vendor history, run exact-head factual-index CI and independent audit, then merge and archive this task
```
