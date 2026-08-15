# OTBM Atlas local preview, storage and codec handover — 2026-08-15

## Purpose

This note preserves the owner decisions, verified repository facts, codec experiment results, open questions and next validation step established after the final technical OTBM Atlas closeout.

It does **not** reopen or weaken `docs/maps/otbm-atlas-completion-audit-20260814.md`. The canonical Atlas runtime remains technically DONE/VERIFIED. This note is about local preview/product review and output-storage optimization.

## Live repository baseline

- repository: `blakinio/Otheryn`
- baseline `main`: `014418f8db8b872bc292134322fc6da51f9a527a`
- baseline commit: `docs(atlas): finalize OTBM atlas closeout (#400)`
- project lane: `otheryn-content`
- no active Atlas implementation task existed at this baseline
- no open Atlas PR existed at this baseline

Unrelated open PRs/tasks remain outside this note's ownership and must not be modified by Atlas preview/storage work.

## Existing canonical Atlas behavior

The current Atlas is a static precomputed viewer pipeline:

1. parse the canonical OTBM;
2. spool world records into bounded 128x128-map-tile chunk files;
3. render detailed canonical map imagery from pinned Tibia assets;
4. write each detailed map chunk as PNG under `tiles/z<z>/<chunkX>_<chunkY>.png`;
5. derive 4x and 8x overview PNG imagery from the detailed PNG pixels;
6. generate spatial JSON, search indexes, factual layers, creature sprites and animation resources;
7. let the browser request only the viewport and a small prefetch margin rather than the complete world.

The certified world contains exactly 3494 chunks across populated `Z=0..15`.

The browser therefore does not display `world.otbm` directly. It displays pre-rendered map image chunks plus generated factual/spatial data and runtime creature/environment overlays.

## What the large generated output represents

The owner observed an approximately 6 GB full generated Atlas output locally. That exact 6 GB value was **not independently measured in this session**, so it remains owner-observed rather than repository-certified evidence.

The large output is expected to be dominated by generated imagery rather than HTML/JS/CSS:

- detailed map chunk PNGs;
- 4x and 8x overview PNGs;
- creature static sprites and animation phase PNGs;
- environment animation phase PNGs;
- generated JSON indexes and factual/spatial shards;
- small static viewer HTML/JS files.

A full build is useful for two independent reasons:

- **static release artifact:** nginx or another static server can return already-rendered files with no OTBM rendering backend;
- **certification:** the repository already proved that every populated floor and all 3494 chunks can be rendered and verified from the pinned sources.

## Owner decision: local preview only

For the current preview phase:

- run the viewer on Synology/Container Manager;
- expose it through the existing Synology DSM reverse-proxy pattern;
- do **not** integrate with Oteryn Platform;
- do **not** add public Oteryn Platform routing;
- do **not** require an SSH tunnel;
- keep this as a temporary/local preview for owner visual and UX review.

Exact hostname, DSM reverse-proxy rule, LAN/public exposure boundary and deployment path are not fixed by this document and must be verified from the live Synology configuration before any deployment mutation.

## Build-location discussion

The desktop is a better place for heavy full-world generation than the Synology NAS. The current documented full build supports parallel render workers, and the owner selected `--workers 8` for desktop generation.

Canonical example:

```text
python -m tools.otbm_atlas.atlas \
  vendor/map-analysis/crystalserver/data-global/world/world.otbm \
  vendor/map-analysis/tibia-client/15.25.bd5a04/assets \
  build/full-map-atlas \
  --workers 8
```

The previous simple deployment concept was:

```text
desktop full build -> verify -> copy generated static output to Synology -> read-only nginx -> DSM reverse proxy -> browser
```

However, copying an approximately multi-gigabyte full artifact motivated the storage/codec investigation below. No final deployment implementation has been accepted yet.

## Large single image versus chunks

A single high-resolution image per floor, cropped only by browser canvas/CSS, was considered and rejected as the default direction.

Reason:

- visually cropping an image does not make arbitrary geographic regions independently addressable over HTTP;
- the browser would operate on a much larger resource even when only a small viewport is visible;
- current chunking allows bounded viewport requests, cache eviction and floor-local loading;
- fewer files are not equivalent to less network transfer or lower decoded memory.

The existing 128x128 map-chunk architecture should therefore be preserved unless a separate measured experiment proves a better independently addressable representation.

## On-demand/lazy rendering option

Server-side lazy rendering was considered as an optional preview architecture:

```text
browser requests detail chunk
-> server checks persistent cache
-> if cached: return it
-> if missing: render from preprocessed/spooled canonical data
-> atomically cache result
-> return it
```

Important constraints if this is ever implemented:

- never send the complete OTBM or asset corpus to the browser;
- do not sequentially rescan the ~19-million-tile world for every HTTP request;
- use bounded preprocessing/index/spool data;
- deduplicate concurrent requests for the same chunk;
- use atomic writes and explicit failure/timeout behavior;
- preserve static full-build/release certification as an independent supported path.

**Current decision:** do not implement lazy rendering merely to solve storage/copy size before the real generated-chunk codec benchmark is complete. A simpler static architecture is preferable if lossless format optimization removes enough storage cost.

## Current PNG implementation fact

`tools/otbm_atlas/assets.py::encode_png()` writes deterministic 8-bit RGBA PNGs using:

- filter byte `0` for every row;
- zlib compression level `9`.

`tools/otbm_atlas/overview.py` also explicitly consumes/produces PNG data for overview generation.

Therefore changing the map-chunk format is a pipeline/runtime contract change, not merely renaming an extension. It must update producer, manifest/viewer consumption, verification and tests together.

## Codec-direction benchmark performed in ChatGPT sandbox

A bounded codec-direction experiment was performed before asking the desktop worker to touch the real generated atlas.

### Inputs

User-supplied files available to the experiment:

- `otservbr(4).otbm`
  - bytes: `184776037`
  - SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`
- `assets(1).zip`
  - bytes: `416822274`
  - SHA-256: `01c45146e2fcec3f4087844e0cbc1817fb1d60b310a35ac5d88c07aab6f73d1a`

Codec environment:

- Pillow `12.3.0`
- WebP support: available
- AVIF support: available
- zlib support: available

### Corpus

The completed codec test used 24 real images from the supplied Tibia asset corpus:

- 8 decoded 384x384 Tibia sprite sheets;
- 16 real minimap tiles.

This was deliberately classified as a **codec-direction benchmark**, not a final `build/full-map-atlas/tiles/**` benchmark.

An attempt was also made to scan the supplied 177 MiB-class OTBM with the repository-equivalent Python parser to generate actual 128x128 atlas chunks. The sequential scan exceeded the execution limit of the ChatGPT sandbox. No final-chunk result was fabricated from that failed attempt.

### Results

| Corpus | Format | Images | Total bytes | vs current PNG | Pixel exact | Max channel error | Encode total | Decode total |
|---|---|---:|---:|---:|---|---:|---:|---:|
| combined | current PNG | 24 | 351021 | baseline | YES | 0 | 0.863 s | 0.057 s |
| combined | optimized PNG | 24 | 554658 | +58.01% | YES | 0 | 1.431 s | 0.092 s |
| combined | WebP lossless | 24 | 200886 | -42.77% | YES | 0 | 1.122 s | 0.046 s |
| combined | AVIF Q100 4:4:4 | 24 | 879784 | +150.64% | NO | 2 | 2.410 s | 0.297 s |

WebP lossless by sub-corpus:

- sprite sheets: `-45.55%`, decoded RGBA exact;
- minimap tiles: `-39.39%`, decoded RGBA exact.

### Interpretation

**PROVEN for this 24-image corpus:**

- WebP lossless preserved decoded RGBA exactly for every tested image;
- WebP lossless reduced total bytes by `42.770945328057294%` against the current Atlas-style PNG encoder on this corpus;
- Pillow "optimized PNG" was larger than the current deterministic PNG on this corpus;
- AVIF Q100 4:4:4 was neither pixel-exact nor storage-competitive in this test and is not accepted as canonical-safe from this evidence.

**NOT PROVEN:**

- that the complete generated Atlas will shrink by 42.77%;
- that an owner-observed ~6 GB output will become any particular exact size;
- browser decode/runtime performance;
- final WebP implementation complexity;
- overview, creature-animation and environment-animation storage gains.

Any statement such as "6 GB becomes ~3.4 GB" is only an illustrative extrapolation from the sample and must not be treated as release evidence.

## Durable benchmark evidence

The compact aggregate benchmark report and raw per-image measurements are stored beside this handover under:

- `docs/maps/evidence/otbm-atlas-codec-direction-20260815/REPORT.md`
- `docs/maps/evidence/otbm-atlas-codec-direction-20260815/summary.csv`
- `docs/maps/evidence/otbm-atlas-codec-direction-20260815/per-image.csv`

They preserve the measured values; they do not upgrade the experiment into full-map certification.

## Required next validation: real generated chunk benchmark

Before changing production Atlas formats, run a local read-only benchmark against existing generated files under the real desktop checkout, expected approximately at:

`build/full-map-atlas/tiles/z*/<chunkX>_<chunkY>.png`

Requirements:

1. do not change Atlas source code;
2. do not commit or push benchmark artifacts;
3. do not regenerate the full Atlas if the output already exists;
4. benchmark at least 200 deterministic real detail chunks, preferably all available chunks when cheap;
5. use original generated PNG bytes as the baseline;
6. encode WebP in genuine lossless mode;
7. decode it and require byte-for-byte RGBA equality for every accepted sample;
8. measure total bytes, distribution/percentiles, encode time and PNG/WebP decode time;
9. calculate exact current total detail-PNG storage if all 3494 files exist;
10. produce at least 24 representative original-PNG/WebP pairs and a local `comparison.html` for owner visual inspection;
11. keep detail-map results separate from overview/creature/environment resources;
12. return measurements to the owner before any format migration is authorized.

The ready-to-run worker instruction is recorded in:

`docs/maps/otbm-atlas-real-chunk-codec-benchmark-prompt-20260815.md`

## Decision gate after the desktop benchmark

No format migration is authorized by this note.

The owner should review:

- exact detail-map total PNG size;
- exact or representative WebP-lossless saving;
- RGBA exactness;
- encode/decode cost;
- the 24 visual A/B samples.

Only then choose among:

- keep current PNG;
- migrate detail chunks to WebP lossless;
- optimize only selected asset classes;
- investigate lazy rendering for reasons beyond storage;
- perform a separate browser/runtime benchmark before final migration.

## Source-of-truth rule

Future workers must verify live `main`, task/PR ownership and the actual generated local Atlas before acting. This document records the state and decisions reached on 2026-08-15; it is not authority to modify Synology, deployment, Oteryn Platform or Atlas runtime without a new explicitly authorized task.
