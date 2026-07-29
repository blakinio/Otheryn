---
task_id: OTH-20260729-prs003b-database-failure-classification
status: completed
branch: dudantas/prs-003b-database-failure-classification
base_branch: main
start_sha: 6a6007667dfd82010b0240342180961cd553466f
feature_pr: "214"
feature_head: 6f5254386a6bc55aeb8d2a0477a8b64c4d4355f5
feature_merge_sha: 4b186c77cee110bd2d6971916226e88f23fe2e5f
lifecycle_pr: "220"
lifecycle_head: 1f105a9083bfdb26d4a22caeefc11a1f5bf55a98
lifecycle_merge_sha: d81210d49f9e90ece3104f62ad9021af2b2ebb7e
issue: "208"
issue_state: closed_completed
created: 2026-07-29
updated: 2026-07-29
completed: 2026-07-29
owned_paths:
  - docs/agents/tasks/archive/OTH-20260729-prs003b-database-failure-classification.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/database/database_failure_classification.hpp
  - src/database/database.cpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/database/CMakeLists.txt
---

# PRS-003B runtime database failure classification and outage publication

## Completion

PRS-003B is complete. Feature PR #214 was squash-merged into `main` as `4b186c77cee110bd2d6971916226e88f23fe2e5f` from exact validated head `6f5254386a6bc55aeb8d2a0477a8b64c4d4355f5`. Issue #208 is closed as completed.

Repository lifecycle is also complete. Lifecycle PR #220 was squash-merged as `d81210d49f9e90ece3104f62ad9021af2b2ebb7e` from exact head `1f105a9083bfdb26d4a22caeefc11a1f5bf55a98` after Required run `30492348066` passed. The active task record no longer exists; this archive is the durable terminal record.

The package adds one narrow database-layer seam that classifies direct runtime database failures into fixed semantic categories and publishes deterministic events to the existing PRS-003A state owner while preserving every caller-visible failure result.

## Implemented contract

- finite operation phases: query, stored-result query, transaction begin, commit and rollback;
- finite native error kinds: none, connection lost, server gone and other;
- finite result kinds: success, known-not-committed failure and unknown commit outcome;
- classification uses operation phase and numeric MySQL error codes, never human-readable error text;
- begin failure is known not committed;
- commit and rollback failures have unknown commit outcome and never authorize replay;
- query/store connection loss or server-gone failures are conservatively unknown;
- other query/store failures are known not committed;
- success and successful empty results publish no outage event;
- generated events use one mutex-serialized monotonic sequence and steady-clock monotonic time;
- deterministic explicit events retain supplied sequence/time so stale, duplicate and regressing events are rejected by PRS-003A;
- concurrent publication is serialized by the publisher and state-owner mutex;
- original `false` and `nullptr` results remain unchanged.

## Runtime ownership

`src/database/database.cpp` owns exactly one function-local `DatabaseOutageStateMachine` and one narrow `DatabaseOutageEventPublisher`. Positive finite integration durations produce complete immutable snapshots only. This slice does not schedule deadlines, gate gameplay, drain players or claim production RTO/RPO.

## Safety boundaries preserved

- no `MYSQL_OPT_RECONNECT`, reconnect, `mysql_ping`, arbitrary SQL replay or retry loop;
- no failure-to-success conversion and no swallowed failure;
- no protocol, login, handoff, gameplay, mutation, player-save or disconnect change;
- no recovery probe or automatic resume;
- no schema, migration, credential, secret, production database or deployment mutation;
- no connection pool;
- no SQL text, player data or unbounded error text in fixed classifications;
- no durable PRS-004 integration or PRS-005/006/007/008 work.

## Changed paths

Feature PR #214 changed exactly:

- `docs/agents/tasks/active/OTH-20260729-prs003b-database-failure-classification.md`, later moved to this archive path;
- `docs/architecture/prs-003-database-outage-state-machine-contract.md`;
- `src/database/database_failure_classification.hpp`;
- `src/database/database.cpp`;
- `tests/unit/database/database_failure_classification_test.cpp`;
- one minimal registration edit in `tests/unit/database/CMakeLists.txt`.

Lifecycle PR #220 changed exactly the active and archive task-record paths. This finalizer changes only this archive path.

## Validation evidence

Exact feature head: `6f5254386a6bc55aeb8d2a0477a8b64c4d4355f5`.

- CI run `30489568822`: PASS;
- Required run `30489568511`: PASS;
- autofix run `30489568509`: PASS with no replacement commit;
- Linux Debug compile, Canary smoke, schema import and unit tests: PASS;
- Linux Release compile, generated-document check, Canary smoke and Global smoke: PASS;
- Windows CMake and Canary smoke: PASS;
- Windows Solution build: PASS;
- macOS compile and Canary smoke: PASS;
- Docker image build and validation: PASS;
- Fast Checks, clang-format, cmake-format, analysis, yamllint and Lua tests: PASS;
- exact changed-path audit: six declared feature paths only;
- feature PR comments, reviews, unresolved threads and requested reviewers: none;
- issue #208 closed automatically as completed by the feature merge.

Exact lifecycle head: `1f105a9083bfdb26d4a22caeefc11a1f5bf55a98`.

- Required run `30492348066`: PASS;
- exact changed-path audit: active record removed and archive record added only;
- lifecycle pre-merge drift: `behind_by=0` against feature merge `4b186c77cee110bd2d6971916226e88f23fe2e5f`;
- lifecycle PR comments, reviews, unresolved threads and requested reviewers: none;
- lifecycle PR was mergeable immediately before expected-head squash merge.

Earlier candidate `caaa8f039c1aa3fa2f96c8baabcb535ade34367f` also passed CI, Required and autofix, but was intentionally superseded when `main` advanced. Only the final exact head above was merged.

## Remaining separate work

- PRS-003C live protocol wiring for account login, game login, channel handoff and an explicit diagnostic route;
- PRS-003D durable mutation admission and bounded draining with PRS-002 final saves;
- PRS-003E recovery probes and controlled failure injection;
- durable PRS-004 fencing integration and PRS-005 through PRS-008.

## Rollback

Revert feature merge `4b186c77cee110bd2d6971916226e88f23fe2e5f` to remove the classifier/publisher integration. No schema, data or deployment rollback is required. Revert lifecycle merge `d81210d49f9e90ece3104f62ad9021af2b2ebb7e` only to restore active/archive record placement.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T23:38:00+02:00
head: d81210d49f9e90ece3104f62ad9021af2b2ebb7e
head_scope: merged feature and completed lifecycle archive; this one-path finalizer records exact terminal metadata
status: completed
feature_pr: 214
feature_head: 6f5254386a6bc55aeb8d2a0477a8b64c4d4355f5
feature_merge_sha: 4b186c77cee110bd2d6971916226e88f23fe2e5f
lifecycle_pr: 220
lifecycle_head: 1f105a9083bfdb26d4a22caeefc11a1f5bf55a98
lifecycle_merge_sha: d81210d49f9e90ece3104f62ad9021af2b2ebb7e
issue: 208
issue_state: closed_completed
ci_run: 30489568822
required_run: 30489568511
autofix_run: 30489568509
lifecycle_required_run: 30492348066
context_routes:
  - production-resilience
  - database
  - outage-handling
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/archive/OTH-20260729-prs003b-database-failure-classification.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/database/database_failure_classification.hpp
  - src/database/database.cpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/database/CMakeLists.txt
proven:
  - PRS-003A is merged and terminally archived
  - PRS-003B feature PR 214 is merged from exact validated head
  - issue 208 is closed completed
  - lifecycle PR 220 moved the task to archive after Required passed
  - active task record is absent
  - fixed numeric and operation-phase classification is live in the database layer
  - caller-visible false/nullptr behavior, disabled reconnect and one-shot execution remain explicit
  - exact feature head passed CI, Required and autofix
  - feature changed exactly six declared paths
  - feature and lifecycle PRs had no comments, reviews, unresolved threads or requested reviewers
  - later protocol, draining, recovery and durable-fencing work remains explicitly separate
derived:
  - the narrow seam preserves caller semantics without message parsing, replay or connection redesign
unknown: []
conflicts: []
first_failure: null
rejected_hypotheses:
  - recreate or replace PRS-003A
  - reconnect or replay after connection loss
  - parse mysql_error text for correctness
  - change DatabaseTasks callback semantics
  - combine protocol, drain, recovery or durable fencing work
  - add pooling or schema changes
changed_paths:
  - docs/agents/tasks/archive/OTH-20260729-prs003b-database-failure-classification.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/database/database_failure_classification.hpp
  - src/database/database.cpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/database/CMakeLists.txt
validation:
  - command: feature CI 30489568822
    result: PASS
    evidence: full exact-head multiplatform CI completed successfully
  - command: feature Required 30489568511
    result: PASS
    evidence: repository required gate completed successfully
  - command: feature autofix 30489568509
    result: PASS
    evidence: formatting gate completed without a replacement commit
  - command: feature terminal scope and discussion audit
    result: PASS
    evidence: six owned paths and no comments, reviews, unresolved threads or requested reviewers
  - command: lifecycle Required 30492348066
    result: PASS
    evidence: exact lifecycle head passed the repository required gate
  - command: lifecycle terminal scope and discussion audit
    result: PASS
    evidence: two task-record paths, behind_by zero and no comments, reviews, unresolved threads or requested reviewers
blockers: []
next_action: none
```
