---
task_id: OTH-20260727-oam053-network-transport-adapt
coordination_id: OAM-053
status: review
branch: dudantas/oam-053-network-transport-adapt
base_branch: main
created: 2026-07-27
updated: 2026-07-27
related_pr: "163"
owned_paths:
  - src/server/network/message/outputmessage.hpp
  - src/server/network/protocol/protocol.hpp
  - src/server/network/protocol/protocol.cpp
  - src/server/network/protocol/protocol_profile.hpp
  - src/server/network/protocol/protocol_profile.cpp
  - src/server/network/protocol/transport_codec.hpp
  - src/server/network/protocol/transport_codec.cpp
  - tests/unit/server/CMakeLists.txt
  - tests/unit/server/network/protocol/oam_053_network_transport_test.cpp
  - docs/oam-053-network-transport-adapt.md
  - docs/agents/tasks/active/OTH-20260727-oam053-network-transport-adapt.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - network transport
  - TransportCodec
optional_reads: []
---

# OAM-053 Network Transport adaptation

## Result target

`network-transport → ADAPT`

## Objective

Adapt the evidence-backed transport authority, framing, validation and rejection/recovery invariants from the pinned Canary donors into current Otheryn while preserving the target's multiprotocol profiles, protocol-session handoff, typed startup profile and unrelated module-engine work.

## Acceptance criteria

- [x] Split current transport ownership into explicit login, sequenced-game and checksum-free-game profiles.
- [x] Make `TransportProfile` authoritative for framing, checksum, compression and encrypted layout.
- [x] Correct checksum-free block-count encode/decode symmetry.
- [x] Consume the complete current first game frame.
- [x] Return typed inbound transport outcomes with expected/received sequence evidence.
- [x] Mutate accepted sequence only after checksum and decrypt acceptance.
- [x] Fail closed on truncated checksum/header, invalid block size, missing inner length/padding and oversized padding.
- [x] Preserve current target protocol profile/session-handoff behavior and all existing profile fixtures.
- [x] Add deterministic target tests for every adapted invariant.
- [ ] Pass exact-final-head repository CI, `Required`, autofix and applicable runtime smoke.
- [ ] Merge with expected-head protection and complete a separate lifecycle archive.

## Safety boundaries

No wholesale `Connection` or `ProtocolGame` replacement. No account authentication, character-list semantics, game opcode layout, gameplay dispatch, schema, map, datapack, deployment, public target, arbitrary packet/credential surface, sustained-load or production claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T01:05:00+02:00
head: d181de15d6678b600efc4bdb8def6396e2e4c63c
branch: dudantas/oam-053-network-transport-adapt
pr: 163
status: validating
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
  - security
proven:
  - Canary OAM-053 preflight PR 979 merged as 6a9e6cf106b3e0193fb6a9d923a37cee38888f66.
  - Otheryn start main is 64ad965eee40f62ff996980fd8a0d329245c519f.
  - Open Otheryn PR 162 excludes protocol wire and does not own these paths.
  - Current Otheryn transport codec matched upstream and lacked the legacy-proven authority, framing and rejection/recovery fixes.
  - Three explicit current transport profiles now preserve the existing six target protocol profiles and session-handoff registry.
  - TransportCodec now owns checksum compression framing and encrypted layout while Protocol retains only per-session key and sequence state.
  - Inbound results are typed and accepted sequence state commits only after checksum and decrypt acceptance.
  - Checksum-free block counts use profile-owned extra bytes and current first-game framing consumes the captured 172-byte body.
  - Truncated checksum/header and malformed encrypted length/padding boundaries fail closed.
  - Deterministic target tests cover profile contracts, 172/168 sizing, checksum-free symmetry, truncation, zero, gap, replay and decrypt rejection.
  - Draft Required run 30224587710 passed; heavy CI was correctly skipped while the PR remained draft.
derived:
  - Semantic target integration preserves Otheryn-specific profile and session-handoff evolution without copying Connection or ProtocolGame lifecycle.
unknown:
  - First ready-state compile and test result on the integrated head.
conflicts: []
first_failure:
  marker: draft-heavy-ci-skipped
  result: EXPECTED
  evidence: Draft PR 163 passed Required while repository policy skipped heavy build jobs until Ready.
rejected_hypotheses:
  - classify target upstream transport as REUSE
  - replace connection and protocol game lifecycle wholesale
  - start login-protocol before transport completion
changed_paths:
  - docs/agents/tasks/active/OTH-20260727-oam053-network-transport-adapt.md
  - docs/oam-053-network-transport-adapt.md
  - src/server/network/message/outputmessage.hpp
  - src/server/network/protocol/protocol.hpp
  - src/server/network/protocol/protocol.cpp
  - src/server/network/protocol/protocol_profile.hpp
  - src/server/network/protocol/protocol_profile.cpp
  - src/server/network/protocol/transport_codec.hpp
  - src/server/network/protocol/transport_codec.cpp
  - tests/unit/server/CMakeLists.txt
  - tests/unit/server/network/protocol/oam_053_network_transport_test.cpp
validation:
  - command: target ownership and donor preflight
    result: PASS
    evidence: No active overlap and exact donor/target revisions are pinned.
  - command: draft Required 30224587710
    result: PASS
    evidence: Metadata and applicable draft gates passed; heavy jobs were policy-skipped.
blockers:
  - ready-state exact-head compile tests runtime smoke and Required
next_action: Mark PR 163 Ready, fix the first concrete compile/test failure, then freeze the exact final head and complete the merge audit.
```
