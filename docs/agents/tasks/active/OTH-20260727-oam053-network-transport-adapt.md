---
task_id: OTH-20260727-oam053-network-transport-adapt
coordination_id: OAM-053
status: implementing
branch: dudantas/oam-053-network-transport-adapt
base_branch: main
created: 2026-07-27
updated: 2026-07-27
related_pr: "pending"
owned_paths:
  - src/server/network/message/outputmessage.hpp
  - src/server/network/protocol/protocol.hpp
  - src/server/network/protocol/protocol.cpp
  - src/server/network/protocol/protocol_profile.hpp
  - src/server/network/protocol/protocol_profile.cpp
  - src/server/network/protocol/transport_codec.hpp
  - src/server/network/protocol/transport_codec.cpp
  - tests/unit/server/CMakeLists.txt
  - tests/unit/server/network/protocol/multiprotocol_test.cpp
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

- [ ] Split current transport ownership into explicit login, sequenced-game and checksum-free-game profiles.
- [ ] Make `TransportProfile` authoritative for framing, checksum, compression and encrypted layout.
- [ ] Correct checksum-free block-count encode/decode symmetry.
- [ ] Consume the complete current first game frame.
- [ ] Return typed inbound transport outcomes with expected/received sequence evidence.
- [ ] Mutate accepted sequence only after checksum and decrypt acceptance.
- [ ] Fail closed on truncated checksum/header, invalid block size, missing inner length/padding and oversized padding.
- [ ] Preserve current target protocol profile/session-handoff behavior and all existing profile fixtures.
- [ ] Add deterministic target tests for every adapted invariant.
- [ ] Pass exact-final-head repository CI, `Required`, autofix and applicable runtime smoke.
- [ ] Merge with expected-head protection and complete a separate lifecycle archive.

## Safety boundaries

No wholesale `Connection` or `ProtocolGame` replacement. No account authentication, character-list semantics, game opcode layout, gameplay dispatch, schema, map, datapack, deployment, public target, arbitrary packet/credential surface, sustained-load or production claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T00:35:00+02:00
head: 64ad965eee40f62ff996980fd8a0d329245c519f
branch: dudantas/oam-053-network-transport-adapt
pr: pending
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
  - security
proven:
  - Canary OAM-053 preflight PR 979 merged as 6a9e6cf106b3e0193fb6a9d923a37cee38888f66.
  - Otheryn start main is 64ad965eee40f62ff996980fd8a0d329245c519f.
  - Open Otheryn PR 162 excludes protocol wire and does not own these paths.
  - Current Otheryn transport codec matches upstream and lacks the legacy-proven authority, framing and rejection/recovery fixes.
  - Donor PR 71 merge bbff04524bbb99ab54c9571c24382399b904cbd8 makes transport profiles authoritative.
  - Donor PR 155 merge 4535836d4df0fc669033ed73f525754a1a2d1b40 fixes checksum-free block-count symmetry.
  - Donor PR 375 merge 5c750e13fb95f46225807b8907a95ce3091283c8 fixes complete current first-frame sizing.
  - SEC-005 merge 1408aaa886240034a90fc33873e9b9e0fa47cab6 provides exact disposable runtime rejection/recovery evidence.
derived:
  - Semantic target integration is required; pure reuse and wholesale donor replacement are both invalid.
unknown:
  - Exact compile/test repairs required after reconciling target multiprotocol fixtures.
conflicts: []
first_failure:
  marker: not-run
  result: NOT_RUN
  evidence: Target implementation has not yet been materialized or validated.
rejected_hypotheses:
  - classify target upstream transport as REUSE
  - replace connection and protocol game lifecycle wholesale
  - start login-protocol before transport completion
changed_paths:
  - docs/agents/tasks/active/OTH-20260727-oam053-network-transport-adapt.md
validation:
  - command: target ownership and donor preflight
    result: PASS
    evidence: No active overlap and exact donor/target revisions are pinned.
blockers: []
next_action: Open a draft target PR, integrate the bounded runtime and tests, then run focused and exact-final validation.
```
