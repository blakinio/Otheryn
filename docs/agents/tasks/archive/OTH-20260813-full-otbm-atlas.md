---
task_id: OTH-20260813-full-otbm-atlas
status: completed
owner: none
created: 2026-08-13
completed: 2026-08-14T16:07:00+02:00
updated: 2026-08-14T16:07:00+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: true
modules_touched:
  - otbm-atlas
---

# Full OTBM atlas implementation — completed

PR #381 completes the repository-owned chunked OTBM atlas implementation. The viewer provides bounded viewport/chunk loading, canonical detailed sprite rendering, `Auto | Detailed | Performance`, raw OTBM X/Y/Z state, URL/local persistence, factual overlays, conservative UNKNOWN handling, canonical NPC outfits/addons, search/details navigation, and bounded cyclic environment animation.

## Verified implementation acceptance

The final product implementation passed atlas unit/runtime tests, canonical Thais scan/render, real Chromium Thais E2E, environment-animation E2E, repository CI, Required and autofix.ci. The final Chromium fixture was corrected to provide the required `data/environment-animations/index.json`; those final corrections changed workflow/test fixture code only, not `tools/otbm_atlas/**`.

Canonical map SHA-256 remains `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`. Review closeout has zero unresolved review threads.

## Owner decision: complete-world certification is a separate release gate

On 2026-08-14 the owner explicitly decided that the expensive 3494-chunk Z0..15 build is not a merge blocker for this implementation task. Repeated four-floor GitHub Actions jobs exceeded 90- and 120-minute limits without reporting a renderer/verifier failure. The complete-world certification is therefore transferred to `OTH-20260814-otbm-atlas-full-world-release-validation`.

The deferred validation is not weakened: it must still prove exactly 3494 chunks, Z0..15, common canonical source fingerprints, verifier `ok=true`, and empty `missingSprites`. The replacement manual release workflow runs one floor per job (16 independent jobs) and aggregates their evidence.

## Closeout

```yaml
closeout:
  implementation_complete: true
  focused_acceptance: PASS
  unresolved_review_threads: 0
  full_world_release_certification: deferred-explicitly-by-owner
  deferred_task: OTH-20260814-otbm-atlas-full-world-release-validation
  task_status: completed
  task_archived: true
  ownership_released: true
```
