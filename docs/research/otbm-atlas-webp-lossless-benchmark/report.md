VERDICT: WEBP_LOSSLESS_WIN

## Environment

- Local checkout commit at measurement time: `d77d78fba6fc50ada1706f9adb5fe63a1581c6f2` (the temporary remote branch was later deleted; this commit is recorded as historical context, not as the durable corpus identity)
- Durable atlas corpus identity from `build/full-map-atlas/manifest.json`: schema 2, atlas version 2, chunk size 128, map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`, assets SHA-256 `4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2`
- Corpus integrity: all 3,494 discovered detail paths matched the manifest path set and every original PNG SHA-256 matched its manifest checksum.
- OS: Windows-11-10.0.26200-SP0
- CPU: AMD64 Family 26 Model 68 Stepping 0, AuthenticAMD
- Python: 3.12.13; Pillow: 12.3.0; libwebp: 1.6.0
- WebP parameters: `lossless=True, method=6, exact=True`

## Corpus

- Discovered: 3494 canonical detail PNG chunks, 10996609082 bytes.
- Benchmarked: 240 chunks; floors [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15].
- Selection: deterministic union of 6 evenly distributed paths per floor, 16 per size quartile, then evenly distributed sorted paths; filled to exactly 240. Exact paths are in `results.csv`.

## Results

| Format | Total bytes | Saving vs PNG | Encode median/p95 | Decode median/p95 | RGBA exact |
|---|---:|---:|---:|---:|---|
| Existing PNG | 626957721 | baseline | n/a | 16.023/55.284 ms | source |
| WebP lossless | 318561438 | 49.19% | 588.882/4672.322 ms | 39.799/156.435 ms | PASS (240/240) |

Saving distribution: mean 62.18%, median 64.08%, p10 34.75%, p25 47.10%, p50 64.08%, p75 79.00%, p90 91.80%, p95 96.62%, best 98.88%, worst -1.92%.

## Per floor

| Floor | n | PNG bytes | WebP bytes | Saving |
|---:|---:|---:|---:|---:|
| 0 | 12 | 6390781 | 2043460 | 68.02% |
| 1 | 17 | 11671891 | 2863844 | 75.46% |
| 2 | 13 | 11016731 | 4241442 | 61.50% |
| 3 | 10 | 3796311 | 1457522 | 61.61% |
| 4 | 7 | 2592177 | 1194684 | 53.91% |
| 5 | 9 | 19544450 | 9624750 | 50.75% |
| 6 | 9 | 24609314 | 15088046 | 38.69% |
| 7 | 14 | 78888470 | 67849432 | 13.99% |
| 8 | 9 | 57269931 | 31011048 | 45.85% |
| 9 | 11 | 47416463 | 25195866 | 46.86% |
| 10 | 30 | 95468901 | 42990196 | 54.97% |
| 11 | 25 | 69283871 | 28323708 | 59.12% |
| 12 | 24 | 61221622 | 21650954 | 64.64% |
| 13 | 23 | 49169837 | 16198756 | 67.06% |
| 14 | 18 | 71462860 | 42959186 | 39.89% |
| 15 | 9 | 17154111 | 5868544 | 65.79% |

## Visual samples

The local benchmark generated `build/otbm-codec-benchmark/comparison.html` and 24 PNG/WebP pairs. Those derived binary images are intentionally not committed; their exact source paths and hashes remain recorded in `summary.json` and `results.csv`. Samples: build/full-map-atlas/tiles/z7/256_254.png, build/full-map-atlas/tiles/z8/258_253.png, build/full-map-atlas/tiles/z7/255_247.png, build/full-map-atlas/tiles/z14/262_257.png, build/full-map-atlas/tiles/z1/80_78.png, build/full-map-atlas/tiles/z10/80_80.png, build/full-map-atlas/tiles/z11/108_109.png, build/full-map-atlas/tiles/z12/94_93.png, build/full-map-atlas/tiles/z11/249_255.png, build/full-map-atlas/tiles/z6/255_250.png, build/full-map-atlas/tiles/z14/249_249.png, build/full-map-atlas/tiles/z12/257_254.png, build/full-map-atlas/tiles/z7/259_244.png, build/full-map-atlas/tiles/z7/262_249.png, build/full-map-atlas/tiles/z12/251_255.png, build/full-map-atlas/tiles/z12/262_249.png, build/full-map-atlas/tiles/z10/101_101.png, build/full-map-atlas/tiles/z10/94_94.png, build/full-map-atlas/tiles/z13/95_93.png, build/full-map-atlas/tiles/z14/95_93.png, build/full-map-atlas/tiles/z0/257_255.png, build/full-map-atlas/tiles/z1/257_246.png, build/full-map-atlas/tiles/z3/255_251.png, build/full-map-atlas/tiles/z4/258_248.png.

## Full-atlas impact

ESTIMATED from the measured aggregate ratio: 5587451091 WebP bytes, saving 5409157991 bytes (49.19%) from the exact current 10996609082 PNG bytes. This is not a full conversion measurement.

## Risks / caveats

This measures codec/storage and local Pillow/libwebp timings only, not browser performance. Implementation complexity was not assessed. Overview and creature/environment assets were excluded. The existing PNG files were used byte-for-byte; only representative copies were written.

## Validation and local-worker assessment

- `results.csv` contains exactly 240 deterministic detail-chunk records spanning Z0-Z15.
- CSV PNG and WebP totals agree exactly with `summary.json` and this report.
- All 240 accepted WebP files decoded to byte-for-byte identical RGBA data.
- The local comparison contained exactly 24 sample directories and every HTML image reference resolved.
- No tracked production or repository source file was modified by the benchmark.
- The complete detail PNG path set and all per-chunk SHA-256 values matched the atlas manifest before the corpus identity was recorded.
- Gemma 4 12B was invoked for workflow analysis and again for result summarization. Its responses were rejected by the local-worker evidence validator for missing or invalid claim/citation structure, including after an explicit `FACT`/`INFERENCE`/`UNKNOWN` retry. No Gemma-generated claim or implementation was accepted as benchmark evidence; Codex independently produced and verified the recorded measurements.

## Reproduction

Run `python tools/otbm_atlas/codec_benchmark.py` from a checkout that already contains `build/full-map-atlas/tiles/z*/*.png` and Pillow with lossless WebP support. The script never regenerates the atlas and writes derived artifacts only under `build/otbm-codec-benchmark/`.
