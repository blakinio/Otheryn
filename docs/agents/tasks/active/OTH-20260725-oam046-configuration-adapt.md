---
task_id: OTH-20260725-oam046-configuration-adapt
status: active
branch: dudantas/oam-046-configuration-adapt
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "3571b35e960cffd5e0a6610de3bd930c7359f589"
related_issue: ""
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260725-oam046-configuration-adapt.md
  - docs/oam-046-configuration-adapt.md
  - src/config/configmanager.cpp
  - tests/unit/config/oam_046_configuration_test.cpp
  - tests/unit/config/CMakeLists.txt
  - tests/unit/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - docs/oam-046-configuration-adapt.md
optional_reads: []
---

# OAM-046 configuration target adaptation

## Final disposition

`ADAPT`.

The target configuration package remains structurally suitable, but successful loads appended OTCR feature IDs into retained vectors. The bounded adaptation parses each current Lua snapshot into local vectors and replaces both retained lists at the end of parsing.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T12:00:00+02:00
head: 3571b35e960cffd5e0a6610de3bd930c7359f589
branch: dudantas/oam-046-configuration-adapt
pr: ""
status: active
context_routes:
  - agent-governance
  - cross-repo
  - engine-foundation
owned_paths:
  - docs/agents/tasks/active/OTH-20260725-oam046-configuration-adapt.md
  - docs/oam-046-configuration-adapt.md
  - src/config/configmanager.cpp
  - tests/unit/config/oam_046_configuration_test.cpp
  - tests/unit/config/CMakeLists.txt
  - tests/unit/CMakeLists.txt
proven:
  - Canary OAM-046 preflight selected configuration with REVALIDATE and merged as a1af14078de0450eb138a2f087e71104c03da4ca.
  - Otheryn task-start main is e8f683e61427e9967cbc180b837220d4b7487d85 and reviewed upstream is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Pre-adaptation target configmanager.cpp blob was 48c0637ba870cb25d119c16fc21d4134d6bdac15.
  - The inherited parser pushed directly into retained enabledFeaturesOTC and disabledFeaturesOTC vectors on every successful load.
  - Repeated successful loads could duplicate IDs, preserve IDs removed from a later table and retain disabled IDs when OTCRFeatures was later omitted.
  - Failed luaL_dofile execution returns before the feature parser and therefore retains the prior snapshot unchanged.
  - The adaptation parses enabled and disabled IDs into local vectors, uses fallback enabled IDs 101/102/103/118 with no disabled IDs and moves both current vectors into the retained members.
  - Adapted configmanager.cpp blob is 18a52bb1095576cc2147bf8581d1007fcef90215.
  - The focused fixture loads custom snapshot A, replacing custom snapshot B, then the omitted-table fallback twice and asserts exact enabled/disabled contents after each successful load.
derived:
  - configuration requires ADAPT rather than REUSE because current successful-load snapshot replacement was ineffective.
  - One local parser correction and one focused contract are sufficient; no package rewrite or ownership expansion is justified.
unknown:
  - Exhaustive key/default correspondence across target, upstream and legacy.
  - Concurrent reload/read synchronization and atomicity of the complete configuration map.
  - Production configuration, secret handling and environment-specific behavior.
  - Maintained-client and physical-client effects for every feature ID.
conflicts: []
first_failure:
  marker: non-idempotent-otcr-feature-load
  evidence: loadLuaOTCFeatures appended parsed/default IDs to retained member vectors without replacing the prior successful snapshot.
rejected_hypotheses:
  - Accept source or header identity as sufficient REUSE evidence.
  - Import legacy-only configuration keys without package-specific target requirements.
  - Expand the adaptation into generic concurrent reload redesign, secret management or controlled feature behavior.
  - Claim client or protocol correctness from server-side list replacement.
changed_paths:
  - docs/agents/tasks/active/OTH-20260725-oam046-configuration-adapt.md
  - docs/oam-046-configuration-adapt.md
  - src/config/configmanager.cpp
  - tests/unit/config/oam_046_configuration_test.cpp
  - tests/unit/config/CMakeLists.txt
  - tests/unit/CMakeLists.txt
validation:
  - command: exact target/upstream/live-legacy root review
    result: PASS
    evidence: Baselines and canonical blobs are recorded in docs/oam-046-configuration-adapt.md.
  - command: bounded parser/source review
    result: PASS
    evidence: Only the retained OTCR feature snapshot assignment is changed; failed-load behavior and all other configuration keys remain untouched.
  - command: focused configuration snapshot contract
    result: NOT_RUN
    evidence: The registered fixture must compile and execute in exact-head Otheryn CI.
blockers:
  - Otheryn exact-head Autofix, CI and Required validation
  - clean discussion and target-main drift audit
  - feature merge and lifecycle archive
next_action: Open the Otheryn feature PR, synchronize its metadata once, require exact-head Autofix, CI and Required, audit discussions and main drift, then squash-merge with the expected head.
```
