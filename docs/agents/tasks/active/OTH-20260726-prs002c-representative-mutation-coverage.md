---
task_id: OTH-20260726-prs002c-representative-mutation-coverage
status: ready
branch: dudantas/prs-002c-representative-mutation-coverage
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "159"
related_pr: "none"
owned_paths:
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/creatures/players/player.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260726-prs002c-representative-mutation-coverage.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/creatures/players/player.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
optional_reads:
  - src/io/iologindata.cpp
  - src/creatures/players/player.hpp
---

# PRS-002C representative mutation coverage

## Goal

Add the first bounded mutation-driven dirty coverage on top of the merged PRS-002A/B generation state and asynchronous scheduling integration.

## Scope

Expose dirty marking without implicit scheduling, select a deliberately small representative set of persistence-relevant `Player` mutations from source evidence, and prove that a mutation racing an in-flight explicit save remains pending for the existing success-follow-up path.

## Explicit non-goals

- no broad mutation sweep or claim of complete persistence coverage;
- no checkpoint interval, automatic retry, backoff, metrics backend or RPO claim;
- no database, KV, schema or deployment change;
- no PRS-003 outage state or PRS-004 fencing;
- no change to `saveAll`, offline save or shutdown behavior.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T00:05:00+02:00
head: 13329031712325045302c51ddf5c74a6962fb770
branch: dudantas/prs-002c-representative-mutation-coverage
pr: none
status: ready
context_routes:
  - production-resilience
  - player-persistence
  - save-scheduling
  - mutation-coverage
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/creatures/players/player.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260726-prs002c-representative-mutation-coverage.md
proven:
  - PRS-002 discovery contract merged as cb0c51b62abe5e595f744f082ebc4304454922b8.
  - PRS-002A state machine merged as cb1777b145a69e500e3023bc18c45de48a0c7210.
  - PRS-002B generation-aware asynchronous save scheduling merged as b9d35d160019895a4ee9631177eb72dd491af569 and lifecycle completed as 7ba0ac1ae6450378ad2fb4f85ccc9026309f902e.
  - SaveManager already owns exact-Player-object generation state, allows one asynchronous checkpoint in flight, coalesces newer explicit requests, acknowledges exact generations and follows up only after success.
  - Failed asynchronous saves preserve dirty state without automatic retry.
  - Issue 159 owns only bounded representative mutation coverage.
derived:
  - Dirty marking can advance the existing exact-owner state without scheduling work by itself.
  - A mutation during an in-flight explicit save can reuse the existing successful acknowledgement follow-up path.
  - The first instrumented call sites must be explicitly documented as partial coverage.
unknown:
  - Which smallest representative mutation set provides useful coverage with low regression risk.
  - Whether any candidate mutation runs before the Player object is fully registered with SaveManager ownership state.
  - The eventual complete mutation inventory and checkpoint interval policy.
conflicts: []
first_failure:
  marker: mutation-paths-do-not-advance-dirty-generation
  evidence: PRS-002B advances generations only for accepted explicit asynchronous savePlayer requests; ordinary persistence-relevant Player mutations remain uninstrumented.
rejected_hypotheses:
  - Instrument every Player mutation in one package.
  - Make markPlayerDirty schedule a save or introduce a periodic timer.
  - Treat the first representative call sites as complete PRS-002 coverage.
  - Begin retry policy, outage handling or session fencing in this slice.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-prs002c-representative-mutation-coverage.md
validation:
  - command: live main and ownership audit
    result: PASS
    evidence: Main is 7ba0ac1ae6450378ad2fb4f85ccc9026309f902e; no open PR or issue owned PRS-002C before issue 159 and this branch were created.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/OTH-20260726-prs002c-representative-mutation-coverage.md --require-checkpoint
    result: NOT_RUN
    evidence: Run after the active task file is materialized locally from this branch.
blockers: []
next_action: Read the required files, inventory candidate Player mutation call sites, choose the smallest representative set, implement markPlayerDirty without implicit scheduling, add focused tests, and open a draft PR before full exact-head validation.
```
