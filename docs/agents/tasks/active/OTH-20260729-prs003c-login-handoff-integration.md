---
task_id: OTH-20260729-prs003c-login-handoff-integration
status: active
branch: dudantas/prs-003c-login-handoff-integration
base_branch: main
start_sha: 25cf8cc223b38ddc70a14382e79cb62d3c7caabd
issue: "222"
feature_pr: "228"
created: 2026-07-29
updated: 2026-07-29
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-login-handoff-integration.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_gate.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - src/server/network/protocol/protocolgame.hpp
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
updated_at: 2026-07-30T00:12:00+02:00
head: pending_exact_final_validation
head_scope: eight declared feature paths on PR 228; temporary patch transport paths removed from the final diff
branch: dudantas/prs-003c-login-handoff-integration
pr: 228
status: validation
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
  - final PR diff contains exactly the eight declared paths
  - current base main is 25cf8cc223b38ddc70a14382e79cb62d3c7caabd
derived:
  - the two-stage game-login evaluation is required to reject outage before database work while preserving the existing closing/closed CanAlwaysLogin behavior from the same immutable snapshot
unknown: []
conflicts: []
first_failure: none
rejected_hypotheses:
  - universal staff outage bypass
  - treating authenticated or hinted handoff as outage-safe
  - reading a second game-login snapshot after authentication or preload
  - adding reconnect, retry, SQL replay, drain orchestration or durable fencing
  - moving outage state ownership into protocol code
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-login-handoff-integration.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_gate.hpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
  - src/server/network/protocol/protocolgame.hpp
  - tests/unit/server/network/protocol/database_outage_admission_gate_test.cpp
  - tests/unit/server/CMakeLists.txt
validation:
  - command: live dependency and boundary audit
    result: PASS
    evidence: issue 222, terminal prerequisite records and exact account, game and handoff source boundaries inspected on main
  - command: PR 228 changed-path audit
    result: PASS
    evidence: exactly the eight declared feature paths remain; temporary workflow and helper paths are absent from the PR diff
  - command: focused source patch review
    result: PASS
    evidence: account and early game gates precede database work; handoff gate precedes ownership mutation; full game decision reuses the captured snapshot after capability preload
  - command: exact-final-head CI, Required and autofix
    result: PENDING
    evidence: final non-draft validation has not completed yet
blockers: []
next_action: run full exact-final-head CI, Required and autofix, audit discussions and base drift, then merge with expected head
```
