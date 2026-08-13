# OTBM atlas pipeline

Repository-owned tooling for deterministic analysis and chunked rendering of the
canonical CrystalServer world documented in `docs/maps/crystalserver-canonical-source.md`.

## Architecture and provenance

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

The first pass spools each tile once into bounded per-chunk binary files. Chunk
reports retain source/spool fingerprints and PNG checksums; matching chunks are
reused on subsequent runs. The viewer supports pan, zoom, floor selection,
coordinate display/jump, and factual mechanics/spawn overlay toggles. NPC markers
use the configured canonical creature outfit from `data-otservbr-global/npc` and
the pinned Tibia 15.25 creature appearances. At zoom below 0.45 they deliberately
remain lightweight dots; an NPC without a decodable explicit `lookType` also stays
a dot rather than receiving an invented image. Outfit PNGs are deduplicated by
look type/colours/addons under `data/npc-sprites/` and loaded lazily through the
existing bounded image LRU cache.
Viewer floor labels are relative to the Tibia surface: raw OTBM Z=7 is floor 0,
Z=0 is +7, and Z=15 is -8. Manifests and factual coordinates retain raw Z.
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
Monster markers are suppressed below zoom 0.25 to avoid drawing tens of
thousands of individual points; their factual shards remain available and no
records are reclassified. Bosses remain explicitly UNKNOWN because the canonical
sources provide no authoritative boss classification.

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

Standalone factual resolution/composition reports can be rebuilt with:

```powershell
python -m tools.otbm_atlas.mechanics build/full-map-atlas/data/mechanics.json `
  data-otservbr-global build/full-map-atlas/data/mechanics-resolution.json
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
