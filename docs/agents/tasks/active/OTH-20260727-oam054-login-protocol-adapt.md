---
task_id: OTH-20260727-oam054-login-protocol-adapt
coordination_id: OAM-054
status: review
branch: dudantas/oam-054-login-protocol-adapt
base_branch: main
created: 2026-07-27
updated: 2026-07-27
related_pr: "165"
owned_paths:
  - src/server/CMakeLists.txt
  - src/server/network/protocol/login_protocol_wire.hpp
  - src/server/network/protocol/login_protocol_wire.cpp
  - src/server/network/protocol/protocollogin.cpp
  - tests/unit/server/CMakeLists.txt
  - tests/unit/server/network/protocol/oam_054_login_protocol_test.cpp
  - docs/oam-054-login-protocol-adapt.md
  - docs/agents/tasks/active/OTH-20260727-oam054-login-protocol-adapt.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - ProtocolLogin
  - login protocol
optional_reads: []
---

# OAM-054 Login Protocol adaptation

## Result target

`login-protocol → ADAPT`

## Objective

Preserve Otheryn secure login-session tokens, explicit current/11.00/8.60 layouts and protocol-session handoff while adapting account-login response serialization into a testable target-owned wire contract corresponding exactly to the maintained-client parser.

## Acceptance criteria

- [x] Preserve current, 11.00 and 8.60 request-layout selection and pre-RSA validation.
- [x] Preserve fail-closed `LoginSessionManager` token issuance and opcode `0x28` handoff.
- [x] Serialize modern world/character lists through a pure target-owned wire helper.
- [x] Serialize the modern account tail as account status, subscription status and premium-expiry timestamp.
- [x] Serialize legacy character lists and `u16` premium days without changing legacy profile semantics.
- [x] Disconnect after the complete response exactly as before.
- [x] Add deterministic tests decoding session-key, modern and legacy responses with the maintained-client field order.
- [x] Cap token authorization, response count, payload records and session hints to the same `u8` character snapshot.
- [ ] Preserve existing OAM-044 profile and OAM-045 session-handoff regressions under full CTest.
- [ ] Pass exact-final-head repository CI, `Required`, autofix and applicable runtime smoke.
- [ ] Merge with expected-head protection and complete a separate lifecycle archive.

## Safety boundaries

No password hashing, credential policy, account repository, game-world authentication, player attach/detach, gameplay opcode, client UI, launcher, schema, datapack, public endpoint, production credential or deployment change.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T09:10:00+02:00
head: 0a528ad0160214cb3ec9fe8c43ee2e90b0dd9720
branch: dudantas/oam-054-login-protocol-adapt
pr: 165
status: validating
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
  - security
  - testing
proven:
  - Canary OAM-054 preflight PR 983 merged as d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61.
  - Otheryn task-start main is 9703da845384423ad85883216bf8853642c21bcd.
  - No active Otheryn PR owns ProtocolLogin or target login-wire paths.
  - Otheryn explicit current/11.00/8.60 request layouts, transport selection, RSA/XTEA, secure token issuance and session hints remain in ProtocolLogin.
  - Target-owned login_protocol_wire writes opcode 0x28 and deterministic modern/legacy opcode 0x64 responses.
  - Modern account tail is explicitly status zero, subscription free/premium and premium-expiry u32, matching maintained OTClient parser order.
  - Legacy response retains character records followed by premium-days u16.
  - A single capped snapshot of at most 255 names now feeds secure-token authorization, serialized payload and session hints.
  - Six deterministic tests decode session key, modern premium/free responses, legacy response and modern/legacy count caps to exact message end.
  - Existing OAM-044/OAM-045 tests remain registered in the same canary_ut target.
derived:
  - The bounded serializer closes the wire-evidence gap without copying Canary ProtocolLogin or changing the maintained client.
unknown:
  - First Ready-state compile, linker and full CTest result.
conflicts: []
first_failure:
  marker: maintained-client-account-tail-correspondence
  result: FIXED
  evidence: Modern serializer now emits explicit AccountStatus Ok, SubscriptionStatus and premium expiry in maintained-client order with deterministic decoding tests.
rejected_hypotheses:
  - classify existing ProtocolLogin as REUSE without wire tests
  - copy Canary ProtocolLogin wholesale
  - change the maintained client before proving server-side correspondence
  - authorize more character names than the u8 response can publish
changed_paths:
  - docs/agents/tasks/active/OTH-20260727-oam054-login-protocol-adapt.md
  - docs/oam-054-login-protocol-adapt.md
  - src/server/CMakeLists.txt
  - src/server/network/protocol/login_protocol_wire.hpp
  - src/server/network/protocol/login_protocol_wire.cpp
  - src/server/network/protocol/protocollogin.cpp
  - tests/unit/server/CMakeLists.txt
  - tests/unit/server/network/protocol/oam_054_login_protocol_test.cpp
validation:
  - command: target ownership and wire-contract preflight
    result: PASS
    evidence: Exact server/client revisions and field order are pinned; no active target overlap exists.
  - command: implementation review
    result: PASS
    evidence: Pure serializer, target integration and deterministic client-order decoder tests are present with bounded character counts.
blockers:
  - Ready-state exact-head compile, full CTest, platform gates, Required and autofix
next_action: Mark PR 165 Ready. Fix only concrete compile/test failures, then freeze the final head, complete exact-head gates and merge audit.
```
