# OTBM atlas pipeline

Repository-owned tooling for deterministic analysis and chunked rendering of the
canonical CrystalServer world documented in `docs/maps/crystalserver-canonical-source.md`.

## Architecture and provenance

The canonical OTBM Atlas source contract is closed and machine-readable:

| Data | Canonical root |
|---|---|
| Map geometry and spawn XML | `vendor/map-analysis/crystalserver/data-global/world` |
| NPC definitions | `vendor/map-analysis/crystalserver/data-global/npc` |
| Monster definitions | `vendor/map-analysis/crystalserver/data-global/monster` |
| Object/creature appearances and sprite sheets | `vendor/map-analysis/tibia-client/15.25.bd5a04/assets` |

`data-otservbr-global` is not a canonical OTBM Atlas input. The canonical builder
rejects map, appearance-asset, or CrystalServer creature-definition roots outside
the pinned `vendor/map-analysis/**` corpus. Missing information remains unresolved;
there is no cross-datapack or network fallback.

The pipeline incrementally parses the pinned gzip-wrapped OTBM, spools bounded
128×128 world chunks, renders canonical detailed PNGs from the pinned 6031-file
Tibia 15.25 asset subset, and derives lightweight overview PNGs by deterministic
4× and 8× nearest-pixel downsampling of those exact detailed pixels. All layers retain
per-chunk SHA-256 checksums in the manifest. No external map geometry or imagery
is used.

Run its focused tests from the repository root:

```powershell
python -m unittest discover -s tools/otbm_atlas/tests -v
```

Run the real pinned creature integration suite with:

```powershell
$env:OTBM_ATLAS_CANONICAL_INTEGRATION = "1"
python -m unittest tools.otbm_atlas.tests.test_canonical_creatures -v
```

Scan the mandatory Thais regression region into deterministic JSON:

```powershell
python -m tools.otbm_atlas.scan `
  vendor/map-analysis/crystalserver/data-global/world/world.otbm `
  --bounds 32280 32440 32155 32305 7 `
  --output build/otbm-atlas/thais-scan.json
```

The command records the source SHA-256, header, tile/item statistics, populated
floors, AIDs, UIDs, teleports, house doors, towns, waypoints, and diagnostics.

Render the same region exclusively from the pinned appearance and sprite assets:

```powershell
python -m tools.otbm_atlas.render `
  vendor/map-analysis/crystalserver/data-global/world/world.otbm `
  vendor/map-analysis/tibia-client/15.25.bd5a04/assets `
  --bounds 32280 32440 32155 32305 7 `
  --output build/otbm-atlas/thais.png `
  --report build/otbm-atlas/thais-render.json
```

Static rendering uses the first object frame group and its declared
`default_start_phase`; elapsed time and random animation start are never used.
Missing appearances, missing sprites, invalid protobuf wire data, malformed LZMA
headers, and unexpected sheet dimensions are explicit failures/diagnostics.

Build resumable 128×128-map-tile chunks and the static viewer:

```powershell
python -m tools.otbm_atlas.atlas `
  vendor/map-analysis/crystalserver/data-global/world/world.otbm `
  vendor/map-analysis/tibia-client/15.25.bd5a04/assets `
  build/full-map-atlas --workers 4
python -m http.server 8000 --directory build/full-map-atlas
```

The atlas build also runs the bounded cyclic-environment exporter against the same pinned object appearances and chunk spool. Decodable cyclic objects can use 32x32, 32x64, 64x32, or 64x64 sprite geometry with canonical shift/height offsets; safe ground and non-topmost stack entries preserve local composition through per-instance underlay/overdraw patches. Shared phase PNGs are deduplicated by canonical appearance/pattern and animated by the browser at runtime rather than prebuilt as GIF/WebP files. Overlapping animated rectangles, chunk-edge risks, undecodable or non-opaque replacement cases, and server-driven state variants remain canonical static pixels. The browser only activates exported phases at close zoom and keeps its animation image/shard caches bounded. See `tools/otbm_atlas/ANIMATION.md` for the full runtime contract.

The first pass spools each tile once into bounded per-chunk binary files. Chunk
reports retain source/spool fingerprints and PNG checksums; matching chunks are
reused on subsequent runs. The viewer supports pan, zoom, floor selection,
coordinate display/jump, and factual mechanics/spawn overlay toggles.

The canonical Tibia asset corpus is marked `-text` in `.gitattributes` because
its fingerprint hashes raw worktree bytes. A Windows checkout created before
that rule may still contain the legacy CRLF representation. Repair that one
known safe line-ending-only delta after pulling with:

```powershell
python -m tools.otbm_atlas.repair_asset_checkout
```

The command is idempotent and refuses to replace any difference that is not
exactly CRLF-to-LF relative to the tracked Git blob.

NPC and monster spawn records are enriched before `data/spawns.json`, spatial
shards and search indexes are written. Both use one shared creature renderer and
only the vendored CrystalServer definitions plus pinned Tibia 15.25 creature
appearances/sprite sheets. At close zoom, resolved NPC and monster records load
pixel-perfect outfit sprites lazily through the existing bounded image LRU. At
lower zoom they remain lightweight markers; monster markers are still suppressed
below zoom 0.25 to avoid drawing tens of thousands of records. Missing, invalid or
ambiguous definitions/appearances/sprites remain factual dots with an explicit
`spriteStatus`. Outfit PNGs are deduplicated by look type/colours/addons under
`data/npc-sprites/` and `data/monster-sprites/`; hundreds of identical spawns share
one PNG. See `tools/otbm_atlas/CREATURES.md` for parser, deduplication and fallback
semantics.

Viewer floor selection and shared URLs use raw OTBM Z values 0 through 15, matching manifests and factual coordinates without a display-only remapping.
Chunks are cropped to their populated bounds plus a conservative two-tile sprite
gutter. This preserves 64×64 sprites and canonical displacement across chunk
edges without allocating a full 4096×4096 canvas for sparse chunks. Workers use
separate bounded renderers; manifest ordering remains deterministic.

Render mode is URL-shareable (`render=auto|detailed|performance`) and persisted
in localStorage; an explicit URL wins. Auto uses 8× overview below zoom 0.25,
4× overview from 0.25 to native 1.0 scale, and canonical detail at or above 1.0.
These boundaries follow the generated 4×/8× pixel densities and the canonical
32-pixel native tile scale rather than an unmeasured performance claim. Detailed requests canonical detailed chunks at
every zoom. Performance requests only overview chunks. Mode changes retain the
view, floor, zoom, layers, and selected-marker state without reloading. Imagery
uses a 128-entry/384 MiB approximate decoded-image LRU; spatial overlay data uses
a 96-entry/32 MiB approximate LRU. Diagnostics are opt-in and report only actual
state/load timings—never invented FPS.

The atlas build also writes `data/mechanics.json` from the same OTBM pass and
`data/spawns.json` from every canonical `*-monster.xml` and `*-npc.xml`. Spawn
X/Y offsets are relative to their group center; the child `z` value is absolute,
matching the canonical XML. Every record retains its source and an origin class.
Additional/event/quest sources remain distinct instead of being silently merged.
`data/composition.json` records which supplemental OTBMs have direct runtime
loading evidence. The base atlas always remains `world.otbm`; even proven runtime
overlays are listed separately. `data/mechanics-resolution.json` links literal
AID/UID registrations and legacy literal UID dispatch tables to Lua scripts with
`RESOLVED`, `AMBIGUOUS`, or `UNRESOLVED` status. Dynamic registrations stay
explicitly `UNKNOWN`.
Large factual overlay collections are additionally partitioned under
`data/chunks/z<z>/<chunkX>_<chunkY>.json`; the browser requests only viewport
chunks plus one 128-tile prefetch margin. `data/search-index.json` contains one
compact factual navigation entry per unique category/label, while details come
from the spatial records.
The base monster layer never guesses boss status by name, folder, appearance or
external knowledge. `verifiedBossSpawns` remains a separate factual layer and is
promoted only from explicit resolved canonical `rewardBoss=true` evidence.

## Prototype evolution

The owner-provided `oteryn-thais-interactive-demo.zip` was inspected as the
primary UI reference. PRESERVED: its dark Otheryn Maps language, dominant map,
top search/current coordinates, compact layer controls, drag/wheel/zoom buttons,
clickable markers, details surface, and shareable view state. ADAPTED: the fixed
Thais image becomes viewport-loaded multi-floor chunks; the NPC-only search and
layer panel use generated factual world indexes; the fixed right sidebar becomes
a floating responsive details panel. REPLACED: prototype demo JSON, single-region
bounds, image-wide transforms, and DOM marker collection are replaced by
canonical generated shards, canvas drawing, bounded caches, and URL/localStorage
state. No prototype map pixels or demo records are authoritative inputs.

## External viewer references

`tibiamaps/tibia-map` was evaluated as a slippy-map interaction reference: its
repository describes an online map viewer and is MIT licensed. No source code,
assets, map data, or styles are copied into this atlas, so no attribution notice
is required for reused code. The Otheryn viewer independently implements only
the applicable navigation patterns with the repository's canonical OTBM and
asset inputs. TibiaMaps.io was used only to assess familiar keyboard/pan/zoom and
overlay-navigation affordances; TibiaRoute's bestiary tracker was used only as
a compact layer/filter UX reference. Neither external service supplies Otheryn
geometry, markers, spawn records, or mechanics.
`data/unknown-items.json` lists every server ID without a canonical appearance,
including occurrence counts and source chunk bounds. These items remain visibly
unresolved; the renderer never substitutes another sprite.

To build only the spawn index:

```powershell
python -m tools.otbm_atlas.spawns `
  vendor/map-analysis/crystalserver/data-global/world `
  build/full-map-atlas/data/spawns.json
```

Standalone factual resolution/composition reports can be rebuilt with the same
vendored CrystalServer corpus:

```powershell
python -m tools.otbm_atlas.mechanics build/full-map-atlas/data/mechanics.json `
  vendor/map-analysis/crystalserver/data-global/scripts `
  build/full-map-atlas/data/mechanics-resolution.json
python -m tools.otbm_atlas.composition `
  vendor/map-analysis/crystalserver/data-global/world . `
  build/full-map-atlas/data/composition.json
```

Verify every manifest entry, PNG header/dimension and checksum independently:

```powershell
python -m tools.otbm_atlas.verify build/full-map-atlas `
  --output build/full-map-atlas/verification.json
```

The node framing follows the authoritative Remere's Map Editor implementation in
`source/filehandle.h` and `source/filehandle.cpp`; semantic work must likewise be
cross-checked against its `source/iomap_otbm.*` implementation.

## Thais counter reconciliation

The historical 15,037 child-item reference and the pinned-world 14,993 result use
the same semantic definition: every decoded non-ground item, including nested
container children. The 44-item difference is source revision drift. Running the
same strict parser over the owner prototype's `otservbr.otbm` (SHA-256
`a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`)
reproduces 15,037 exactly; the pinned canonical `world.otbm` (SHA-256
`3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`)
contains 14,993 in the same bounds. Both contain 24,311 tiles and 24,292 ground
items. The pipeline therefore does not force the historical total.
