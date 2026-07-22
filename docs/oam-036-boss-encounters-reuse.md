# OAM-036 Boss Encounters reuse proof

## Disposition

`boss-encounters → REUSE`

## Immutable baselines

- Otheryn target: `6275021bbb83dc28d2f5d6cf8db5b16aa7206544`
- Canary preflight merge: `08434e88435cbebe6965d4bd2f13382fdc8a586e`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `boss-encounters` owns reward-boss encounter participation, contribution tracking, target-list reconciliation, boss-death score normalization, reward generation, reward-container insertion and the persistence handoff for offline rewards. Generic boss AI and definitions, static/dynamic spawn scheduling, raids, Bosstiary progression, quest access/cooldowns and encounter-specific scripts remain outside this boundary.

## Reuse decision

Task-start Otheryn, fresh upstream Canary and legacy Canary share exact selected roots: `data/libs/systems/reward_boss.lua` blob `72476dfcbdd8fd92d6b5bd3ad3015efef87cf2f3` and `data/scripts/systems/reward_chest.lua` blob `4abe17ad2f3103f30f172f23ebdca391197f8646`.

Identity alone is not the proof. Semantic review confirms that the first root owns reward-container serialization plus participant target-state maintenance, while the second root reconciles boss participants, normalizes damage/healing contribution scores, generates per-player rewards, writes reward containers, saves offline players and clears encounter state. Delivered-PR searches identified no stronger bounded legacy donor for those roots.

The smallest valid target package is therefore `REUSE`: preserve production code unchanged and add one source-contract proof for the canonical encounter lifecycle. No maintained-client or protocol mutation is selected.

## Proof boundary

The OAM-036 regression test verifies that the target retains:

- persistent reward-container insertion through `InsertRewardItems` and `ITEM_REWARD_CONTAINER`;
- per-boss participant state via `_G.GlobalBosses`, `GetPlayerStats` and target-list activity reconciliation;
- reward-boss filtering and boss-death lifecycle;
- normalized damage/taken/healing scoring and participant-sensitive reward generation;
- reward-container insertion, offline-player save handoff and encounter-state cleanup;
- health-change participation accounting through the `BossParticipation` event.

The proof does not validate score arithmetic against official Tibia values or execute a physical-client boss fight.

## Nonclaims

OAM-036 does not claim exact participant eligibility, contribution-score arithmetic, loot factor or roll parity, reward-table correctness, Bosstiary bonus correctness, persistence atomicity, crash recovery, generic boss AI correctness, spawn or raid correctness, quest/cooldown behavior, protocol/client compatibility, physical-client boss E2E closure or full Real Tibia parity.
