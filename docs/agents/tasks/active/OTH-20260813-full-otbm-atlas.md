---
task_id: OTH-20260813-full-otbm-atlas
status: implementing
owner: chatgpt-github-20260813
created: 2026-08-13
updated: 2026-08-13T18:33:45+02:00
project_lane: otheryn-content
related_pr: "377"
ownership_released: false
execution_budget_minutes: 120
execution_budget_reason: fresh full-world generation is required after detailed-render semantics changed
modules_touched:
  - otbm-atlas
---

# Deterministic full OTBM atlas — continuation

This task was reopened because live repository state contradicted the terminal closeout recorded by PR #376. Current work is on PR #377.

## Current verified repair

- nested container contents are counted/indexed but no longer drawn as visible tile-stack sprites;
- stackable and splash/fluid sprite patterns use decoded canonical appearance flags plus the OTBM subtype/count, cross-checked against pinned OTClient semantics;
- broad Lua numeric-table UID inference was removed; only literal numeric AID/UID registrations resolve, while dynamic/indexed cases remain UNKNOWN/UNRESOLVED;
- base-map NPC/monster spatial layers are separated from supplemental event/custom/quest/runtime records;
- atlas version is 3, preventing reuse of v2 detailed-render fingerprints;
- dedicated atlas CI covers unit/runtime tests plus canonical Thais scan/render;
- `ci:final-gate` now gates a fresh 3494-chunk full-world v3 build and independent `verify.py` pass.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-13T18:33:45+02:00
head: 5e63c53b25373c819b260b7fc063244f0597f2d2
branch: agent/oth-20260813-full-otbm-atlas-repair
pr: 377
status: implementing
phase: validate
session_id: chatgpt-github-20260813-001
session_role: implementer
execution_mode: chat-github
execution_reason: GitHub connector and repository CI are sufficient; no owner-funded Codex/OpenAI API use is authorized
project_lane: otheryn-content
invocation_started_at: 2026-08-13T17:46:00+02:00
last_progress_at: 2026-08-13T18:33:45+02:00
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
decomposition_reason: one integrated atlas delivery with renderer, factual indexes, viewer and full-world evidence gates
context_routes:
  - AGENTS.md
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - tools/otbm_atlas/README.md
  - docs/maps/crystalserver-canonical-source.md
  - vendor/map-analysis/README.md
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-atlas-tests.yml
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
  - docs/agents/tasks/archive/OTH-20260813-full-otbm-atlas.md
proven:
  - canonical world SHA-256 is 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - PR #374 previously proved a 3494-chunk Z0..15 v2 full-world build and browser E2E
  - PR #377 head 810ed860c812710134c200a23b865585d993cacb passed 37 focused atlas tests plus Required, CI and autofix.ci
  - later canonical-data runs passed the real Thais scan against the canonical fingerprint
  - tools/otbm_atlas/README.md documents current v3 renderer, spawn-origin and mechanics-resolution semantics
derived:
  - old v2 PNG/checksum evidence is not final proof for corrected v3 detailed rendering
unknown:
  - exact full-world v3 render/statistics deltas
  - exact-head canonical Thais render result after latest commits
  - independent post-repair auditor identity/result
  - terminal disposition of stale handover PR #375
conflicts:
  - PR #375 remains open with stale pre-#374 continuation state and must become terminal before closeout
  - PR #376 closeout lacked the independent-auditor evidence required by current governance
first_failure:
  marker: material PR #373 review findings remained applicable on main after prior closeout
  evidence: live review threads plus direct inspection of current-main render/spawn/mechanics code
rejected_hypotheses:
  - all PR #373 findings were superseded by PR #374
  - broad Lua numeric table-key discovery is safe factual UID evidence
changed_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-atlas-tests.yml
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
validation:
  - command: OTBM Atlas Tests run 31720019319 on 810ed860c812710134c200a23b865585d993cacb
    result: PASS
    evidence: 37 tests, zero failures
  - command: Required/CI/autofix.ci on 810ed860c812710134c200a23b865585d993cacb
    result: PASS
    evidence: all applicable checks successful
blockers: []
next_action: collect exact-head unit/canonical CI, apply ci:final-gate to PR #377, then collect full-world v3 build and independent verifier evidence
```
