# Otheryn native gameplay protocol correspondence

Coordination ID: `OTS-20260804-native-protocol-selection`  
Canonical contract: `blakinio/Oteryn-Platform/docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CONTRACT.md`  
Canonical contract revision: `2`  
Canonical schema revision: `2`  
Canonical schema SHA-256: `9c67f19525400fb9890d2a3541ceb6d02eb955061540ad39ca1c1d891c06eba9`  
Canonical merged Platform revision: `PENDING_PLATFORM_PR_540_MERGE`  
Candidate Platform head reviewed by this draft: `19a9b3a27d2b00d4dfb8fd83ebf24dec15233b91`  
Local architecture boundary: `docs/architecture/oteryn-native-gameplay-protocol.md`

## Status

Contract correspondence only. This PR implements no Game Session v2 storage, listener, TLS, protobuf, action result, snapshot, delta, readiness or automatic-selection behavior.

Otheryn remains the authoritative gameplay server with ASIO networking. Canary compatibility profiles remain isolated in their existing compatibility mechanism. The native Oteryn producer has exactly one identity—`family = oteryn`, `native_protocol_version = 1`—and has no native profile field, alias, placeholder, catalogue, enum, registry, factory, ordering or selector.

This draft must not merge while `Canonical merged Platform revision` is pending. After Platform PR #540 merges, that marker must be replaced by the exact immutable merge commit and the candidate head must be verified as an ancestor of that merge.

## Normative adoption

Otheryn adopts the exact canonical Platform revision and digest above for:

- one Gateway-selected candidate and bound World Registry policy revision;
- opaque hashed-at-rest Game Session v2 bearer reference with server-side claims;
- `game_account_id`, security generation, world, channel, endpoint audience and atomic first-character admission;
- exact native tuple `family = oteryn`, `native_protocol_version = 1`, `transport = tcp.tls13.protobuf.be32.v1`;
- schema revision `2`, exact schema SHA-256 and exact sorted capability digest;
- TLS 1.3, ALPN `oteryn-game/1`, unsigned 32-bit big-endian framing, protobuf and no v1 compression;
- stream/command sequences, UUIDv4 command ID, exact received-command byte hash, server tick and state revision;
- authoritative action lifecycle and stable typed reasons;
- complete digest-checked snapshot, strict deltas, movement reconciliation and one bounded resync;
- no resume, reconnect replay, password fallback, byte sniffing, packet translation or in-session adapter switch;
- replay, cross-character/world/channel/native-version/endpoint and redaction requirements.

Any implementation package must pin the exact merged Platform commit, exact IDL SHA-256 and Platform fixture manifest. A later canonical revision requires an explicit correspondence update before implementation.

## Existing source correspondence

| Current boundary | Current role | Native target |
|---|---|---|
| `protocol_profile.hpp` | Canary-compatible protocol/login/transport profiles | remains compatibility-only; native does not import, alias or extend it |
| `transport_codec.hpp` | current Canary length/XTEA/checksum/sequence/compression behavior | separate TLS + BE32 + protobuf codec |
| `protocolgame.cpp` | Canary packet decode and authoritative action dispatch | native semantic commands converge only at explicit authoritative game/domain seams |
| ASIO connection/service architecture | asynchronous sockets/lifecycle | retained; no Tokio/server runtime replacement |
| current Game Session admission | current Gateway world-entry authorization | later opaque v2 claim lookup and exact native tuple binding |
| current Canary profile/port configuration | Canary listeners | separate native listener disabled by default and exact-readiness gated |
| existing protobuf dependency | build capability | permits later generated bindings but creates no runtime behavior now |

## Future producer responsibilities

### Admission

- look up the opaque credential by repository-approved hash;
- validate v2 version, expiry, security generation, exact audience/endpoint, world/channel, policy revision, family/native-version/transport/schema/capability tuple;
- reject any native identity other than `family = oteryn` and `native_protocol_version = 1`;
- load current ownership of the requested character for `game_account_id`;
- atomically transition `ISSUED_UNBOUND` to `ACTIVE_BOUND(character_id, connection_id)` once;
- expose no gameplay state before success;
- make replay, wrong binding and ambiguous consume/bind outcomes terminal.

Otheryn does not receive the raw Identity subject. Authority comes from Platform ticket redeem and stored account/security-generation claims.

### Native transport and command path

- separate configurable TLS 1.3 listener, off by default, with ALPN `oteryn-game/1`;
- bounded unsigned BE32/protobuf parser under existing ASIO lifecycle ownership;
- no native/Canary sniffing or translation;
- exact per-direction stream and command sequences;
- bounded duplicate-result cache keyed by command ID, sequence and SHA-256 of exact received serialized `CommandEnvelope` bytes;
- exact duplicate returns the prior result/effects; command-ID payload conflict is fatal; an out-of-window duplicate fails closed;
- semantic commands call existing authoritative movement, target, spell, item, loot, chat and logout seams;
- one terminal result per admitted command unless session termination prevents delivery;
- TCP receipt never means gameplay success.

### State production

- monotonic server sequence, tick and domain revisions;
- bounded initial snapshot whose digest covers exact on-wire `SnapshotChunk` envelope payload bytes;
- only validated contiguous deltas with explicit base/new revisions;
- duplicate, regressed or conflicting delta is fatal; a gap allows one bounded replacement-snapshot resync;
- reversible movement correlation by command ID;
- inventory, containers, loot, combat, resources, cooldowns and persistence remain server-authoritative;
- no native v1 resume or reconnect replay.

### Policy, readiness and rollback

- authenticated readiness reports exactly `enabled`, family, native protocol version, transport, schema revision/hash, capability digest, endpoint ID, ALPN and TLS minimum;
- readiness contains no native profile-shaped key or value;
- disabling advertisement stops new issuance;
- admission validates the stored session tuple against local listener/readiness identity without live World Registry lookup;
- already-issued unexpired sessions may bind/drain after normal advertisement disablement unless explicit admission revocation or emergency listener shutdown applies;
- emergency shutdown closes native sessions and never migrates them to Canary.

### Security and operations

- finite independent handshake, frame, command, heartbeat and resync limits;
- no credentials, session/command IDs, account/character IDs, chat or payloads in logs/artifacts;
- low-cardinality contract/native-version/reason/deployment metrics;
- Canary behavior unchanged and native disabled until integrated evidence.

## Prohibited shortcuts

No native opcodes in Canary compatibility profiles, native-to-Canary translation, client-authoritative account/world/character/native-version claims, native profile field or selector, password/OAuth/Game Login Ticket authentication at Otheryn, v1 compression/resume/replay, ASIO replacement or activation from a contract task.

## Fixture ownership and rollout

Otheryn owns Game Session v2 admission fixtures, cross-language producer golden frames, action/revision tests, parser/fuzz regressions and exact generated-schema provenance. Fixtures are synthetic and contain no real credential, identity, endpoint, chat or proprietary capture.

A native-capable Otheryn may merge server-first only with listener and advertisement disabled. Canary compatibility profiles remain independent. Enablement is atomic-required with exact Platform/Gateway and Rust revisions. Rollback disables advertisement first, drains/closes native sessions and then disables the listener; no active or failed native session switches adapters.

Use `blakinio/Oteryn-Platform/docs/agents/prompts/OTS_OTHERYN_NATIVE_PROTOCOL_IMPLEMENTATION.md` only after Platform correction, Otheryn correspondence and Rust correspondence have merged in the required order.
