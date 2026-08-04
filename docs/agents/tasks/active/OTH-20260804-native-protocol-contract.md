---
task_id: OTH-20260804-native-protocol-contract
status: validating
branch: docs/OTS-20260804-native-protocol-contract
base_branch: main
created: 2026-08-04
updated: 2026-08-04
related_pr: "blakinio/Otheryn#356"
owned_paths:
  - docs/agents/tasks/active/OTH-20260804-native-protocol-contract.md
  - docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CORRESPONDENCE.md
  - docs/architecture/oteryn-native-gameplay-protocol.md
required_reads:
  - AGENTS.md
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - src/server/network/protocol/protocol_profile.hpp
  - src/server/network/protocol/transport_codec.hpp
  - src/server/network/protocol/protocolgame.cpp
search_first:
  - OTS-20260804-native-protocol-selection
optional_reads:
  - vcpkg.json
  - config.lua.dist
---

# Otheryn native gameplay protocol contract correspondence

## Goal

Record Otheryn producer and session-enforcement responsibilities for the canonical native gameplay protocol contract without modifying runtime behavior.

## Acceptance criteria

- [x] Canonical Platform contract and shared coordination ID are linked.
- [x] Canary-compatible profiles remain separate from the native family.
- [x] Native listener, opaque Game Session v2, command/result and state boundaries are explicit.
- [x] No unimplemented behavior is claimed.
- [x] Independent consistency review has no remaining material findings.
- [x] Required workflow passed on content head `4a7150f688539726bb7b42c6d715b57eb475cdf8`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-04T15:31:00Z
head: 4a7150f688539726bb7b42c6d715b57eb475cdf8
branch: docs/OTS-20260804-native-protocol-contract
pr: blakinio/Otheryn#356
status: validating
context_routes:
  - coordination:OTS-20260804-native-protocol-selection
  - canonical-pr:blakinio/Oteryn-Platform#519
  - consumer-correspondence:blakinio/otclient#265
owned_paths:
  - docs/agents/tasks/active/OTH-20260804-native-protocol-contract.md
  - docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CORRESPONDENCE.md
  - docs/architecture/oteryn-native-gameplay-protocol.md
proven:
  - Current networking remains ASIO-based and profile-driven.
  - Current Canary-compatible wire behavior is unchanged.
  - Native is a separate TLS, BE32 and protobuf family.
  - Target Game Session v2 is an opaque server-side-bound reference with atomic first-character admission.
  - Native commands converge only at authoritative game/domain seams.
  - This task changes documentation only.
derived:
  - Otheryn is the native gameplay producer and admission authority, not the selector or reusable-credential authority.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - native opcodes inside Canary profiles
  - first-byte protocol sniffing
  - replacing ASIO with Tokio
changed_paths:
  - docs/agents/tasks/active/OTH-20260804-native-protocol-contract.md
  - docs/architecture/oteryn-native-gameplay-protocol.md
  - docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CORRESPONDENCE.md
validation:
  - command: Required run 30924282180
    result: PASS
    evidence: content head 4a7150f688539726bb7b42c6d715b57eb475cdf8
  - command: independent contract consistency review
    result: PASS
    evidence: correspondence matches exact canonical authority, session, duplicate, state and rollback rules
blockers:
  - Platform PR must merge first
  - checkpoint exact-head workflow
next_action: verify checkpoint workflow, refresh merged canonical revision, then merge after Platform
```
