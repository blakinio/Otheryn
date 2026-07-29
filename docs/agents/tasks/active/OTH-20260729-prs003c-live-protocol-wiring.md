---
task_id: OTH-20260729-prs003c-live-protocol-wiring
status: active
branch: dudantas/prs-003c-clean-rebuild
base_branch: main
start_sha: 25cf8cc223b38ddc70a14382e79cb62d3c7caabd
created: 2026-07-29
updated: 2026-07-29
related_issue: "222"
related_pr: "227"
duplicate_issue: "224"
superseded_pr: "226"
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-live-protocol-wiring.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/server/network/protocol/database_outage_protocol_admission.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/unit/server/network/protocol/database_outage_protocol_admission_test.cpp
  - tests/unit/server/CMakeLists.txt
---

# PRS-003C-B live login and handoff database-outage admission

## Goal

Wire the accepted PRS-003C-A pure policy to the real account-login, game-login and existing-session/channel-handoff boundaries using the immutable PRS-003B process snapshot. Preserve existing lifecycle ordering and messages, reject outage admission before database-backed work or ownership mutation, and keep staff diagnostics unavailable except through a separately named evaluator with an explicit diagnostic capability.

## Canonical ownership

- canonical issue: `#222`;
- canonical feature PR: `#227`;
- exact clean base: `25cf8cc223b38ddc70a14382e79cb62d3c7caabd`;
- duplicate issue `#224` is closed as duplicate;
- draft PR `#226` contains the superseded construction history and must be closed without merge once PR `#227` is confirmed canonical;
- final feature tree is rebuilt directly from the exact clean base and changes only the seven declared paths.

## Required reads completed

- `AGENTS.md`;
- `docs/agents/CONTEXT_HANDOFF.md`;
- `docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md`;
- `docs/architecture/production-resilience-and-recovery.md`;
- `docs/architecture/prs-003-database-outage-state-machine-contract.md`;
- `docs/architecture/prs-003c-login-handoff-admission-policy.md`;
- `docs/architecture/oam-004d-player-save-failure-propagation.md`;
- terminal PRS-003B and PRS-003C-A archive records;
- terminal parallel-coordination archive.

The requested paths `docs/agents/REPOSITORY_MAP.md`, `docs/agents/CONTEXT_ROUTING.md` and `docs/agents/EXECUTION_MODE_ROUTING.md` were not present on the audited `main`; no replacement path was guessed.

## Implemented runtime contract

- `database_outage_protocol_admission.hpp` obtains the immutable process snapshot and applies the existing pure admission policy;
- adapter output is typed as allow, reject or defer-existing-lifecycle and carries only fixed bounded messages;
- account login evaluates after the existing startup/maintenance gates and before IP-ban, account loading and account authentication;
- ordinary game login evaluates after existing startup/maintenance gates and before IP-ban/world authentication, then evaluates again before player loading;
- ordinary game-login closing/closed decisions are deferred until the existing player capability is available, preserving current `CanAlwaysLogin` ordering and messages;
- existing-session/channel handoff evaluates before old-client disconnect, before replacement scheduling and before final `player->client` ownership assignment;
- handoff supplies `CanAlwaysLogin` only from the identified existing player and never allows it to override degraded, draining or maintenance rejection;
- lifecycle-closed handoff preserves the configured maintenance message when present and the existing default closed message otherwise;
- `evaluateStaffDiagnostic()` always classifies `StaffDiagnostic`, requires a separate caller-supplied capability and never infers it from `CanAlwaysLogin`;
- the diagnostic evaluator performs no database query, reconnect, recovery action, resume or state mutation;
- ordinary login and handoff helpers cannot select the diagnostic operation.

## Caller-visible behavior

Existing startup, shutdown, maintenance, closing and closed responses remain in their established paths. New outage responses are fixed and bounded:

- degraded: persistence temporarily unavailable;
- draining: gameworld entering maintenance;
- maintenance: existing maintenance response;
- unknown operation/lifecycle/outage or missing diagnostic capability: generic persistence unavailable.

No SQL text, player name, account identifier, credential, exception payload or high-cardinality value is exposed.

## Deterministic and failure-injection plan

Focused tests cover:

- healthy, degraded, draining and maintenance decisions for account login, game login and handoff;
- outage rejection despite `CanAlwaysLogin`;
- deferred ordinary game-login closing/closed behavior;
- handoff closing behavior with and without the existing player capability;
- separate diagnostic capability and maintenance-only diagnostic allowance;
- unknown operation, lifecycle and outage values rejecting fail closed;
- fixed bounded messages without SQL or player text;
- repeated deterministic evaluation with immutable snapshot input.

Exact call-site review must prove account/game gates precede database-backed work and every handoff gate precedes its disconnect, replacement or ownership mutation. Controlled disposable-database fault injection remains PRS-003E; this package consumes deterministic injected snapshots and owns no connection, retry or replay mechanism.

## Non-goals

- no durable mutation admission or gameplay/economy gating;
- no degraded or drain deadline scheduler;
- no online-population drain, disconnect orchestration or PRS-002 final-save change;
- no recovery probe, reconnect, SQL replay, retry, auto-resume or operator-resume implementation;
- no schema, migration, credential, production database or deployment change;
- no durable PRS-004 fencing or PRS-005/006/007/008 work;
- no new client opcode, universal staff bypass or disclosure of private state;
- no authentication redesign beyond pre-database outage admission.

## Rollback

Revert the eventual squash merge of PR `#227`. The rollback removes one header-only adapter, two narrow live call-site integrations, one focused test, one test-registration line, the architecture update and this task record. No schema, data, credential or deployment rollback is required.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T23:59:00+02:00
head: pending_exact_final_head
head_scope: clean seven-path candidate on exact main base; canonical metadata recorded before final validation
branch: dudantas/prs-003c-clean-rebuild
pr: 227
issue: 222
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
  - coordinator issue 205 and lifecycle are terminal
  - canonical issue 222 reserves exactly this package
  - duplicate issue 224 is closed as duplicate
  - clean candidate is based directly on main 25cf8cc223b38ddc70a14382e79cb62d3c7caabd
  - final candidate tree contains only the seven declared paths
  - adapter consumes only the immutable accepted outage snapshot
  - account login gates before account database work
  - ordinary game login gates before world authentication and player loading
  - handoff gates before old-client disconnect, replacement scheduling and ownership assignment
  - CanAlwaysLogin is supplied only from an existing player and never overrides outage rejection
  - explicit staff diagnostics require a separate capability and perform no I/O
  - fixed messages contain no SQL text, identifiers, credentials or unbounded values
  - the implementation tree passed pre-clean CI 30493725646 and Required 30493725361
  - the architecture contract distinguishes implemented Slice C from remaining Slice D and Slice E work
derived:
  - repeated handoff checks fail closed if outage state changes before a later ownership boundary
unknown:
  - exact-final-head CI, Required and autofix run identifiers
  - feature merge SHA and lifecycle archive/finalizer metadata
conflicts:
  - issue 224 duplicated canonical issue 222 and was closed without owning canonical lifecycle
  - PR 226 is superseded by the clean exact-main candidate PR 227
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
  - command: live dependency, issue, PR and task preflight
    result: PASS
    evidence: terminal dependencies, canonical issue 222 and exact clean base were verified
  - command: protocol and persistence boundary audit
    result: PASS
    evidence: account/game database boundaries, handoff ownership mutation and OAM-004D limits were reviewed
  - command: pre-clean CI 30493725646
    result: PASS
    evidence: full CI passed after adapter, tests, architecture and live call sites were present
  - command: pre-clean Required 30493725361
    result: PASS
    evidence: Required passed before exact-main tree reconstruction
  - command: exact-final-head validation
    result: NOT_RUN
    evidence: canonical metadata commit requires fresh CI, Required and autofix
blockers: []
next_action: Mark PR 227 ready, close superseded PR 226, then require exact-final-head CI, Required and autofix before merge.
```
