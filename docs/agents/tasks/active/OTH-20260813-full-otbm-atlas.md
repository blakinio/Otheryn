---
task_id: OTH-20260813-full-otbm-atlas
status: implementing
owner: chatgpt-github-20260813
created: 2026-08-13
updated: 2026-08-13T18:17:49+02:00
project_lane: otheryn-content
related_pr: null
ownership_released: false
execution_budget_minutes: 120
execution_budget_reason: canonical full-world rebuild previously required about 56 minutes and must be repeated after render-semantics repair
modules_touched:
  - otbm-atlas
---

# Deterministic full OTBM atlas — continuation

The task is reopened from the repository state produced by PRs #373, #374 and #376 because live GitHub evidence contradicts the terminal closeout recorded by #376. Preserve the canonical vendored map/assets, chunked browser architecture, canonical sprite imagery, `Auto | Detailed | Performance`, bounded caches, factual overlays, and URL/localStorage state.

Verified repair scope:

- exact-detail rendering no longer treats nested container contents as visible map-stack items;
- canonical stack-count and modern-fluid subtype patterns are derived from the pinned OTClient item-pattern rules and decoded appearance flags;
- heuristic Lua table-key promotion to factual UID resolution is removed; only literal UID registrations resolve, while dynamic registrations stay UNKNOWN/UNRESOLVED;
- base-map NPC/monster overlays are separated from verified supplemental event/custom/quest/runtime records;
- atlas public version is 3 so corrected render semantics do not reuse v2 detail-cache fingerprints;
- focused atlas unit/runtime tests now have a dedicated path-filtered GitHub Actions workflow because the repository's generic CI does not execute this suite.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-13T18:17:49+02:00
head: 072abb1be2ec3d7fcf3f1ec986361df5db0b837c
branch: agent/oth-20260813-full-otbm-atlas-repair
pr: none
status: implementing
phase: validate
session_id: chatgpt-github-20260813-001
session_role: implementer
execution_mode: chat-github
execution_reason: GitHub connector plus repository CI is sufficient for source repair; no owner-funded Codex/OpenAI API use is authorized
project_lane: otheryn-content
invocation_started_at: 2026-08-13T17:46:00+02:00
last_progress_at: 2026-08-13T18:17:49+02:00
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
decomposition_reason: one existing atlas task with coupled renderer, factual-index, viewer and full-world evidence
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
  - .github/workflows/otbm-atlas-tests.yml
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
  - docs/agents/tasks/archive/OTH-20260813-full-otbm-atlas.md
  - docs/maps/otbm-atlas-conversation-handover-20260813.md
proven:
  - canonical primary map remains vendor/map-analysis/crystalserver/data-global/world/world.otbm with documented SHA-256 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - PR #374 records the previous successful 3494-chunk Z0..15 full-world build, independent PNG verification and browser E2E
  - current repair excludes nested container descendants from visible render operations while retaining structural statistics
  - current repair decodes appearance cumulative/liquidpool/liquidcontainer flags and follows verified OTClient stack/fluid pattern selection
  - current repair no longer promotes arbitrary Lua table keys to resolved UIDs
  - current repair maps non-base spawn origins to supplementalNpcSpawns/supplementalMonsterSpawns instead of base layers
  - atlas public entrypoint sets core ATLAS_VERSION to 3 before build functions execute
  - focused regression tests cover appearance flags, stack/fluid patterns, nested containers, conservative UID handling and spawn-origin sharding
derived:
  - old v2 full-world PNG/checksum evidence cannot be reused as final evidence for corrected detailed rendering
  - a fresh v3 real-data build or equivalent exhaustive regeneration is required before closeout
unknown:
  - exact full-world v3 output deltas and mechanics-resolution counts after the repairs
  - focused CI result for current repair head
  - independent post-repair auditor identity/result
conflicts:
  - archived task said no action remained while live review/source state proved material work; archive copy was removed on the repair branch and the task is active again
  - PR #375 remains open with stale pre-#374 continuation facts
first_failure:
  marker: unresolved PR #373 findings remained applicable on main
  evidence: current-code source inspection plus live unresolved PR #373 review threads
rejected_hypotheses:
  - all PR #373 findings were superseded by PR #374: current-main inspection disproved this
  - dynamic Lua table keys can be safely inferred as UIDs: rejected in favor of UNKNOWN unless literally registered
changed_paths:
  - tools/otbm_atlas/assets.py
  - tools/otbm_atlas/render.py
  - tools/otbm_atlas/mechanics.py
  - tools/otbm_atlas/spatial.py
  - tools/otbm_atlas/viewer.py
  - tools/otbm_atlas/atlas.py
  - tools/otbm_atlas/_atlas_core.py
  - tools/otbm_atlas/tests/test_assets.py
  - tools/otbm_atlas/tests/test_render.py
  - tools/otbm_atlas/tests/test_mechanics.py
  - tools/otbm_atlas/tests/test_spatial.py
  - .github/workflows/otbm-atlas-tests.yml
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
validation:
  - command: live GitHub inspection of main and PRs #373-#376
    result: PASS
    evidence: main cfa10ad2; material unresolved review/closeout state confirmed
  - command: upstream OTClient source inspection
    result: PASS
    evidence: item.cpp stack/fluid pattern logic plus appearances.proto fields 6/12/19 and const.h fluid enums
blockers: []
next_action: open a repair PR to trigger focused atlas tests and repository CI, repair any failures, then perform fresh v3 real-data validation
```
