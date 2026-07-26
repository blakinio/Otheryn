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

Adapt evidence-backed transport authority, framing, validation and rejection/recovery invariants into current Otheryn while preserving target multiprotocol profiles, protocol-session handoff, typed startup profile and unrelated module-engine work.

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
- [x] Pass implementation-head repository CI, `Required`, autofix and applicable runtime smoke.
- [ ] Pass exact-final-head repository CI, `Required` and autofix without another commit.
- [ ] Merge with expected-head protection and complete a separate lifecycle archive.

## Safety boundaries

No wholesale `Connection` or `ProtocolGame` replacement. No account authentication, character-list semantics, game opcode layout, gameplay dispatch, schema, map, datapack, deployment, public target, arbitrary packet/credential surface, sustained-load or production claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T01:30:00+02:00
head: 28832771921a6e18f9128aad796667c77f42a626
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
  - Otheryn task-start and current main are 64ad965eee40f62ff996980fd8a0d329245c519f.
  - Open Otheryn PR 162 excludes protocol wire and does not own these paths.
  - Three explicit current transport profiles preserve all six target protocol profiles and session-handoff registry.
  - TransportCodec owns checksum compression framing and encrypted layout while Protocol retains only per-session key and sequence state.
  - Inbound results are typed and accepted sequence state commits only after checksum and decrypt acceptance.
  - Checksum-free block counts use profile-owned extra bytes and current first-game framing consumes the captured 172-byte body.
  - Truncated checksum/header and malformed encrypted length/padding boundaries fail closed.
  - Deterministic target tests cover profile contracts, 172/168 sizing, checksum-free symmetry, truncation, zero, gap, replay and decrypt rejection.
  - Implementation head 422ce59ca8fede681d595764965c0534d11edc16 passed CI 30225272288, Required 30225272219 and autofix 30225272241 without a follow-up commit.
  - CI 30225272288 passed Fast Checks, Lua, Docker, Linux release/debug, full Linux CTest, Canary and Global smoke, macOS smoke and Windows CMake/Solution builds.
  - The first Ready head Docker failure occurred before project compilation during vcpkg bootstrap with curl connection reset; the next unchanged Docker path passed.
  - The first Linux-debug compile failure was an inherited donor-only dispatcher test hook; target-native forced connection cleanup fixed it without runtime production changes.
derived:
  - Semantic target integration preserves Otheryn-specific profile and session-handoff evolution without copying Connection or ProtocolGame lifecycle.
  - The validated disposition is ADAPT, not REUSE or wholesale migration.
unknown:
  - Exact-final checkpoint gate and merge result.
conflicts: []
first_failure:
  marker: donor-only-test-cleanup-hook
  result: FIXED
  evidence: Linux debug rejected Dispatcher::executeSerialEventsForTest; focused connections are never accepted, so close(true) is sufficient target-native cleanup and the full subsequent CTest passed.
rejected_hypotheses:
  - classify target upstream transport as REUSE
  - replace connection and protocol game lifecycle wholesale
  - alter production runtime to satisfy a test-only cleanup mismatch
  - treat the transient Docker download reset as a source defect
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
  - command: implementation-head CI 30225272288
    result: PASS
    evidence: All applicable platform builds, runtime smoke and full Linux CTest passed.
  - command: implementation-head Required 30225272219
    result: PASS
    evidence: Applicable CI workflows were accepted.
  - command: implementation-head autofix 30225272241
    result: PASS
    evidence: Formatting passed with no follow-up commit.
  - command: Docker failure classification
    result: PASS
    evidence: Initial curl connection reset occurred before project compilation; the next full Docker job passed unchanged source semantics.
blockers:
  - exact-final-head CI Required and autofix must pass without another commit
next_action: Freeze this exact head, verify exact-final gates, audit eleven paths, discussions and behind_by zero, then squash-merge with expected-head protection and complete lifecycle archival.
```
