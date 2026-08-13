# OTBM atlas pipeline

Repository-owned tooling for deterministic analysis and chunked rendering of the
canonical CrystalServer world documented in `docs/maps/crystalserver-canonical-source.md`.

## Delivery status

This directory is under phased implementation. The current verified component is
the bounded-memory escaped node-stream reader in `nodefile.py`. It recognizes a
gzip wrapper by magic bytes and reports structural corruption with byte offsets.
It does not yet claim semantic OTBM decoding, asset decoding, rendering, atlas UI,
overlay composition, or a completed full-map run.

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
coordinate display/jump, and factual mechanics/spawn overlay toggles.
Chunks are cropped to their populated bounds plus a conservative two-tile sprite
gutter. This preserves 64×64 sprites and canonical displacement across chunk
edges without allocating a full 4096×4096 canvas for sparse chunks. Workers use
separate bounded renderers; manifest ordering remains deterministic.

## Viewer UX contract

The atlas must remain usable for the complete canonical OTBM, not just selected
regions. The browser must therefore never load the full world sprite render or
full OTBM into one canvas/document. The complete world is preprocessed once by
the pipeline, while the browser loads only the current viewport plus a small
prefetch margin.

The default browsing experience should follow the lightweight slippy-map model
used by TibiaMaps/TibiaRoute: users can pan over the world, zoom, switch floors,
see world coordinates, and jump directly to an `X/Y/Z` position without first
loading detailed sprites for the whole map.

Rendering is intentionally layered by zoom level:

- low and medium zoom use lightweight pre-generated overview/minimap tiles;
- higher zoom uses progressively more detailed overview tiles as needed;
- maximum/detail zoom switches to the canonical 32 px-per-map-tile sprite render
  decoded from the pinned OTBM plus pinned Tibia assets;
- exact zoom thresholds are implementation parameters and must be selected from
  measured browser/runtime behavior rather than hard-coded from this document.

Overview/minimap tiles are derived from the canonical world data; they are not a
replacement source of map truth. The exact sprite layer remains authoritative for
fine visual inspection.

Map imagery and factual overlays must be spatially chunked. Mechanics, spawns,
NPCs, houses, AIDs, UIDs and teleports should be fetched for the visible region
rather than loading a world-sized overlay payload when that becomes materially
large. Floor data remains independently addressable for Z=0..15.

`https://github.com/tibiamaps/tibia-map` should be evaluated as an implementation
reference and potential viewer-core source before writing equivalent frontend
behavior from scratch. Its map data must not replace the canonical Otheryn OTBM.
Any reused code must comply with its license and retain required attribution.
`https://tibiamaps.io/map#32823,31962,7:0` and
`https://tibiaroute.com/pl/bestiary-tracker` are UX references for the desired
default map-navigation experience, not authoritative sources for Otheryn map
content.

The resulting user experience should allow both extremes efficiently: zoomed-out
navigation over the entire indexed world and, after maximum zoom, exact canonical
sprite-level inspection of the currently visible map fragment.

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

The node framing follows the authoritative Remere's Map Editor implementation in
`source/filehandle.h` and `source/filehandle.cpp`; semantic work must likewise be
cross-checked against its `source/iomap_otbm.*` implementation.
