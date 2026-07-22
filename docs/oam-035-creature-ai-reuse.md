# OAM-035 Creature AI reuse proof

## Disposition

`creature-ai → REUSE`

## Immutable baselines

- Otheryn target: `4771350b44665c5a37b0c058b3d413c0c0de542d`
- Canary governance after preflight: `0f288fe2722d66753c74d859196688a7f9f60e60`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `creature-ai` owns Monster runtime think, target/friend maintenance, target search and selection, follow/flee/movement decisions, attack/defense execution, callbacks, spawn/despawn and summon-ownership interactions. It depends only on completed `creature-definitions`; static spawn placement, creature definition loading, generic combat formulas, raids and boss reward orchestration remain separate boundaries.

## Reuse decision

Task-start Otheryn and fresh upstream Canary share exact canonical owned core blobs: `src/creatures/monsters/monster.cpp` at `30cdadf4076d29116eb96fb8bb5f7f46bebddcd5` and `monster.hpp` at `a5426fdd22533179a9d54834dbe7b340a5d45012`. The reviewed legacy Canary core diverges on both files and is not a stronger whole-module donor.

The clean target already contains the newer modular AI architecture: Monster delegates bounded work to `monster_targeting`, `monster_pathfinding`, `monster_combat_intention` and `MonsterComputeService`, while the Monster lifecycle retains explicit think, target, follow, movement, attack, defense and spawn/despawn surfaces. Existing focused unit tests cover targeting, pathfinding, combat intention, compute service and relevance behavior.

The smallest valid target package is therefore `REUSE`: preserve production code unchanged and add one OAM source-contract proof that guards the canonical lifecycle surface and modular compute wiring. No protocol, maintained-client, data, schema, map, asset or deployment change is selected.

## Proof boundary

The OAM-035 regression test verifies that the target retains:

- the independent `Monster` runtime lifecycle surface for think, attacked/follow creature selection, target search/selection and target-list refresh;
- target and defense think hooks plus the asynchronous follow-path, target-search and combat-intention compute requests;
- the modular targeting, pathfinding, combat-intention and compute-service includes in the owned Monster implementation.

Existing component tests remain the behavioral evidence for those extracted helpers. This OAM proof does not duplicate their algorithms or claim full Monster AI parity.

## Nonclaims

OAM-035 does not claim Real Tibia AI parity, exact target-choice weights, pathfinding parity, thread-safety proof, scheduler fairness, combat formula parity, spawn timing parity, summon ownership completeness, boss AI/reward correctness, raid behavior, protocol/client compatibility, physical-client gameplay E2E closure or full Oteryn readiness.
