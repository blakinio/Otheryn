---
task_id: OTH-20260815-otbm-atlas-creature-animation
status: completed
owner: none
branch: feat/otbm-atlas-creature-animation
base_branch: main
created: 2026-08-15T10:47:00+02:00
updated: 2026-08-15T12:21:00+02:00
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "399"
merge_commit: ffc839a02921caf52077c87d91247d92466afae3
ownership_released: true
---

# Canonical OTBM Atlas creature animation — archived

Final disposition: **completed and merged**.

PR #399 adds bounded, time-based canonical NPC and monster animation to the production OTBM Atlas using only pinned data under `vendor/map-analysis/**`. Spawn positions and provenance remain factual; the viewer animates canonical appearance frame groups at those positions and never simulates creature pathing.

Delivered behavior includes:

- preserved canonical outfit `idle` / `moving` frame-group identity;
- canonical north/east/south/west direction patterns for supported outfits;
- all renderable canonical phases with outfit recolouring and addons preserved;
- canonical/default-start, synchronization, random-start and loop timing semantics with conservative fallback;
- bounded viewport-only runtime animation, bounded image/shard/descriptor/start-clock caches and no whole-world animation preload;
- static canonical sprite/dot fallback for unsupported or unresolved animation metadata;
- real pinned-data NPC and monster integration plus production Chromium phase-playback evidence.

## Terminal evidence

```yaml
closeout:
  implementation_complete: true
  vertical_slice_complete: true
  audit:
    result: PASS
    independent_validator: OTBM Creature Animation Audit clean runner
    exact_head_run: 31878003672
    material_findings_open: 0
  e2e:
    result: PASS
    journeys:
      - canonical NPC phase playback in production viewer
      - canonical monster phase playback in production viewer
    exact_head_run: 31878003617
    prior_human_viewable_artifact_run: 31876571280
    prior_artifact_id: 9245078739
  canonical_examples:
    npc:
      name: Tanyt
      look_type: 1199
      phases: 8
      phase_duration_ms: 300
      directions: [north, east, south, west]
    monster:
      name: Silver Rabbit
      look_type: 262
      phases: 8
      phase_duration_ms: 300
      directions: [north, east, south, west]
  final_ci:
    head: c6b1bc6acafcf52c376bd2095ab8e7dd938c2d35
    result: PASS
    required_checks:
      - Required 31878003609
      - CI 31878003676
      - autofix.ci 31878003610
      - OTBM Atlas Tests 31878003687
      - OTBM Canonical Creature Showcase 31878003689
      - OTBM Environment Animation E2E 31878003600
      - OTBM Creature Animation E2E 31878003617
      - OTBM Creature Animation Audit 31878003672
      - OTBM Atlas Factual Layer Audit 31878003660
      - OTBM Atlas Factual Layers 31878003597
  pull_requests:
    open_related_prs: 0
    unresolved_review_threads: 0
    terminal_prs:
      - number: 399
        state: merged
        merge_commit: ffc839a02921caf52077c87d91247d92466afae3
  task_status: completed
  task_archived: true
  ownership_released: true
  stale_branches_reconciled: true
```

`main` was directly verified at `ffc839a02921caf52077c87d91247d92466afae3` after the squash merge.
