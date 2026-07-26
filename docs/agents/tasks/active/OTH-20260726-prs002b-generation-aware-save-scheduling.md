---
task_id: OTH-20260726-prs002b-generation-aware-save-scheduling
status: validating
branch: dudantas/prs-002b-generation-aware-save-scheduling
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "148"
related_pr: "149"
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
updated_at: 2026-07-26T21:34:00+02:00
head: 4a316ce583e542bdde607507348b0e795ca59c55
branch: dudantas/prs-002b-generation-aware-save-scheduling
pr: 149
status: validating
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
  - PlayerPersistenceState operations are internally synchronized for save-request and worker-acknowledgement races.
  - SaveManager state is keyed by weak_ptr ownership identity, preserving exact Player object generation without GUID reuse.
  - Each accepted asynchronous savePlayer request marks dirty; at most one captured generation is in flight.
  - A newer explicit request coalesces while in flight and is scheduled once after successful older-generation acknowledgement.
  - Failure acknowledges the captured attempt, preserves dirty state and does not trigger automatic retry.
  - GUID/timestamp player coalescing is removed; server-wide m_scheduledAt behavior remains unchanged.
  - saveAll and offline/shutdown synchronous save paths remain structurally unchanged.
derived:
  - A request racing before serialization may cause a conservative follow-up save because the worker acknowledges only its captured generation.
  - Expired weak ownership entries are pruned on later state lookup without conflating a reconnected Player object.
unknown:
  - Broad gameplay mutation coverage and first representative dirty-marking call sites for Slice C.
  - Retry timing, backoff, metrics and operator policy after asynchronous failure.
  - Interaction policy between a server-wide save and an already in-flight per-player generation beyond existing PlayerLock serialization.
conflicts: []
first_failure:
  marker: timestamp-coalescing-has-no-result-ack
  evidence: RESOLVED_IN_BRANCH by exact-owner state, captured generations and result acknowledgement; full ready-head CI remains required.
rejected_hypotheses:
  - Store state by GUID, which can conflate later Player object generations.
  - Add state directly to Player when weak_ptr owner identity keeps this first integration smaller.
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
  - command: standalone C++20 -Wall -Wextra -Werror pthread state concurrency harness
    result: PASS
    evidence: Concurrent dirty marking, single checkpoint ownership and mutation-during-ack semantics passed locally.
  - command: draft-head CI 30216990907 and Required 30216990690
    result: PASS
    evidence: Checkpoint and applicable draft checks passed on implementation head 4a316ce583e542bdde607507348b0e795ca59c55.
  - command: exact-head full repository CI and Required
    result: NOT_RUN
    evidence: Trigger after this checkpoint publication and ready-for-review transition.
blockers: []
next_action: Mark PR 149 ready, require exact-head full CI and Required, fix only Slice B failures, then perform the six-path discussion and main-drift audit before expected-head merge.
```
