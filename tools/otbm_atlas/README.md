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
  build/full-map-atlas
python -m http.server 8000 --directory build/full-map-atlas
```

The first pass spools each tile once into bounded per-chunk binary files. Chunk
reports retain source/spool fingerprints and PNG checksums; matching chunks are
reused on subsequent runs. The viewer supports pan, zoom, floor selection,
coordinate display/jump, and factual mechanics/spawn overlay toggles.

The node framing follows the authoritative Remere's Map Editor implementation in
`source/filehandle.h` and `source/filehandle.cpp`; semantic work must likewise be
cross-checked against its `source/iomap_otbm.*` implementation.
