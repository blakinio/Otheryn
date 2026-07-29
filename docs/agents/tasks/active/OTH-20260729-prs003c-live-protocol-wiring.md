---
task_id: OTH-20260729-prs003c-live-protocol-wiring
status: active
branch: dudantas/prs-003c-live-protocol-wiring
base_branch: main
start_sha: bb749e92236d5e7e63b033cbe396c2b183835a9b
created: 2026-07-29
updated: 2026-07-29
related_issue: "224"
related_pr: pending
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
- PRS-003A, PRS-003B and PRS-003C-A are merged, archived and terminally finalized;
- issue `#224` exclusively owns this live wiring package;
- no competing live PRS-003C issue or PR was found;
- `getDatabaseOutageSnapshot()` returns one immutable snapshot from the PRS-003B publisher/state owner;
- `DatabaseOutageAdmissionPolicy::evaluate()` already rejects unknown operation/lifecycle/outage values fail closed and distinguishes account login, game login, channel handoff and staff diagnostic;
- `ProtocolLogin::onRecvFirstMessage()` applies existing startup and maintenance messages before IP-ban and account database work;
- `ProtocolGame::onRecvFirstMessage()` applies existing startup and maintenance messages before IP-ban and world authentication;
- existing-player replacement can disconnect the old client before `ProtocolGame::connect()` assigns the new client, so handoff admission must precede that disconnect and later ownership mutation;
- ordinary player closing/closed checks occur after player preload, because `CanAlwaysLogin` is available only from the player object;
- OAM-004D keeps player save failure fail closed and records SQL/KV non-atomicity; this package does not change save or durable mutation behavior.

## Accepted implementation shape

- add one header-only runtime adapter that obtains the immutable snapshot and calls the existing pure policy;
- expose fixed low-cardinality caller outcomes and bounded outage messages;
- expose separate helpers for ordinary protocol admission and explicit staff-diagnostic admission; diagnostic capability must be supplied explicitly and cannot be inferred from `CanAlwaysLogin`;
- account login evaluates after the existing startup/maintenance lifecycle gates and before IP-ban/account load/authentication;
- ordinary game login evaluates after existing startup/maintenance gates and before IP-ban/world authentication; only outage reasons are enforced early so current closing/closed capability ordering remains unchanged;
- handoff evaluates when an existing online player/client has been identified and before the old client is disconnected or replacement ownership is scheduled;
- handoff supplies `CanAlwaysLogin` only from that existing player object;
- lifecycle rejection messages remain the current protocol messages; new fixed messages apply only to database-outage reasons;
- no mutable global is introduced outside the existing PRS-003B owner.

## Explicit diagnostic path

The adapter exposes one separately named staff-diagnostic evaluation function. It always classifies the operation as `StaffDiagnostic`, requires a caller-supplied diagnostic capability and never derives that capability from ordinary login flags. It returns the typed policy decision and immutable snapshot context only; it performs no database query, reconnect, resume or state mutation. No ordinary login or handoff call site can select this path.

## Non-goals

- no mutation admission or durable operation classification;
- no degraded/drain deadline scheduler;
- no player draining, disconnect orchestration or PRS-002 final-save changes;
- no recovery probe, reconnect, auto-resume or operator-resume implementation;
- no schema, migration, credential, production database or deployment change;
- no PRS-004 durable fencing or PRS-005/006/007/008 work;
- no new network protocol, client opcode, universal staff bypass or disclosure of private state;
- no change to account/player authentication semantics beyond pre-database outage admission.

## Failure-injection and deterministic test plan

- evaluate account login, game login and handoff against healthy, degraded, draining and maintenance snapshots;
- prove outage rejection is independent of `CanAlwaysLogin`;
- prove handoff lifecycle closing/closed still respects the existing player capability;
- prove explicit staff diagnostics require the separate capability and are allowed only where the pure contract allows;
- prove unknown operation/lifecycle/outage values reject fail closed;
- prove fixed messages contain no SQL text, player names, IDs or exception strings;
- source-contract assertions prove account/game gates precede database-backed calls and handoff gate precedes old-client disconnect/ownership mutation;
- source-contract assertions prove existing startup/maintenance/closing/closed messages remain present and ordered;
- repeated identical inputs produce identical decisions and do not mutate the snapshot;
- audit source for no reconnect, replay, retry, recovery probe, resume or save-path mutation.

Controlled database failure injection is deferred to PRS-003E. This package deterministically consumes injected immutable snapshots and does not own a database connection.

## Rollback

Revert the feature merge. The rollback removes one header-only adapter, two narrow call-site integrations, one focused test, one minimal test-registration line, the architecture update and this task record. No schema, data, credential or deployment rollback is required.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T23:50:00+02:00
head: bb749e92236d5e7e63b033cbe396c2b183835a9b
head_scope: exact task-start main before implementation
branch: dudantas/prs-003c-live-protocol-wiring
pr: pending
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
  - issue 224 exclusively owns live protocol wiring
  - no competing issue or PR was found
  - the accepted immutable outage snapshot getter is available
  - the pure policy supplies fixed account, game, handoff and diagnostic decisions
  - current account and game lifecycle messages and database-backed boundaries were audited
  - current existing-player replacement can disconnect the old client before ownership assignment
  - the seven exact owned paths are declared before implementation
derived:
  - one narrow adapter can preserve lifecycle messages while enforcing outage-only early rejection
  - existing-player handoff has enough context to supply CanAlwaysLogin without creating a staff bypass
unknown:
  - exact implementation head and deterministic test result
  - exact feature PR number and exact-head CI, Required and autofix evidence
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
validation:
  - command: live main, issue, PR and task preflight
    result: PASS
    evidence: terminal dependencies, no competing scope and exact task-start main were verified
  - command: protocol and persistence boundary audit
    result: PASS
    evidence: account/game database boundaries, handoff ownership mutation and OAM-004D limits were reviewed
  - command: implementation and deterministic tests
    result: NOT_RUN
    evidence: task ownership was declared before source changes
blockers: []
next_action: Implement the seven-path runtime adapter, protocol gates, focused tests and architecture update, then run exact-head validation.
```
