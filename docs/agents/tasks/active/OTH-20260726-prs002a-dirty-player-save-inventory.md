---
task_id: OTH-20260726-prs002a-dirty-player-save-inventory
status: investigating
branch: dudantas/prs-002a-dirty-player-save-inventory
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "143"
related_pr: null
owned_paths:
  - docs/agents/tasks/active/OTH-20260726-prs002a-dirty-player-save-inventory.md
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/save_manager.hpp
  - src/io/iologindata.cpp
  - tests/unit/game/scheduling
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
search_first:
  - src/game/scheduling/save_manager.cpp
  - src/io/iologindata.cpp
  - src/creatures/players/player.hpp
  - tests/unit
optional_reads:
  - docs/architecture/oam-004d-player-save-failure-propagation.md
---

# PRS-002A dirty-player save inventory

## Goal

Establish the current save-entry, synchronization, SQL/KV and failure-propagation boundaries needed to select the smallest safe dirty-generation implementation package.

## Bounded scope

- characterize current player-save entry points and async scheduling behavior;
- record the player lock and object-pinning guarantees;
- distinguish the SQL transaction from post-commit KV staging;
- identify observable failure and unresolved mutation-during-save behavior;
- add focused characterization tests before introducing dirty generations or checkpoint queues.

## Current inventory

- `SaveManager::saveAll()` snapshots the current online-player map, optionally submits one thread-pool future per player, waits for every future and aggregates failures.
- `SaveManager::savePlayer()` schedules online players outside shutdown, but directly saves offline players and shutdown-state players.
- `schedulePlayer()` pins the requesting object through a weak pointer, coalesces by GUID and timestamp, and detached async execution skips an expired object or superseded schedule.
- `doSavePlayer()` takes `Player::PlayerLock`, erases the scheduled marker, executes `IOLoginData::savePlayer()` and returns/logs the result.
- `IOLoginData::savePlayer()` wraps SQL-backed player domains in one `DBTransaction`; Wheel KV staging happens only after SQL commit.
- No dirty generation, saved-generation acknowledgement, oldest-dirty metric or bounded retry policy is present in the inspected save manager boundary.

## Non-goals

- no checkpoint timer or RPO claim;
- no PRS-003 database-outage state machine;
- no multichannel fencing, ledger/outbox or SQL/KV reconciliation framework;
- no production operation or schema change.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T21:08:00+02:00
head: d585c1b8120973d50a3e846fb9e3b063ef3019ff
branch: dudantas/prs-002a-dirty-player-save-inventory
pr: none
status: investigating
context_routes:
  - database-persistence
  - player-lifecycle
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260726-prs002a-dirty-player-save-inventory.md
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/save_manager.hpp
  - src/io/iologindata.cpp
  - tests/unit/game/scheduling
proven:
  - SaveManager saveAll aggregates per-player future failures and returns false when any player save fails.
  - Online non-shutdown savePlayer requests are scheduled; offline or shutdown-state requests call doSavePlayer directly.
  - Detached player saves pin the originally requested Player object and coalesce newer requests by GUID and schedule timestamp.
  - doSavePlayer holds PlayerLock while serializing and propagates the IOLoginData save result to its caller.
  - IOLoginData saves SQL-backed player domains inside one transaction and stages Wheel KV only after SQL commit.
  - The inspected SaveManager boundary has no dirty generation, saved-generation acknowledgement or retry policy.
derived:
  - A dirty-generation design can be attached to the pinned Player object without using GUID re-resolution.
  - Clearing dirty state on request scheduling would be unsafe because scheduling may be superseded or the weak pointer may expire.
unknown:
  - Exact logout, shutdown and explicit gameplay call sites that invoke SaveManager savePlayer or saveAll.
  - Whether every player mutation executes under Player mutex or only serialization does.
  - Which domains mutate after SQL snapshot assembly but before post-commit KV staging.
  - Existing test seams for deterministic IOLoginData failure injection without production database access.
conflicts: []
first_failure:
  marker: none-yet
  evidence: No focused PRS-002A validation has failed; characterization tests have not been added.
rejected_hypotheses:
  - Implement a periodic 60-second checkpoint before inventory and crash proof.
  - Clear dirty state when an async save is merely scheduled.
  - Re-resolve a player by GUID inside detached save work.
  - Merge database-outage or multichannel fencing behavior into PRS-002A.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-prs002a-dirty-player-save-inventory.md
validation:
  - command: source inspection of SaveManager and IOLoginData boundaries
    result: PASS
    evidence: Current main sources establish scheduling, locking, SQL transaction, post-commit KV and failure-return behavior.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/OTH-20260726-prs002a-dirty-player-save-inventory.md --require-checkpoint
    result: NOT_RUN
    evidence: Run after the task record is updated to the published branch head and PR number.
blockers: []
next_action: Add focused characterization tests for superseded async player-save requests and failed save-result propagation without introducing dirty-generation state.
```
