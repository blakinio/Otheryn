---
task_id: OTH-20260815-otbm-atlas-preview-codec-handover
status: completed
owner: none
branch: docs/otbm-atlas-preview-codec-handover
base_branch: main
created: 2026-08-15T13:54:00+02:00
updated: 2026-08-15T14:01:00+02:00
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "401"
ownership_released: true
---

# OTBM Atlas preview/storage/codec handover — archived

## Objective

Persist the owner decisions and verified evidence from the post-closeout Atlas preview/storage discussion without changing Atlas runtime, canonical source data, Synology, deployment or Oteryn Platform.

## Delivered documentation

- `docs/maps/otbm-atlas-preview-codec-handover-20260815.md`
- `docs/maps/otbm-atlas-real-chunk-codec-benchmark-prompt-20260815.md`
- `docs/maps/evidence/otbm-atlas-codec-direction-20260815/REPORT.md`
- `docs/maps/evidence/otbm-atlas-codec-direction-20260815/summary.csv`
- `docs/maps/evidence/otbm-atlas-codec-direction-20260815/per-image.csv`

The handover explicitly preserves the existing technical Atlas closeout rather than reopening it, records the local Synology/DSM reverse-proxy preview boundary, distinguishes the static full-build release/certification path from considered lazy rendering, preserves the bounded codec-direction measurements and their limitations, and requires a real generated-detail-chunk desktop benchmark before any image-format migration.

## Evidence classification

PROVEN:

- baseline `main` at task start: `014418f8db8b872bc292134322fc6da51f9a527a`;
- no active Atlas implementation task and no open Atlas PR existed at the baseline;
- current Atlas producer writes detailed map chunks as PNG and derives PNG overview imagery;
- the 24-image codec-direction corpus measured WebP lossless at `-42.770945328057294%` aggregate bytes versus the current Atlas-style PNG encoder with exact decoded RGBA on every tested WebP image;
- the tested optimized-PNG variant was larger on this corpus;
- the tested AVIF Q100 4:4:4 variant was not pixel-exact across the corpus;
- the attempt to produce actual final Atlas chunks from the supplied OTBM inside the ChatGPT sandbox exceeded the execution limit, so no final full-Atlas codec claim is made.

OWNER DECISION:

- current preview is Synology/Container Manager plus the existing DSM reverse-proxy pattern;
- no Oteryn Platform integration for this preview;
- no SSH tunnel;
- desktop full-build discussions use `--workers 8`;
- no WebP migration or lazy-render implementation is authorized until the real generated-chunk benchmark and visual A/B review are complete.

UNKNOWN / NOT VERIFIED:

- exact size breakdown of the owner-observed approximately 6 GB generated Atlas output;
- exact WebP-lossless saving on `build/full-map-atlas/tiles/**`;
- browser WebP decode/runtime behavior for the production viewer;
- final Synology hostname, reverse-proxy rule, deployment path or exposure boundary.

## Closeout

```yaml
closeout:
  implementation_complete: true
  feature_scope: documentation
  runtime_changed: false
  deployment_changed: false
  oteryn_platform_changed: false
  audit:
    result: PASS
    method: fresh exact-diff documentation audit in the same owner invocation
    material_findings_open: 0
  e2e:
    result: NOT_APPLICABLE
    reason: documentation/evidence preservation only; no runtime or deployment behavior changed
  pull_requests:
    lifecycle_pr: "#401"
    unresolved_review_threads_at_archive: 0
    terminal_state_evidence: verify from live GitHub after exact final-head checks and merge
  final_ci:
    evidence_rule: verify on exact final PR head after this archive commit; do not encode a prior-head PASS
  task_status: completed
  task_archived: true
  ownership_released: true
```

This archive record becomes authoritative on `main` only when PR #401 passes the required exact-head repository checks and reaches terminal merged state. GitHub PR/check state is the terminal evidence for that self-referential lifecycle step.
