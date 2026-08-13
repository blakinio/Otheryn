---
task_id: OTH-20260813-full-otbm-atlas
status: implementing
owner: chatgpt-github-20260813
created: 2026-08-13
updated: 2026-08-13T17:56:09+02:00
project_lane: otheryn-content
related_pr: null
ownership_released: false
modules_touched:
  - otbm-atlas
---

# Deterministic full OTBM atlas — continuation

The task is reopened from the repository state produced by PRs #373, #374 and #376 because live GitHub evidence contradicts the terminal closeout recorded by #376. Preserve the canonical vendored map/assets, chunked browser architecture, canonical sprite imagery, `Auto | Detailed | Performance`, bounded caches, factual overlays, and URL/localStorage state.

Current verified gaps on `main` `cfa10ad2a70d7980bc0e959b9c591b6d0c6edfa9`:

- PR #373 is merged but has unresolved review threads. Current code still mixes supplemental spawn origins into the same base creature layers, renders nested container contents as visible tile sprites, and can collect unrelated numeric table keys as UID dispatch keys.
- PR #374 is merged; its two review findings are resolved and it contains the successful full-world build/E2E evidence.
- PR #376 is merged but has two unresolved closeout findings: independent-validator evidence is missing and the terminal PR inventory omitted the lifecycle PR.
- PR #375 remains open with a handover document whose continuation-point facts predate PR #374; it must be reconciled rather than merged unchanged.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-13T17:56:09+02:00
head: cfa10ad2a70d7980bc0e959b9c591b6d0c6edfa9
branch: agent/oth-20260813-full-otbm-atlas-repair
pr: none
status: implementing
phase: implement
session_id: chatgpt-github-20260813-001
session_role: implementer
execution_mode: chat-github
execution_reason: GitHub connector plus repository CI is sufficient for this bounded repair phase
project_lane: otheryn-content
invocation_started_at: 2026-08-13T17:46:00+02:00
last_progress_at: 2026-08-13T17:56:09+02:00
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 1
stall_warnings: 0
context_pressure: high
context_growth: stable
context_score: 10
decomposition_decision: phased
decomposition_reason: one existing atlas task with coupled renderer, factual-index and viewer semantics
context_routes:
  - AGENTS.md
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/CONTEXT_HANDOFF.md
  - tools/otbm_atlas/README.md
  - docs/maps/crystalserver-canonical-source.md
  - vendor/map-analysis/README.md
owned_paths:
  - tools/otbm_atlas/**
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
  - docs/agents/tasks/archive/OTH-20260813-full-otbm-atlas.md
  - docs/maps/otbm-atlas-conversation-handover-20260813.md
proven:
  - canonical primary map remains vendor/map-analysis/crystalserver/data-global/world/world.otbm with documented SHA-256 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - PR #374 records a successful 3494-chunk Z0..15 full-world build, independent PNG verification and browser E2E
  - current render.py flattens walk_items(tile.items) into the visible render list
  - current spawns.py aggregates base and supplemental spawn XML into the same monsterSpawns/npcSpawns arrays while retaining origin metadata
  - current mechanics.py finds any UID-dispatch expression then applies TABLE_KEY across the entire file
  - PR #376 has two unresolved closeout threads and PR #375 is open
derived:
  - the archived terminal completion claim is not valid under current live repository state
  - renderer and mechanics repairs change generated output semantics and require affected revalidation
unknown:
  - exact generated-data deltas after the repairs
  - independent post-repair audit result
conflicts:
  - archived task says no action remains while live review and source state prove open material work
first_failure:
  marker: unresolved PR #373 findings remain applicable on current main
  evidence: live PR #373 review threads plus current render.py, spawns.py and mechanics.py
rejected_hypotheses:
  - all PR #373 findings were superseded by PR #374: three remain reproducible by source inspection
changed_paths:
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
validation:
  - command: live GitHub inspection of main and PRs #373-#376
    result: PASS
    evidence: main cfa10ad2; #373 and #376 have unresolved material threads; #375 is open
blockers: []
next_action: repair renderer, spawn-layer and UID-resolution semantics with focused regression tests
```
