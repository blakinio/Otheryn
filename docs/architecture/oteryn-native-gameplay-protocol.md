# Otheryn native gameplay producer boundary

Coordination ID: `OTS-20260804-native-protocol-selection`  
Canonical contract: `blakinio/Oteryn-Platform/docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CONTRACT.md`  
Local correspondence: `docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CORRESPONDENCE.md`

## Architectural rule

Native gameplay is a new protocol adapter and transport profile inside the existing Otheryn ASIO server architecture. It is not a replacement server runtime, a Canary profile variant or a packet translation layer.

```text
ASIO listener/service ownership
  -> native TLS connection and bounded frame codec
  -> Game Session v2 admission and exact profile binding
  -> native protobuf command/event adapter
  -> existing authoritative game/domain operations
  -> native action results and revisioned state producer
```

Canary-compatible paths remain:

```text
existing ASIO listener
  -> existing TransportCodec/Profile
  -> existing ProtocolGame packet parser
  -> authoritative game/domain operations
```

The two paths may converge only after protocol decoding at explicit protocol-neutral authoritative operations. Native bytes never enter Canary decoders; Canary bytes never enter the native parser.

## Listener and readiness separation

The later producer package must define a distinct native listener configuration with:

- disabled default;
- exact bind host/port and TLS server name;
- TLS 1.3 and ALPN `oteryn-game/1`;
- certificate/key source owned by deployment policy;
- maximum connections, handshake rate/deadline and frame rate;
- exact profile `oteryn.native.v1`;
- exact schema revision/hash and capability digest;
- readiness false until Game Session v2 validation and producer schema are ready.

World Registry/Gateway advertisement must depend on this exact readiness identity, not only a healthy TCP port.

## Session lifecycle

```text
TCP accepted
-> TLS/ALPN validated
-> bounded ClientHello
-> Game Session v2 lookup/validation
-> authoritative character ownership check
-> atomic ISSUED/UNBOUND -> ACTIVE/BOUND transition
-> ServerHello
-> complete initial snapshot
-> gameplay commands/deltas
-> typed SessionEnded or deterministic close
```

Before atomic bind, no map, entity, account or character state is exposed. A credential with an ambiguous consume/bind outcome is terminal. A replacement session is new state and does not inherit native command/result cache, sequence or snapshot revision.

## Execution and concurrency ownership

- ASIO owns socket callbacks, TLS I/O and connection cancellation.
- The native connection owns one bounded inbound parser state and one bounded outbound queue.
- Protocol parsing validates all external lengths/counts before allocation.
- Commands cross into the authoritative dispatcher/game thread through an explicit bounded queue or existing safe dispatch seam.
- Results/state return through explicit session-owned output scheduling.
- Shutdown cancels reads/writes, rejects queued stale-session work and joins/releases all connection-owned work deterministically.
- No blocking database/session lookup may run directly on an ASIO I/O callback; the implementation package must use the repository's approved asynchronous/off-thread seam.

## State publication model

The native producer maintains per-session projection state sufficient to emit:

- one complete bounded initial snapshot;
- `base_revision -> revision` deltas;
- session-scoped opaque entity/item/container handles;
- canonical mutation ordering and hashes;
- action-result correlation;
- bounded replacement snapshot on resync.

This projection is a network/session view, not a second authoritative simulation or database. Otheryn domain state remains authoritative.

## Current-to-target mapping

| Current concept | Native target |
|---|---|
| `ProtocolProfileId` Canary-compatible variants | separate native adapter identity; do not add as a fake Tibia client version |
| `TransportProfile` XTEA/checksum/compression variants | separate TLS + BE32 + protobuf codec |
| current packet sequence/checksum behavior | native `stream_sequence` under TLS integrity |
| game login session key/account-password layouts | Game Session v2 `ClientHello` credential only |
| current opcodes and field layouts | semantic protobuf command/event messages |
| implicit packet effects | explicit action result lifecycle plus authoritative deltas |
| full map/player packet sequence | bounded revisioned snapshot records |
| reconnect behavior | fresh login/session/full snapshot; no native v1 resume |

## Validation obligations for the later producer package

1. current Canary exact-profile regression and no changed packet bytes;
2. native TLS/ALPN positive and certificate/ALPN negatives;
3. Game Session replay/cross-character/world/profile/audience/generation negatives;
4. protobuf/frame limits, arbitrary/truncated/oversize inputs and allocation bounds;
5. exact command duplicate/idempotency and sequence tests;
6. authoritative movement/combat/spell/item/loot/chat/logout tests;
7. snapshot/delta/revision/resync deterministic tests;
8. parser fuzzing with minimized regression fixtures;
9. load/soak evidence for ASIO thread, dispatcher queue, memory and shutdown;
10. redaction and low-cardinality metrics review;
11. exact generated-schema provenance and cross-language golden fixtures;
12. independent security review before advertisement can be enabled.

## Non-goals

This document does not authorize changes to ASIO architecture, current Canary profiles, current ports, runtime dependencies, Game Session storage, deployment, production configuration or the gameplay implementation itself.
