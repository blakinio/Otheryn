# OAM-053 Network Transport adaptation

## Disposition

```text
network-transport → ADAPT
```

Otheryn retained its complete connection, protocol-profile and multiprotocol architecture. The package adapted only evidence-backed transport correctness and ownership invariants absent from the target's upstream-derived codec.

## Pinned revisions

- Canary preflight merge: `6a9e6cf106b3e0193fb6a9d923a37cee38888f66`;
- Otheryn task-start main: `64ad965eee40f62ff996980fd8a0d329245c519f`;
- exact target feature head: `7376eff79e166595a91f4581d8eef6e6c228e754`;
- target feature merge: `c25fff72dd8b89f6ef1565af2d84ab9eef33dce9`;
- upstream Canary: `7644bcbcbbad4a09e52a5707ed531e4dd21d8a79`;
- maintained OTClient: `5568cb6f5e2fd6162c78cde304deea5d32461e05`.

Donor merges:

- authoritative transport profiles: `bbff04524bbb99ab54c9571c24382399b904cbd8`;
- checksum-free block-count correction: `4535836d4df0fc669033ed73f525754a1a2d1b40`;
- complete first current-game frame: `5c750e13fb95f46225807b8907a95ce3091283c8`;
- SEC-005 current-main recovery: `1408aaa886240034a90fc33873e9b9e0fa47cab6`.

## Adapted behavior

- `TransportProfile` selects inbound/outbound checksum, compression, modern block-count adjustment, encrypted payload layout and first-frame header semantics.
- `Protocol` retains only session-local XTEA keys and accepted sequence counters; checksum selection switches complete current transport profiles.
- `TransportCodec::prepareInbound` returns typed status plus expected/received sequence evidence.
- Accepted client sequence state commits only after checksum and XTEA acceptance.
- Truncated checksum, invalid encrypted block length, missing legacy inner length, missing modern padding byte and oversized padding fail closed.
- `OutputMessage::writeMessageLength` uses profile-owned extra bytes, making checksum-free block-count encode/decode symmetric.
- Existing six target protocol profiles, account/game login layouts and session-handoff behavior remain present.

## Deterministic regressions

`Oam053NetworkTransportTest` proves distinct current transport contracts, captured 172/168-byte first-frame sizing, checksum-free block-count symmetry, truncated checksum rejection, zero/gap/replay handling and decrypt rejection without consuming the next accepted sequence. Existing multiprotocol and protocol-session-handoff tests remain in the same full CTest suite.

## First failures and repairs

1. The first Ready head inherited donor-only `Dispatcher::executeSerialEventsForTest()`. Target-native `close(true)` cleanup was sufficient because focused connections were never accepted into `Connection::protocol`; the unavailable helper and include were removed.
2. The first Docker job failed before project compilation with `curl: (35) Recv failure: Connection reset by peer` during vcpkg bootstrap. No source or Docker change was made; the next complete run passed.

## Exact-final validation

Exact head `7376eff79e166595a91f4581d8eef6e6c228e754` passed:

- repository CI `30225971903`;
- `Required` `30225971757`;
- autofix `30225971771` with no follow-up commit;
- Fast Checks and Lua;
- Linux release and Linux debug;
- full Linux CTest, Canary smoke and schema import;
- Docker image;
- macOS build/runtime smoke;
- Windows CMake/runtime smoke.

The feature PR changed exactly eleven intended paths, had no comments, reviews or review threads, was `behind_by=0`, and squash-merged with expected-head protection as `c25fff72dd8b89f6ef1565af2d84ab9eef33dce9`.

## Evidence boundary

The green result proves the registered target unit/runtime assertions for the exact revision. It does not prove arbitrary protocol parity, every legacy client, account authorization, gameplay packet correctness, session races, hostile-server client safety, sustained capacity or production deployment safety.

## Lifecycle

The durable completed task is `docs/agents/tasks/archive/OTH-20260727-oam053-network-transport-adapt.md`. Lifecycle PR and merge evidence are appended by the separate docs-only lifecycle delivery.
