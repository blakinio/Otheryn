VERDICT: WEBP_LOSSLESS_WIN

## Environment

- Repository head: `a4878325b892b2044f514d27a1a3104e5ce843f7`
- OS: Windows-11-10.0.26200-SP0
- CPU: AMD64 Family 26 Model 68 Stepping 0, AuthenticAMD
- Python: 3.12.13; Pillow: 12.3.0; libwebp: 1.6.0
- WebP parameters: `lossless=True, method=6, exact=True`

## Corpus

- Discovered: 3494 canonical detail PNG chunks, 10995096999 bytes.
- Benchmarked: 240 chunks; floors [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15].
- Selection: deterministic union of 6 evenly distributed paths per floor, 16 per size quartile, then evenly distributed sorted paths; filled to exactly 240 Exact paths are in `results.csv`.

## Results

| Format | Total bytes | Saving vs PNG | Encode median/p95 | Decode median/p95 | RGBA exact |
|---|---:|---:|---:|---:|---|
| Existing PNG | 629930622 | baseline | n/a | 18.056/59.456 ms | source |
| WebP lossless | 320113728 | 49.18% | 734.989/5718.798 ms | 46.609/179.995 ms | PASS (240/240) |

Saving distribution: mean 62.20%, median 63.85%, p10 34.73%, p25 46.96%, p50 63.85%, p75 79.00%, p90 91.80%, p95 96.62%, best 98.88%, worst -1.92%.

## Per floor

| Floor | n | PNG bytes | WebP bytes | Saving |
|---:|---:|---:|---:|---:|
| 0 | 12 | 6390575 | 2044432 | 68.01% |
| 1 | 17 | 11671453 | 2862500 | 75.47% |
| 2 | 13 | 11012303 | 4238520 | 61.51% |
| 3 | 10 | 3796436 | 1456254 | 61.64% |
| 4 | 8 | 2940927 | 1338272 | 54.49% |
| 5 | 6 | 8637911 | 4534732 | 47.50% |
| 6 | 9 | 24346202 | 14672352 | 39.73% |
| 7 | 15 | 88925289 | 72963686 | 17.95% |
| 8 | 8 | 49653875 | 27509704 | 44.60% |
| 9 | 14 | 57215542 | 29692180 | 48.10% |
| 10 | 31 | 101228253 | 45921198 | 54.64% |
| 11 | 24 | 68656100 | 28161162 | 58.98% |
| 12 | 24 | 60707867 | 21357270 | 64.82% |
| 13 | 23 | 49165953 | 16193356 | 67.06% |
| 14 | 19 | 74592731 | 43391982 | 41.83% |
| 15 | 7 | 10989205 | 3776128 | 65.64% |

## Visual samples

Open `build/otbm-codec-benchmark/comparison.html`. Samples: build/full-map-atlas/tiles/z7/256_254.png, build/full-map-atlas/tiles/z8/258_253.png, build/full-map-atlas/tiles/z7/255_247.png, build/full-map-atlas/tiles/z14/262_257.png, build/full-map-atlas/tiles/z1/80_78.png, build/full-map-atlas/tiles/z10/80_80.png, build/full-map-atlas/tiles/z11/108_109.png, build/full-map-atlas/tiles/z12/94_93.png, build/full-map-atlas/tiles/z11/249_255.png, build/full-map-atlas/tiles/z6/255_250.png, build/full-map-atlas/tiles/z14/249_249.png, build/full-map-atlas/tiles/z12/257_254.png, build/full-map-atlas/tiles/z7/259_244.png, build/full-map-atlas/tiles/z7/262_249.png, build/full-map-atlas/tiles/z12/251_255.png, build/full-map-atlas/tiles/z12/262_249.png, build/full-map-atlas/tiles/z10/101_101.png, build/full-map-atlas/tiles/z10/94_94.png, build/full-map-atlas/tiles/z13/95_93.png, build/full-map-atlas/tiles/z14/95_93.png, build/full-map-atlas/tiles/z0/257_255.png, build/full-map-atlas/tiles/z1/257_246.png, build/full-map-atlas/tiles/z3/255_251.png, build/full-map-atlas/tiles/z4/261_255.png.

## Full-atlas impact

ESTIMATED from the measured aggregate ratio: 5587411323 WebP bytes, saving 5407685676 bytes (49.18%) from the exact current 10995096999 PNG bytes. This is not a full conversion measurement.

## Risks / caveats

This measures codec/storage and local Pillow/libwebp timings only, not browser performance. Implementation complexity was not assessed. Overview and creature/environment assets were excluded. The existing PNG files were used byte-for-byte; only representative copies were written.
