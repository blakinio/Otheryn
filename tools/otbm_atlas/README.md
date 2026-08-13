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

The node framing follows the authoritative Remere's Map Editor implementation in
`source/filehandle.h` and `source/filehandle.cpp`; semantic work must likewise be
cross-checked against its `source/iomap_otbm.*` implementation.
