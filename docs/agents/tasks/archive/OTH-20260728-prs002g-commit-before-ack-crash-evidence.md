---
task_id: OTH-20260728-prs002g-commit-before-ack-crash-evidence
status: complete
branch: dudantas/prs-002g-commit-before-ack-crash-evidence
base_branch: main
start_sha: d46e39d6f28557b85f6f4c7e78dc707bb287b77f
feature_head: 86ec5475f0820ea13fc65b572f8d6de11ee88d29
feature_merge_sha: 472971b618b905d9d5722eee9bee5dc0ae546504
created: 2026-07-28
updated: 2026-07-28
related_issue: "179"
related_pr: "180"
owned_paths:
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_checkpoint_commit_before_ack_crash_it.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/archive/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
---

# PRS-002G commit-before-ack crash evidence

## Result

Completed and merged through feature PR #180. Issue #179 closed automatically by the protected squash merge.

## Proven evidence

- the integration fixture uses only the disposable MariaDB test database;
- one dedicated InnoDB probe table starts with value `100` and is removed by teardown;
- a GoogleTest `threadsafe` death test launches a fresh child process with its own database connection;
- the child marks generation `1` dirty and begins checkpoint generation `1`;
- the child enters `executePlayerCheckpointAttempt` and commits the probe update to `200` through `DBTransaction::executeWithinTransaction`;
- the child calls `std::_Exit(86)` from inside the save callback after commit success and before `executePlayerCheckpointAttempt` can call `acknowledgeSuccess`;
- the surviving parent observes committed value `200`;
- a newly constructed `PlayerPersistenceState` is clean with no dirty, acknowledged or in-flight generation and no failure count;
- therefore the durable SQL commit survives while dirty-generation ownership and acknowledgement state die with the process.

## Accepted conclusion

PRS-002G proves the commit-before-ack ambiguity. The current in-memory checkpoint state is not durable and a restarted process cannot infer that a pre-crash dirty generation existed or automatically require its retry. The result does not imply that the complete player SQL/KV checkpoint finished.

## Validation

- exact feature head: `86ec5475f0820ea13fc65b572f8d6de11ee88d29`;
- CI #559, run `30395893383`: PASS;
- Required #597, run `30395893226`: PASS;
- autofix #480, run `30395893053`: PASS with no head change;
- Fast Checks and Lua: PASS;
- Windows CMake compile and smoke: PASS;
- Linux debug compile: PASS;
- disposable MariaDB schema import: PASS;
- full Linux debug CTest, including the fresh-process death test: PASS;
- final drift audit: branch `behind_by=0`, exactly four owned feature paths;
- final discussion audit: no review threads, reviews or requested reviewers;
- feature squash merge: `472971b618b905d9d5722eee9bee5dc0ae546504`.

## Safety boundaries preserved

- no production/shared database access or credentials;
- no production schema migration or deployment mutation;
- no production crash failpoint, signal handler, scheduler or restart-policy change;
- no automatic rollback or retry;
- no SQL/KV completeness, checkpoint interval or measured RPO claim;
- no PRS-003 outage state, PRS-004 fencing or PRS-006 reconciliation implementation.

## Remaining PRS-002 gaps

- controlled process crash before a pending dirty generation is saved;
- overloaded checkpoint queue behavior;
- queue capacity, oldest dirty age, attempt and failure observability;
- production RPO remains unknown until a separately authorized controlled crash drill measures it.

## Rollback

Revert feature merge `472971b618b905d9d5722eee9bee5dc0ae546504`. The test owns and removes only its dedicated disposable probe table; no production data or deployment rollback is required.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-28T22:42:00+02:00
head: 472971b618b905d9d5722eee9bee5dc0ae546504
branch: dudantas/archive-prs-002g-commit-before-ack-crash-evidence
pr: null
status: complete
context_routes:
  - production-resilience
  - player-persistence
  - process-crash
  - integration-testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
  - docs/agents/tasks/archive/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
proven:
  - Feature PR 180 merged at 472971b618b905d9d5722eee9bee5dc0ae546504.
  - Issue 179 is closed as completed.
  - Exact-head CI, Required and autofix passed.
  - Linux debug full CTest proved committed SQL survives child exit before acknowledgement.
derived:
  - A fresh process cannot reconstruct the lost in-memory dirty generation without future durable metadata or reconciliation.
unknown:
  - Queue-overload behavior and measured production RPO.
conflicts: []
first_failure: null
rejected_hypotheses:
  - claim a complete SQL/KV checkpoint
  - claim automatic retry or measured RPO
changed_paths:
  - docs/agents/tasks/active/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
  - docs/agents/tasks/archive/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
validation:
  - command: feature exact-head validation
    result: PASS
    evidence: CI 559, Required 597 and autofix 480 succeeded on 86ec5475f0820ea13fc65b572f8d6de11ee88d29.
  - command: feature merge and issue closure
    result: PASS
    evidence: PR 180 merged as 472971b618b905d9d5722eee9bee5dc0ae546504 and issue 179 closed.
blockers: []
next_action: Merge the docs-only lifecycle archive after its exact-head Required check passes.
```