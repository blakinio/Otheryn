# Canonical creature sprites

OTBM Atlas renders static NPC and monster outfit markers from one shared creature pipeline.

## Canonical sources

The production atlas source contract is intentionally closed:

| Data | Canonical root |
|---|---|
| OTBM geometry and spawn XML | `vendor/map-analysis/crystalserver/data-global/world` |
| NPC definitions | `vendor/map-analysis/crystalserver/data-global/npc` |
| Monster definitions | `vendor/map-analysis/crystalserver/data-global/monster` |
| Object/creature appearances and sprite sheets | `vendor/map-analysis/tibia-client/15.25.bd5a04/assets` |

`data-otservbr-global` is not a canonical OTBM Atlas input. The canonical builder rejects a non-vendored map, appearance asset root, or CrystalServer data root. It never downloads or borrows an outfit from another datapack.

## Architecture

`creature_sprites.py` owns the canonical `CreatureOutfit` model, definition-index conflict rules, colour-mask handling, addon pattern selection, bounded decoded-sheet/sprite caches, deterministic sprite extraction and deduplicated spawn enrichment.

`npc_sprites.py` and `monster_sprites.py` are thin definition layers:

- NPC definitions require a literal `internalNpcName` and `npcConfig.outfit` with a positive `lookType`.
- Monster definitions require a literal `Game.createMonsterType("...")` and `monster.outfit` with a positive `lookType`.
- matching is case-insensitive;
- identical duplicate definitions collapse deterministically to the first sorted source;
- conflicting outfit definitions for one canonical name are `ambiguous-definition` and remain unresolved;
- aliases are accepted only from explicit evidence supplied to the definition index; filenames, folders, descriptions and appearance similarity are never aliases.

The shared renderer resolves `lookType` against the pinned `appearances-*.dat`, extracts the exact pinned sprite IDs, applies Tibia outfit masks for head/body/legs/feet, applies addon bits, and writes one PNG per outfit key. Multiple spawns with the same outfit therefore share one asset.

Generated paths are:

- `data/npc-sprites/<outfitKey>.png` and `data/npc-sprites/index.json`;
- `data/monster-sprites/<outfitKey>.png` and `data/monster-sprites/index.json`.

The index files include source-root provenance and resolution statistics.

## Spawn enrichment and fallback

NPC and monster spawns are enriched immediately after `scan_spawns(...)`, before `data/spawns.json`, spatial shards and search indexes are written. Consequently a resolved monster record carries the same factual outfit fields as a resolved NPC record:

- `lookType`;
- `lookHead`;
- `lookBody`;
- `lookLegs`;
- `lookFeet`;
- `lookAddons`;
- `outfitSource`;
- `sprite`;
- `spriteStatus`.

If a definition, look type, creature appearance or sprite cannot be proven from the vendored corpus, the record remains factual and `spriteStatus` records the unresolved reason. The viewer keeps the existing dot marker. No appearance is invented and no cross-datapack fallback is attempted.

## Viewer policy

At close zoom, `drawCreatureSprite(record, ...)` is shared by NPC and monster spawn kinds. Browser image loading remains lazy and bounded by the existing LRU, image smoothing stays disabled for pixel-perfect scaling, and marker hit-testing/details/search/URL state continue to use the same records.

Monster overlays remain suppressed below zoom `0.25`; the viewer does not try to load or draw the world-wide monster population at low zoom.

## Animation boundary

This slice is **static canonical creature sprite parity**. It does not implement creature idle/walk animation, direction changes, simulated movement, GIFs or animated WebP. The runtime item/environment animation system remains separate. A future creature-animation layer should reuse the same appearance lookup, outfit model and bounded caches rather than create another renderer.

## Verification

`tools/otbm_atlas/tests/test_canonical_creatures.py` is the real pinned-data integration suite (enabled with `OTBM_ATLAS_CANONICAL_INTEGRATION=1`). `.github/workflows/otbm-creature-showcase.yml` runs it, generates full NPC/monster resolution statistics, renders a real vendored map region containing one renderable NPC and monster, proves both sprite resources load in real Chromium, and uploads `otbm-creature-showcase` with the screenshot and JSON source fingerprints.
