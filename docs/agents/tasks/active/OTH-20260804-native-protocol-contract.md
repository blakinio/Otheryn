---
task_id: OTH-20260804-native-protocol-contract
status: implementing
branch: docs/OTS-20260804-native-protocol-contract
base_branch: main
created: 2026-08-04
updated: 2026-08-04
related_pr: ""
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

Record Otheryn producer and session-enforcement responsibilities for the canonical native gameplay protocol contract without modifying ASIO, login admission, protocol handlers, schema, dependencies or runtime behavior.

## Acceptance criteria

- The document points to the exact canonical Platform contract and coordination ID.
- Current Canary-compatible profiles remain distinct from the future native family.
- Native framing, session validation, action authority, synchronization and downgrade boundaries are explicit.
- No unimplemented Otheryn behavior is claimed as present.
- Required documentation/governance validation and exact-head CI pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-04T14:50:00Z
head: UNKNOWN
branch: docs/OTS-20260804-native-protocol-contract
pr: none
status: implementing
context_routes:
  - coordination:OTS-20260804-native-protocol-selection
  - canonical:blakinio/Oteryn-Platform/docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CONTRACT.md
owned_paths:
  - docs/agents/tasks/active/OTH-20260804-native-protocol-contract.md
  - docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CORRESPONDENCE.md
  - docs/architecture/oteryn-native-gameplay-protocol.md
proven:
  - Current Otheryn game networking is ASIO-based and profile-driven.
  - Current Canary-compatible transport profiles include explicit framing, encryption, checksum, sequence and compression behavior.
  - protobuf is already an Otheryn build dependency, but no native gameplay schema/runtime is authorized in this task.
derived:
  - Native protocol must be a separate producer family and must not reuse or translate through Canary-compatible packet profiles.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses: []
changed_paths:
  - docs/agents/tasks/active/OTH-20260804-native-protocol-contract.md
validation:
  - command: repository documentation/governance validation
    result: NOT_RUN
    evidence: correspondence documents not yet complete
blockers: []
next_action: add the Otheryn correspondence and architecture boundary documents
```
