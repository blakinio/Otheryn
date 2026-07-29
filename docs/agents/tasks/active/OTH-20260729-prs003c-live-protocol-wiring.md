---
task_id: OTH-20260729-prs003c-live-protocol-wiring
status: active
branch: dudantas/prs-003c-live-protocol-wiring
base_branch: main
start_sha: bb749e92236d5e7e63b033cbe396c2b183835a9b
created: 2026-07-29
updated: 2026-07-29
related_issue: "224"
related_pr: "226"
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-live-protocol-wiring.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/server/network/protocol/database_outage_protocol_admission.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/unit/server/network/protocol/database_outage_protocol_admission_test.cpp
  - tests/unit/server/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - docs/architecture/oam-004d-player-save-failure-propagation.md
  - docs/agents/tasks/archive/OTH-20260729-prs003b-database-failure-classification.md
  - docs/agents/tasks/archive/OTH-20260729-prs003c-login-handoff-admission-policy.md
search_first:
  - docs/agents/tasks/active/
  - docs/agents/tasks/archive/
  - src/database/database.cpp
  - src/database/database_failure_classification.hpp
  - src/server/network/protocol/database_outage_admission_policy.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - src/server/network/protocol/protocol_session_hint.hpp
  - tests/unit/server/network/protocol/
  - tests/unit/server/CMakeLists.txt
---

# PRS-003C live login and handoff database-outage admission

## Goal

Wire the accepted PRS-003C-A pure admission policy to the live account-login, game-login and existing-session/channel-handoff boundaries using the immutable PRS-003B process snapshot. Preserve existing lifecycle ordering and messages, reject outage admission before database-backed work or ownership mutation, and expose a separate explicit staff-diagnostic runtime evaluation path.

## Audited baseline

- exact task-start `main`: `bb749e92236d5e7e63b033cbe396c2b183835a9b`;
- current integration base after parallel coordination lifecycle closeout: `25cf8cc223b38ddc70a14382e79cb62d3c7caabd`;
- PRS-003A, PRS-003B and PRS-003C-A are merged, archived and terminally finalized;
- coordinator issue `#205` and its lifecycle are terminal;
- issue `#224` exclusively owns this live wiring package;
- no competing live PRS-003C implementation PR was found;
- `getDatabaseOutageSnapshot()` returns one immutable snapshot from the PRS-003B publisher/state owner;
- `DatabaseOutageAdmissionPolicy::evaluate()` rejects unknown operation/lifecycle/outage values fail closed and distinguishes account login, game login, channel handoff and staff diagnostic;
- existing account/game startup and maintenance messages, later closing/closed checks and OAM-004D player-save boundaries were audited before edits.

## Implemented runtime contract

- `database_outage_protocol_admission.hpp` obtains the accepted immutable process snapshot and applies the pure policy;
- adapter output is typed as allow, reject or defer-existing-lifecycle and carries only fixed bounded messages;
- account login evaluates after the existing startup/maintenance gates and before IP-ban, account load and account authentication;
- ordinary game login evaluates after existing startup/maintenance gates and before IP-ban/world authentication, then evaluates again before player preload;
- closing/closed ordinary game-login decisions are deferred to the existing player-capability gate so current `CanAlwaysLogin` ordering and messages remain intact;
- existing-session/channel handoff evaluates before the first old-client disconnect, before replacement scheduling and again before final `player->client` ownership assignment;
- handoff supplies `CanAlwaysLogin` only from the identified existing player; it never overrides degraded, draining or maintenance rejection;
- lifecycle-closed handoff uses the existing configured maintenance message when present and the existing default closed message otherwise;
- a separately named `evaluateStaffDiagnostic()` path always classifies `StaffDiagnostic`, requires a dedicated caller-supplied diagnostic capability and never infers it from `CanAlwaysLogin`;
- the diagnostic path returns a typed snapshot decision only and performs no database query, reconnect, resume or state mutation;
- no ordinary login or handoff helper can select the diagnostic operation.

## Caller-visible behavior

Existing startup, maintenance, closing and closed messages remain unchanged. New database-outage responses are fixed, bounded and low-cardinality:

- degraded: persistence temporarily unavailable;
- draining: gameworld entering maintenance;
- maintenance: existing maintenance message;
- unknown operation/lifecycle/outage or missing diagnostic capability: generic persistence unavailable.

No SQL text, player name, account identifier, credential or arbitrary exception string is included.

## Deterministic evidence

`database_outage_protocol_admission_test.cpp` covers:

- healthy/degraded/draining/maintenance decisions for account login, game login and handoff;
- outage rejection despite `CanAlwaysLogin`;
- deferred ordinary game-login closing/closed behavior;
- handoff closing behavior with and without the existing player capability;
- separate diagnostic capability and maintenance-only allowance;
- unknown operation/lifecycle/outage fail-closed handling;
- fixed bounded messages without SQL/player text;
- repeated deterministic evaluation with immutable snapshot input.

The exact call-site diff proves account/game gates precede their database-backed boundaries and each handoff gate precedes the corresponding disconnect, replacement or ownership mutation. Controlled disposable-database failure injection remains PRS-003E; this package consumes deterministic injected snapshots and owns no database connection.

## Non-goals

- no mutation admission or durable operation classification;
- no degraded/drain deadline scheduler;
- no online-population drain, disconnect orchestration or PRS-002 final-save change;
- no recovery probe, reconnect, auto-resume or operator-resume implementation;
- no schema, migration, credential, production database or deployment change;
- no PRS-004 durable fencing or PRS-005/006/007/008 work;
- no new network protocol, client opcode, universal staff bypass or disclosure of private state;
- no change to authentication semantics beyond pre-database outage admission.

## Rollback

Revert the feature merge. The rollback removes one header-only adapter, two narrow call-site integrations, one focused test, one minimal test-registration line, the architecture update and this task record. No schema, data, credential or deployment rollback is required.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T23:55:00+02:00
head: pending_clean_exact_main_candidate
head_scope: seven-path implementation complete; branch history is being collapsed onto current main before exact-head validation
branch: dudantas/prs-003c-live-protocol-wiring
pr: 226
status: active
context_routes:
  - production-resilience
  - database-outage
  - authentication
  - protocol-handoff
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-live-protocol-wiring.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/server/network/protocol/database_outage_protocol_admission.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/unit/server/network/protocol/database_outage_protocol_admission_test.cpp
  - tests/unit/server/CMakeLists.txt
proven:
  - PRS-003B and PRS-003C-A are terminal
  - coordinator issue 205 and lifecycle are terminal on main 25cf8cc223b38ddc70a14382e79cb62d3c7caabd
  - issue 224 and PR 226 exclusively own live protocol wiring
  - the adapter consumes only the immutable accepted outage snapshot
  - account login gates before account database work
  - ordinary game login gates before world authentication and player preload
  - handoff gates before old-client disconnect, replacement scheduling and ownership assignment
  - CanAlwaysLogin is supplied only from an existing player and never overrides outage rejection
  - explicit staff diagnostics require a separate capability and perform no I/O
  - fixed messages contain no SQL text, identifiers, credentials or unbounded values
  - focused adapter tests compile and the pre-clean implementation head passed CI and Required
  - the architecture contract distinguishes implemented Slice C from remaining Slice D and Slice E work
derived:
  - the live call sites preserve existing lifecycle messages without overloading GameState_t with database health
  - repeated handoff checks fail closed if outage state changes before a later ownership boundary
unknown:
  - exact clean candidate head on current main
  - exact-final-head CI, Required and autofix run identifiers
  - feature merge SHA and lifecycle archive/finalizer metadata
conflicts: []
first_failure: null
rejected_hypotheses:
  - overload GameState_t with database-health state
  - treat authenticated or hinted sessions as outage-safe
  - derive diagnostic capability from CanAlwaysLogin
  - disconnect the old client before handoff admission
  - query the database to decide whether database admission is safe
  - reconnect, replay or auto-resume
  - combine mutation, draining, recovery or durable fencing work
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-live-protocol-wiring.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/server/network/protocol/database_outage_protocol_admission.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/unit/server/network/protocol/database_outage_protocol_admission_test.cpp
  - tests/unit/server/CMakeLists.txt
validation:
  - command: live main, issue, PR and task preflight
    result: PASS
    evidence: terminal dependencies, exclusive issue 224 and exact task-start/current integration bases were verified
  - command: protocol and persistence boundary audit
    result: PASS
    evidence: account/game database boundaries, handoff ownership mutation and OAM-004D limits were reviewed
  - command: pre-clean CI 30493725646
    result: PASS
    evidence: full CI passed after the adapter, tests and live call-site implementation were present
  - command: pre-clean Required 30493725361
    result: PASS
    evidence: Required passed on the implementation tree before final branch-history collapse
  - command: exact-final-head validation
    result: NOT_RUN
    evidence: clean candidate on current main is pending
blockers: []
next_action: Collapse the seven-path tree onto current main, mark PR 226 ready, then require exact-final-head CI, Required and autofix before merge.
```
