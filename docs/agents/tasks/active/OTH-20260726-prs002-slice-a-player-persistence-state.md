---
task_id: OTH-20260726-prs002-slice-a-player-persistence-state
status: implementing
branch: dudantas/prs-002-slice-a-player-persistence-state
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "145"
related_pr: "146"
owned_paths:
  - docs/agents/tasks/active/OTH-20260726-prs002-slice-a-player-persistence-state.md
  - src/creatures/players/player_persistence_state.hpp
  - tests/unit/game/prs_002_player_persistence_state_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - src/game/scheduling/save_manager.cpp
  - src/creatures/players
optional_reads:
  - docs/architecture/oam-004d-player-save-failure-propagation.md
---

# PRS-002 Slice A player persistence state

## Goal

Implement the accepted pure, database-independent generation and acknowledgement state machine before any SaveManager integration.

## Accepted transitions

- clean to dirty monotonic generation;
- one coalesced checkpoint capture and at most one in-flight generation;
- mutation during save remains dirty;
- success acknowledges only the captured generation;
- stale acknowledgement is rejected;
- failure preserves dirty state and bounded retry eligibility.

## Explicit non-goals

- no SaveManager integration or mutation instrumentation;
- no checkpoint interval, RPO claim, database, KV, schema or production change;
- no PRS-003 outage state or PRS-004 fencing.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T21:12:00+02:00
head: c47451bd869ea9df31050df3f7a2643d520650ac
branch: dudantas/prs-002-slice-a-player-persistence-state
pr: 146
status: implementing
context_routes:
  - database-persistence
  - player-lifecycle
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260726-prs002-slice-a-player-persistence-state.md
  - src/creatures/players/player_persistence_state.hpp
  - tests/unit/game/prs_002_player_persistence_state_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - PRS-002 discovery contract merged as cb0c51b62abe5e595f744f082ebc4304454922b8.
  - The accepted next package is Slice A only, a pure PlayerPersistenceState with deterministic tests.
  - SaveManager integration, mutation instrumentation, outage handling and session fencing are excluded from this slice.
  - The target state must use monotonic generations rather than scheduling timestamps.
  - Issue 145 and draft PR 146 own the four declared Slice A paths.
derived:
  - A header-only value object can keep Slice A database-independent and avoid build-system changes outside the focused test registration.
unknown:
  - Final method names and token shape that produce the smallest readable API for later SaveManager integration.
  - Exact bounded retry representation required by the deterministic tests.
conflicts: []
first_failure:
  marker: none-yet
  evidence: No Slice A implementation or focused test has run on this branch.
rejected_hypotheses:
  - Reopen the already completed PRS-002 discovery inventory.
  - Integrate the state machine into SaveManager in the same package.
  - Use wall-clock timestamps as dirty generations.
  - Add a checkpoint timer or make an RPO claim.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-prs002-slice-a-player-persistence-state.md
validation:
  - command: live ownership and duplicate-scope audit
    result: PASS
    evidence: Duplicate issue 143 and PR 144 were closed after main showed completed PRS-002 discovery issue 137 and PR 139.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/OTH-20260726-prs002-slice-a-player-persistence-state.md --require-checkpoint
    result: PASS
    evidence: Compact checkpoint schema and evidence-state constraints validated before handoff.
blockers: []
next_action: Implement the pure PlayerPersistenceState header and deterministic Slice A transition tests, then run the focused unit target.
```
