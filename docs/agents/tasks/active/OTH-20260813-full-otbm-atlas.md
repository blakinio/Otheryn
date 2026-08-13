---
task_id: OTH-20260813-full-otbm-atlas
status: implementing
created: 2026-08-13
updated: 2026-08-13
project_lane: otheryn-content
related_pr: "374"
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
updated_at: 2026-08-13T22:00:00+02:00
head: a9e8c1d965545aa0b1441caed80a2c29c158ba50
branch: blakinio/otbm-full-map-atlas
pr: 374
status: validating
phase: exact-head-validation
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
last_progress_at: 2026-08-13T18:05:00+02:00
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
  - all 8 canonical spawn XML files parse strictly to 87565 monster and 1068 NPC records using center-relative X/Y and absolute Z
  - full factual scan finds 2311 AID records (736 unique), 597 UID records, 2406 teleports, 109744 house tiles, 4527 house doors, 33 towns and 18 waypoints
  - conservative Lua resolution yields 496 RESOLVED, 18 AMBIGUOUS and 819 UNRESOLVED unique AID/UID values; 103 dynamic registrations remain UNKNOWN
  - composition inventory classifies 1 base map, 1 conditional custom overlay, 28 runtime-loaded overlays and 2 UNKNOWN maps; none are flattened into the base atlas
  - cropped rendering preserves a conservative two-tile 64x64/displacement gutter; a one-tile canonical chunk renders at 96x96 in 0.032 seconds
  - full four-worker atlas build completes all 3494 chunks in 3367.867 seconds and writes 10996609082 PNG bytes
  - independent verification recomputes every PNG checksum/header/dimension with zero manifest or file-set errors
  - full atlas has 24504222 render operations, 18996181 ground items and 5508042 child items
  - exactly one canonical item server ID 2141 at 33572,32528,14 lacks an appearance; it is recorded in unknown-items.json and is not substituted
  - 995 canonical houses parse from world-house.xml
  - unchanged full-atlas cache verification completes in 19.418 seconds without rerendering chunks
  - viewer exposes relative floor labels -8 through +7 while preserving raw OTBM Z=0..15 in manifests and data
  - render-mode runtime tests pass for URL precedence, persistence, state preservation, layer selection and bounded LRU
  - full world has 3494 verified detail, 3494 4x overview and 3494 8x overview PNGs plus 2595 spatial overlay shards
  - historical 15037 versus canonical 14993 Thais child-item totals reproduce exactly from different OTBM SHA-256 inputs
  - browser E2E proves Auto low/high, Detailed low, Performance high, floor switch, search, URL state and marker details without page errors
derived:
  - semantic parsing must operate incrementally over node events to preserve bounded memory
  - current 77.074 second framing scan needs profiling before it can be accepted for repeated full runs
  - the 44-item Thais discrepancy is source revision drift, not a counting-definition mismatch
unknown:
  - peak browser and pipeline memory on owner hardware
  - owner-hardware performance beyond the owner's qualitative smoothness report
conflicts:
  - historical OAM-040 excluded target-local tooling; the later explicit owner task requests repository-owned atlas tooling
first_failure:
  marker: canonical file initially rejected as raw OTBM
  evidence: magic bytes 1F 8B established gzip wrapper; fixed by magic-byte detection and regression test
rejected_hypotheses:
  - canonical world.otbm is an uncompressed OTBM stream: file magic is gzip and decompressed framing validates
  - 44 missing Thais child items are repeated compact tile items: preserving repeated compact items did not change the canonical count
changed_paths:
  - tools/otbm_atlas/**
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
validation:
  - command: node --check tools/otbm_atlas/viewer_app.js; python -m unittest discover -s tools/otbm_atlas/tests -v
    result: PASS
    evidence: viewer syntax passes and 32 focused tests pass
  - command: spool_map canonical world.otbm with chunk size 128
    result: PASS
    evidence: 18997668 tiles, 3494 chunks, 545977318 bytes, Z 0 through 15, 180.07 seconds
  - command: render_tiles build/full-map-atlas/.spool/z7/252_251.bin
    result: PASS
    evidence: 4096x4096 PNG; 16384 tiles, 8821 child items, 25205 operations, zero missing, 10.966 seconds
  - command: python -m tools.otbm_atlas.spawns canonical-world build/full-map-atlas/data/spawns.json
    result: PASS
    evidence: 8 sources; 87565 monster and 1068 NPC spawns; 36182644-byte deterministic JSON index
  - command: spool_map canonical world.otbm with factual indexing
    result: PASS
    evidence: 18997668 tiles in 224.498 seconds; facts.json contains all mechanics totals and is 29093099 bytes
  - command: resolve_mechanics facts.json data-otservbr-global
    result: PASS
    evidence: 496 RESOLVED, 18 AMBIGUOUS, 819 UNRESOLVED; regression AID 5555 and UID 65207 independently resolve
  - command: python -m tools.otbm_atlas.composition canonical-world repository output
    result: PASS
    evidence: 32 OTBMs classified; only winterlight island and ferumbras habitats remain UNKNOWN; mergedIntoBaseAtlas false for every source
  - command: python -m tools.otbm_atlas._parallel_smoke
    result: PASS
    evidence: two Windows spawn workers rendered separate real canonical chunks and returned [1, 1]; temporary smoke module removed afterward
  - command: python -m tools.otbm_atlas.atlas canonical-map canonical-assets build/full-map-atlas --workers 4
    result: PASS
    evidence: 3494 PNG/report pairs across Z0..15; 3367.867 seconds; 11642482558 total atlas bytes including spool/data
  - command: python -m tools.otbm_atlas.verify build/full-map-atlas
    result: PASS
    evidence: all 3494 independent checksums and PNG dimensions pass; zero file-set errors; one explicit missing appearance and zero missing sprites
  - command: cached python -m tools.otbm_atlas.atlas canonical inputs same output
    result: PASS
    evidence: 19.418 seconds; no chunk rerender required
  - command: python -m tools.otbm_atlas.verify build/full-map-atlas; Playwright Thais E2E
    result: PASS
    evidence: 3494 chunks per imagery layer verify; mode request routing, floor, search and details pass
blockers:
  - none
next_action: commit and push final fixes, then run exact-head CI and PR closeout checks
```
