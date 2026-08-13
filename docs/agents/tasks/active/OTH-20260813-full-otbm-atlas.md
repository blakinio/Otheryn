---
task_id: OTH-20260813-full-otbm-atlas
status: implementing
created: 2026-08-13
updated: 2026-08-13
project_lane: otheryn-content
related_pr: none
modules_touched:
  - otbm-atlas
---

# Deterministic full OTBM atlas

Deliver a repository-owned pipeline that parses the pinned CrystalServer world,
decodes only the pinned Tibia 15.25 assets, builds bounded/resumable map chunks,
indexes factual mechanics and spawns, and serves a static interactive atlas.

Delivery classification: `full_stack`, user-facing, backend/frontend/integration
and real non-mocked E2E required. The owner's explicit 2026-08-13 atlas request
authorizes this new scope; historical OAM-040 remains evidence of the earlier
target disposition and is not silently rewritten.

Phases are parser and provenance; mechanics/spawns/composition; asset decoder and
Thais regression; chunk cache and viewer; full-world run; independent audit/E2E;
exact-head CI and PR closeout. No generated multi-gigabyte atlas is committed.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-13T13:00:00+02:00
head: a7baaa9c26f9a5a36eeca1887f35c7c55b13c032
branch: blakinio/otbm-full-map-atlas
pr: none
status: implementing
phase: parser-foundation
session_id: codex-20260813-001
session_role: implementer
execution_mode: codex
execution_reason: full checkout, binary fixtures, multi-file implementation and test loops required
project_lane: otheryn-content
context_pressure: high
context_growth: rising
context_score: 12
decomposition_decision: phased
decomposition_reason: one integrated product with seven sequential evidence gates
invocation_started_at: 2026-08-13T12:10:00+02:00
last_progress_at: 2026-08-13T13:00:00+02:00
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 1
stall_warnings: 0
owned_paths:
  - tools/otbm_atlas/**
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
context_routes:
  - AGENTS.md
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/maps/crystalserver-canonical-source.md
  - vendor/map-analysis/README.md
  - docs/oam-040-otbm-tooling-do-not-migrate.md
proven:
  - canonical base head is a7baaa9c26f9a5a36eeca1887f35c7c55b13c032
  - vendor/map-analysis/README.md pins CrystalServer 5e89bf8 and exactly 6031 client assets
  - canonical world.otbm is gzip-wrapped by magic bytes and its decompressed node stream is structurally balanced
  - authoritative RME framing uses FE start, FF end and FD escape
  - focused node reader tests pass 6 of 6
  - full canonical framing scan sees 25170978 nodes, maximum depth 7 and 135815603 payload bytes
derived:
  - semantic parsing must operate incrementally over node events to preserve bounded memory
  - current 77.074 second framing scan needs profiling before it can be accepted for repeated full runs
unknown:
  - exact semantic tile and item totals
  - effective overlay composition
  - appearance-to-sprite decoding completeness
  - full atlas runtime, size and peak memory
conflicts:
  - historical OAM-040 excluded target-local tooling; the later explicit owner task requests repository-owned atlas tooling
first_failure:
  marker: canonical file initially rejected as raw OTBM
  evidence: magic bytes 1F 8B established gzip wrapper; fixed by magic-byte detection and regression test
rejected_hypotheses:
  - canonical world.otbm is an uncompressed OTBM stream: file magic is gzip and decompressed framing validates
changed_paths:
  - tools/otbm_atlas/__init__.py
  - tools/otbm_atlas/nodefile.py
  - tools/otbm_atlas/tests/__init__.py
  - tools/otbm_atlas/tests/test_nodefile.py
  - tools/otbm_atlas/README.md
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
validation:
  - command: python -m unittest discover -s tools/otbm_atlas/tests -v
    result: PASS
    evidence: 6 tests pass including gzip detection and malformed framing
  - command: full iter_node_events scan of canonical world.otbm
    result: PASS
    evidence: balanced 25170978 start/data/end events; depth 7; 77.074 seconds
blockers:
  - none
next_action: implement incremental semantic decoding for root, map metadata, tile areas, tiles, items, towns and waypoints with fail-visible unknown diagnostics and focused fixtures
```
