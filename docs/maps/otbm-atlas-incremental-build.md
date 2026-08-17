# OTBM Atlas incremental build and publication contract

Status: production integration under final exact-head validation for `OTH-20260816-atlas-incremental-build-ci`.

## Objective

An ordinary Atlas change must never imply a canonical full-world rebuild merely because one monolithic OTBM file or the complete asset tree received a new SHA-256. The normal path is:

```text
immutable source snapshot
        |
        v
persistent spatial spool / local hashes
        |
        v
chunk dependency + reverse-dependency index
        |
        v
change-impact plan
        |
        +--> changed detail chunks only
        +--> changed overview chunks only
        +--> changed environment-animation chunks only
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

The former `tools/otbm_atlas/atlas.py` cache fingerprint included the SHA-256 of the complete `world.otbm`, the SHA-256 of the complete appearance-asset tree and the local spool SHA. Consequently a change anywhere in the monolithic map or asset tree could invalidate every detail chunk even when almost all local pixels were unchanged. Its global source-state transition also recreated the complete spool.

The production-integrated incremental path deliberately does not put those global source hashes into a detail or environment-animation chunk fingerprint.

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

## Production spatial state

`tools/otbm_atlas/production_incremental.py` is the local production authority used by `tools/otbm_atlas/atlas.py`. The PR planner remains a base-vs-head GitHub CI tool; the production builder instead compares the current canonical snapshot with the last successfully committed local state under:

```text
<atlas-output>/.incremental-state/production-render-state.json
```

The production state records per-chunk render fingerprints and per-chunk spool SHA-256 values. The spool itself remains under `<atlas-output>/.spool`.

When the canonical map SHA is unchanged, production validates the persisted spool bytes against the state before reusing them. A corrupted shard is not trusted from metadata: the canonical OTBM is reparsed and the stable spool is reconciled. If canonical bytes are unchanged, repairing the spool does not itself dirty the detail image.

When the monolithic OTBM changes, one sequential parse may still be required because OTBM is the source container. Candidate bytes are then reconciled per spatial shard:

- changed/new chunk bytes replace only their matching stable shard;
- byte-identical shards remain untouched;
- removed chunks are deleted explicitly;
- factual `tile-facts/*.jsonl` shards are reconciled independently;
- `facts.json` is replaced only when its bytes changed.

A monolithic source read is therefore distinct from a full-world render. Ordinary source edits may require reading the source once but render only locally dirty chunks.

## Legacy publication adoption

The first production-integrated run can adopt the existing certified Atlas image corpus without rerendering it when:

- no production incremental state exists yet;
- existing manifest source identity exactly matches the canonical map/assets/chunk contract;
- expected detail PNG/report files exist.

That migration run binds the existing spool to per-chunk SHA-256 state. Later runs require byte-verified state and no longer rely on unbound legacy reuse.

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

The sprite selection calculation mirrors the renderer's position patterns, stack count, hangable hook direction, fluid subtype and declared default animation phase. Container descendants remain part of canonical spool/report data but are not promoted to visible render dependencies when the renderer itself does not draw them.

## Asset invalidation

Asset state is decomposed into:

- semantic digest per object appearance;
- SHA-256 and sprite-ID range per sprite sheet for detail-render dependency impact;
- one global gutter profile containing maximum sprite dimensions and global shift extrema.

An appearance change invalidates only chunks in that appearance's reverse index. A sprite-sheet byte change invalidates only chunks whose selected sprite IDs fall in that sheet's old or new ID range.

The gutter profile is intentionally global today because the certified renderer computes conservative chunk crop bounds from global sprite dimensions and appearance shift extrema. If that profile changes, the rendering contract truthfully requires all detail chunks to be considered dirty. This is a machine-readable `GLOBAL_GUTTER_PROFILE_CHANGED` full-build reason rather than a hidden cache miss.

Current chunk rendering draws only tiles sourced by that chunk into its own conservative gutter. It does not draw neighboring source chunks into the image, so a local tile edit does not require speculative neighbor invalidation. If a future renderer introduces cross-chunk source composition, the render-core version and invalidation contract must change together.

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

Planner/publication refactors do not change the render-contract digest. Pixel-semantics changes in the incremental core require an explicit `RENDER_CORE_VERSION` bump; changes in renderer semantics are detected by the render-contract guard.

## Production detail execution

`tools/otbm_atlas/atlas.py` now asks the production planner for exact `dirtyDetailChunks`, `reusedDetailChunks` and `deletedDetailChunks`.

Only dirty detail chunks become renderer jobs. Removed chunks delete only their detail/overview outputs. Stable detail chunks are reused directly; ordinary builds do not re-hash the complete ~11 GB detail corpus merely to prove a cache hit.

Parallel dirty rendering preserves the existing bounded worker behavior. The production renderer uses the same guarded incremental-core spool decoder and crop-bounds semantics as the change-impact path.

The resulting `data/statistics.json` includes `incrementalBuild` evidence with dirty/reused/deleted counts, full-build reasons and spool reconciliation/integrity state.

## Independent overview invalidation

4x and 8x overview images remain deterministic derivatives of the detail PNG. A changed detail chunk invalidates its own overview derivatives. Existing overview fingerprinting means an unchanged detail checksum reuses the overview. A global overview semantic change remains a separate invalidation domain and must not imply a detail rerender.

## Environment-animation local invalidation

The resumable environment exporter is also local. `tools/otbm_atlas/environment_incremental.py` separates the genuinely global environment contract from chunk dependencies.

The global contract contains only:

- environment export contract version;
- Atlas manifest schema/chunk size;
- animation zoom;
- global overlap-safety radius.

It explicitly excludes complete-map SHA, complete-asset SHA and the full manifest chunk inventory.

Each environment-animation checkpoint fingerprint contains:

```text
global environment contract
local spool SHA-256
logical chunk bounds
appearance semantics actually used by that chunk
SHA-256 of exact decoded sprite pixels referenced by those appearances
```

A sprite sheet is only a storage container here: changing an unrelated sprite in the same sheet does not invalidate a chunk that never references that sprite. Tests prove that changing a sprite used only by chunk B leaves chunk A's checkpoint fingerprint unchanged.

Checkpoint reuse also verifies referenced output bytes. A deleted Atlas chunk removes its stale environment checkpoint/shard, and unreferenced environment payload files are garbage-collected only after surviving checkpoint references are known.

`EXPORT_VERSION=3` is the one-time contract transition from the earlier global-manifest fingerprint to this local dependency model.

## Data-domain classification

The PR impact plan classifies changed paths independently from map rendering. Current machine-readable domains include:

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

A spawn XML or viewer-only change therefore does not become a reason to render all map images. Existing specialized generators remain responsible for their own data outputs unless and until they are migrated behind equivalent local fingerprints.

## Full-build guard

Every PR impact plan declares:

```json
{
  "fullBuildRequired": false,
  "fullBuildReasons": []
}
```

When a global render semantic really changes, the planner sets `fullBuildRequired: true` and records exact reasons. Normal CI fails closed rather than silently falling back to the complete world.

The production `atlas.py` path follows the same policy. A detail-wide semantic transition raises an error with the exact reason. The only production override is explicit:

```bash
python3 -m tools.otbm_atlas.atlas ... --allow-full-build
```

This flag is for a consciously authorized recovery/semantic transition, never an automatic response to a changed source SHA.

The repository retains separately gated full-world validation/recovery paths. Clean execution remains the equivalence authority when it is genuinely required.

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

The default remains **128**. `tools/otbm_atlas/chunk_benchmark.py` measures the same bounded canonical region at 32, 64 and 128 and reports chunk cardinality, populated tiles, nominal invalidation area, encoded bytes, render operations and render time.

Smaller chunks improve invalidation locality but increase file/request/manifest cardinality. The GitHub benchmark is implemented and verified; this task does not change the production chunk contract without browser/deployment evidence demonstrating that the tradeoff is superior.

Representative command:

```bash
python3 -m tools.otbm_atlas.chunk_benchmark \
  --bounds 32280 32440 32155 32305 7 \
  --sizes 32 64 128 \
  --output /tmp/atlas-chunk-benchmark.json
```

## GitHub-hosted execution

`.github/workflows/otbm-atlas-incremental.yml` uses only GitHub-hosted `ubuntu-latest` runners and does not use Synology runners. It provides:

1. focused syntax/unit validation;
2. exact base-vs-head canonical impact planning;
3. fail-closed full-build guard;
4. proportional non-render validation;
5. exact dirty-detail execution in bounded process shards;
6. representative byte/pixel equivalence when render-sensitive paths change;
7. bounded 32/64/128 benchmark when its relevant contract changes.

Generated Tibia/CipSoft-derived render images are temporary validation data and are deleted before job completion. The workflow does not upload the generated map corpus as a public artifact.

Documentation/task-only changes do not trigger the incremental workflow. Superseded runs are cancelled so obsolete PR generations do not consume runner time unnecessarily.

## GitHub Pages / hosting decision

GitHub Pages is **not enabled for the current full Atlas**. The measured current detail corpus alone is about 11 GB, before the rest of the product, and this task does not authorize public redistribution of generated third-party-derived render assets.

This does not block moving build/test CPU to GitHub-hosted Actions. Hosting/storage is intentionally separated from CI. Synology may remain a private runtime/storage destination; ordinary Atlas build/test CPU is no longer required to run there.

## Required equivalence discipline

Incremental correctness is not inferred from cache hits. Validation covers:

- identical committed production state -> zero dirty detail chunks;
- exact legacy certified publication -> adoption without detail rerender plus binding of spool hashes;
- one changed spatial fingerprint -> only that detail chunk is dirty;
- canonical-map candidate reconciliation -> unchanged spatial shards remain byte-identical;
- corrupted persisted spool -> rebuild/reconcile from canonical OTBM rather than trusting corrupt cache;
- changed used appearance/sprite -> only reverse-dependent chunks are dirty;
- unrelated sprite -> unrelated environment checkpoint remains reusable;
- monolithic map/assets SHA change alone -> unchanged environment checkpoint remains reusable;
- deleted environment chunk -> stale checkpoint/shard/payload cleanup;
- global gutter/render-contract change -> explicit full-build requirement;
- real bounded canonical incremental rendering -> established renderer/equivalence gates;
- content-addressed publication preserves unchanged object identities;
- explicit clean-build evidence remains available to detect a missing dependency edge.

A future change to an input dependency that is not represented in this contract is a correctness defect, not permission to add a global map hash back into every local fingerprint.
