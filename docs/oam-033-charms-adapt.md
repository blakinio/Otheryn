# OAM-033 Charms adaptation

## Disposition

`charms → ADAPT`

## Immutable baselines

- Otheryn target: `1a4bbceda2c805bc69c68c1592e04e63d7e9a269`
- Canary legacy/governance: `f05ea5e916af00ab1469a2332aaec2d3c9df7478`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `charms` covers definitions, costs, unlock state, assignment and combat effects and depends on completed `combat`, `cyclopedia`, `player-persistence` and `protocol`. TSD-004 explicitly preserves this independent ownership even though `IOBestiary` hosts some Charm helper methods.

## Selected adaptation boundary

Merged legacy PR #188 contains exactly two selected Charm-owned corrections:

1. `registerCharm.category` now tests `mask.category` before passing that value to `charm:category(...)`; target and fresh upstream incorrectly gate the field on unrelated `mask.type`.
2. The all-Charm reset price is `100000 + (level - 100) * 11000` above level 100; target and fresh upstream incorrectly charge `level * 11000`, effectively charging the surcharge for the first 100 levels again.

The current legacy retains both corrections. The same donor PR also contains Bestiary null-safety/difficulty, Bosstiary missing-row recovery and Cyclopedia Character pagination corrections already owned by OAM-031, OAM-030 and OAM-029 respectively; those are excluded here. PR #192 is Bestiary/Bosstiary monster-data remediation and PR #243 is validator/workflow control. No maintained OTClient change is selected.

The smallest valid disposition is therefore `ADAPT`, changing only `data/scripts/lib/register_bestiary_charm.lua` and the all-Charm reset-price expression in `src/io/iobestiary.cpp`, plus focused proof and task evidence.

## Proof-boundary maintenance

The first exact-head Linux-debug suite on PR #67 passed 421/422 tests. Its sole failure was the older OAM-031 test `CharmResetPricingRemainsOutsideBestiaryPackage`, which explicitly required the pre-OAM-033 reset-price formula and rejected the corrected formula. That assertion was valid while Charm pricing was deliberately excluded from OAM-031, but became obsolete once OAM-033 took explicit Charm ownership and changed the formula. The obsolete Charm-specific assertion was removed from the OAM-031 proof file; OAM-031 Bestiary null-safety and difficulty proofs remain unchanged. No production change was made in response to this test failure.

## Nonclaims

OAM-033 does not claim exhaustive Charm definition/value parity, all unlock costs, assignment-slot rules, combat proc formulas, element/resistance behavior, Bestiary progress correctness, protocol/client compatibility, maintained-client rendering, persistence atomicity, economy transaction atomicity, physical-client Charm E2E closure, or full Real Tibia parity.
