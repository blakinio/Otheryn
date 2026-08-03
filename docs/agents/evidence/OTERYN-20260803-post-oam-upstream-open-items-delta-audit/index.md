# Evidence index

Audit: `OTERYN-20260803-post-oam-upstream-open-items-delta-audit`

## Durable files

- `inventory.json.gz` — gzip-compressed complete 103-row machine-readable JSON inventory.
- `inventory.csv.gz` — gzip-compressed tabular CSV export of the same inventory.
- `report.md` — human-readable reconciliation and independent challenge.
- `validation.txt` — deterministic local artifact validation result.

## Exact target evidence used for material Issues

- `src/creatures/players/player.cpp`: stash withdrawal reconciliation, experience-rate division and null-tile creature update.
- `src/creatures/combat/condition.cpp`: serialized condition index writes.
- `src/lua/functions/creatures/npc/npc_functions.cpp`: NPC purchase creation-before-payment behavior.
- `data/npclib/npc_system/bank_system.lua`: inverted guild-deposit balance predicate.
- `src/game/game.cpp`: `playerSaySpell` walk-exhaust early return.
- `src/creatures/monsters/monster.cpp`: rename path sends a partial known-creature update.
- `data/modules/scripts/gamestore/catalog/extras_usefull_things.lua`: Prey Wildcard counts/prices.
- `data-otservbr-global/npc/storkus.lua`: Storkus outfit/dialogue/storage defects.
- eleven Djinn NPC scripts: recognition storage is not consulted before greeting rejection.
- `data-otservbr-global/npc/sven.lua` and `.../barbarian_test/action_mead.lua`: quest reset and counter defects.
- `data-otservbr-global/scripts/quests/soul_war/soul_war_mechanics.lua`: nil attacker dereference.
- `data-otservbr-global/scripts/globalevents/others/raids_schedule.lua`: process-lifetime `alreadyExecuted` state.

## Historical/governance evidence

- completed `CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION`;
- OAM-001 through OAM-054;
- `OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`;
- canonical module registry;
- Canary-owned `UPSTREAM_INTELLIGENCE_PROGRAM.md`.

## External revisions

Every open PR row pins its exact head SHA in `inventory.json`. Issue-only rows pin repository, number, URL and final query timestamp and remain unproven unless exact target evidence is separately named.
