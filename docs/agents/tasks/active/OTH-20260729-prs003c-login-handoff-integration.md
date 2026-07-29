---
task_id: OTH-20260729-prs003c-login-handoff-integration
status: active
branch: dudantas/prs-003c-login-handoff-integration
base_branch: main
start_sha: 25cf8cc223b38ddc70a14382e79cb62d3c7caabd
issue: "222"
feature_pr: "228"
created: 2026-07-29
updated: 2026-07-30
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-login-handoff-integration.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_gate.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - src/server/network/protocol/protocolgame.hpp
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - tests/unit/server/network/protocol/database_outage_admission_gate_test.cpp
  - tests/unit/server/CMakeLists.txt
---

# PRS-003C-B live login and handoff outage admission wiring

## Goal

Wire the accepted PRS-003A snapshot owner and PRS-003C-A pure policy into the real account-login, game-login and protocol-session handoff boundaries without adding recovery, persistence, draining or universal staff-bypass scope.

## Boundaries

- `ProtocolLogin::onRecvFirstMessage`: capture and evaluate one live immutable snapshot before IP-ban and account database work.
- `ProtocolGame::onRecvFirstMessage`: capture one immutable snapshot before IP-ban and game-world authentication, and use the pure `GameLogin` policy with normal lifecycle to reject non-healthy or unknown outage state before database work.
- `ProtocolGame::login`: reuse that same snapshot after the existing minimal player preload exposes `CanAlwaysLogin`, then perform the full lifecycle/capability decision before name-lock, account-ban, waiting-list, full player load or placement work.
- `ProtocolGame::connect`: capture and evaluate one fresh snapshot from the already-resolved player before channel removal, modal/session mutation or `player->client` ownership transfer.
- Preserve existing startup, shutdown, maintenance, closing and closed responses and ordering.
- Reuse `getDatabaseOutageSnapshot()` and `DatabaseOutageAdmissionPolicy::evaluate()`; do not recreate outage classification, publication, state ownership or policy tables.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T00:50:00+02:00
head: pending_contract_test_update
head_scope: nine declared feature paths on PR 228; validation discovered one stale pre-integration source-contract assertion
branch: dudantas/prs-003c-login-handoff-integration
pr: 228
status: implementation_fix
context_routes:
  - production-resilience
  - database-outage
  - protocol-integration
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-login-handoff-integration.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_gate.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - src/server/network/protocol/protocolgame.hpp
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - tests/unit/server/network/protocol/database_outage_admission_gate_test.cpp
  - tests/unit/server/CMakeLists.txt
proven:
  - issue 222 is the reserved PRS-003C-B package
  - PRS-003B snapshot publication and PRS-003C-A pure policy are terminal on main
  - account login evaluates one live snapshot before IP-ban and account work
  - game login captures one snapshot before IP-ban and authentication, rejects outage before database work, then reuses the same snapshot after minimal capability preload
  - handoff evaluates one fresh snapshot before channel, modal and client-ownership mutation
  - only existing lifecycle-specific and maintenance protocol responses are used
  - CanAlwaysLogin is derived only from the existing player flag and never bypasses a non-healthy outage
  - Linux release, Windows CMake, Windows Solution, macOS, Docker and Docker quickstart validated the implementation successfully on e2d6598bf6b190033d80c753a47447354e8e1c47
  - Linux debug compiled and completed smoke setup before one stale source-contract assertion failed
  - current base main is 25cf8cc223b38ddc70a14382e79cb62d3c7caabd
derived:
  - the two-stage game-login evaluation is required to reject outage before database work while preserving the existing closing/closed CanAlwaysLogin behavior from the same immutable snapshot
  - the old lifecycle-only source assertion must become a lifecycle-and-outage integration assertion because PRS-003C-B intentionally adds DatabaseOutage admission references to both protocol sources
unknown: []
conflicts: []
first_failure: Prs003DatabaseOutageContractTest.RecordsLifecycleOnlyLoginGates rejects the intentional DatabaseOutage integration in protocollogin.cpp and protocolgame.cpp
rejected_hypotheses:
  - universal staff outage bypass
  - treating authenticated or hinted handoff as outage-safe
  - reading a second game-login snapshot after authentication or preload
  - adding reconnect, retry, SQL replay, drain orchestration or durable fencing
  - moving outage state ownership into protocol code
  - weakening or deleting the source-contract test instead of updating it to the accepted integration boundary
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-login-handoff-integration.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_gate.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - src/server/network/protocol/protocolgame.hpp
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - tests/unit/server/network/protocol/database_outage_admission_gate_test.cpp
  - tests/unit/server/CMakeLists.txt
validation:
  - command: live dependency and boundary audit
    result: PASS
    evidence: issue 222, terminal prerequisite records and exact account, game and handoff source boundaries inspected on main
  - command: focused source patch review
    result: PASS
    evidence: account and early game gates precede database work; handoff gate precedes ownership mutation; full game decision reuses the captured snapshot after capability preload
  - command: exact-head CI run 30495405143 attempt 2
    result: FAIL
    evidence: 626 of 627 tests passed; only Prs003DatabaseOutageContractTest.RecordsLifecycleOnlyLoginGates retained the pre-PRS-003C-B expectation that protocol sources contain no DatabaseOutage reference
  - command: exact-final-head CI, Required and autofix
    result: PENDING
    evidence: update the reserved compatibility test, then run all gates on the new exact head
blockers: []
next_action: update the reserved PRS-003 source-contract test to assert the accepted AccountLogin, GameLogin and ChannelHandoff integration, then rerun exact-final-head validation
```
