---
task_id: OTH-20260815-atlas-environment-animation-export-performance
status: ready
owner: none
branch: none
base_branch: main
created: 2026-08-15
updated: 2026-08-15
project_lane: otheryn-content
related_pr: ""
owned_paths:
  - tools/otbm_atlas/environment_animation.py
  - tools/otbm_atlas/tests/test_environment_animation.py
  - docs/maps/atlas-environment-animation.md
required_reads:
  - AGENTS.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/SESSION_RECOVERY_AND_ORPHANED_EXECUTION.md
  - docs/maps/atlas-environment-animation.md
---

# Make full-world environment-animation export bounded and resumable

## Goal

Prevent the canonical Atlas full build from repeatedly spending multiple hours rebuilding environment-animation outputs after interruption. Preserve exact rendering and runtime contracts while adding measurable progress, bounded file creation and safe resume or cache reuse.

## Reproduction evidence

- Exact source: `origin/main` at `a4878325b892b2044f514d27a1a3104e5ce843f7`.
- Command: `python -m tools.otbm_atlas.atlas vendor/map-analysis/crystalserver/data-global/world/world.otbm vendor/map-analysis/tibia-client/15.25.bd5a04/assets build/full-map-atlas --workers 8`.
- The 3,494 detail chunks, both overview levels and manifest v3 completed before the expensive phase.
- Both bounded attempts remained inside `enrich_environment_animations` when interrupted: first after about 82 minutes and second after 120 minutes.
- Trace evidence identified repeated `_phase_rgba`, `_opaque_composite` and `_blend` work in `tools/otbm_atlas/environment_animation.py`.
- The exporter created hundreds of thousands of small files and continued making measurable CPU/filesystem progress; this was not a deadlock.
- `--workers 8` accelerates detail rendering but does not materially parallelize this phase.
- Restarting the canonical build did not resume at the previous environment-animation position; the phase rebuilt a substantial portion of its output.
- The PNG/WebP detail benchmark does not consume `data/environment-animations/`, so the codec measurement is intentionally decoupled from this follow-up.

## Acceptance criteria

1. A full-world export exposes deterministic progress totals and current progress without counting the output tree externally.
2. A controlled interruption leaves a durable checkpoint or content-addressed cache that a subsequent identical invocation reuses.
3. Restart does not delete or rewrite already-verified phase images, underlays or shards whose complete input fingerprint still matches.
4. Output file cardinality and byte totals are reported; duplicate per-occurrence assets are detected and avoided where the runtime contract permits deduplication.
5. `--workers` behaviour for this phase is explicit; safe bounded parallelism is used only if deterministic output and memory bounds are proven.
6. Focused tests cover clean build, interrupted build, resume, stale-fingerprint invalidation and exact output equivalence.
7. A real canonical full-world run completes within the declared heavy-execution budget, or records a measured remaining bottleneck with a smaller next action.
8. Existing environment-animation browser/runtime behaviour and pixel correctness remain unchanged.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T18:20:00+02:00
head: a4878325b892b2044f514d27a1a3104e5ce843f7
branch: none
pr: none
status: ready
phase: investigate
execution_mode: codex
project_lane: otheryn-content
context_routes:
  - docs/maps/atlas-environment-animation.md
owned_paths:
  - tools/otbm_atlas/environment_animation.py
  - tools/otbm_atlas/tests/test_environment_animation.py
  - docs/maps/atlas-environment-animation.md
proven:
  - detail and overview rendering completes before environment-animation enrichment
  - two controlled full-world attempts exceeded 82 and 120 minutes respectively inside environment-animation enrichment
  - the phase makes progress but produces hundreds of thousands of files and does not resume efficiently
  - the codec benchmark is independent of environment-animation outputs
derived:
  - resumability and output-cardinality measurement should be addressed before attempting another uninterrupted full-world export
unknown:
  - exact number of unique reusable phase images, underlays and shards expected for the full canonical world
  - dominant split between pixel composition CPU time and Windows small-file filesystem time
conflicts: []
first_failure:
  marker: KeyboardInterrupt in enrich_environment_animations after bounded execution
  evidence: traces reached _phase_rgba, _opaque_composite and _blend during both attempts
rejected_hypotheses:
  - deadlock; CPU use and output cardinality continued increasing
  - detail rendering bottleneck; all 3494 detail chunks and overviews completed before this phase
changed_paths:
  - docs/agents/tasks/active/OTH-20260815-atlas-environment-animation-export-performance.md
validation:
  - command: canonical full build with --workers 8
    result: FAIL
    evidence: bounded attempts interrupted in enrich_environment_animations after continuous measurable progress
blockers: []
next_action: instrument a focused canonical scan to count occurrences, unique content keys, output cardinality and time by exporter stage before designing the resume/cache boundary
```
