---
task_id: OTH-20260729-prs003c-login-handoff-integration
status: terminal
branch: dudantas/prs-003c-login-handoff-integration
base_branch: main
start_sha: 25cf8cc223b38ddc70a14382e79cb62d3c7caabd
issue: "222"
feature_pr: "228"
feature_head_sha: 0dee1dbe0251d09abd38a10eb0aabf9ea1075826
feature_merge_sha: ec14b683b04078aabca42cbe051fff3c5f0554a1
lifecycle_pr: pending
lifecycle_merge_sha: pending
created: 2026-07-29
updated: 2026-07-30
owned_paths:
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

## Terminal result

PRS-003C-B is complete. Feature PR #228 merged into `main` as `ec14b683b04078aabca42cbe051fff3c5f0554a1`, and issue #222 closed as completed.

The implementation:

- evaluates one immutable live outage snapshot in account login before IP-ban and account database work;
- captures one game-login snapshot before IP-ban and authentication, rejects non-healthy or unknown outage state before database work, and reuses the same snapshot after minimal preload for the real lifecycle and `CanAlwaysLogin` decision;
- evaluates a fresh `ChannelHandoff` snapshot before channel, modal or client-ownership mutation;
- reuses the accepted PRS-003 snapshot owner and pure PRS-003C policy;
- preserves existing startup, shutdown, maintenance, closing and closed responses;
- adds deterministic tests for one-snapshot capture/reuse, lifecycle privilege, fail-closed unknown state and no post-rejection mutation;
- updates the earlier source-contract test from its intentionally temporary lifecycle-only expectation to the accepted PRS-003C-B protocol integration contract.

## Validation

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T01:07:15+02:00
status: terminal
feature_pr: 228
feature_head: 0dee1dbe0251d09abd38a10eb0aabf9ea1075826
feature_merge: ec14b683b04078aabca42cbe051fff3c5f0554a1
issue: 222
issue_state: closed_completed
proven:
  - account login gates outage before database-backed admission work
  - game login captures before database work and reuses the identical immutable snapshot after capability preload
  - handoff gates outage before ownership and session mutation
  - CanAlwaysLogin never bypasses a non-healthy or unknown outage state
  - no reconnect, retry, SQL replay, recovery probe, draining orchestration, schema, deployment, diagnostic route or durable PRS-004 fencing was added
  - final feature diff contains the nine declared paths
  - PR discussions, reviews and review threads were empty
  - base remained fresh through feature merge
validation:
  - command: CI #638 on exact head 0dee1dbe0251d09abd38a10eb0aabf9ea1075826
    result: PASS
    evidence: Fast Checks, Lua, Linux release/debug tests, Windows CMake/Solution, macOS, Docker and Docker quickstart completed successfully
  - command: Required #696
    result: PASS
    evidence: required workflow accepted the exact feature head
  - command: autofix #550
    result: PASS
    evidence: no corrective commit was produced
  - command: issue and merge audit
    result: PASS
    evidence: PR 228 merged as ec14b683b04078aabca42cbe051fff3c5f0554a1 and issue 222 closed completed
blockers: []
next_action: merge this lifecycle archive PR, then record its PR number and merge SHA in one metadata-only finalizer
```
