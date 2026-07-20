# OAM-023 — Parties reuse proof

## Immutable task-start baselines

- legacy/governance Canary: `0a39a0f76d5f811098dfaa7be9deea40347279d5`
- clean target Otheryn: `50dfa248251f245f5519495a4fbd430b6814ffe4`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Canonical boundary

OAM-023 revalidates only canonical `parties`.

The registry boundary is `src/creatures/players/grouping/party.*` and depends only on completed `character-lifecycle` from OAM-005. Party chat transport, protocol packet compatibility, persistent guild membership, generic combat formula correctness, vocation correctness and Wheel of Destiny correctness are outside this package.

## Evidence-driven disposition

Candidate disposition:

```text
parties -> REUSE
```

This decision is not based on path or blob identity alone.

At the immutable task-start revisions, the bounded production files are exact-identical across clean target, fresh upstream and legacy:

- `party.cpp`: `c3493c962548bffa5e393adc3359137b200b6384`
- `party.hpp`: `52b08e7321dd4e35bfb68415254239245ed236ee`

The current Party lifecycle was also reviewed semantically across creation/leader ownership, member and invitation state, join/leave/revoke/leadership transitions, disband cleanup, shared-experience state and fail-closed no-leader behavior. Legacy history candidates found around party-related behavior were checked for changed-file ownership: the reviewed multichannel, Gameplay Analytics shared-experience and Forge premium-Dust changes do not modify the canonical `party.*` boundary. No stronger independent legacy donor for the canonical Party core was identified.

The existing `party.cpp` contains interactions with vocation/Wheel behavior, but those are already present identically in target/upstream/legacy and remain outside the correctness claim of this bounded package. OAM-023 does not use their presence to claim Wheel or vocation parity.

## Target proof

This target change is proof-only:

- no production `party.*` mutation;
- one focused unit test file asserting stable shared-experience status values, empty initial Party state and fail-closed behavior when no leader exists;
- one test build registration entry;
- this evidence document.

Final `REUSE` acceptance requires exact-head target CI and focused test success. A failing proof must be investigated as either a proof-harness defect or a real target defect before the disposition is finalized.

## Client and protocol boundary

The canonical `parties` registry record has no maintained-client path. Protocol packet compatibility is explicitly excluded from this package. No maintained OTClient write is required or authorized by this proof, and OAM-023 makes no claim of physical-client Party UI, party-channel or wire-protocol E2E closure.

## Explicit exclusions

OAM-023 does not claim or change:

- party chat transport or channel behavior;
- protocol packet compatibility or maintained OTClient behavior;
- shared-experience formula parity beyond the focused structural proof;
- generic combat correctness;
- vocation or Wheel of Destiny correctness;
- persistence redesign or OAM-004 SQL/KV atomicity;
- guild lifecycle;
- map, OTBM, `items.otb`, assets, schema or deployment;
- physical-client Party E2E closure.
