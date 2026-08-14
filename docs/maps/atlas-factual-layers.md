# OTBM Atlas factual mechanics and world-service layers

The canonical OTBM Atlas consumes factual indices produced from the exact pinned CrystalServer corpus under `vendor/map-analysis/crystalserver`.

## Provenance

The factual source revision is `zimbadev/crystalserver@5e89bf8329ea406cb4ea8f4a18f32954f13e5418`.

The consumer uses:

- `data-global/scripts/**` for AID/UID registrations and statically provable scripted transitions;
- `data-global/raids/**` plus pinned script raids for raid/event geometry and participants;
- `data-global/monster/**` for explicit `rewardBoss` classification evidence;
- `data-global/npc/**` plus `data/npclib/npc_system/**` for NPC shop, bank, guild-bank and travel semantics.

The producer package is `tools/otbm_atlas_facts`. The browser never executes Lua.

## Spatial layers

The generated atlas keeps direct OTBM teleports and scripted transitions separate:

- `teleports` — destination encoded directly in the canonical OTBM;
- `scriptedTeleports` — a map AID/UID resolved to exactly one pinned script registration with a `PROVEN_STATIC` scripted teleport destination. Conditional transitions remain labelled `conditional=true`;
- `raidPointSpawns` — exact single-spawn positions from raid/event definitions;
- `raidAreas` — exact source rectangles. Their `position` field is only a derived navigation/search center and never replaces the rectangle;
- `npcServices` — base-map NPC spawn positions enriched with resolved or ambiguous pinned service evidence;
- `verifiedBossSpawns` — only exact base-map or raid-point positions whose monster definition resolves explicit `rewardBoss=true`.

Raid rectangles are copied into every intersecting spatial chunk so viewport loading remains correct at chunk boundaries. The browser still requests only visible chunk shards and keeps its existing bounded overlay cache.

## Uncertainty policy

`UNKNOWN`, `UNRESOLVED` and `AMBIGUOUS` evidence remains in generated reports and detail payloads. It is not silently converted into a navigable transition or verified boss location.

A monster path, filename, directory such as `bosses/`, or name is never sufficient boss evidence. A dynamic event with no statically proven position remains spatially unknown.

## Generated reports

Canonical builds additionally emit:

- `data/factual-layers.json` — source fingerprint, policy and compact statistics;
- `data/mechanics-resolution.json` — pinned CrystalServer AID/UID resolution;
- `data/monster-metadata.json`;
- `data/npc-services.json`;
- `data/npc-system-semantics.json`;
- `data/raids-events.json`.

The search index contains only facts with a usable spatial position. Dynamic spatially unknown events remain in their factual report instead of being assigned guessed coordinates.
