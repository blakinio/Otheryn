# Canonical creature sprites and animation

OTBM Atlas renders canonical NPC and monster outfit overlays from one shared creature pipeline. Resolved creatures retain the established static PNG fallback and may additionally expose bounded time-based animation derived from the pinned Tibia appearance frame groups.

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

`assets.py` preserves the outer Tibia appearance frame-group identity in addition to each group's sprite/animation metadata. Creature groups are interpreted only by the pinned protobuf contract:

- `FIXED_FRAME_GROUP_OUTFIT_IDLE` -> `idle`;
- `FIXED_FRAME_GROUP_OUTFIT_MOVING` -> `moving`;
- unrelated/unsupported frame-group kinds are not promoted to creature animation truth.

`creature_sprites.py` owns the canonical `CreatureOutfit` model, definition-index conflict rules, colour-mask handling, addon pattern selection, bounded decoded-sheet/sprite caches, deterministic sprite extraction, animation phase rendering and deduplicated spawn enrichment.

`npc_sprites.py` and `monster_sprites.py` remain thin definition layers:

- NPC definitions require a literal `internalNpcName` and `npcConfig.outfit` with a positive `lookType`;
- monster definitions require a literal `Game.createMonsterType("...")` and `monster.outfit` with a positive `lookType`;
- matching is case-insensitive;
- identical duplicate definitions collapse deterministically to the first sorted source;
- conflicting outfit definitions for one canonical name are `ambiguous-definition` and remain unresolved;
- aliases are accepted only from explicit evidence supplied to the definition index; filenames, folders, descriptions and appearance similarity are never aliases.

The shared renderer resolves `lookType` against the pinned `appearances-*.dat`, extracts the exact pinned sprite IDs, applies Tibia outfit masks for head/body/legs/feet and applies addon bits to every rendered phase.

## Static sprite contract

The established static marker remains the conservative fallback. One PNG is written per outfit key and reused by every spawn with that outfit:

- `data/npc-sprites/<outfitKey>.png`;
- `data/monster-sprites/<outfitKey>.png`.

If a definition, look type, creature appearance or sprite cannot be proven from the vendored corpus, the record remains factual and `spriteStatus` records the unresolved reason. The viewer keeps the existing dot marker when no canonical sprite is available.

## Animation export contract

When a resolved appearance has a safely renderable canonical idle or moving group with more than one phase, the exporter writes one deduplicated animation package per outfit instead of one animation per spawn:

- `data/<kind>-sprites/<outfitKey>/animation.json`;
- `data/<kind>-sprites/<outfitKey>/<group>/<direction>/<phase>.png`.

The manifest retains:

- frame-group type/id;
- canonical phase count;
- phase duration ranges and deterministic runtime durations;
- default start phase;
- synchronization metadata;
- loop type/count;
- supported presentation directions;
- the exact exported phase paths.

Direction semantics are conservative. Four-pattern-or-wider creature groups expose canonical north/east/south/west pattern indices `0/1/2/3`; one-pattern groups expose one presentation direction using their only provable pattern. Two- or three-pattern groups are not assigned invented cardinal meanings.

The production map does **not** simulate creature pathing. Spawn coordinates remain the factual XML positions. A moving frame group can be presented in place as canonical appearance animation, but the atlas never claims that the NPC or monster walked to another tile or faced a server-observed direction.

If animation metadata or phase resources cannot be rendered safely, `spriteAnimationStatus` remains explicit and the browser retains the canonical static sprite. No generated/mock frame, cross-datapack fallback or guessed movement is used.

## Browser runtime

`creature_animation_runtime.js` owns the time-based browser overlay. It is separate from the base map canvas and reuses the existing atlas timing/cache concepts rather than producing GIFs, animated WebP or videos for production.

Runtime behavior is bounded:

- creature animation activates only at close zoom (`CREATURE_ANIMATION_SCALE = 0.45`);
- only enabled creature layers are considered;
- only visible spatial chunks are loaded;
- chunk JSON, animation descriptors and decoded images use bounded LRUs;
- the browser never requests a world-wide creature animation payload at startup;
- image smoothing stays disabled for pixel-art scaling;
- marker hit testing, details, search and URL state continue to use the same factual spawn records.

Monster overlays retain their existing low-zoom suppression below `0.25`.

## Relationship to environment animation

Creature animation and item/environment animation use different appearance categories and exporters. They intentionally share only safe runtime concepts such as bounded caches and canonical phase timing. Creature frame-group/direction semantics are not inferred from object animation semantics.

## Verification

`tools/otbm_atlas/tests/test_canonical_creatures.py` is the real pinned-data integration suite (enabled with `OTBM_ATLAS_CANONICAL_INTEGRATION=1`). It requires renderable canonical creature records and verifies that at least one real NPC and one real monster can export time-based canonical animation metadata and phase resources.

`.github/workflows/otbm-creature-showcase.yml` remains the static canonical NPC/monster regression showcase.

`.github/workflows/otbm-creature-animation-tests.yml` is the dedicated animation gate. It builds a real fixture from the pinned world/definitions/assets, opens the production viewer in real Chromium, requires multiple canonical phase resources for the same NPC and the same monster, verifies time-varying creature overlay output, and uploads machine-readable provenance plus human-viewable map-context/phase evidence.

A creature animation feature is not considered complete merely because phase PNGs were exported. The Chromium phase-playback gate and exact-head repository validation must pass.
