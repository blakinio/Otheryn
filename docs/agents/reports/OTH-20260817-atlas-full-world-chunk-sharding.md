# OTH-20260817 — Atlas full-world chunk-centric certification

## Decision

The clean/recovery full-world gate is chunk-centric rather than floor-centric.

The canonical world contains **3,494 populated Atlas chunks** at chunk size 128 across Z0..Z15. A planner performs one canonical full spool, measures exact spool bytes per chunk, and deterministically partitions the complete set into **32 LPT-balanced assignments**. Each assignment runs on one standard `ubuntu-latest` GitHub runner with **four bounded worker processes**.

Maximum horizontal compute when account concurrency permits is therefore 32 runner shards × 4 workers = up to 128 worker processes, without CPU oversubscription inside a standard 4-vCPU hosted runner. GitHub account concurrency may queue shards; queueing changes wall-clock time, not the certification contract.

## Why floors are no longer the execution unit

The previous gate bound one runner to each Z floor. Z7 contains 346 chunks and the exact-head run `31972862621` reached the workflow's 180-minute job timeout while its environment exporter was healthy and still progressing (212/346 completed). The failure was a scheduling-granularity problem, not a renderer correctness failure.

A chunk is already the local rendering/invalidation unit in the production Atlas pipeline. Keeping floor as execution ownership created an artificial straggler. Floor remains spatial metadata and an aggregate certification dimension only.

## Planner contract

`tools/otbm_atlas/world_shards.py` owns the clean certification plan.

1. Parse the canonical OTBM into a temporary planner-local spool.
2. Enumerate every populated `zN/x_y` chunk.
3. Weight each chunk by exact spool bytes.
4. Partition with deterministic largest-processing-time balancing.
5. Emit one compact plan with exact canonical source identity, 32 assignments, per-assignment inventory/digest, full coverage digest, floor counts and world-plan digest.

The full generated spool is deleted before the planner job exits. Only the compact plan is uploaded between GitHub jobs.

## Runner contract

Each shard runner downloads the compact plan, parses the canonical OTBM once, and materializes only its assigned chunks into its private spool. For that assignment it performs static detail render, overview and low-overview render, environment-animation export, independent shard verification and compact evidence emission.

Both static rendering and environment animation remain capped at four worker processes. Generated tiles, overviews, animation frames, checkpoints and other Tibia-derived corpora never leave the runner.

## Global product-data boundary

Source-driven global phases such as spawns, houses, factual layers, search/spatial metadata and viewer assets are deliberately **not repeated 32 times**. Their exact-head product-data tests remain authoritative. The chunk-shard gate certifies the expensive full-clean static/environment corpus; deployment preflight remains an assembled complete-world boundary.

## Aggregate acceptance

The final job accepts the world only when shard indices 0..31 occur exactly once; producer SHA is identical; 3,494 chunk keys occur exactly once globally; floor counts are Z0=87, Z1=120, Z2=150, Z3=183, Z4=213, Z5=240, Z6=251, Z7=346, Z8=285, Z9=286, Z10=265, Z11=238, Z12=234, Z13=201, Z14=210, Z15=185; all reports share one world-plan digest and source identity; canonical map SHA-256 is `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`; chunk size is 128 and Atlas version is 3; every runner uses four bounded workers; independent static/environment verification is PASS; `missingSprites` is empty; environment completed chunks equals assigned chunks; and no generated map/animation corpus is published as a workflow artifact.

## Compatibility

The existing manual label `ci:full-world-16` remains accepted so the current PR gate can be re-triggered without changing repository label state. `ci:full-world-32` is also accepted as the semantic name for the new architecture.

The legacy workflow path `.github/workflows/otbm-atlas-full-world-16.yml` is retained for this integration PR to avoid unnecessary workflow-path churn; its workflow name and execution model are now explicitly 32-shard chunk-centric.
