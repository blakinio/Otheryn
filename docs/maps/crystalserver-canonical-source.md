# Canonical CrystalServer map source

This document records the map source selected by the repository owner for ongoing Otheryn map-analysis and atlas work.

## Canonical source package

Owner-provided archive name:

`crystalserver-main(2).zip`

The archive contains the CrystalServer source tree. For the global-world work discussed in the OTS project, the canonical primary map is:

`crystalserver-main/data-global/world/world.otbm`

Verified package-local properties from the owner-provided archive:

- file size: `52,836,960` bytes
- SHA-256: `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`

The archive also contains a separate Crystal-specific world:

`crystalserver-main/data-crystal/world/world.otbm`

- file size: `11,373,094` bytes
- SHA-256: `3021fa0cd15a0a34cb805571f783da0f852441a6bbe98fed99ad277787710817`

Unless a task explicitly says otherwise, **the `data-global/world/world.otbm` file above is the baseline map for subsequent comparison, rendering, completeness analysis, and atlas work**.

## Related world data

Do not treat the primary OTBM as the complete runtime world by itself. The owner-provided CrystalServer archive also includes supplemental world data such as:

- `data-global/world/world-house.xml`
- `data-global/world/world_changes/**`
- `data-global/world/quest/**/*.otbm`
- `data-global/world/annual_events/**/*.otbm`
- `data-global/world/custom/global-custom.otbm`

Any full-world completeness or runtime-equivalence analysis must account for those overlays/auxiliary maps separately rather than silently flattening or ignoring them.

## Atlas/rendering baseline

The validated rendering approach used in this project is source-derived, not AI-generated:

1. parse the real OTBM tile/item structure;
2. resolve client appearances and sprite sheets from the real client asset package;
3. render deterministically in coordinate-aligned chunks;
4. extract AID, UID, teleports, house metadata and other OTBM attributes directly from the map;
5. add spawn/NPC/script layers only when they are grounded in corresponding server source data;
6. mark unresolved or unavailable layers as `UNKNOWN` rather than inferring them.

For whole-map output, prefer chunked map tiles plus a manifest/index over one monolithic PNG.

## Provenance rule

Do not replace this baseline with a different CrystalServer/Canary/Otheryn map merely because another repository revision is newer. A change of canonical map source requires an explicit owner decision and should update this document with the new exact file identity/hash.

The uploaded ZIP itself is not committed by this documentation change. This file records the exact selected source identity so future agents can verify a supplied copy byte-for-byte before using it.