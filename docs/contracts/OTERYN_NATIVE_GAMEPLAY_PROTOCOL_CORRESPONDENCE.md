# Otheryn native gameplay protocol correspondence

Coordination ID: `OTS-20260804-native-protocol-selection`  
Canonical source of truth: `blakinio/Oteryn-Platform/docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CONTRACT.md`  
Canonical review PR: `blakinio/Oteryn-Platform#519`  
Local architecture boundary: `docs/architecture/oteryn-native-gameplay-protocol.md`

## Status

Contract correspondence only. This document does not implement or enable native gameplay framing, a TLS listener, protobuf generation, Game Session v2, action results, snapshots, deltas or automatic selection.

Current Otheryn remains the authoritative gameplay server with existing ASIO networking and profile-driven Canary-compatible protocol/transport behavior. Native `oteryn.native.v1` is a separate future producer family.

## Normative adoption

Otheryn adopts the meanings and limits in the canonical contract for:

- Gateway-selected candidate and World Registry policy revision;
- Game Session contract version 2;
- bind-on-first-admission character/session semantics;
- family `oteryn`, profile `oteryn.native.v1`, transport `tcp.tls13.protobuf.be32.v1`;
- TLS 1.3 and ALPN `oteryn-game/1`;
- 32-bit big-endian length framing and protobuf schema revision 1;
- exact frame/message/string/collection/snapshot bounds;
- stream sequence, command ID, client sequence, server tick and state revision semantics;
- action result state machine and stable reason vocabulary;
- full snapshot, ordered delta and bounded resync behavior;
- no session resume, command replay or in-session adapter switch;
- downgrade, replay, cross-character/world/profile and log-redaction requirements.

If this document and the canonical contract differ, the canonical merged revision controls. A local implementation task must pin the exact canonical commit and review IDL SHA-256 before mutation.

## Current source correspondence

| Existing Otheryn boundary | Current role | Native target relationship |
|---|---|---|
| `src/server/network/protocol/protocol_profile.hpp` | enumerates Canary-compatible protocol, feature, login and transport profiles | remains compatibility-only; native identifiers are not added until the producer package |
| `src/server/network/protocol/transport_codec.hpp` | owns current profile-selected length/encryption/checksum/sequence/compression behavior | native uses a separate codec and TLS boundary; it must not reuse XTEA/Canary framing by familiarity |
| `src/server/network/protocol/protocolgame.cpp` | decodes current client packets and dispatches authoritative game actions | native adapter maps semantic commands to the same authoritative game/domain operations through bounded explicit adapters |
| ASIO connection/service architecture | owns asynchronous sockets and lifecycle | retained; no Tokio/server runtime replacement is authorized |
| current Game Session-compatible admission path | accepts current Gateway-issued world-entry authorization | later extended to contract v2 and exact native selection binding |
| current profile/port configuration | chooses current/legacy Canary-compatible listeners | native listener is separate, disabled by default and readiness-advertised only after exact deployment proof |
| `vcpkg.json` protobuf dependency | available build capability | permits later generated schema use but creates no runtime behavior in this task |

## Otheryn producer responsibilities

The future Otheryn implementation package solely owns:

1. **Admission**
   - validate credential version, expiry, generation, audience, world/channel, policy revision, family/profile/transport/schema/capability digest;
   - validate selected character ownership;
   - atomically bind and consume one session for one connection and character;
   - reject replay/cross-binding before gameplay state is exposed.

2. **Native transport**
   - separate configurable TCP listener;
   - TLS 1.3, certificate/service identity and ALPN `oteryn-game/1`;
   - exact bounded framing and protobuf parsing;
   - deterministic cancellation, close and resource limits using existing ASIO ownership.

3. **Command handling**
   - validate monotonic stream/command sequences and deduplicate exact commands;
   - map native semantic intent into existing authoritative movement, target, spell, item, loot, chat and logout operations;
   - emit the canonical action lifecycle without claiming effects before authoritative state changes.

4. **State production**
   - assign monotonic server sequence/tick and state revision;
   - emit canonical initial snapshot records and ordered deltas;
   - correlate reversible movement reconciliation to command ID;
   - remain authoritative for inventory, containers, loot, combat, resources and cooldowns;
   - provide one bounded resync path and no v1 resume/replay.

5. **Security/operations**
   - enforce handshake, frame, rate, command and resync limits independently;
   - redact credentials, IDs, payloads and chat from logs;
   - expose low-cardinality readiness/metrics for exact contract/profile/schema/capability identity;
   - preserve Canary behavior and keep native disabled until exact integrated evidence.

## Prohibited implementation shortcuts

Otheryn must not:

- add native opcodes to an existing Canary profile;
- translate native protobuf messages into synthetic Canary packets before dispatch;
- sniff the first bytes and fall back to another profile;
- accept a family/profile/schema/capability tuple not bound to Game Session;
- use client-supplied account/world/character/profile claims without authoritative validation;
- acknowledge TCP receipt as gameplay success;
- replay a command after disconnect or ambiguous persistence outcome;
- allow native compression in profile v1;
- log raw credentials, session/command IDs, account/character IDs, chat text or frames;
- enable the listener or advertise native in this contract task.

## Core action mapping obligations

| Native command | Otheryn authoritative seam |
|---|---|
| `Step`, `StopMovement` | movement admission, collision/speed/path and final position |
| attack/follow set/clear | target visibility/rules/path and target state |
| `CastSpell` | spell knowledge, cooldown, resource, range/LOS and effects |
| `Use`, `UseWith`, `MoveItem` | item identity/location/ownership/quantity/capacity/scripts and committed mutations |
| `QuickLoot`, `LootCorpse` | corpse ownership/rules/range/capacity/destination and transfers |
| `Say` | channel/private permission, moderation and delivery |
| `Logout` | fight/condition/lifecycle checks, final save/close policy |

The implementation package must identify exact current source functions and prove that no native path bypasses their authority.

## Fixture ownership

Otheryn owns:

- canonical native producer golden frames for every message it emits;
- Game Session v2 admission fixtures and replay/cross-binding negatives;
- action lifecycle and state revision tests;
- malformed frame/parser/fuzz regression fixtures;
- exact schema SHA-256 and generated-code provenance.

Synthetic fixtures only. No real credential, account, character, endpoint, chat or packet capture enters Git.

## Compatibility and rollout

- A native-capable Otheryn may merge before the Rust adapter only with listener and World Registry advertisement disabled.
- Canary-compatible profiles remain unchanged and independently selectable.
- Readiness must report the exact native profile, schema hash and capability digest; Gateway must not advertise contradictory readiness.
- Enablement is atomic-required with exact Platform/Gateway, Otheryn and Rust revisions.
- Rollback disables advertisement first, drains/closes native sessions and then disables the listener. Active native sessions never switch to Canary.

## Later task

Use `blakinio/Oteryn-Platform/docs/agents/prompts/OTS_OTHERYN_NATIVE_PROTOCOL_IMPLEMENTATION.md` only after the canonical contract and all three correspondence PRs are merged and archived.
