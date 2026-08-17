# OTBM Atlas environment-animation parallel benchmark

Date: 2026-08-16
Task: `OTH-20260816-atlas-incremental-build-ci`
PR: `#426`
Benchmark run: `31962299340`
Benchmark head: `ca384f6d7b23babb7a09431f0fa75d9d1dc00048`

## Runner evidence

The real GitHub-hosted `ubuntu-latest` runner reported:

- `nproc=4`
- `MemTotal=16,766,414,848 bytes`
- Ubuntu 24.04.4

The environment exporter therefore caps ordinary CPU-heavy process parallelism to four workers on this runner class. Increasing process count beyond `nproc` is not the scaling strategy; additional full-build parallelism is obtained by using additional independent GitHub-hosted runners.

## Canonical Z7 benchmark

Four historically expensive canonical Z7 chunks were selected:

- `z7/249_242`
- `z7/254_242`
- `z7/257_242`
- `z7/263_242`

Combined benchmark result:

| Mode | Wall time | CPU utilization | Output |
| --- | ---: | ---: | ---: |
| 1 worker | 543.646 s (9m 03.6s) | ~99% | 54,459 instances / 85,687,091 bytes |
| 4 workers | 231.072 s (3m 51.1s) | ~385% | 54,459 instances / 85,687,091 bytes |

Measured speedup: **2.352718x**.

The sequential and four-worker outputs were compared by statistics and SHA-256 tree identity. Result: **byte equivalence PASS**.

The four-worker run retained deterministic per-chunk checkpoints and emitted heartbeats while long chunks were active. Peak process RSS stayed far below the 16 GB runner memory boundary and no swap was used.

## Production decision

Environment-animation export uses a bounded persistent worker pool:

- default maximum: 4 CPU-heavy workers;
- never exceed detected CPU count;
- each process keeps its `AssetRenderer` and local caches alive across chunks;
- work is dynamically scheduled with historically expensive chunks first;
- parent/coordinator alone performs final garbage collection and index finalization;
- long-running chunks emit heartbeat evidence;
- completed per-chunk checkpoints remain resumable.

Local environment fingerprints exclude monolithic map/asset SHA values and bind only the global environment semantic contract plus local spool, logical bounds, used appearance semantics and exact referenced sprite pixels.

## Full-world certification decision

A deliberate clean/full-world certification is rare and is now horizontally distributed as:

```text
Z0  -> runner 0  -> up to 4 workers
Z1  -> runner 1  -> up to 4 workers
...
Z7  -> runner 7  -> up to 4 workers
...
Z15 -> runner 15 -> up to 4 workers
```

The canonical full-world gate therefore has **16 independent floor jobs**, each on its own `ubuntu-latest` runner, with `max-parallel: 16`. If GitHub account concurrency is temporarily lower than 16, excess floor jobs queue without changing correctness.

Only compact verification evidence is uploaded. Generated map/animation corpora remain runner-local and are not published from the public repository.

Normal development remains incremental and does **not** launch 16 runners. The 16-floor path is reserved for deliberate clean certification/recovery.

## Recovery note

The earlier monolithic Z7 recovery run `31948409173` ended `cancelled` during `Build exactly Z7`; its assembly/deploy job was skipped. It must not be restarted using the same monolithic execution model. Future clean Z7 work uses the bounded parallel exporter and the one-floor-per-runner certification path.
