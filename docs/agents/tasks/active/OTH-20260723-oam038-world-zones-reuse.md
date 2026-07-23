---
task_id: OTH-20260723-oam038-world-zones-reuse
status: validating
branch: dudantas/oam-038-world-zones-reuse
base_branch: main
created: 2026-07-23
updated: 2026-07-23
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260723-oam038-world-zones-reuse.md
  - docs/oam-038-world-zones-reuse.md
  - tests/unit/game/oam_038_world_zones_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/game/zones/zone.cpp
  - src/game/zones/zone.hpp
  - tests/unit/game/zone_weak_cache_test.cpp
  - tests/unit/game/CMakeLists.txt
optional_reads: []
---

# OAM-038 World Zones target reuse proof

## Goal

Prove the bounded canonical `world-zones` runtime is already present in the clean Otheryn target and preserve it without importing unrelated map runtime, tile PvP/protection semantics, quest/event scripting, instance allocation, physical-client orchestration, map content, assets, schema or deployment work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T11:30:00+02:00
head: 6b423d1a100f762f0b41874fffeed6ecd6c46be2
branch: dudantas/oam-038-world-zones-reuse
pr: null
status: validating
context_routes:
  - cpp-runtime
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260723-oam038-world-zones-reuse.md
  - docs/oam-038-world-zones-reuse.md
  - tests/unit/game/oam_038_world_zones_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 651ff1c6261eb25bd0992d7530e50e3690c2b5de.
  - Canary OAM-038 preflight merged as 615648ae0b17c18ee58c3f118b38f78607316a2d and selected canonical world-zones as a REUSE candidate.
  - Canonical world-zones depends only on completed world-map-runtime and owns the Zone registry indexing membership-cache removal refresh variant and XML-loading lifecycle.
  - Otheryn and the reviewed fresh upstream baseline share exact zone.cpp blob f80af238eb2b4b10193a9b5961652591d9dafeb5 and zone.hpp blob d413dccc690d37dc1a24af6c5d2e630b14b087d1.
  - Legacy Canary diverges on zone.cpp blob 99346f8190a023964f027bf9ae1ac5ba4dce1a28 and zone.hpp blob b8cbfdc9935fac88ee5288db04c4e6247293ee22.
  - Target and fresh upstream retain cacheMutex protection around weak membership-cache reads writes removals and refresh plus typed weak-pointer erasure behavior absent from the reviewed legacy core.
  - Existing zone_weak_cache_test.cpp already proves expired weak owners are removed without changing key ordering; the OAM-038 source-contract proof complements it with registry indexing synchronized cache lifecycle cleanup variant and XML-loading coverage.
  - The bounded target package changes exactly four intended proof/task paths and no production runtime or data path.
derived:
  - OAM-038 final disposition is world-zones REUSE if the bounded source-contract proof and exact-head target gates pass without production repair.
  - No maintained-client mutation is expected because canonical world-zones has no client path and does not alter the wire contract.
unknown:
  - Exact final target CI Required and platform-gate evidence until the OAM-038 PR executes.
  - Whether exact-head validation exposes a concrete world-zones-owned target defect requiring reclassification to ADAPT.
conflicts: []
first_failure:
  marker: none
  evidence: No task-specific validation failure observed before target CI execution.
rejected_hypotheses:
  - Infer final REUSE from blob identity alone; this package adds semantic source-contract proof for the owned zone lifecycle.
  - Import the divergent legacy zone roots wholesale; target and fresh upstream retain stronger membership-cache synchronization and weak-pointer removal safeguards.
  - Expand world-zones into map runtime tile PvP/protection quest/event instance or physical-client ownership because those remain separate boundaries.
changed_paths:
  - docs/agents/tasks/active/OTH-20260723-oam038-world-zones-reuse.md
  - docs/oam-038-world-zones-reuse.md
  - tests/unit/game/oam_038_world_zones_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: exact-root and semantic target preflight
    result: PASS
    evidence: canonical target roots match fresh upstream and retain stronger synchronized weak-cache behavior than the divergent legacy roots
  - command: bounded source-contract proof construction
    result: PASS
    evidence: proof covers registry/index lifecycle synchronized weak membership caches dynamic cleanup removal variant and XML-loading surfaces without production mutation
  - command: immutable-base changed-path audit
    result: PASS
    evidence: target branch is intended to change exactly four proof/task paths and no production path
blockers: []
next_action: Open the clean OAM-038 target proof PR, bind its PR number, require exact-current-head CI and Required gates, audit comments reviews review threads and target-main drift, then expected-head squash merge if all gates remain clean.
```
