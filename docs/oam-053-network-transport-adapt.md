# OAM-053 Network Transport adaptation

## Disposition

```text
network-transport → ADAPT
```

Otheryn already owns the complete connection, protocol-profile and multiprotocol transport surface, so the package is not a source migration. The adaptation is limited to evidence-backed transport correctness and ownership invariants that are absent from the target's upstream-derived codec.

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

These differences are correctness and evidence gaps, not proof that all legacy connection/session code should move.

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

## Evidence boundary

A green result will prove the registered unit/runtime assertions for the exact target revision. It will not prove arbitrary protocol parity, all legacy clients, account authorization, gameplay packet correctness, session races, hostile-server client safety, load capacity or production deployment safety.

## Delivery evidence

Pending target implementation, exact-final validation, feature merge and lifecycle archive.
