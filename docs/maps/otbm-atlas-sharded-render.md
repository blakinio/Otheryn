# OTBM Atlas sharded dirty-render execution

Status: implementation contract for `OTH-20260816-atlas-sharded-render`.

## Objective

Keep the already-merged spatial incremental contract while using all safe CPU available on one GitHub-hosted runner. The expensive monolithic OTBM preprocessing remains a single pass; only the resulting dirty chunks are divided into execution shards.

```text
canonical snapshot
      |
      v
one cached preprocessing / spatial spool
      |
      v
exact dirty-chunk plan
      |
      v
LPT shard planner (spool bytes as deterministic work weight)
      |
      +--> process worker 1: shard(s)
      +--> process worker 2: shard(s)
      +--> ...
      |
      v
fail-closed deterministic merge
      |
      v
one incremental-render.json
```

## Shard planner

`tools/otbm_atlas/incremental_shards.py` uses deterministic largest-processing-time scheduling. Dirty chunks are sorted by descending exact spool-file bytes, with canonical chunk order as a stable tie-break. Each chunk is assigned to the currently lightest shard, with shard index as the final tie-break.

Properties:

- every dirty chunk appears in exactly one shard;
- the same spool and dirty set always produce the same plan;
- requested shard count is capped to the dirty chunk count;
- byte weight is measured from the already-produced spatial spool, so planning does not rescan `world.otbm`;
- a missing spool file fails visibly rather than falling back to full-world work.

The normal runner uses `nproc` process workers and four shards per worker. Extra shards reduce tail imbalance while the worker count remains bounded by actual CPU availability.

## Execution and failure semantics

Every process renders through the already-certified `incremental_core.render_selected_chunks()` implementation into its own temporary shard directory. No pixel/render semantic code is duplicated in the sharding layer.

The parent process merges only after every worker future succeeds. Chunk files have disjoint logical paths; any unexpected non-identical collision is a hard failure. The final `incremental-render.json` is written only after complete coverage equals the planned dirty-chunk set.

Temporary shard directories and duplicate dependency/asset-state files are removed in `finally`. A failed shard therefore cannot produce a successful final render manifest.

## Security and redistribution boundary

This implementation intentionally parallelizes **within one GitHub-hosted job**. It does not upload generated map PNGs as GitHub Actions artifacts and does not pass generated Tibia-derived render data between public-repository jobs.

Cross-runner rendering would require a separately approved protected transport such as encrypted/private artifact storage. It is not introduced merely to gain more parallelism.

Synology remains the private deployment/storage target; it is not the ordinary render-compute target.

## Chunk size

This change does not alter the canonical 128x128 map-tile chunk size. The existing measured 32/64/128 benchmark remains the decision gate for any future chunk-size migration. Sharding and spatial chunk size are independent controls:

- chunk size controls invalidation granularity/browser object cardinality;
- shard count controls how already-dirty chunks are scheduled onto CPU workers.

## Validation requirements

Acceptance requires:

1. deterministic unit tests for complete/non-overlapping assignment and weighted balancing;
2. invalid worker/shard counts fail closed;
3. real canonical E2E renders at least two chunks through separate shards;
4. sharded detail PNGs are byte-identical to the established renderer path;
5. overview outputs exist for every sharded detail output;
6. the final manifest covers exactly the planned dirty set;
7. generated render corpus is removed before the GitHub-hosted validation job completes;
8. repository `CI`, `Required`, and applicable OTBM Atlas Incremental checks are green on the exact final head.
