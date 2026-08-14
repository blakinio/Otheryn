# Otheryn full OTBM atlas — viewer UI contract

This document freezes the production viewer decisions derived from the owner-provided Oteryn Thais interactive prototype and the durable atlas handover. Canonical OTBM data and pinned Tibia assets remain the source of truth; the prototype is a UI/interaction reference only.

## Prototype classification

| Prototype behavior | Production classification | Production contract |
| --- | --- | --- |
| Dark Oteryn Maps visual language | PRESERVED | Dark, map-dominant canvas with compact floating controls. |
| Map-dominant central surface | PRESERVED | The map canvas remains the primary viewport. |
| Top search/navigation | PRESERVED | Search remains immediately accessible above the map. |
| Compact layer controls | ADAPTED | Controls cover all factual chunked layers rather than only prototype NPCs. |
| X/Y/Z display and copy | PRESERVED | Coordinates use canonical raw OTBM `Z=0..15`; copied coordinates round-trip through search and URL state. |
| Floor switching | ADAPTED | The selector exposes raw OTBM Z directly, preserving X/Y, zoom, render mode and layers. |
| Mouse-wheel zoom and +/- controls | PRESERVED | Zoom is continuous and URL-persisted. |
| Pan/drag navigation | PRESERVED | Panning changes viewport state without loading the world globally. |
| Clickable markers and tooltips | PRESERVED | Hit testing is restricted to current visible shards. |
| Details/info panel | ADAPTED | Details expose only factual fields present in the indexed record; missing values are not inferred. |
| NPC-only search | REPLACED | Search spans factual NPC, monster, town, AID, UID, waypoint, mechanics and house indexes plus `X,Y,Z`. |
| Single fixed Thais image | REPLACED | Multi-resolution canonical chunk imagery supports the complete world and every populated Z. |
| Prototype URL hash | REPLACED | Query-state persists X/Y/Z, zoom, render mode, layers and selected marker. |

## Render modes

`Auto` is the default: overview imagery at low/medium zoom and exact canonical sprite chunks at detail zoom.

`Detailed` always selects canonical detailed imagery while retaining viewport-only chunk loading and bounded caches.

`Performance` never automatically requests detailed sprite chunks and remains on overview imagery.

Explicit URL `render` state takes precedence over local storage. Changing render mode preserves location, zoom, layers and selected marker state.

## Coordinate contract

All externally visible coordinates use canonical raw OTBM `X/Y/Z`. Valid Z values are `0..15`. There is no alternate `7-z` floor-number encoding in URLs, search, copy output, details, tooltips or the jump control.

This deliberately matches the original Thais prototype (`..., ..., 7`) and canonical OTBM records. It also guarantees that copied `X,Y,Z` can be pasted into search without conversion.

## Search and selection contract

Selecting a factual search result:

1. moves to the record X/Y/Z;
2. raises zoom to a useful minimum when necessary;
3. enables and persists the matching factual layer if it is disabled;
4. loads only the containing spatial shard;
5. selects the exact matching record;
6. opens its factual details panel;
7. persists the resulting navigation/layer/marker state in the URL.

Coordinate search navigates directly to raw X/Y/Z without inventing a marker.

## Factual layers

First-class layers are NPCs, monsters, supplemental NPCs, supplemental monsters, teleports, houses, house doors, Action IDs, Unique IDs, towns/temples, waypoints and mechanics. Supplemental creature records remain visually and semantically separate from base-map records.

Bosses remain disabled and explicitly `UNKNOWN` until an authoritative boss classification source is available. Names are never used as a boss heuristic.

Mechanics resolution retains `RESOLVED`, `AMBIGUOUS`, `UNRESOLVED` and `UNKNOWN`; the viewer does not choose among ambiguous candidates.

## Bounded browser resources

Base imagery uses a bounded LRU of 128 entries / 384 MiB approximate decoded image budget. Overlay shards use 96 entries / 32 MiB. Environment animation images use 256 entries / 64 MiB and animation shards 64 entries / 8 MiB.

Only viewport chunks plus the configured small prefetch margin are considered for base/overlay drawing. Environment animation is additionally culled by viewport and close-zoom threshold and is suspended while the page is hidden.

The diagnostics panel may show factual cache counts, approximate tracked byte totals, current mode/base layer, current X/Y/Z, zoom, visible chunk count and measured recent load timings. It must not fabricate FPS or unavailable metrics.

## Animation boundary

Cyclic appearance animation decoded from pinned client appearance metadata is browser-rendered only for conservatively promoted environment objects. Server-driven state changes such as doors, switches, quest state and on/off variants are separate mechanics and are never inferred as cyclic animation.

## Development versus final acceptance

During implementation, the required focused gates are atlas unit/runtime tests, canonical Thais scan/render, real Chromium Thais E2E, environment-animation Chromium E2E, repository CI and Required checks.

`Full canonical world v3` is intentionally not a synchronize-time development test. It is invoked once on the frozen final SHA by explicitly adding `ci:final-gate` (or manual workflow dispatch), and must then build and independently verify the complete 3494-chunk `Z=0..15` atlas before final release/merge certification.
