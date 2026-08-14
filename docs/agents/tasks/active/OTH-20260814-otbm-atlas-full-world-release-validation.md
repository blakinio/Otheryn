---
task_id: OTH-20260814-otbm-atlas-full-world-release-validation
status: ready
owner: none
created: 2026-08-14
updated: 2026-08-14T16:07:00+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: true
modules_touched:
  - otbm-atlas
---

# OTBM atlas full-world release validation

This task owns the expensive complete-world certification intentionally deferred from `OTH-20260813-full-otbm-atlas` by explicit owner decision.

## Trigger

Run `.github/workflows/otbm-atlas-full-world-release.yml` manually only when a release/certification of the complete generated atlas is required. It is not a normal PR synchronize-time development gate.

## Required evidence

The workflow must:

- run one independent job per canonical floor Z0..15;
- build from `vendor/map-analysis/crystalserver/data-global/world/world.otbm` and the pinned Tibia 15.25 vendored assets;
- independently verify every floor;
- require `verification.ok == true` and `missingSprites == {}` for every floor;
- aggregate exactly 16 floor evidence artifacts;
- require exactly 3494 chunks across Z0..15;
- require identical canonical source fingerprints across all floors;
- require map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`;
- keep this certification separate from routine atlas implementation CI.

## Rationale

The previous four-floor-per-job gate repeatedly exceeded GitHub Actions 90- and 120-minute limits. Those cancellations occurred inside `build_atlas()` and did not report a functional verifier/renderer failure. Per-floor isolation bounds each job independently and prevents one expensive floor group from invalidating all remaining evidence.

```yaml
checkpoint_version: 1
status: ready
phase: deferred-release-validation
source_task: OTH-20260813-full-otbm-atlas
workflow: .github/workflows/otbm-atlas-full-world-release.yml
merge_blocking_for_pr_381: false
next_action: run manually when full-world release certification is required
```
