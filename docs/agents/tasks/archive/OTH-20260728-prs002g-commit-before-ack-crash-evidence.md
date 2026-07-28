---
task_id: OTH-20260728-prs002g-commit-before-ack-crash-evidence
status: completed
branch: dudantas/prs-002g-commit-before-ack-crash-evidence
base_branch: main
start_sha: d46e39d6f28557b85f6f4c7e78dc707bb287b77f
feature_head: 86ec5475f0820ea13fc65b572f8d6de11ee88d29
feature_merge_sha: 472971b618b905d9d5722eee9bee5dc0ae546504
lifecycle_pr: "181"
lifecycle_head: 94c236d760a7b18564353ecf9a4ad538e047a354
lifecycle_merge_sha: 91d8d7d07f21971a29299057a4f0514cae33c587
created: 2026-07-28
updated: 2026-07-28
completed: 2026-07-28
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

Completed and merged through feature PR #180. Issue #179 closed automatically by the protected squash merge, and lifecycle PR #181 moved the durable task record from `active` to `archive`.

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
- final feature drift audit: branch `behind_by=0`, exactly four owned feature paths;
- final feature discussion audit: no comments, review threads or reviews;
- feature squash merge: `472971b618b905d9d5722eee9bee5dc0ae546504`;
- lifecycle head: `94c236d760a7b18564353ecf9a4ad538e047a354`;
- lifecycle Required #598, run `30397354141`: PASS;
- lifecycle scope: exactly the active/archive task pair;
- lifecycle discussion audit: no comments, review threads or reviews;
- lifecycle squash merge: `91d8d7d07f21971a29299057a4f0514cae33c587`;
- active task record: absent from `main`;
- archive task record: present on `main`.

## Safety boundaries preserved

- no production/shared database access or credentials;
- no production schema migration or deployment mutation;
- no production crash failpoint, signal handler, scheduler or restart-policy change;
- no automatic rollback or retry;
- no SQL/KV completeness, checkpoint interval or measured RPO claim;
- no PRS-003 outage state, PRS-004 fencing or PRS-006 reconciliation implementation.

## Remaining parent-program gaps

These are separate future packages, not unfinished PRS-002G work:

- controlled process crash before a pending dirty generation is saved;
- overloaded checkpoint queue behavior;
- queue capacity, oldest dirty age, attempt and failure observability;
- production RPO remains unknown until a separately authorized controlled crash drill measures it.

## Rollback

Revert feature merge `472971b618b905d9d5722eee9bee5dc0ae546504`. The test owns and removes only its dedicated disposable probe table; no production data or deployment rollback is required.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-28T22:43:23+02:00
head: 91d8d7d07f21971a29299057a4f0514cae33c587
head_scope: final lifecycle archive merge on main; later record-only corrections do not alter PRS-002G implementation or validation evidence
branch: main
pr: 181
status: completed
context_routes:
  - production-resilience
  - player-persistence
  - process-crash
  - integration-testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/archive/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
proven:
  - Feature PR 180 changed exactly four owned paths and merged from exact head 86ec5475f0820ea13fc65b572f8d6de11ee88d29 as 472971b618b905d9d5722eee9bee5dc0ae546504.
  - Exact-head CI 30395893383, Required 30395893226 and autofix 30395893053 passed.
  - Linux debug full CTest proved committed SQL survives child exit before acknowledgement while a fresh persistence state is clean.
  - Final feature audit found behind_by zero and no comments, reviews or review threads.
  - Issue 179 closed as completed after the feature merge.
  - Lifecycle PR 181 changed exactly the active/archive task pair, passed Required 30397354141 and merged as 91d8d7d07f21971a29299057a4f0514cae33c587.
  - The active task record is absent from main and this archive record is present.
derived:
  - A fresh process cannot reconstruct the lost in-memory dirty generation without future durable metadata or reconciliation.
  - PRS-002G requires no further implementation, validation, merge or archive action.
unknown:
  - Queue-overload behavior and measured production RPO remain parent-program gaps outside PRS-002G.
conflicts: []
first_failure: null
rejected_hypotheses:
  - claim a complete SQL/KV checkpoint
  - claim automatic retry or measured RPO
  - treat parent-program resilience gaps as unfinished PRS-002G scope
changed_paths:
  - docs/agents/tasks/active/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
  - docs/agents/tasks/archive/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
validation:
  - command: feature exact-head CI, Required and autofix
    result: PASS
    evidence: Runs 30395893383, 30395893226 and 30395893053 succeeded on 86ec5475f0820ea13fc65b572f8d6de11ee88d29.
  - command: feature final audit and expected-head merge
    result: PASS
    evidence: Exactly four owned paths, behind_by zero, no discussion or review items, and squash merge 472971b618b905d9d5722eee9bee5dc0ae546504.
  - command: lifecycle archive PR 181
    result: PASS
    evidence: Exactly the active/archive task pair changed; Required 30397354141 succeeded and squash merge produced 91d8d7d07f21971a29299057a4f0514cae33c587.
  - command: final repository-state audit
    result: PASS
    evidence: Issue closed, feature and lifecycle PRs merged, active record absent and archive record present.
blockers: []
next_action: No further action is required for PRS-002G; start any remaining parent-program gap only as a separately scoped task with a fresh preflight.
```
