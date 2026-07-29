---
task_id: OTH-20260729-prs003b-database-failure-classification
status: completed
branch: dudantas/prs-003b-database-failure-classification
base_branch: main
start_sha: 6a6007667dfd82010b0240342180961cd553466f
feature_pr: "214"
feature_head: 6f5254386a6bc55aeb8d2a0477a8b64c4d4355f5
feature_merge_sha: 4b186c77cee110bd2d6971916226e88f23fe2e5f
lifecycle_pr: pending
lifecycle_head: pending
lifecycle_merge_sha: pending
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

PRS-003B feature work is complete. Feature PR #214 was squash-merged into `main` as `4b186c77cee110bd2d6971916226e88f23fe2e5f` from exact validated head `6f5254386a6bc55aeb8d2a0477a8b64c4d4355f5`. Issue #208 is closed as completed.

The package adds one narrow database-layer seam that classifies direct runtime database failures into fixed semantic categories and publishes deterministic events to the existing PRS-003A state owner while preserving every caller-visible failure result.

Repository lifecycle archive placement is being completed by the dedicated lifecycle PR recorded above. A separate one-path finalizer must replace the pending lifecycle metadata after that PR merges.

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

- `docs/agents/tasks/active/OTH-20260729-prs003b-database-failure-classification.md`, moved to this archive path by lifecycle handling;
- `docs/architecture/prs-003-database-outage-state-machine-contract.md`;
- `src/database/database_failure_classification.hpp`;
- `src/database/database.cpp`;
- `tests/unit/database/database_failure_classification_test.cpp`;
- one minimal registration edit in `tests/unit/database/CMakeLists.txt`.

The lifecycle PR changes exactly the active and archive task-record paths. The later finalizer changes only this archive path.

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

Earlier candidate `caaa8f039c1aa3fa2f96c8baabcb535ade34367f` also passed CI, Required and autofix, but was intentionally superseded when `main` advanced. Only the final exact head above was merged.

## Remaining separate work

- PRS-003C live protocol wiring for account login, game login, channel handoff and an explicit diagnostic route;
- PRS-003D durable mutation admission and bounded draining with PRS-002 final saves;
- PRS-003E recovery probes and controlled failure injection;
- durable PRS-004 fencing integration and PRS-005 through PRS-008.

## Rollback

Revert feature merge `4b186c77cee110bd2d6971916226e88f23fe2e5f` to remove the classifier/publisher integration. No schema, data or deployment rollback is required. Revert the lifecycle merge only to restore active/archive record placement.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T23:30:00+02:00
head: 4b186c77cee110bd2d6971916226e88f23fe2e5f
head_scope: merged feature on main; lifecycle archive PR and terminal metadata are pending
status: completed
feature_pr: 214
feature_head: 6f5254386a6bc55aeb8d2a0477a8b64c4d4355f5
feature_merge_sha: 4b186c77cee110bd2d6971916226e88f23fe2e5f
lifecycle_pr: pending
lifecycle_head: pending
lifecycle_merge_sha: pending
issue: 208
issue_state: closed_completed
ci_run: 30489568822
required_run: 30489568511
autofix_run: 30489568509
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
  - fixed numeric and operation-phase classification is live in the database layer
  - caller-visible false/nullptr behavior, disabled reconnect and one-shot execution remain explicit
  - exact feature head passed CI, Required and autofix
  - feature changed exactly six declared paths
  - feature PR had no comments, reviews, unresolved threads or requested reviewers
  - later protocol, draining, recovery and durable-fencing work remains explicitly separate
derived:
  - the narrow seam preserves caller semantics without message parsing, replay or connection redesign
unknown:
  - lifecycle PR number, exact lifecycle head, Required result and lifecycle merge SHA
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
  - command: lifecycle archive placement
    result: NOT_RUN
    evidence: dedicated lifecycle branch has been created and the lifecycle PR is pending
blockers: []
next_action: Open and validate the two-path lifecycle PR, merge it from its exact head, then update this archive in a one-path terminal finalizer PR.
```
