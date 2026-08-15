# OTBM Atlas codec benchmark

Basis: 24 real images from the user-provided Tibia asset corpus (8 sprite sheets + 16 minimap tiles). This is a codec-direction benchmark, not a final full-map-atlas chunk-size certification.

| Corpus | Format | Images | Total bytes | vs current PNG | Pixel exact | Max channel error | Encode total | Decode total |
|---|---|---:|---:|---:|---|---:|---:|---:|
| combined | png_current | 24 | 351,021 | +0.00% | YES | 0 | 0.863s | 0.057s |
| combined | png_optimized | 24 | 554,658 | +58.01% | YES | 0 | 1.431s | 0.092s |
| combined | webp_lossless | 24 | 200,886 | -42.77% | YES | 0 | 1.122s | 0.046s |
| combined | avif_q100_444 | 24 | 879,784 | +150.64% | NO | 2 | 2.410s | 0.297s |

## Corpus-specific WebP lossless result

- sprite_sheet: -45.55% vs current PNG; pixel exact=True
- minimap: -39.39% vs current PNG; pixel exact=True

## Limitation

The supplied 177 MB OTBM was also attempted with the repository-equivalent Python parser to produce actual 128x128 atlas chunks, but the full sequential scan exceeded the sandbox execution limit. Therefore no claim is made that the final ~6 GB full-map-atlas will shrink by exactly the same percentage. A final decision should be confirmed on generated atlas chunks in the normal repository/desktop environment.
