# OAM-034 Creature definitions adaptation

## Final disposition

`creature-definitions → ADAPT`

## Task-start baselines

- Canary/governance and legacy evidence: `ab2fb5548260544f42f786d11d4dd1b600c39a06`
- Otheryn target: `2fe646dfff3d4fc0672c3fbeca85708dabc4ce87`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `465b7a2192b176cf8cb9d58e000c38863e4a6e4c`

Canonical `creature-definitions` has no fundamental dependencies and owns monster definition data under `data/monster/**` and `data-otservbr-global/monster/**`. Creature AI, spawn placement, raids and boss encounter orchestration remain separate canonical boundaries.

## Selected donor boundary

Merged legacy Canary PR #192 is the accepted bounded donor. OAM-031 and earlier Cyclopedia-family packages deliberately left its monster-definition data outside their ownership. Fresh OAM-034 comparison confirmed that the task-start Otheryn target and fresh upstream still share the same pre-fix content for all six selected files, while current legacy preserves the exact reviewed corrections:

1. Agrestic Chicken adds `BESTY_RACE_BIRD` numeric Bestiary race metadata.
2. Terrified Elephant adds `BESTY_RACE_MAMMAL` numeric Bestiary race metadata.
3. Alternate Eradicator form changes `bossRaceId` from Rupture `1225` to Eradicator `1226`.
4. Monk's Apparition changes Bestiary `raceId` from `1946` to `2636`.
5. Haunted Dragon adds `BESTY_RACE_DRAGON` numeric Bestiary race metadata.
6. Crypt Warrior adds Bestiary `raceId = 1995` and `BESTY_RACE_UNDEAD` numeric race metadata.

The PR #192 Cyclopedia validator, validator tests, project logs and governance/task documentation are not imported. The target adds one focused OAM-034 source-contract test registered in the existing unit suite to prove all six selected data corrections and explicitly reject the two old colliding IDs.

## Adaptation boundary

Production changes are limited to the six reviewed monster definition files. No creature AI, spawn, raid, generic monster loader, Bestiary runtime, Bosstiary runtime, protocol, maintained-client, map, asset, schema, persistence or deployment path is changed.

## Nonclaims

OAM-034 does not claim full monster catalogue parity, exhaustive monster statistics, loot, spell, resistance or immunity correctness, creature AI behavior, spawn correctness, raid correctness, boss encounter mechanics, Bestiary or Bosstiary runtime correctness, protocol/client compatibility, persistence correctness, map or asset parity, physical-client creature E2E closure, or full Real Tibia parity.
