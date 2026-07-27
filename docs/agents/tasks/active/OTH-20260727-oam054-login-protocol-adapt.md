---
task_id: OTH-20260727-oam054-login-protocol-adapt
coordination_id: OAM-054
status: implementing
branch: dudantas/oam-054-login-protocol-adapt
base_branch: main
created: 2026-07-27
updated: 2026-07-27
related_pr: "pending"
owned_paths:
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

- [ ] Preserve current, 11.00 and 8.60 request-layout selection and pre-RSA validation.
- [ ] Preserve fail-closed `LoginSessionManager` token issuance and opcode `0x28` handoff.
- [ ] Serialize modern world/character lists through a pure target-owned wire helper.
- [ ] Serialize the modern account tail as account status, subscription status and premium-expiry timestamp.
- [ ] Serialize legacy character lists and `u16` premium days without changing legacy profile semantics.
- [ ] Disconnect after the complete response exactly as before.
- [ ] Add deterministic tests decoding session-key, modern and legacy responses with the maintained-client field order.
- [ ] Preserve existing OAM-044 profile and OAM-045 session-handoff regressions.
- [ ] Pass exact-final-head repository CI, `Required`, autofix and applicable runtime smoke.
- [ ] Merge with expected-head protection and complete a separate lifecycle archive.

## Safety boundaries

No password hashing, credential policy, account repository, game-world authentication, player attach/detach, gameplay opcode, client UI, launcher, schema, datapack, public endpoint, production credential or deployment change.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T08:45:00+02:00
head: 9703da845384423ad85883216bf8853642c21bcd
branch: dudantas/oam-054-login-protocol-adapt
pr: pending
status: implementing
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
  - Otheryn already has explicit current/11.00/8.60 account layouts, secure token issuance and protocol-session hints.
  - Maintained OTClient parser consumes modern account status u8, subscription u8 and premium expiry u32; legacy consumes premium days u16.
  - Maintained client treats subscription value one as premium through the existing server boolean convention and legacy conversion; account status OK is zero.
  - Existing OAM-044/OAM-045 tests prove layout metadata and handoff hints but not complete response serialization.
derived:
  - A bounded target-owned serializer can close the wire-evidence gap without copying Canary ProtocolLogin or changing the client.
unknown:
  - First compile/test result after extracting response serialization.
conflicts: []
first_failure:
  marker: maintained-client-account-tail-correspondence
  result: BLOCKED
  evidence: Existing target writes premium remaining days into the client account-status field and has no direct response-decoding regression.
rejected_hypotheses:
  - classify existing ProtocolLogin as REUSE without wire tests
  - copy Canary ProtocolLogin wholesale
  - change the maintained client before proving server-side correspondence
changed_paths:
  - docs/agents/tasks/active/OTH-20260727-oam054-login-protocol-adapt.md
validation:
  - command: target ownership and wire-contract preflight
    result: PASS
    evidence: Exact server/client revisions and field order are pinned; no active target overlap exists.
blockers: []
next_action: Open a draft target PR, add the bounded serializer and deterministic response-decoding tests, then run focused and exact-final validation.
```
