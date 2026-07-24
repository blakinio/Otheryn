# OAM-043 quests adaptation proof

## Disposition

`quests → ADAPT`

The clean Otheryn target and pinned current upstream share the same complete 978-file canonical quest inventory, but exact three-way inventory, source analysis and world-map correlation isolated six bounded target gaps. OAM-043 repairs three concrete defects in existing scripts and restores three legacy-only handlers that are still required by the configured map. It does not bulk-copy the legacy quest tree.

No OTBM binary, map asset, protocol, maintained client, schema or deployment path is changed.

## Exact baselines and inventory

Task-start baselines:

- Otheryn target: `3a37f3d5e4c01ddf4469f1c71461c40ca749142f`;
- current upstream `opentibiabr/canary`: `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`;
- legacy `blakinio/canary`: `13ec3077babba0ac81bb1e30e79f0ea4827ae2fe`.

The exact inventory workflow run `30089008736` produced manifest SHA-256 `391e38d963b1a791e4fd59edf8ce6adbb4a75dfc8e8a34da351c50f080267925` and artifact digest `sha256:2272eea7e77e3c04a4ed6e8ddf30e75dcdf18f115a1dcf8f624d00e9f7191f76`:

- target: `978` files;
- current upstream: `978` files;
- legacy: `981` files;
- `973` paths identical in all three repositories;
- `5` paths where target and upstream are identical and legacy diverges;
- `3` legacy-only paths;
- no target-only, upstream-only, target/legacy-only or all-divergent paths.

This identity is discovery evidence, not by itself a reuse decision.

## Complete source and map evidence

The complete target scan covered all `978` selected Lua files. Source digest `a97442a2e77aee6cd02ba094a8158965a1da9681d0426114c7cd1c3546e3ef40` contains `12027` static evidence entries:

- `704` action IDs and `519` unique IDs;
- `992` item IDs;
- `5824` position references and `1972` teleport destinations;
- `2016` storage references: `1088` reads and `928` writes.

The scanner retained `1045` unresolved expressions rather than evaluating them:

- `593` dynamic storage expressions;
- `266` dynamic or out-of-range positions;
- `182` dynamic or out-of-range item expressions;
- `4` unresolved unique-ID registrations.

The configured world map was downloaded from the target-declared Canary v3.6.1 release URL and verified as SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`. The deterministic World Index was SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a` and recorded `17972761` tiles, `23359571` item placements, `9339` mechanic placements and zero unknown attribute tails.

Complete source-to-map correlation produced:

- `8860` confirmed findings;
- `484` script-only findings;
- `2683` unresolved findings;
- zero map-only findings;
- zero conflicting findings.

The `484` script-only findings and `1045` unresolved source expressions are not silently promoted to target defects or handled gameplay. They describe shared target/upstream content boundaries that require separate bounded reviews.

## Accepted bounded adaptation

### Existing-script corrections

1. `hero_of_rathleton/actions_reward.lua`
   - fixes the reward hook from `The Professors Nut` to the registered catalogue name `The Professor's Nut`;
   - the exact target catalogue entry is in `data/scripts/lib/register_achievements.lua`.

2. `soulpit/soulpit_fight.lua`
   - replaces an undefined `creature` reference inside `onUse(player, ...)` with the actual `player` parameter;
   - does not restore the legacy local `encounter:countMonsters` override because target `data/libs/systems/encounters.lua` already owns the generic `Encounter:countMonsters(name)` contract.

3. `the_ancient_tombs/actions_oasis_lever_door.lua`
   - restores timed transformation of open door item `1663` back to closed item `1662` together with lever/carrot cleanup;
   - retains only existing AID `12107`;
   - candidate donor run `30089658579` classified legacy AID `12108` as `script-only` with zero map placements, so that registration is explicitly rejected.

### Map-backed legacy-only handlers

Candidate donor proof run `30089339771` scanned the three legacy-only `The Beginning` scripts and correlated them with the exact configured map:

- `72` evidence entries across three files;
- `47` confirmed findings;
- zero script-only, map-only or conflicting findings;
- one dynamic table-backed storage expression retained unresolved.

The proof confirms map-backed AID registrations `50058` through `50088`, UID `50085`, relevant positions, and item mechanics. OAM-043 therefore restores exactly:

- `the_beginning_tutorial_moveevents.lua`;
- `the_beginning_zirella_door.lua`;
- `the_beginning_zirella_wood.lua`.

The resulting canonical quest-root inventory is `981` files. No other legacy-only path exists in the reviewed roots.

## Rejected donor hypotheses

- The legacy Ape City and Wrath of the Emperor variants call `hasAccountQuestAccess` and `unlockAccountQuestAccess`. Exact target symbol search found neither API in Otheryn, so importing those calls would create an unowned player-persistence/API dependency. Existing character-storage behavior is retained.
- The legacy Soulpit-local monster counter duplicates the completed generic Encounter/Zone runtime and is not imported.
- AID `12108` is not imported because exact configured-map correlation found zero placements.
- The full legacy quest tree is not copied. The target/current-upstream 978-file inventory remains authoritative except for the six evidence-backed changes above.

## Source-contract proof

`tests/unit/game/oam_043_quests_adapt_test.cpp` verifies:

- the registered achievement name and corrected Soulpit handler parameter;
- generic Encounter count ownership without a duplicated local override;
- timed oasis-door closure while rejecting AID `12108`;
- map-backed `The Beginning` AID/UID/item/position contracts;
- absence of unimplemented account-wide quest-access calls;
- representative KV persistence handoff in the Blue Valley teleport;
- the final `981`-file canonical quest inventory.

## Boundaries

OAM-043 does not claim:

- exhaustive correctness of every quest, reward, access gate, storage transition or NPC/spawn dependency;
- a proven storage-transition graph from lexical reads and writes;
- execution or correctness of the `1045` unresolved dynamic source expressions;
- repair or gameplay disposition of all `484` shared script-only findings;
- reachability or live usability of every confirmed map mechanic;
- exact Real Tibia quest, reward, timing, dialogue or progression parity;
- protocol/client UI parity, production gameplay parity, physical-client quest E2E closure or full world-content readiness.

The accepted result is a bounded `ADAPT`: six exact quest-source changes, deterministic source/map provenance, explicit rejected donor hypotheses, and no unrelated architecture or content migration.
