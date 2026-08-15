---
task_id: OTH-20260814-atlas-factual-source-index
status: completed
owner: none
branch: agent/oth-20260814-atlas-factual-source-index
base_branch: main
created: 2026-08-14
updated: 2026-08-15T12:22:00+02:00
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "385"
merge_commit: 2cf8035401a05873c307af7388872141a76309ef
ownership_released: true
---

# Factual CrystalServer source index for the atlas — archived

Final disposition: **completed, merged and consumed by the production atlas**.

PR #385 implemented the conservative deterministic factual-source producer against the exact pinned CrystalServer corpus. It preserves `RESOLVED`, `AMBIGUOUS`, `UNRESOLVED` and `UNKNOWN` evidence instead of executing Lua or promoting uncertain behavior to fact.

Delivered producer contracts cover static AID/UID mechanics, proven scripted teleport destinations, explicit `rewardBoss` evidence, raid/event areas and point spawns, and NPC shop/bank/guild-bank/travel evidence with exact provenance.

PR #390 subsequently consumed this producer in `tools/otbm_atlas/**`, closing the original producer/consumer boundary. The historical closeout PR #388 was closed as superseded on 2026-08-15 because its missing-consumer P1 is no longer applicable and its unique archive intent is preserved here.

## Terminal evidence

```yaml
closeout:
  implementation_complete: true
  vertical_slice_complete: true
  producer:
    pr: 385
    merge_commit: 2cf8035401a05873c307af7388872141a76309ef
    exact_head: 18535002a6de147c24759aba5ec17a2c72b5f5e8
    deterministic_double_compile: PASS
    conservative_status_contract: PASS
    independent_pinned_fact_audit: PASS
  consumer:
    pr: 390
    merge_commit: 2bfacdd8349003aaa9675604269b8ae8004c19a6
    production_atlas_integration: PASS
  audit:
    result: PASS
    material_findings_open: 0
  e2e:
    result: PASS
    journeys:
      - pinned CrystalServer source corpus to deterministic factual JSON
      - deterministic factual JSON to production chunked atlas layers
  pull_requests:
    open_related_prs: 0
    terminal_prs:
      - number: 385
        state: merged
        merge_commit: 2cf8035401a05873c307af7388872141a76309ef
      - number: 388
        state: closed_superseded
      - number: 390
        state: merged
        merge_commit: 2bfacdd8349003aaa9675604269b8ae8004c19a6
  task_status: completed
  task_archived: true
  ownership_released: true
  stale_branches_reconciled: true
```

No factual-source-index work remains schedulable under `docs/agents/tasks/active/`.
