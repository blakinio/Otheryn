# OAM-027 Houses Adaptation

## Disposition

```text
houses ADAPT
```

## Immutable task-start inputs

- legacy/governance Canary: `0251b96105720cb67d5ed7a1b3ec8350baa8e312`
- Otheryn target: `5003753e491250732910e9d5857b20293d1bd9ab`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `houses` depends on the active/mapped/audited `otbm-tooling` evidence foundation and completed player-persistence foundation. Protocol/Cyclopedia presentation and generic map geometry remain interaction boundaries.

## Accepted donor boundary

Task-start Otheryn and fresh upstream share `src/map/house/house.cpp` blob `25fa954a55763bc9473234682d143c9761843403`. Current legacy differs, but whole-file legacy reuse is rejected because the fork also contains separately owned multichannel house ownership/mirroring work.

The only accepted production donor is merged legacy PR #60 (`a6977beb06883fb4384476315f3dc17772f99ba4`), limited to four transfer-safety changes in `House::transferToDepot`, `House::handleWrapableItem` and `House::collectMovableItemsFromContainer`:

1. iterate tile/container item snapshots instead of mutating live collections during traversal;
2. ignore stale snapshot entries whose parent already changed;
3. deduplicate the final move queue by item identity;
4. validate wrapped results before queueing and preserve the original item ID for failure logging.

No legacy multichannel ownership, `account_house_ownership`, `houses.channel_id`, cluster handoff, protocol/client, OTBM/map, schema or deployment change is imported.

## Proof

The focused OAM-027 unit proof preserves basic House identity/state behavior and source-contract guards for all four accepted donor invariants. Full target CI remains authoritative for compilation and regression safety.

## Known gaps

This package does not claim generic house purchase/auction transaction atomicity, crash-safe transfer recovery, distributed/multiwriter house ownership, cross-channel house safety, Cyclopedia house-tab correctness, protocol/client UI compatibility, exhaustive rent/auction parity, physical-client house E2E, Real Tibia parity, or map/OTBM correctness.
