# OAM-053 Network Transport adaptation

## Disposition

```text
network-transport → ADAPT
```

Otheryn already owns the complete connection, protocol-profile and multiprotocol transport surface, so the package is not a source migration. The adaptation is limited to evidence-backed transport correctness and ownership invariants that were absent from the target's upstream-derived codec.

## Pinned revisions

- Canary preflight merge: `6a9e6cf106b3e0193fb6a9d923a37cee38888f66`;
- Otheryn task-start main: `64ad965eee40f62ff996980fd8a0d329245c519f`;
- Canary donor/laboratory main at selection: `ba08e346540f017773b9268832d304c7f5664ac2`;
- upstream Canary: `7644bcbcbbad4a09e52a5707ed531e4dd21d8a79`;
- maintained OTClient: `5568cb6f5e2fd6162c78cde304deea5d32461e05`.

Donor merges:

- authoritative transport profiles: `bbff04524bbb99ab54c9571c24382399b904cbd8`;
- checksum-free block-count correction: `4535836d4df0fc669033ed73f525754a1a2d1b40`;
- complete first current-game frame: `5c750e13fb95f46225807b8907a95ce3091283c8`;
- SEC-005 current-main recovery: `1408aaa886240034a90fc33873e9b9e0fa47cab6`.

## Target gap

At task start Otheryn still used one `CurrentModern` transport profile and retained checksum/compression authority in mutable `Protocol` state. Inbound sequence state advanced before complete checksum and XTEA validation, rejection returned only `bool`, and several truncated/padding boundaries lacked explicit guards. The checksum-free block-count encoder also unconditionally subtracted four bytes.

These differences were correctness and evidence gaps, not proof that all legacy connection/session code should move.

## Adapted boundary

The target package owns only:

- complete transport-profile authority;
- distinct current login, current sequenced-game and current checksum-free-game contracts;
- symmetric modern block-count framing;
- complete current first-frame sizing;
- typed inbound rejection results;
- post-validation sequence commit;
- bounded malformed/decrypt guards;
- deterministic target regressions.

It preserves current Otheryn profile identities, legacy profile fixtures, protocol-session hints, typed `GameProfile`, module registry/composition work and unrelated connection lifecycle.

## Implemented target behavior

- `TransportProfile` now selects inbound/outbound checksum, compression, modern block-count adjustment, encrypted payload layout and first-frame header semantics.
- `Protocol` retains only session-local XTEA keys and accepted sequence counters; checksum selection switches complete current transport profiles.
- `TransportCodec::prepareInbound` returns a typed status plus expected/received sequence evidence.
- Accepted client sequence state is committed only after checksum and XTEA acceptance.
- Truncated checksum, invalid encrypted block length, missing legacy inner length, missing modern padding byte and oversized padding fail closed.
- `OutputMessage::writeMessageLength` uses profile-owned extra bytes, making checksum-free block-count encode/decode symmetric.
- Existing six target protocol profiles and account/game login layouts remain present; only the current transport contract is split.

## Deterministic regressions

`Oam053NetworkTransportTest` proves:

- distinct current login, sequenced-game and checksum-free-game profile contracts;
- captured `0x0015` first-frame decoding to 172 bytes with sequence/checksum and 168 bytes without checksum;
- checksum-free encrypted block-count round-trip symmetry;
- truncated checksum rejection without sequence consumption;
- zero, gap and replay rejection with the still-expected accepted sequence;
- decrypt rejection without consuming the next expected sequence.

Existing multiprotocol and protocol-session-handoff tests remain in the same `canary_ut` suite.

## Validation and first failures

The first Ready head `df879c4c5a5f3f0135b1b5a7f4e0efd3eb882fda` exposed two independent failures:

1. Linux debug test compilation inherited donor-only `Dispatcher::executeSerialEventsForTest()`. Current Otheryn has no such public test hook. Because the focused connections are never accepted into `Connection::protocol`, `close(true)` already synchronously releases the manager entry/socket without queuing protocol release; the unavailable hook and include were removed.
2. Docker failed before project compilation while bootstrapping vcpkg with `curl: (35) Recv failure: Connection reset by peer`. No Docker or source change was made. The next complete run passed the same Docker build.

Validated implementation head `422ce59ca8fede681d595764965c0534d11edc16`:

- repository CI `30225272288`: PASS;
- `Required` `30225272219`: PASS;
- autofix `30225272241`: PASS with no follow-up commit;
- Fast Checks and Lua: PASS;
- Linux release: PASS with Canary and Global datapack runtime smoke;
- Linux debug: PASS with Canary smoke, schema import and full CTest;
- Docker image: PASS;
- macOS build/runtime smoke: PASS;
- Windows CMake and Solution builds: PASS.

## Evidence boundary

The green result proves the registered target unit/runtime assertions for the exact validated revision. It does not prove arbitrary protocol parity, all legacy clients, account authorization, gameplay packet correctness, session races, hostile-server client safety, load capacity or production deployment safety.

## Delivery evidence

Implementation is validated. Exact-final checkpoint gates, merge and lifecycle archive remain pending.
