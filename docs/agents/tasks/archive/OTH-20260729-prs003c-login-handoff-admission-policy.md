---
task_id: OTH-20260729-prs003c-login-handoff-admission-policy
status: completed
branch: dudantas/prs-003c-login-handoff-admission-policy
base_branch: main
start_sha: 6a6007667dfd82010b0240342180961cd553466f
feature_pr: "213"
feature_head: d1a36eada901dacb4634f6b417ff7535e046d5b2
feature_merge_sha: 3790aa4a0d5d43bbcc09f0e8725849fbcfe7d4fb
lifecycle_pr: pending
lifecycle_head: pending
lifecycle_merge_sha: pending
issue: "206"
issue_state: closed_completed
created: 2026-07-29
updated: 2026-07-29
completed: 2026-07-29
owned_paths:
  - docs/agents/tasks/archive/OTH-20260729-prs003c-login-handoff-admission-policy.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_policy.hpp
  - tests/unit/server/network/protocol/database_outage_admission_policy_test.cpp
  - tests/unit/server/CMakeLists.txt
---

# PRS-003C-A pure login and handoff outage admission policy

## Completion

PRS-003C-A is complete. Feature PR #213 was squash-merged into `main` as `3790aa4a0d5d43bbcc09f0e8725849fbcfe7d4fb` from exact validated head `d1a36eada901dacb4634f6b417ff7535e046d5b2`. Issue #206 is closed as completed.

The package adds one deterministic, header-only, `constexpr` and `noexcept` admission decision component. It accepts only an immutable PRS-003A outage snapshot, an explicit operation class, narrow caller capabilities and the existing `GameState_t`. It returns an explicit allow/reject disposition, a fixed reason code and sufficient typed context for a later protocol adapter.

No live account-login, game-login, protocol-session handoff, socket, session, player, channel, database or lifecycle behavior was modified.

## Admission table

Assuming lifecycle `GAME_STATE_NORMAL`:

| Operation | Healthy | Degraded | Draining | Maintenance |
|---|---|---|---|---|
| account login | allow | reject: `OutageDegraded` | reject: `OutageDraining` | reject: `OutageMaintenance` |
| game login | allow | reject: `OutageDegraded` | reject: `OutageDraining` | reject: `OutageMaintenance` |
| channel or protocol-session handoff | allow | reject: `OutageDegraded` | reject: `OutageDraining` | reject: `OutageMaintenance` |
| explicit staff diagnostic operation with diagnostic capability | allow | reject: `OutageDegraded` | reject: `OutageDraining` | allow |

Lifecycle restrictions are evaluated before outage admission:

- `STARTUP` and `SHUTDOWN` reject every operation;
- lifecycle `MAINTAIN` rejects ordinary login and handoff, while allowing only the explicitly classified diagnostic operation with its separate capability;
- `CLOSING` and `CLOSED` preserve the current narrow `CanAlwaysLogin` exception for game login and handoff only;
- `CanAlwaysLogin` never bypasses Degraded, Draining or outage Maintenance;
- a valid handoff hint or existing authentication does not make handoff outage-safe;
- unknown operation, lifecycle and outage values reject fail closed.

## Changed paths

- `docs/agents/tasks/active/OTH-20260729-prs003c-login-handoff-admission-policy.md` during feature development, moved to this archive path by lifecycle handling;
- `docs/architecture/prs-003c-login-handoff-admission-policy.md`;
- `src/server/network/protocol/database_outage_admission_policy.hpp`;
- `tests/unit/server/network/protocol/database_outage_admission_policy_test.cpp`;
- one source registration line in shared `tests/unit/server/CMakeLists.txt`.

The feature PR changed exactly those five feature paths. It did not edit `ProtocolLogin`, `ProtocolGame`, `ProtocolSessionHintStore`, result classification, outage publication, drain orchestration or any live channel-handoff implementation.

## Validation evidence

Exact feature head: `d1a36eada901dacb4634f6b417ff7535e046d5b2`.

- CI run `30487806313`: PASS;
- Required run `30487806104`: PASS;
- autofix run `30487806142`: PASS with no replacement commit;
- Linux Debug job `90698087922`: compile, Canary smoke, schema import and all unit tests PASS;
- Linux Release: compile, generated-document check, Canary smoke and Global smoke PASS;
- Windows CMake and Canary smoke: PASS;
- Windows Solution: PASS;
- macOS compile and Canary smoke: PASS;
- Docker image build and validation: PASS;
- Fast Checks, clang-format, cmake-format, analysis, yamllint, Lua tests and lightweight linters: PASS;
- exact pre-merge base drift: `behind_by=0` against `main` `a263e7c7370b39bbf65557ccb570cf29ed775e74`;
- exact changed-path audit: five declared feature paths only;
- feature PR comments, reviews and unresolved threads: none;
- feature PR was mergeable immediately before expected-head squash merge.

The first superseded validation head failed only the test assertion `static_assert(noexcept(...))` because test helper `makeSnapshot()` lacked a `noexcept` declaration. The production policy was already `noexcept`. Marking the helper `constexpr noexcept` fixed the confirmed cause; the final exact head passed every required gate.

Database failure injection was not applicable because this pure package performs no database operation, outage publication or runtime wiring.

## Remaining PRS-003C integration work

A later independently mergeable protocol-wiring package must:

- obtain the immutable outage snapshot from the accepted state owner;
- classify the exact account-login, game-login and handoff entry point;
- derive `CanAlwaysLogin` only where the existing player capability is available;
- expose a genuinely separate diagnostic route before supplying diagnostic capability;
- map fixed policy reasons to existing caller-visible protocol responses;
- place each gate before database-backed admission work or handoff ownership mutation;
- preserve startup, shutdown, maintenance and closing ordering;
- add focused integration tests without weakening this pure admission table.

Snapshot ownership, caller-visible wording, exact adapter insertion points and PRS-004 durable handoff fencing remain outside this package.

## Rollback

Revert feature merge `3790aa4a0d5d43bbcc09f0e8725849fbcfe7d4fb`. The feature is isolated to one pure header, deterministic tests, one minimal test registration line, one architecture document and its task record. Revert the lifecycle merge only to restore active/archive record placement.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T22:35:00+02:00
head: 3790aa4a0d5d43bbcc09f0e8725849fbcfe7d4fb
head_scope: merged feature on main; lifecycle archive PR and merge metadata are pending
status: completed
feature_pr: 213
feature_head: d1a36eada901dacb4634f6b417ff7535e046d5b2
feature_merge_sha: 3790aa4a0d5d43bbcc09f0e8725849fbcfe7d4fb
lifecycle_pr: pending
lifecycle_head: pending
lifecycle_merge_sha: pending
issue: 206
issue_state: closed_completed
ci_run: 30487806313
required_run: 30487806104
autofix_run: 30487806142
context_routes:
  - production-resilience
  - database-outage
  - protocol-policy
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/archive/OTH-20260729-prs003c-login-handoff-admission-policy.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_policy.hpp
  - tests/unit/server/network/protocol/database_outage_admission_policy_test.cpp
  - tests/unit/server/CMakeLists.txt
proven:
  - the pure admission policy and full deterministic matrix are merged
  - exact feature head passed CI, Required and autofix
  - issue 206 is closed completed
  - no live protocol wiring changed
  - later protocol integration remains explicitly separate
derived:
  - identical immutable inputs fully determine the decision
unknown:
  - exact lifecycle PR, head and merge SHA
conflicts: []
first_failure:
  marker: linux-debug test helper noexcept assertion on a superseded head
  evidence: makeSnapshot lacked noexcept; production evaluate was already noexcept and final exact head passed all gates after the bounded helper correction
rejected_hypotheses:
  - universal staff outage bypass
  - authenticated handoff is automatically outage-safe
  - mutable global outage lookup inside policy
  - live protocol wiring in this package
changed_paths:
  - docs/agents/tasks/archive/OTH-20260729-prs003c-login-handoff-admission-policy.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_policy.hpp
  - tests/unit/server/network/protocol/database_outage_admission_policy_test.cpp
  - tests/unit/server/CMakeLists.txt
validation:
  - command: feature CI 30487806313
    result: PASS
    evidence: full exact-head multiplatform CI completed successfully
  - command: feature Required 30487806104
    result: PASS
    evidence: repository required gate completed successfully
  - command: feature autofix 30487806142
    result: PASS
    evidence: formatting gate completed without a replacement commit
  - command: feature terminal scope and discussion audit
    result: PASS
    evidence: five owned paths, behind_by zero, no comments, reviews or unresolved threads
blockers: []
next_action: validate and merge the record-only lifecycle archive PR, then finalize this archive with exact lifecycle metadata
```
