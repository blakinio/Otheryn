---
task_id: OTH-20260813-full-otbm-atlas
status: ready
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
updated_at: 2026-08-13T13:00:00+02:00
head: 1880fc08cf7f92065e0940d7fc79bff7c4190d3e
branch: blakinio/otbm-full-map-atlas
pr: 374
status: ready
phase: full-world-render-verified
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
  - a single canonical scan spools all 18997668 tiles into 3494 bounded 128x128 chunk files covering Z 0 through 15
  - the canonical spool is 545977318 bytes and completed in 180.07 seconds
  - canonical chunk z7/252_251 renders at 4096x4096 with 16384 tiles, 25205 render operations and zero missing appearances or sprites
  - the static viewer implements pan, zoom, floor selection, coordinate display/jump and required overlay toggles without an external service
  - all 8 canonical spawn XML files parse strictly to 87565 monster and 1068 NPC records
  - canonical spawn coordinates use center-relative X/Y and absolute child Z; all 88633 canonical records agree with their group center Z
  - full factual scan finds 2311 AID records (736 unique), 597 UID records, 2406 teleports, 109744 house tiles, 4527 house doors, 33 towns and 18 waypoints
  - conservative Lua resolution yields 496 RESOLVED, 18 AMBIGUOUS and 819 UNRESOLVED unique AID/UID values; 103 dynamic registrations remain UNKNOWN
  - AID 5555 resolves only to scripts/movements/teleport/sorcerer_guild_thais.lua and UID 65207 only to the literal dispatch table in quest_system2.lua
  - composition inventory classifies 1 base map, 1 conditional custom overlay, 28 runtime-loaded overlays and 2 UNKNOWN maps; none are flattened into the base atlas
  - cropped rendering preserves a conservative two-tile 64x64/displacement gutter; a one-tile canonical chunk renders at 96x96 in 0.032 seconds
  - two-process Windows spawn smoke test renders two real canonical chunks successfully
  - full four-worker atlas build completes all 3494 chunks in 3367.867 seconds and writes 10996609082 PNG bytes
  - independent verification recomputes every PNG checksum/header/dimension with zero manifest or file-set errors
  - full atlas has 24504222 render operations, 18996181 ground items and 5508042 child items
  - exactly one canonical item server ID 2141 at 33572,32528,14 lacks an appearance; it is recorded in unknown-items.json and is not substituted
  - 995 canonical houses parse from world-house.xml
  - unchanged full-atlas cache verification completes in 19.418 seconds without rerendering chunks
derived:
  - semantic parsing must operate incrementally over node events to preserve bounded memory
  - current 77.074 second framing scan needs profiling before it can be accepted for repeated full runs
  - Thais child-item discrepancy requires asset-aware ground/appearance classification rather than counter adjustment
  - current Thais output is semantically coherent but the old reference counters are not reproducible from the pinned OTBM node inventory
unknown:
  - exact semantic item total
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
  - tools/otbm_atlas/atlas.py
  - tools/otbm_atlas/viewer.py
  - tools/otbm_atlas/tests/test_atlas.py
  - tools/otbm_atlas/tests/test_viewer.py
  - tools/otbm_atlas/spawns.py
  - tools/otbm_atlas/tests/test_spawns.py
  - tools/otbm_atlas/mechanics.py
  - tools/otbm_atlas/composition.py
  - tools/otbm_atlas/tests/test_mechanics.py
  - tools/otbm_atlas/tests/test_composition.py
  - tools/otbm_atlas/houses.py
  - tools/otbm_atlas/verify.py
  - tools/otbm_atlas/tests/test_houses.py
  - tools/otbm_atlas/tests/test_verify.py
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
  - command: spool_map canonical world.otbm with chunk size 128
    result: PASS
    evidence: 18997668 tiles, 3494 chunks, 545977318 bytes, Z 0 through 15, 180.07 seconds
  - command: render_tiles build/full-map-atlas/.spool/z7/252_251.bin
    result: PASS
    evidence: 4096x4096 PNG; 16384 tiles, 8821 child items, 25205 operations, zero missing, 10.966 seconds
  - command: python -m unittest discover -s tools/otbm_atlas/tests -v
    result: PASS
    evidence: 22 tests pass including spool round-trip/corruption handling, spawn coordinate semantics, and static-viewer controls
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
  - command: HTTP GET viewer manifest mechanics spawns real z7 chunk
    result: PASS
    evidence: all return 200 with correct HTML JSON and image/png content types
blockers:
  - none
next_action: commit verification tooling, perform exact-head CI/PR checks, and complete browser E2E if the Chrome extension initialization blocker clears
```
