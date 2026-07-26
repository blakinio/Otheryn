---
task_id: OTH-20260726-prs002b-generation-aware-save-scheduling
status: implementing
branch: dudantas/prs-002b-generation-aware-save-scheduling
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "148"
related_pr: "none"
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/agents/tasks/active/OTH-20260726-prs002b-generation-aware-save-scheduling.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
optional_reads:
  - src/io/iologindata.cpp
  - src/creatures/players/player.hpp
---

# PRS-002B generation-aware asynchronous save scheduling

## Goal

Integrate the proven `PlayerPersistenceState` into asynchronous online `savePlayer` request scheduling without broad mutation instrumentation, retry timers or changes to synchronous/server-wide save semantics.

## Scope

This slice replaces GUID/timestamp coalescing only for asynchronous per-player save requests. State ownership is keyed by the exact `Player` shared-ownership control block, and a worker acknowledges only its captured generation after the save result is known.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T21:28:00+02:00
head: 2986c62edf0ffa392c66dd7bec655462d39f5027
branch: dudantas/prs-002b-generation-aware-save-scheduling
pr: none
status: implementing
context_routes:
  - production-resilience
  - player-persistence
  - save-scheduling
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/agents/tasks/active/OTH-20260726-prs002b-generation-aware-save-scheduling.md
proven:
  - PRS-002 discovery contract merged as cb0c51b62abe5e595f744f082ebc4304454922b8.
  - PRS-002A state machine merged as cb1777b145a69e500e3023bc18c45de48a0c7210 and lifecycle completed as 2986c62edf0ffa392c66dd7bec655462d39f5027.
  - Duplicate Slice A PR 146 and issue 145 were closed without modifying their branch after main already contained the completed implementation.
  - Existing async SaveManager coalescing uses player GUID plus wall-clock timestamp and erases that entry before persistence.
  - Exact Player object ownership is already preserved by weak-to-strong pointer capture.
  - saveAll and offline/shutdown saves use separate synchronous doSavePlayer calls and remain outside this slice.
derived:
  - SaveManager-owned state keyed with weak_ptr owner ordering preserves exact object-generation identity without modifying the large Player class.
  - A new explicit save request during an in-flight save can remain dirty and require one follow-up after successful acknowledgement.
  - A failed save can remain dirty without an automatic retry, preserving the later policy boundary.
unknown:
  - Broad gameplay mutation coverage and first representative dirty-marking call sites for Slice C.
  - Retry timing, backoff, metrics and operator policy after asynchronous failure.
  - Interaction policy between a server-wide save and an already in-flight per-player generation beyond existing PlayerLock serialization.
conflicts: []
first_failure:
  marker: timestamp-coalescing-has-no-result-ack
  evidence: SaveManager currently skips by GUID timestamp and does not preserve a newer requested generation or acknowledge the generation associated with the eventual save result.
rejected_hypotheses:
  - Store state by GUID, which can conflate later Player object generations.
  - Add state directly to Player when weak_ptr owner identity can keep this first integration smaller.
  - Automatically retry failed saves or introduce a checkpoint interval in Slice B.
  - Change saveAll, offline save or broad gameplay mutation paths in this package.
changed_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/agents/tasks/active/OTH-20260726-prs002b-generation-aware-save-scheduling.md
validation:
  - command: PRS-002A exact-head CI 30215762245 and Required 30215762190
    result: PASS
    evidence: The pure state machine and its deterministic transitions passed before runtime integration started.
  - command: source-first SaveManager ownership and concurrency inventory
    result: PASS
    evidence: Exact source establishes weak_ptr object pinning, GUID/timestamp coalescing, detached worker execution and synchronous saveAll/offline boundaries.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/OTH-20260726-prs002b-generation-aware-save-scheduling.md --require-checkpoint
    result: NOT_RUN
    evidence: Run after implementation is materialized on the working branch.
  - command: exact-head state and SaveManager contract tests
    result: NOT_RUN
    evidence: Run through repository CI after the draft PR is opened.
blockers: []
next_action: Commit the thread-safe state and generation-aware asynchronous SaveManager integration, validate the checkpoint, open a draft PR, and run exact-head CI without expanding into mutation instrumentation or retry policy.
```
