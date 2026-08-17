---
task_id: OTH-20260816-atlas-incremental-build-ci
status: completed
owner: none
branch: perf/OTH-20260816-atlas-production-incremental-entry
base_branch: main
created: "2026-08-16T10:04:00+02:00"
completed: "2026-08-17T09:47:28+02:00"
updated: "2026-08-17T09:49:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "426"
ownership_released: true
---

# OTBM Atlas incremental build and GitHub CI — completed

The production OTBM Atlas entry point is now incremental and fail-closed. Ordinary `tools/otbm_atlas/atlas.py` runs reuse byte-verified local state and render only the local dependency closure that changed. Full detail rebuilds require explicit `--allow-full-build` authorization.

## Delivered

- spatial per-chunk map reconciliation and per-chunk spool hashes;
- local appearance/sprite dependency fingerprints instead of monolithic map/asset invalidation;
- byte-verified legacy publication adoption and corruption repair from canonical OTBM source;
- local detail and overview invalidation with persistent production render state;
- local environment-animation checkpoints bound to spool bytes, logical bounds, used appearance semantics and exact referenced sprite pixels;
- bounded four-worker environment export with longest-first scheduling and coordinator-only cleanup;
- incremental spatial/factual/tile-inspector production phases;
- explicit fail-closed global render transitions;
- deterministic 32 weighted-chunk full-world certification on GitHub-hosted runners;
- canonical world certification for exactly 3,494 populated chunks across Z0..Z15 with zero missing sprites and complete environment checkpoint coverage.

## Terminal verification

Implementation head:

`f063853515abf59747df3467991d7a7100715e9f`

Implementation PR:

`blakinio/Otheryn#426`

Merge commit now on `main`:

`0c97d905dbff794499a01072904e7eabc4c2dafd`

Exact-head validation:

- `OTBM Atlas Full World 32 Chunk Shards` run `31998905477` — SUCCESS;
- final aggregate `Certify exact 3494-chunk full world` — SUCCESS;
- `CI` run `32004607489` — SUCCESS;
- `Required` run `32004607192`, attempt 2 — SUCCESS;
- `OTBM Atlas Incremental` run `31998866904` — SUCCESS;
- `OTBM Atlas Tests` run `31998866901` — SUCCESS;
- `OTBM Environment Animation E2E` run `31998866898` — SUCCESS;
- `OTBM Atlas Factual Layers` run `31998866914` — SUCCESS;
- `OTBM Atlas Factual Layer Audit` run `31998866903` — SUCCESS;
- `OTBM Creature Animation E2E` run `31998866941` — SUCCESS;
- `OTBM Creature Animation Audit` run `31998866893` — SUCCESS;
- `OTBM Canonical Creature Showcase` run `31998866897` — SUCCESS.

The first Ready-state `Required` attempt timed out after its fixed 35-minute polling window while the same-head `CI` run was still in progress. The CI subsequently completed successfully without source changes. Only the failed `Required` job was rerun; attempt 2 observed the already-successful exact-head CI and passed. This was a gate-timing failure, not a build/test failure.

## Fresh closeout audit

- complete changed-file inventory for PR #426 reviewed;
- critical production entry, render-state, environment invalidation, sharding, verification and CI exact-head paths inspected;
- PR comments: 0;
- submitted reviews: 0;
- unresolved review threads: 0;
- drift from the original PR base to pre-merge `main` was documentation-only and did not overlap Atlas implementation paths;
- no material audit findings remained before merge;
- post-merge `main` was re-read and contains the incremental production entry point and explicit full-build guard;
- implementation branch was automatically deleted after merge.

## Related PR lifecycle

- #418 — merged — resumable environment-animation exporter;
- #419 — merged — product/tile-inspector integration;
- #421 — merged — spatial incremental pipeline;
- #424 — merged — sharded dirty rendering;
- #426 — merged — final production-entry integration.

No related implementation PR remains unintentionally open.

## Closeout

```yaml
closeout:
  implementation_complete: true
  complete_feature_or_declared_partial: true
  outcome_verified: true
  audit:
    result: PASS
    validator: fresh-chat-closeout-20260817
    findings_open_material: 0
  e2e:
    result: PASS
    journeys:
      - incremental-no-change-reuse
      - local-dirty-dependency-closure
      - local-environment-invalidation
      - full-world-3494-chunk-certification
  final_ci:
    head: f063853515abf59747df3467991d7a7100715e9f
    result: PASS
    ci_run: 32004607489
    required_run: 32004607192
    required_attempt: 2
    full_world_run: 31998905477
  pull_requests:
    open_related_prs: 0
    unresolved_review_threads: 0
    terminal_prs:
      - "blakinio/Otheryn#418 merged"
      - "blakinio/Otheryn#419 merged"
      - "blakinio/Otheryn#421 merged"
      - "blakinio/Otheryn#424 merged"
      - "blakinio/Otheryn#426 merged"
  post_merge:
    main: 0c97d905dbff794499a01072904e7eabc4c2dafd
    production_entry_verified: true
    implementation_branch_deleted: true
  task_archived_or_terminal: true
  ownership_released: true
  stale_branches_reconciled: true
```

## Final state

All acceptance criteria for the bounded Atlas incremental-build/CI task are satisfied. Full Atlas hosting/publication remains a separate deployment/storage decision; this task does not enable GitHub Pages or publish the generated render corpus.
