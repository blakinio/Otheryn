---
task_id: OTH-20260814-atlas-factual-source-index
status: completed
owner: openai
branch: agent/oth-20260814-atlas-factual-source-index
base_branch: main
created: 2026-08-14
updated: 2026-08-14T19:15:00+02:00
related_pr: "385"
merge_commit: 2cf8035401a05873c307af7388872141a76309ef
ownership_released: true
modules_touched:
  - otbm-atlas-facts
---

# Factual CrystalServer source index for the atlas

## Delivered

A conservative static-analysis producer now compiles deterministic evidence from the exact pinned CrystalServer corpus already vendored in Otheryn. It does not execute Lua and does not promote uncertain behavior to fact.

Delivered contracts cover:

- literal and simple numeric-table AID/UID registrations plus statically proven scripted teleport destinations;
- explicit monster `rewardBoss` evidence, with path/category retained only as separate provenance and never used alone as boss truth;
- XML raids and statically provable script raid/event areas, point spawns, conditions and monster evidence while dynamic spatial behavior remains `UNKNOWN`;
- NPC shop, bank, guild-bank and statically proven travel-route metadata;
- pinned shared NPC-system semantics for travel and bank helpers;
- deterministic JSON output with `RESOLVED`, `AMBIGUOUS`, `UNRESOLVED` and `UNKNOWN` states and exact source provenance.

## Terminal evidence

```yaml
closeout:
  implementation_complete: true
  vertical_slice_complete: true
  implementation_status: producer_complete
  user_facing_feature_complete: false
  missing_consumers:
    - tools/otbm_atlas spatial and viewer integration
  audit:
    result: PASS
    independent_validator: github-actions clean-runner audit-contract
    workflow_run: 31822755644
    material_findings_open: 0
    remediated_findings:
      - P1 NPC StdModule.travel function-region proof
      - P1 resolved-vs-relative raid provenance root
  e2e:
    result: NOT_APPLICABLE
    reason: non-UI contract producer; complete public boundary is pinned source corpus to deterministic factual JSON
  validation:
    factual_source_index_run: 31822755644
    factual_source_index: PASS
    independent_contract_audit: PASS
    deterministic_double_compile: PASS
    pinned_examples: PASS
    conservative_status_contract: PASS
  final_ci:
    head: 18535002a6de147c24759aba5ec17a2c72b5f5e8
    result: PASS
    required_checks:
      - OTBM Atlas Facts Tests
      - CI
      - Required
  pull_requests:
    terminal_prs:
      - number: 385
        state: merged
        merge_commit: 2cf8035401a05873c307af7388872141a76309ef
    unresolved_review_threads: 0
  provenance:
    crystal_commit: 5e89bf8329ea406cb4ea8f4a18f32954f13e5418
    scripts_tree: 0e3b0102c7d841345dc5b9d4a3b81631930dc362
    raids_tree: 95da7008cf26e5b41ad9f6ef6b5666707feb295c
    npc_system_tree: 8c95fc6faf1dc2c6c573cb57973838897a458a28
```

## Follow-up boundary

The producer is intentionally separate from the user-facing atlas consumer. The next slice may consume these contracts in `tools/otbm_atlas/**` to expose proven scripted teleport links, raid/event regions, verified boss evidence and NPC services while preserving all uncertainty/provenance fields.
