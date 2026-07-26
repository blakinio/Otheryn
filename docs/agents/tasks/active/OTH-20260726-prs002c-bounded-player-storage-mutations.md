---
task_id: OTH-20260726-prs002c-bounded-player-storage-mutations
status: validating
branch: dudantas/prs-002c-bounded-player-storage-mutations
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "151"
related_pr: "152"
owned_paths:
  - src/game/scheduling/save_manager.hpp
  - src/creatures/players/components/player_storage.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/agents/tasks/active/OTH-20260726-prs002c-bounded-player-storage-mutations.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/creatures/players/components/player_storage.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
optional_reads:
  - src/io/iologindata.cpp
  - src/creatures/players/components/player_storage.hpp
---

# PRS-002C bounded player storage mutation coverage

## Goal

Instrument only the tracked SQL-backed `PlayerStorage` mutation boundary so an existing in-flight player checkpoint cannot acknowledge an older generation as fully clean after a newer storage change.

## Scope

This slice adds a dirty-generation marker without scheduling a save. It covers tracked storage upserts/removals and explicitly excludes login ingestion, persistence preparation, broad player domains, retry policy and checkpoint timing.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T23:00:00+02:00
head: 408ee8de72badd569b9bc735091726195dcfa643
branch: dudantas/prs-002c-bounded-player-storage-mutations
pr: 152
status: validating
context_routes:
  - production-resilience
  - player-persistence
  - storage-persistence
  - mutation-coverage
  - testing
  - agent-governance
owned_paths:
  - src/game/scheduling/save_manager.hpp
  - src/creatures/players/components/player_storage.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/agents/tasks/active/OTH-20260726-prs002c-bounded-player-storage-mutations.md
proven:
  - PRS-002 discovery, Slice A and Slice B are merged and lifecycle-archived through main commit 7ba0ac1ae6450378ad2fb4f85ccc9026309f902e.
  - SaveManager already owns one generation-aware PlayerPersistenceState per exact Player shared-ownership control block.
  - Successful acknowledgement already schedules one follow-up when a newer generation remains dirty.
  - PlayerStorage ingest calls add with shouldTrackModification false and must not create runtime dirty generations.
  - PlayerStorage tracked add/remove operations produce the SQL storage delta persisted with player data.
  - PR 152 contains exactly the marker, bounded storage instrumentation, source-contract test and active task.
derived:
  - A marker-only SaveManager API can advance the existing exact-owner state without introducing a timer or second scheduling policy.
  - Instrumenting PlayerStorage first is a bounded representative SQL-backed mutation slice and leaves all other domains explicitly unknown.
unknown:
  - Which SQL-backed domain should be instrumented next after storage evidence is accepted.
  - Controlled SQL failure, commit-before-ack and queue-overload behavior reserved for Slice D.
  - Production checkpoint interval, oldest-dirty metrics and measured RPO.
conflicts: []
first_failure:
  marker: storage-mutations-unversioned
  evidence: RESOLVED_IN_BRANCH by marker-only SaveManager API and tracked PlayerStorage add/remove calls; exact-head CI remains required.
rejected_hypotheses:
  - Instrument all Player setters or the monolithic player.cpp in one PR.
  - Make a storage mutation call savePlayer or create a timer.
  - Change existing PRS-002B save-request generation and coalescing semantics in Slice C.
  - Begin PRS-003 outage handling, PRS-004 fencing or production deployment.
changed_paths:
  - src/game/scheduling/save_manager.hpp
  - src/creatures/players/components/player_storage.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/agents/tasks/active/OTH-20260726-prs002c-bounded-player-storage-mutations.md
validation:
  - command: source-first PRS-002C ownership and mutation-boundary inventory
    result: PASS
    evidence: PlayerStorage add/remove own tracked SQL delta changes; ingest explicitly disables modification tracking; SaveManager exact-owner state and follow-up behavior are already merged.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/OTH-20260726-prs002c-bounded-player-storage-mutations.md --require-checkpoint
    result: PASS
    evidence: Compact checkpoint schema, evidence states and limits validated locally after task materialization.
  - command: exact-head full repository CI and Required
    result: NOT_RUN
    evidence: Run after this checkpoint publication and ready-for-review transition.
blockers: []
next_action: Mark PR 152 ready, require exact-head full CI and Required, fix only bounded PRS-002C failures, then perform the four-path discussion and main-drift audit before expected-head merge.
```
