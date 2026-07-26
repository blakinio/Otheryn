---
task_id: OTH-20260726-prs002a-player-persistence-state
status: implementing
branch: dudantas/prs-002a-player-persistence-state
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "141"
related_pr: "none"
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/CMakeLists.txt
  - docs/agents/tasks/active/OTH-20260726-prs002a-player-persistence-state.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/save_manager.hpp
  - tests/unit/game
optional_reads:
  - src/io/iologindata.cpp
---

# PRS-002A player persistence generation state

## Goal

Implement only Slice A from the accepted PRS-002 contract: a pure database-independent state object for dirty generations, one in-flight checkpoint, exact acknowledgement and bounded retry eligibility.

## Scope

This task does not integrate the state into `Player`, `SaveManager`, mutation call sites, databases or production scheduling. Integration is a separate Slice B after this value/state object is proven.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T20:52:00+02:00
head: 5901f0038f7f6ebd6eb08aa4522a23281d27d919
branch: dudantas/prs-002a-player-persistence-state
pr: none
status: implementing
context_routes:
  - production-resilience
  - player-persistence
  - save-scheduling
  - state-machine
  - testing
  - agent-governance
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/CMakeLists.txt
  - docs/agents/tasks/active/OTH-20260726-prs002a-player-persistence-state.md
proven:
  - PRS-002 discovery contract PR 139 merged as cb0c51b62abe5e595f744f082ebc4304454922b8 and lifecycle PR 140 merged as 5901f0038f7f6ebd6eb08aa4522a23281d27d919.
  - Issue 141 owns only the pure PlayerPersistenceState Slice A.
  - The accepted contract requires monotonic dirty generations, exact in-flight acknowledgement, newer mutations remaining dirty and failures preserving dirty state.
  - Session fencing, outage handling, scheduler integration and mutation instrumentation remain separate packages or slices.
derived:
  - A pure state object can prove generation and acknowledgement semantics without database or scheduler dependencies.
  - A caller-supplied failure budget can bound eligibility without embedding timers or retry policy in the state object.
unknown:
  - SaveManager integration shape and ownership of per-player state.
  - Which first mutation call sites should mark the state dirty in Slice C.
  - Timing, backoff, metrics and queue fairness policy for Slice B.
conflicts: []
first_failure:
  marker: generation-state-not-implemented
  evidence: The merged discovery contract defines semantics but main has no reusable PlayerPersistenceState implementation.
rejected_hypotheses:
  - Integrate into SaveManager in the same Slice A PR.
  - Add automatic retries, timers or a checkpoint interval to the pure state object.
  - Reset failure budget silently on every new mutation.
  - Begin PRS-003 outage handling or PRS-004 fencing.
changed_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/CMakeLists.txt
  - docs/agents/tasks/active/OTH-20260726-prs002a-player-persistence-state.md
validation:
  - command: PRS-002 discovery exact-head CI 30214786201 and Required 30214786123
    result: PASS
    evidence: The parent contract and source-characterization tests passed before Slice A started.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/OTH-20260726-prs002a-player-persistence-state.md --require-checkpoint
    result: NOT_RUN
    evidence: Run after the task is materialized on the branch.
  - command: PlayerPersistenceState deterministic unit tests
    result: NOT_RUN
    evidence: Run through exact-head repository CI after the draft PR is opened.
blockers: []
next_action: Commit the pure PlayerPersistenceState and deterministic tests, validate the checkpoint, open a draft PR, and require exact-head CI before any SaveManager integration.
```
