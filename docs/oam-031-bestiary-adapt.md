# OAM-031 Bestiary adaptation

## Disposition

`bestiary → ADAPT`

## Immutable baselines

- Otheryn target: `6a7e54ee3c9597e3ab265a14c2b783631ef3776f`
- Canary legacy/governance: `9aa582eb6b8ab9444294e08798f628cd053d2428`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical Bestiary owns the narrow server root `src/io/iobestiary.*` and depends on completed `cyclopedia` and `player-persistence`.

## Accepted adaptation

Merged legacy PR #188 provides two independently bounded Bestiary-owned correctness repairs that are absent from the task-start target and fresh upstream, which share exact `iobestiary.cpp` blob `c0497c4d1814e7950ad8fc27b9a4ec1f86d4a5cd`:

1. `addBestiaryKill` now checks `player` and `mtype` before dereferencing `mtype->info.raceid`, preserving the existing zero-race early return.
2. `calculateDifficult` performs floating-point conversion before dividing by `1000.0`, preserving fractional difficulty thresholds instead of truncating through integer division.

The PR #188 all-Charm reset-price correction remains deliberately excluded because Charm purchase/reset semantics belong to canonical `charms`. PR #192 monster definition changes are also excluded because monster definition files are evidence inputs, not the Bestiary module ownership root.

Focused OAM-031 proof verifies both selected source contracts and explicitly guards that the Charm reset-price formula remains unchanged by this package.

## Nonclaims

OAM-031 does not claim full Bestiary parity, exhaustive kill-stage/reward correctness, Charm correctness, monster-definition parity, exact protocol/client rendering compatibility, persistence completeness, tracker refresh correctness under every runtime state, database durability, physical-client Bestiary E2E closure, or full Real Tibia parity.
