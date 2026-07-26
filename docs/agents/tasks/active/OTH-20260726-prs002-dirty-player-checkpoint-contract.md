---
task_id: OTH-20260726-prs002-dirty-player-checkpoint-contract
status: validating
branch: dudantas/prs-002-dirty-player-checkpoint-contract
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "137"
related_pr: "139"
owned_paths:
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - tests/unit/game/prs_002_dirty-player-checkpoint-contract_test.cpp
  - tests/unit/game/CMakeLists.txt
  - docs/agents/tasks/active/OTH-20260726-prs002-dirty-player-checkpoint-contract.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/oam-004a-database-transaction-integrity.md
  - docs/architecture/oam-004d-player-save-failure-propagation.md
search_first:
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/save_manager.hpp
  - src/io/iologindata.cpp
  - src/io/functions/iologindata_save_player.cpp
  - src/creatures/players/player.cpp
  - tests/unit/game
optional_reads:
  - docs/operations/production-recovery-runbook.md
---

# PRS-002 dirty-player checkpoint contract

## Goal

Establish a source-backed dirty-player checkpoint contract and deterministic characterization tests before changing runtime persistence scheduling.

## Scope

This milestone owns only the current-behavior inventory, accepted generation/ack contract, source contract tests and task evidence. Runtime checkpoint state, mutation instrumentation, retry scheduling, schema work, outage handling and session fencing remain outside this branch.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T20:24:00+02:00
head: a7e904a00c0d2b40ed8f9c717a26573edd9a7c6e
branch: dudantas/prs-002-dirty-player-checkpoint-contract
pr: 139
status: validating
context_routes:
  - production-resilience
  - player-persistence
  - save-scheduling
  - database-persistence
  - testing
  - agent-governance
owned_paths:
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - tests/unit/game/prs_002_dirty-player-checkpoint-contract_test.cpp
  - tests/unit/game/CMakeLists.txt
  - docs/agents/tasks/active/OTH-20260726-prs002-dirty-player-checkpoint-contract.md
proven:
  - PRS-001 feature and lifecycle are merged; issue 137 owns the bounded PRS-002 discovery milestone.
  - SaveManager schedules online saves asynchronously and returns scheduling acceptance before persistence completes.
  - Scheduled saves retain the requested Player object through weak-to-strong ownership instead of GUID re-resolution.
  - Timestamp coalescing skips older queued work but is not a dirty generation or acknowledgement protocol.
  - doSavePlayer holds PlayerLock and returns the IOLoginData save result.
  - A representative persisted mutation, addSkillAdvance, does not acquire PlayerLock.
  - Player SQL domains commit inside one transaction; Wheel KV staging occurs after SQL commit.
  - SaveManager exposes no dirty generation, acknowledged generation, retry owner or oldest-dirty-age state.
derived:
  - Save-side locking alone cannot prove a consistent async snapshot when representative mutators do not use the same lock.
  - A mutation during or after serialization can remain unsaved when no later save request is guaranteed.
  - A post-commit KV failure is an unknown cross-domain outcome and must not acknowledge a captured dirty generation.
unknown:
  - Complete inventory of every mutation path that must mark player persistence dirty.
  - Exact logout, channel-handoff and graceful-shutdown acknowledgement semantics across all callers.
  - Measured crash-loss window and any defensible checkpoint RPO.
  - Queue capacity and fairness behavior under repeated per-player save failures.
conflicts: []
first_failure:
  marker: dirty-generation-ack-contract-missing
  evidence: SaveManager coalesces by timestamp and logs asynchronous failures but has no generation-aware dirty acknowledgement state.
rejected_hypotheses:
  - Treat timestamp coalescing as equivalent to dirty-generation tracking.
  - Claim PlayerLock serializes all gameplay mutations.
  - Begin PRS-003 outage handling or PRS-004 fencing in this milestone.
  - Add a production timer or claim a 60-second RPO before controlled crash evidence.
changed_paths:
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - tests/unit/game/prs_002_dirty-player-checkpoint-contract_test.cpp
  - tests/unit/game/CMakeLists.txt
  - docs/agents/tasks/active/OTH-20260726-prs002-dirty-player-checkpoint-contract.md
validation:
  - command: source inventory of SaveManager, IOLoginData and representative Player mutation
    result: PASS
    evidence: Exact source establishes async scheduling, object pinning, timestamp coalescing, save result propagation and the SQL/post-commit KV boundary.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/OTH-20260726-prs002-dirty-player-checkpoint-contract.md --require-checkpoint
    result: PASS
    evidence: Local validator accepted the compact checkpoint before publication on the synchronized branch.
  - command: focused PRS-002 unit source-contract test
    result: NOT_RUN
    evidence: Run through exact-head repository CI after the draft PR is opened.
blockers: []
next_action: Require exact-head CI and Required on PR 139, fix only discovery-contract failures, then mark ready and merge after a clean four-path discussion and main-drift audit.
```
