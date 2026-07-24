# OAM-044 protocol compatibility target reuse proof

## Final disposition

`protocol-compatibility → REUSE` with explicit server/client evidence boundaries.

The clean Otheryn target retains the reviewed current-upstream protocol-profile registry. No production server, maintained-client, transport, login, session-handoff, packet, asset, schema or deployment mutation is required.

## Exact baselines

- Canary OAM-044 preflight merge: `47611c10be8a2262d66421c9da65de6cc5c7264d`
- Otheryn task-start main: `3f3c15917610e45430aa3902d110806dd25e10a8`
- reviewed current upstream: `opentibiabr/canary@7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- legacy Canary evidence baseline: `blakinio/canary@a5cafe1b7ce148af59c64d1382963ac6ac633334`
- maintained client: `blakinio/otclient@b3bcea2a95959bb4e92cc0b80cd49f36b63699b2`

The target and reviewed current upstream share exact Git blobs:

- `src/server/network/protocol/protocol_profile.hpp`: `b9f1eec01e1ba348c22315be43ccefe74b210e45`
- `src/server/network/protocol/protocol_profile.cpp`: `5405c343cfa2c2d75a173d6678ecf8afc7690120`

The maintained-client compatibility root is:

- `modules/game_features/features.lua`: `8b458b864ad765185fd856414f2c097d565a5a22`

Legacy Canary diverges at the server registry roots:

- `protocol_profile.hpp`: `d045189c02eedfc0c3c4d03c37052cc34390e5ae`
- `protocol_profile.cpp`: `d89d951c469547370ef4346b133e7c7e32a257cf`

Those legacy differences include a more granular transport-profile split. They are not imported because framing, checksum, sequence, XTEA and compression behavior belongs to canonical `network-transport`, while login serialization and hint lifecycle belong to `login-protocol` and `protocol-session-handoff`.

## Canonical responsibility

This package owns:

- server protocol-profile identity and support state;
- client-version, wire-family and asset-signature profile resolution;
- item-mapper policy;
- challenge and login-layout metadata;
- server `ProtocolFeature` masks;
- the maintained-client version-gated `GameFeature` inventory;
- explicit reviewed server/client compatibility pairs.

It does not own:

- socket lifecycle or framing;
- checksum, sequence, XTEA or compression execution;
- account authentication or broad login serialization;
- protocol-session hint registration, lease or consumption;
- general gameplay packet semantics;
- maintained-client rendering;
- physical-client orchestration.

## Reviewed server profile manifest

The focused target contract covers all six registered profiles:

| Profile | Version | State | Mapper | Bounded statement |
|---|---:|---|---|---|
| `Current` | 1525 | enabled | not required | current official-profile metadata |
| `Tibia1100` | 1100 | enabled | not required | legacy session-key layouts |
| `Cipsoft860Vanilla` | 860 | enabled | required before world enter | classic account/password layouts |
| `Cipsoft860ExtendedAssets` | 860 | enabled | not required | explicit extended-assets metadata |
| `Cipsoft860CanaryExtended` | 860 | enabled | not required | shipped reviewed extended asset signatures |
| `OTCv8Extended860` | 860 | blocked pending fixture | required before world enter | fail-closed; no login layouts |

Unknown versions remain rejected. Repeated support labels are collapsed to the reviewed user-facing description `15.25, 10x and 8.6`.

## Reviewed current server/client pairs

The exact maintained-client source enables the corresponding client features at the listed thresholds. The target contract asserts only the semantically reviewed pairs:

| Server feature | Maintained-client gate | First reviewed version |
|---|---|---:|
| `MarketPackets` | `GamePlayerMarket` | 940 |
| `CustomMonkPackets` | `GameVocationMonk` | 1500 |
| `OfficialWeaponProficiencyPayload` | `GameProficiency` | 1510 |
| `GraphicalEffectSourceByte` | `GameEffectSource` | 1514 |
| `PlayerDataLevelPercentU16` | `GameLevelPercentU16` | 1520 |
| `OfficialTaskboardPackets` | `GameTaskboard` | 1520 |

Similar names outside this table are not promoted to one-to-one compatibility.

## Physical current-profile continuity

OAM-006 physical run `29531221365` passed two protocol-1525 login/relog cycles against:

- Otheryn `c547d8ad70ef1252624c255476e6cb83fa125e14`;
- maintained client `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.

The selected roots at those tested revisions are byte-identical to the OAM-044 target roots:

- server header `b9f1eec01e1ba348c22315be43ccefe74b210e45`;
- server implementation `5405c343cfa2c2d75a173d6678ecf8afc7690120`;
- maintained-client feature matrix `8b458b864ad765185fd856414f2c097d565a5a22`.

This proves bounded current-profile source/runtime continuity. It does not prove Tibia 11.00, CipSoft 8.60 or OTCv8 8.60 physical parity.

## Focused target contract

`tests/unit/server/network/protocol/oam_044_protocol_compatibility_test.cpp` proves:

- the six-profile manifest, support states and mapper policies;
- rejection of unknown versions and blocked OTCv8 layouts;
- the selected current server/client feature pairs;
- current account/game session-key layouts;
- Tibia 11.00 legacy metadata;
- shipped 8.60 extended-asset resolution and feature mask;
- classic 8.60 account/password layouts.

The test is registered in the existing unit-test target. It adds no second harness and no production mutation.

## Conclusion

The evidence supports bounded `REUSE`:

- target/current-upstream server registry identity is exact;
- the current-profile server/client roots retain the exact physically tested OAM-006 blobs;
- focused target fixtures preserve the complete registered profile manifest and selected paired semantics;
- no protocol-compatibility-owned target defect is isolated.

## Nonclaims

OAM-044 does not claim exhaustive one-to-one mapping of every `ProtocolFeature` and `GameFeature`, byte-level compatibility for every packet/profile combination, provenance or correctness of every proprietary asset signature, physical login/world-entry parity for Tibia 11.00 or 8.60 variants, OTCv8 8.60 readiness, transport framing/checksum/sequence/XTEA/compression correctness, login authentication correctness, session-handoff correctness, maintained-client rendering parity, production gameplay parity or full protocol parity.
