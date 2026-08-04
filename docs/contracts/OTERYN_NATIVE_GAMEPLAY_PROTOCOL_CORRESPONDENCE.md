# Otheryn native gameplay protocol correspondence

Coordination ID: `OTS-20260804-native-protocol-selection`  
Canonical source of truth: `blakinio/Oteryn-Platform/docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CONTRACT.md`  
Canonical review PR: `blakinio/Oteryn-Platform#519`  
Local architecture boundary: `docs/architecture/oteryn-native-gameplay-protocol.md`

## Status

Contract correspondence only. This PR implements no Game Session v2 storage, listener, TLS, protobuf, action result, snapshot, delta, readiness or automatic selection behavior.

Current Otheryn remains the authoritative gameplay server with ASIO networking and profile-driven Canary-compatible protocol/transport behavior. Native `oteryn.native.v1` is a separate future producer family.

## Normative adoption

Otheryn adopts the canonical definitions for:

- one Gateway-selected candidate and bound World Registry policy revision;
- opaque hashed-at-rest Game Session v2 bearer reference with server-side claims;
- exact `game_account_id`, generation, world, initial `channel_id = 1`, endpoint audience and atomic bind-on-first-character-admission;
- family `oteryn`, profile `oteryn.native.v1`, transport `tcp.tls13.protobuf.be32.v1`;
- deterministic schema and sorted-capability digest rules;
- TLS 1.3, ALPN `oteryn-game/1`, BE32 framing and protobuf schema revision 1;
- exact frame/message/string/collection/snapshot limits and no v1 compression;
- stream/command sequences, command ID, exact received-command byte hash, server tick and state revision;
- action lifecycle and stable reasons including `STALE_COMMAND`;
- full digest-checked snapshot, strict deltas, movement reconciliation and one bounded resync;
- no resume, reconnect replay, password fallback, byte sniffing or in-session adapter switch;
- replay, cross-character/world/channel/profile/endpoint and redaction requirements.

If correspondence differs from the merged canonical contract, the exact canonical revision controls. The implementation package must pin that commit, the exact IDL SHA-256 and Platform producer fixture manifest.

## Existing source correspondence

| Current boundary | Current role | Native target |
|---|---|---|
| `src/server/network/protocol/protocol_profile.hpp` | Canary-compatible protocol/login/transport profiles | remains compatibility-only; native is not a fake Tibia client version |
| `src/server/network/protocol/transport_codec.hpp` | current length/XTEA/checksum/sequence/compression behavior | separate TLS + BE32 + protobuf codec; no reuse by familiarity |
| `src/server/network/protocol/protocolgame.cpp` | packet decode and authoritative action dispatch | native semantic commands converge only at explicit authoritative game/domain seams |
| ASIO connection/service architecture | asynchronous sockets/lifecycle | retained; no Tokio/server runtime replacement |
| current Game Session-compatible admission | current Gateway world-entry authorization | extended later with opaque v2 claims and exact selection binding |
| profile/port configuration | current/legacy Canary listeners | separate native listener, disabled by default and exact-readiness gated |
| existing protobuf dependency | build capability | permits later generated bindings but creates no runtime behavior now |

## Future producer responsibilities

### Admission

- look up the opaque credential by repository-approved hash;
- validate v2 version, expiry, generation, exact audience/endpoint, world/channel, policy revision and profile/transport/schema/list/digest;
- load current ownership of `selected_character_id` for `game_account_id`;
- atomically transition `ISSUED_UNBOUND` to `ACTIVE_BOUND(character_id, connection_id)` once;
- expose no gameplay state before success;
- make replay, wrong binding and ambiguous consume/bind outcomes terminal.

Otheryn does not receive the raw Identity subject. Account authority comes from Platform ticket redeem and the stored `game_account_id`/generation claims.

### Native transport

- separate configurable TCP listener disabled by default;
- TLS 1.3, certificate/service identity and ALPN `oteryn-game/1`;
- bounded BE32 frame and protobuf parser using existing ASIO lifecycle ownership;
- deterministic cancellation/shutdown and finite handshake/frame/rate limits;
- no native/Canary first-byte sniffing.

### Commands and results

- validate exact stream and command sequences;
- use SHA-256 of exact received serialized `CommandEnvelope` submessage bytes for bounded duplicate-result identity;
- return cached exact duplicate results without reapplying, reject expired-cache duplicates as `STALE_COMMAND`, and close on same ID/sequence with different payload;
- map movement, target, spell, item, loot, chat and logout intent directly to existing authoritative operations;
- eventually emit one terminal action result for every admitted command unless session termination prevents delivery;
- never report TCP receipt as gameplay success.

### State production

- emit monotonic server sequence/tick/revision;
- emit a bounded initial snapshot whose digest covers the exact on-wire `SnapshotChunk` envelope payload bytes;
- emit only `base_revision -> base_revision + 1` deltas;
- treat duplicate/regressed/conflicting deltas as protocol faults and gaps as one bounded replacement-snapshot resync;
- correlate reversible movement prediction by command ID;
- retain sole authority for inventory, containers, loot, combat, resources, cooldowns and persistence;
- provide no native v1 resume or reconnect replay.

### Policy/readiness and rollback

- readiness reports exact family/profile/transport/schema/list/digest and listener state;
- Gateway stops new issuance when advertisement/readiness is disabled;
- Otheryn does not query World Registry live during admission; it validates stored session tuple against local listener/readiness identity;
- already-issued unexpired sessions may bind/drain after normal advertisement disablement unless explicit admission revocation or emergency listener shutdown applies;
- emergency shutdown closes native sessions and never migrates them to Canary.

### Security/operations

- independent finite handshake, frame, command, heartbeat and resync limits;
- logs/artifacts exclude credentials, session/command IDs, account/character IDs, chat and payloads;
- metrics use low-cardinality contract/profile/reason/deployment labels;
- current Canary behavior remains unchanged and native remains disabled until integrated evidence.

## Prohibited shortcuts

Otheryn must not:

- add native opcodes to a Canary profile;
- translate native protobuf through synthetic Canary packets;
- accept a tuple not stored in Game Session;
- trust client account/world/character/profile authority;
- add password, OAuth-token or Game Login Ticket authentication;
- enable v1 compression, resume or command replay;
- advertise/enable native in the contract task.

## Action authority map

| Native command | Authoritative seam |
|---|---|
| step/stop | movement admission, collision/speed/path and final position |
| attack/follow | target visibility/rules/path and target state |
| spell | knowledge, cooldown, resources, range/LOS and effects |
| use/use-with/move | identity, location, ownership, quantity, capacity, scripts and committed mutations |
| quick/corpse loot | corpse ownership/rules/range/capacity/destination and transfers |
| chat | permission, moderation and delivery |
| logout | fight/condition/save/session lifecycle |

The implementation task must name exact source functions and prove that native paths do not bypass their authority.

## Fixture ownership

Otheryn owns Game Session v2 admission fixtures, cross-language producer golden frames, action/revision tests, malformed parser/fuzz regressions and exact generated-schema provenance. Fixtures are synthetic and contain no real credential, identity, endpoint, chat or proprietary capture.

## Rollout and later task

A native-capable Otheryn may merge server-first only with listener/advertisement disabled. Canary profiles remain independent. Enablement is atomic-required with exact Platform/Gateway and Rust revisions. Rollback disables advertisement first, drains/closes native sessions and then disables the listener; no active native session switches adapters.

Use `blakinio/Oteryn-Platform/docs/agents/prompts/OTS_OTHERYN_NATIVE_PROTOCOL_IMPLEMENTATION.md` only after all contract PRs merge and archive.
