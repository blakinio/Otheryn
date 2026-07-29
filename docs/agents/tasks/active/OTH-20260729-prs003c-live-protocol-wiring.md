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
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - tests/unit/server/CMakeLists.txt
---

# PRS-003C-B live login and handoff database-outage admission

## Goal

Wire the accepted PRS-003C-A policy to real account-login, game-login and existing-session/channel-handoff boundaries using immutable PRS-003B snapshots. Preserve existing lifecycle ordering and messages, reject outage admission before database work or ownership mutation, and keep staff diagnostics behind a separately named evaluator with an explicit capability.

## Canonical ownership

- canonical issue: `#222`;
- canonical PR: `#227`;
- clean base: `25cf8cc223b38ddc70a14382e79cb62d3c7caabd`;
- duplicate issue `#224` is closed as duplicate;
- superseded PR `#226` is closed without merge;
- the package now owns exactly eight final paths after exact-head CI exposed one stale PRS-003 discovery contract test that asserted live outage wiring must not exist.

## Implemented runtime contract

- one header-only adapter reads the immutable process snapshot and applies the pure policy;
- account login evaluates after existing startup/maintenance gates and before IP-ban, account loading and authentication;
- ordinary game login evaluates after startup/maintenance and before world authentication, then again before player loading;
- closing/closed ordinary game-login handling remains deferred until the existing player capability is available;
- handoff evaluates before old-client disconnect, replacement scheduling and final `player->client` ownership assignment;
- `CanAlwaysLogin` comes only from the identified existing player and never overrides degraded, draining or maintenance rejection;
- configured lifecycle-closed messaging remains preserved;
- `evaluateStaffDiagnostic()` requires a dedicated capability, performs no database I/O and cannot be selected by ordinary login or handoff helpers;
- all new messages are fixed, bounded and contain no SQL, identifiers, credentials or exception payloads.

## Deterministic and failure-injection plan

Focused adapter tests cover healthy, degraded, draining and maintenance snapshots for account login, game login and handoff; closing/closed deferral; explicit diagnostic capability; unknown-value fail-closed handling; bounded messages; and repeated immutable evaluation.

The existing PRS-003 source-contract test must be updated from its obsolete discovery assertion (`DatabaseOutage` absent from live protocols) to prove the accepted Slice C integration instead:

- account helper present after lifecycle-only checks;
- game and handoff helpers present;
- direct `DEGRADED`/`DRAINING` lifecycle enum additions remain absent;
- adapter calls precede database-backed or ownership-mutating boundaries.

Disposable-database fault injection remains PRS-003E. This package owns no connection, replay, retry, recovery or resume path.

## Non-goals

- no durable mutation admission;
- no degraded/drain scheduler or online-population drain;
- no PRS-002 final-save change;
- no recovery probe, reconnect, SQL replay, retry, auto-resume or operator resume;
- no schema, migration, credential, production database or deployment change;
- no PRS-004 durable fencing or PRS-005/006/007/008 work;
- no new client opcode or universal staff bypass.

## Rollback

Revert the eventual squash merge of PR `#227`. No schema, data, credential or deployment rollback is required.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T00:18:00+02:00
head: pending_corrected_exact_head
head_scope: eight-path package; stale discovery contract test declared before correction
branch: dudantas/prs-003c-clean-rebuild
pr: 227
issue: 222
status: active
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-live-protocol-wiring.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/server/network/protocol/database_outage_protocol_admission.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/unit/server/network/protocol/database_outage_protocol_admission_test.cpp
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - tests/unit/server/CMakeLists.txt
proven:
  - PRS-003B and PRS-003C-A are terminal
  - canonical issue 222 owns this package
  - duplicate issue 224 and superseded PR 226 are closed without merge
  - clean candidate started directly from main 25cf8cc223b38ddc70a14382e79cb62d3c7caabd
  - account, game and handoff gates are in the intended live boundaries
  - explicit diagnostic capability is separate and performs no I/O
  - autofix 30494443887 passed
  - exact-head CI 30494444157 passed Fast Checks, Lua, Linux release, macOS, Docker and Windows Solution
  - exact-head CI failed only Linux debug test 277 because the old discovery test still required DatabaseOutage to be absent from protocols
derived:
  - the failed test is stale contract evidence, not a runtime or compile failure
unknown:
  - corrected exact-head CI and Required results
  - feature merge and lifecycle metadata
conflicts: []
first_failure:
  run: 30494444157
  job: 90720371262
  test: Prs003DatabaseOutageContractTest.RecordsLifecycleOnlyLoginGates
  cause: obsolete discovery assertion expected DatabaseOutage wiring to remain absent
rejected_hypotheses:
  - remove the live adapter to satisfy stale discovery evidence
  - add DEGRADED or DRAINING to GameState_t
  - bypass exact-head rerun after changing the test
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-live-protocol-wiring.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - src/server/network/protocol/database_outage_protocol_admission.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/unit/server/network/protocol/database_outage_protocol_admission_test.cpp
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - tests/unit/server/CMakeLists.txt
validation:
  - command: pre-clean CI 30493725646 and Required 30493725361
    result: PASS
  - command: exact-head autofix 30494443887
    result: PASS
  - command: exact-head CI 30494444157
    result: FAIL
    evidence: one obsolete source-contract assertion; all compile/platform jobs except Linux debug test job passed
blockers: []
next_action: Update the declared source-contract test to assert live Slice C wiring, then rerun full exact-head CI, Required and autofix.
```
