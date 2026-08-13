---
task_id: OTH-20260813-full-otbm-atlas
status: ready
created: 2026-08-13
updated: 2026-08-13
project_lane: otheryn-content
related_pr: "373"
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
head: e7f7cbe0d55183c070050e83a81b83150b67f344
branch: blakinio/otbm-full-map-atlas
pr: 373
status: ready
phase: chunk-pipeline-ready
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
last_progress_at: 2026-08-13T14:08:00+02:00
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
  - semantic parser strict scan covers 18997668 tiles across every Z level 0 through 15 with zero diagnostics
  - Thais scan exactly matches 24311 tiles and 24292 ground items and independently locates AID 5555 and UID 65207
  - canonical scan CLI output fingerprints world.otbm as 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - pinned assets decode to 42107 object appearances and 4927 sprite sheets with 75623 referenced sprite IDs and zero missing catalog sprites
  - Thais renders at 5152x4832 from vendored sprites with zero missing appearances and zero missing sprites
derived:
  - semantic parsing must operate incrementally over node events to preserve bounded memory
  - current 77.074 second framing scan needs profiling before it can be accepted for repeated full runs
  - Thais child-item discrepancy requires asset-aware ground/appearance classification rather than counter adjustment
  - current Thais output is semantically coherent but the old reference counters are not reproducible from the pinned OTBM node inventory
unknown:
  - exact semantic tile and item totals
  - effective overlay composition
  - full atlas runtime, size and peak memory
conflicts:
  - historical OAM-040 excluded target-local tooling; the later explicit owner task requests repository-owned atlas tooling
first_failure:
  marker: canonical file initially rejected as raw OTBM
  evidence: magic bytes 1F 8B established gzip wrapper; fixed by magic-byte detection and regression test
rejected_hypotheses:
  - canonical world.otbm is an uncompressed OTBM stream: file magic is gzip and decompressed framing validates
  - 44 missing Thais child items are repeated compact tile items: preserving repeated compact items did not change the canonical count
changed_paths:
  - tools/otbm_atlas/__init__.py
  - tools/otbm_atlas/nodefile.py
  - tools/otbm_atlas/tests/__init__.py
  - tools/otbm_atlas/tests/test_nodefile.py
  - tools/otbm_atlas/README.md
  - tools/otbm_atlas/semantic.py
  - tools/otbm_atlas/scan.py
  - tools/otbm_atlas/tests/test_semantic.py
  - tools/otbm_atlas/tests/test_scan.py
  - tools/otbm_atlas/assets.py
  - tools/otbm_atlas/render.py
  - tools/otbm_atlas/tests/test_assets.py
  - tools/otbm_atlas/tests/test_render.py
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
validation:
  - command: python -m unittest discover -s tools/otbm_atlas/tests -v
    result: PASS
    evidence: 6 tests pass including gzip detection and malformed framing
  - command: full iter_node_events scan of canonical world.otbm
    result: PASS
    evidence: balanced 25170978 start/data/end events; depth 7; 77.074 seconds
  - command: python -m unittest discover -s tools/otbm_atlas/tests -v
    result: PASS
    evidence: 13 tests pass for framing, gzip, semantics, attributes, nesting, mechanics and provenance
  - command: python -m tools.otbm_atlas.scan world.otbm --bounds 32280 32440 32155 32305 7
    result: PASS
    evidence: build/otbm-atlas/thais-scan.json; 24311 tiles, 24292 ground, 14993 decoded child items, zero diagnostics
  - command: python -m unittest discover -s tools/otbm_atlas/tests -v
    result: PASS
    evidence: 17 tests pass including protobuf wire decoding, catalog layout, PNG and alpha compositing
  - command: python -m tools.otbm_atlas.render world.otbm assets --bounds 32280 32440 32155 32305 7
    result: PASS
    evidence: build/otbm-atlas/thais.png and thais-render.json; 39285 operations, 863 appearances, 1002 sprites, zero missing
blockers:
  - none
next_action: implement the single-pass disk-spooled chunk builder, resumable manifest, and static atlas viewer
```
