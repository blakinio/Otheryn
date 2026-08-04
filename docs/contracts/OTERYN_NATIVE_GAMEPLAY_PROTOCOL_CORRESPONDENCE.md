# Otheryn native gameplay protocol correspondence

Coordination ID: `OTS-20260804-native-protocol-selection`  
Canonical contract: `blakinio/Oteryn-Platform/docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CONTRACT.md`  
Canonical merged revision: `9035ae987db67c062a8778721a2c8e686ce76750`  
Local architecture boundary: `docs/architecture/oteryn-native-gameplay-protocol.md`

## Status

Contract correspondence only. This PR implements no Game Session v2 storage, listener, TLS, protobuf, action result, snapshot, delta, readiness or automatic selection behavior.

Current Otheryn remains the authoritative gameplay server with ASIO networking and profile-driven Canary-compatible protocol/transport behavior. Native `oteryn.native.v1` is a separate future producer family.

## Normative adoption

Otheryn adopts the exact canonical revision above for:

- one Gateway-selected candidate and bound World Registry policy revision;
- opaque hashed-at-rest Game Session v2 bearer reference with server-side claims;
- `game_account_id`, generation, world, initial `channel_id = 1`, endpoint audience and atomic first-character admission;
- family `oteryn`, profile `oteryn.native.v1`, transport `tcp.tls13.protobuf.be32.v1`;
- deterministic schema and sorted-capability digests;
- TLS 1.3, ALPN `oteryn-game/1`, BE32 framing, protobuf schema revision 1 and no v1 compression;
- stream/command sequences, command ID, exact received-command byte hash, server tick and state revision;
- action lifecycle and stable reasons including `STALE_COMMAND`;
- full digest-checked snapshot, strict deltas, movement reconciliation and one bounded resync;
- no resume, reconnect replay, password fallback, byte sniffing, packet translation or in-session adapter switch;
- replay, cross-character/world/channel/profile/endpoint and redaction requirements.

Any implementation package must pin this exact Platform commit, the exact IDL SHA-256 and Platform producer fixture manifest. A later canonical revision requires an explicit correspondence update before implementation.

## Existing source correspondence

| Current boundary | Current role | Native target |
|---|---|---|
| `protocol_profile.hpp` | Canary-compatible protocol/login/transport profiles | remains compatibility-only; native is not a fake Tibia client version |
| `transport_codec.hpp` | current length/XTEA/checksum/sequence/compression behavior | separate TLS + BE32 + protobuf codec |
| `protocolgame.cpp` | packet decode and authoritative action dispatch | native semantic commands converge only at explicit authoritative game/domain seams |
| ASIO connection/service architecture | asynchronous sockets/lifecycle | retained; no Tokio/server runtime replacement |
| current Game Session admission | current Gateway world-entry authorization | later opaque v2 claim lookup and exact selection binding |
| current profile/port configuration | Canary listeners | separate native listener disabled by default and exact-readiness gated |
| existing protobuf dependency | build capability | permits later bindings but creates no runtime behavior now |

## Future producer responsibilities

### Admission

- look up the opaque credential by repository-approved hash;
- validate v2 version, expiry, generation, exact audience/endpoint, world/channel, policy revision and profile/transport/schema/list/digest;
- load current ownership of the requested character for `game_account_id`;
- atomically transition `ISSUED_UNBOUND` to `ACTIVE_BOUND(character_id, connection_id)` once;
- expose no gameplay state before success;
- make replay, wrong binding and ambiguous consume/bind outcomes terminal.

Otheryn does not receive the raw Identity subject. Authority comes from Platform ticket redeem and stored account/generation claims.

### Native transport and command path

- separate configurable TLS 1.3 listener, off by default, with ALPN `oteryn-game/1`;
- bounded BE32/protobuf parser under existing ASIO lifecycle ownership;
- no native/Canary sniffing or translation;
- exact per-direction stream and command sequences;
- bounded duplicate-result cache keyed by command ID, sequence and SHA-256 of exact received serialized `CommandEnvelope` bytes;
- cached duplicate returns prior result; payload conflict is fatal; expired-cache duplicate returns `STALE_COMMAND`;
- semantic commands call existing authoritative movement, target, spell, item, loot, chat and logout seams;
- one terminal result per admitted command unless session termination prevents delivery;
- TCP receipt never means gameplay success.

### State production

- monotonic server sequence/tick/revision;
- bounded initial snapshot whose digest covers exact on-wire `SnapshotChunk` envelope payload bytes;
- only `base_revision -> base_revision + 1` deltas;
- duplicate/regressed/conflicting delta is fatal; gap allows one bounded replacement-snapshot resync;
- reversible movement correlation by command ID;
- inventory, containers, loot, combat, resources, cooldowns and persistence remain server-authoritative;
- no native v1 resume or reconnect replay.

### Policy, readiness and rollback

- readiness reports exact family/profile/transport/schema/list/digest and listener state;
- disabling advertisement stops new issuance;
- admission validates stored session tuple against local listener/readiness identity without live World Registry lookup;
- already-issued unexpired sessions may bind/drain after normal advertisement disablement unless explicit admission revocation or emergency listener shutdown applies;
- emergency shutdown closes native sessions and never migrates them to Canary.

### Security and operations

- finite independent handshake, frame, command, heartbeat and resync limits;
- no credentials, session/command IDs, account/character IDs, chat or payloads in logs/artifacts;
- low-cardinality contract/profile/reason/deployment metrics;
- Canary behavior unchanged and native disabled until integrated evidence.

## Prohibited shortcuts

No native opcodes in Canary profiles, native-to-Canary translation, client-authoritative account/world/character/profile claims, password/OAuth/Game Login Ticket authentication, v1 compression/resume/replay, ASIO replacement or contract-task enablement.

## Fixture ownership and rollout

Otheryn owns Game Session v2 admission fixtures, cross-language producer golden frames, action/revision tests, parser/fuzz regressions and exact generated-schema provenance. Fixtures are synthetic and contain no real credential, identity, endpoint, chat or proprietary capture.

A native-capable Otheryn may merge server-first only with listener/advertisement disabled. Canary profiles remain independent. Enablement is atomic-required with exact Platform/Gateway and Rust revisions. Rollback disables advertisement first, drains/closes native sessions and then disables the listener; no active native session switches adapters.

Use `blakinio/Oteryn-Platform/docs/agents/prompts/OTS_OTHERYN_NATIVE_PROTOCOL_IMPLEMENTATION.md` only after all contract tasks are archived.
