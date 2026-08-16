# OTBM Atlas incremental build and publication contract

Status: implementation contract for `OTH-20260816-atlas-incremental-build-ci`.

## Objective

An ordinary Atlas change must never imply a canonical full-world rebuild merely because one monolithic OTBM file or the complete asset tree received a new SHA-256. The normal path is:

```text
immutable source snapshot
        |
        v
spatial spool / local hashes
        |
        v
chunk dependency + reverse-dependency index
        |
        v
change-impact plan
        |
        +--> changed detail chunks only
        +--> changed overview chunks only
        +--> changed data domain only
        +--> frontend only when appropriate
        |
        v
content-addressed changed objects
        |
        v
atomic publication manifest
```

A full build is a deliberate recovery/semantic-transition operation, not a default response to a changed file.

## Verified baseline and why this is required

The current v3 Atlas uses 128x128 map-tile chunks and the certified canonical world contains 3,494 detail chunks across Z0..Z15. The current canonical detail PNG corpus alone is measured at 10,995,096,999 bytes before overviews, environment animation, creature sprites, JSON data and other publication files.

The legacy `tools/otbm_atlas/atlas.py` cache fingerprint includes the SHA-256 of the complete `world.otbm`, the SHA-256 of the complete appearance-asset tree and the local spool SHA. Consequently a change anywhere in the monolithic map or asset tree can invalidate every detail chunk even when almost all local pixels are unchanged. Its global source-state transition also recreates the complete spool.

The new incremental path deliberately does not put those global source hashes into a detail fingerprint.

## Source snapshot versus build delta

This work does **not** change the accepted Game -> Atlas contract. The producer may continue to supply a complete deterministic immutable snapshot. Incrementality is an Atlas consumer/build concern:

```text
Game export N (complete snapshot)
            |
            v
Atlas spatial comparison
            |
            v
only changed derived outputs
```

A future Game -> Atlas delta protocol remains a separate evidence-triggered decision. Complete snapshots remain the recovery truth.

## Spatial spool

`tools/otbm_atlas/incremental_core.py` parses the source map and assigns every tile to a stable `(z, chunkX, chunkY)` spool. The current default remains 128. Parsing a monolithic OTBM may still require one sequential pass, but the resulting unchanged spool bytes are not rewritten and, more importantly, they do not trigger rendering.

`reconcile_spool()` compares candidate and stable per-chunk SHA-256 values and performs only three actions:

- replace changed/new chunk bytes atomically;
- retain byte-identical chunks;
- remove chunks that disappeared from the target snapshot.

Changing the chunk size itself is not treated as an ordinary incremental transition. It requires a clean spatial spool transition.

## Render dependency index

For each spatial chunk the dependency index records:

- local spool SHA-256;
- exact appearance IDs participating in visible tile rendering;
- exact selected sprite IDs for the current deterministic static rendering policy.

It also records reverse indexes:

```text
appearance ID -> chunks
sprite ID     -> chunks
```

The sprite selection calculation mirrors the renderer's position patterns, stack count, hangable hook direction, fluid subtype and declared default animation phase. It does not need to decode every sprite sheet merely to determine dependency identity.

Container descendants remain part of the spool because they contribute to canonical report statistics, but they are not promoted to visible render dependencies when the renderer itself does not draw them.

## Asset invalidation

Asset state is decomposed into:

- semantic digest per object appearance;
- SHA-256 and sprite-ID range per sprite sheet;
- one global gutter profile containing maximum sprite dimensions and global shift extrema.

An appearance change invalidates only chunks in that appearance's reverse index. A sprite-sheet byte change invalidates only chunks whose selected sprite IDs fall in that sheet's old or new ID range.

The gutter profile is intentionally global today because the certified renderer computes conservative chunk crop bounds from global sprite dimensions and appearance shift extrema. If that profile changes, the current rendering contract truthfully requires all detail chunks to be considered dirty. This is a machine-readable `GLOBAL_GUTTER_PROFILE_CHANGED` full-build reason rather than a hidden cache miss.

Current chunk rendering draws only tiles sourced by that chunk into its own conservative gutter. It does not draw neighboring source chunks into the image, so a local tile edit does not require speculative neighbor invalidation. If a future renderer introduces cross-chunk source composition, the render-core version and invalidation contract must be changed together.

## Local detail fingerprint

A detail fingerprint contains only inputs that can affect that chunk under the current contract:

```text
chunk size
local spool SHA-256
semantic digest of appearances used by this chunk
SHA-256 of sprite sheets containing sprites used by this chunk
global gutter profile
render-contract digest
```

It does not contain the SHA-256 of the complete map or complete asset tree.

Planner/publication refactors do not change the render-contract digest. Pixel-semantics changes in the incremental core require an explicit `RENDER_CORE_VERSION` bump; changes in `render.py`, `assets.py` or `semantic.py` are detected directly.

## Independent overview invalidation

4x and 8x overview images remain deterministic derivatives of the detail PNG. A changed detail chunk invalidates its own overview derivatives. A change confined to `overview.py` may invalidate all overview chunks without forcing any detail PNG to be rendered again.

This is a separate invalidation domain by design.

## Data-domain classification

The impact plan classifies changed paths independently from map rendering. Current machine-readable domains include:

- `mapGeometry`;
- `renderAssets`;
- `spawns`;
- `npcDefinitions`;
- `monsterDefinitions`;
- `mechanics`;
- `factualData`;
- `frontend`;
- `ci`;
- `documentation`.

A spawn XML or viewer-only change therefore does not become a reason to render all map images. Existing specialized generators remain responsible for their own domain outputs until they are migrated behind equivalent local fingerprints.

## Full-build guard

Every plan declares:

```json
{
  "fullBuildRequired": false,
  "fullBuildReasons": []
}
```

When a global render semantic really changes, the planner sets `fullBuildRequired: true` and records exact reasons. `python -m tools.otbm_atlas.incremental guard <plan>` fails closed in normal CI. The only override is explicit `--allow-full-build`.

The incremental workflow never silently responds by building the entire canonical world.

The repository already has a separately gated full-world Atlas workflow path triggered deliberately by its final-gate/manual mechanism. It is not the ordinary PR path. Full clean execution remains the recovery/equivalence authority when such evidence is genuinely required.

## Content-addressed publication

Changed rendered files can be stored as immutable objects:

```text
objects/sha256/<first-two>/<full-sha256>
```

A publication manifest maps each logical browser path to one immutable object digest and byte count. Reusing unchanged logical paths reuses their existing object records. A patch manifest records changed, deleted and unchanged paths between publication manifests.

Promotion order is:

1. write and verify immutable changed objects;
2. compose the target manifest from the prior manifest + changed objects - deleted paths;
3. write the candidate manifest;
4. atomically replace the selected publication manifest.

A failed partial build therefore cannot make a half-populated candidate the selected publication simply because some objects were already written.

## Chunk-size decision: 32 vs 64 vs 128

The default is **not** changed from 128 by assumption. `tools/otbm_atlas/chunk_benchmark.py` measures the same bounded canonical region at 32, 64 and 128 and reports:

- number of produced chunks;
- populated tiles;
- nominal invalidation area in map tiles;
- encoded detail bytes;
- render operations;
- measured render seconds.

Smaller chunks improve invalidation locality but increase file/request/manifest cardinality. A future default must be chosen from measured build and browser evidence, not from chunk area alone.

Representative command:

```bash
python3 -m tools.otbm_atlas.chunk_benchmark \
  --bounds 32280 32440 32155 32305 7 \
  --sizes 32 64 128 \
  --output /tmp/atlas-chunk-benchmark.json
```

## GitHub-hosted execution

`.github/workflows/otbm-atlas-incremental.yml` uses only GitHub-hosted `ubuntu-latest` runners and does not use Synology runners. It performs:

1. focused syntax/unit validation;
2. an exact base-vs-head canonical impact plan;
3. the fail-closed full-build guard;
4. real canonical one-chunk incremental rendering and byte-for-byte comparison with the established renderer path;
5. the bounded 32/64/128 Thais benchmark.

Generated Tibia/CipSoft-derived render images are temporary validation data and are deleted before job completion. The workflow does not upload the generated map corpus as a public artifact.

Documentation/task-only changes do not trigger this workflow. `pull_request:labeled` is also not an incremental-workflow trigger.

## GitHub Pages / hosting decision

GitHub Pages is **not enabled for the current full Atlas**. The measured current detail corpus alone is about 11 GB, before the rest of the product, and the current public repository task does not authorize public redistribution of generated third-party-derived render assets.

This does not block moving build/test CPU to GitHub-hosted Actions. Hosting/storage is intentionally separated from CI. A future hosting decision must use measured final corpus size, traffic, cache/object-store economics and explicit asset-redistribution authority.

## Migration boundary with active Atlas work

At the time this incremental path was introduced, active PRs independently owned the legacy `atlas.py`, product viewer files and existing specialized Atlas workflows. To prevent concurrent-writer conflicts, the incremental engine, tests, benchmark and new workflow were introduced as non-overlapping files first.

The final migration step after those owners become terminal is to route the ordinary canonical Atlas build entry point through this impact plan/local fingerprint state and to remove any remaining unconditional global invalidation from the legacy entry path. That integration must preserve the environment-animation resumability and tile-inspector/product changes merged in the meantime rather than overwriting them.

## Required equivalence discipline

Incremental correctness is not inferred from cache hits. Validation must prove:

- identical input -> zero dirty detail chunks;
- one changed spatial chunk -> only that detail chunk plus its derivatives are dirty;
- changed used appearance/sprite -> only reverse-dependent chunks are dirty;
- unrelated asset -> no unrelated chunk rebuild;
- overview-code-only change -> overview invalidation without detail invalidation;
- global gutter/render-contract change -> explicit full-build requirement;
- one real canonical incremental chunk -> byte-identical detail PNG to the established renderer path;
- content-addressed publication preserves unchanged object identities;
- periodic/explicit clean-build evidence remains available to detect a missing dependency edge.

A future change to an input dependency that is not represented in this contract is a correctness defect, not permission to add a global map hash back into every local fingerprint.
