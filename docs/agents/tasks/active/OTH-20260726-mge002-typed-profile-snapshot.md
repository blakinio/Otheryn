# OTH-20260726 — MGE-002 typed profile snapshot

Status: **validating fixture compatibility fix**

Issue: `#132`
Branch: `dudantas/mge-002-typed-profile-snapshot`
Pull request: `#133`
Target repository: `blakinio/Otheryn`
Synchronized main: `d585c1b8120973d50a3e846fb9e3b063ef3019ff`

## Objective

Add a bounded typed immutable startup `GameProfile` snapshot with fail-closed validation, atomic publication, reload immutability and selected bootstrap/content/protocol consumer migration.

## Safety boundaries

- no `ModuleRegistry`, module graph, module lifecycle or dynamic plugins;
- no historical primary profile enablement;
- no protocol wire behavior, gameplay, Lua binding, persistence, schema, map, datapack or deployment change;
- no runtime profile hot reload;
- no MGE-003+ work.

## Delivered paths

- `config.lua.dist`
- `src/config/game_profile.hpp`
- `src/config/configmanager.hpp`
- `src/config/configmanager.cpp`
- `src/canary_server.cpp`
- `src/server/network/protocol/protocol_profile.hpp`
- `src/server/network/protocol/protocol_profile.cpp`
- `src/server/network/protocol/protocol_port_utils.hpp`
- `tests/unit/config/CMakeLists.txt`
- `tests/unit/config/mge_002_game_profile_test.cpp`
- `tests/shared/game/events_scheduler_test_fixture.hpp`
- `tests/shared/imbuements/imbuements_test_fixture.hpp`
- `vcproj/canary.vcxproj`
- `docs/architecture/typed-game-profile-snapshot.md`
- this task record

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-26T19:05:00+02:00"
head: "b581add19bbb584509b8fad0b52b2f3ec9812d8f"
branch: "dudantas/mge-002-typed-profile-snapshot"
pr: 133
status: "validating"
context_routes:
  - "docs/architecture/modular-game-engine-and-profiles.md"
  - "docs/architecture/current-engine-ownership-and-dependencies.md"
  - "docs/architecture/typed-game-profile-snapshot.md"
owned_paths:
  - "config.lua.dist"
  - "src/config/game_profile.hpp"
  - "src/config/configmanager.hpp"
  - "src/config/configmanager.cpp"
  - "src/canary_server.cpp"
  - "src/server/network/protocol/protocol_profile.hpp"
  - "src/server/network/protocol/protocol_profile.cpp"
  - "src/server/network/protocol/protocol_port_utils.hpp"
  - "tests/unit/config/CMakeLists.txt"
  - "tests/unit/config/mge_002_game_profile_test.cpp"
  - "tests/shared/game/events_scheduler_test_fixture.hpp"
  - "tests/shared/imbuements/imbuements_test_fixture.hpp"
  - "vcproj/canary.vcxproj"
  - "docs/architecture/typed-game-profile-snapshot.md"
  - "docs/agents/tasks/active/OTH-20260726-mge002-typed-profile-snapshot.md"
proven:
  - "MGE-001 inventory and the modular-engine architecture contract are merged on main."
  - "The branch is synchronized through main d585c1b8120973d50a3e846fb9e3b063ef3019ff."
  - "The implementation publishes shared_ptr<const GameProfile> only after successful validation."
  - "ConfigManager reload preserves the startup-only snapshot and selected compatibility values."
  - "The PR diff contains only declared MGE-002 implementation, fixture, test and documentation paths and no transport workflow or payload."
  - "Explicit test fixture overrides do not mutate or republish the immutable startup GameProfile."
derived:
  - "Snapshot-backed compatibility getters keep selected legacy consumers on the startup contract without a broad caller migration."
unknown:
  - "Module dependency graphs and lifecycle remain future MGE packages."
conflicts: []
first_failure:
  marker: "linux-debug-fixture-reload"
  evidence: "CI run 30211805149 compiled and smoke-tested all platforms, but five integration tests failed because fixture reloads could no longer replace snapshot-owned coreDirectory; the explicit test override fixes that boundary without weakening production reload semantics."
rejected_hypotheses:
  - "A typed profile snapshot is equivalent to a ModuleRegistry."
  - "Selecting an existing legacy protocol as the primary profile is authorized by MGE-002."
changed_paths:
  - "config.lua.dist"
  - "docs/agents/tasks/active/OTH-20260726-mge002-typed-profile-snapshot.md"
  - "docs/architecture/typed-game-profile-snapshot.md"
  - "src/canary_server.cpp"
  - "src/config/configmanager.cpp"
  - "src/config/configmanager.hpp"
  - "src/config/game_profile.hpp"
  - "src/server/network/protocol/protocol_port_utils.hpp"
  - "src/server/network/protocol/protocol_profile.cpp"
  - "src/server/network/protocol/protocol_profile.hpp"
  - "tests/unit/config/CMakeLists.txt"
  - "tests/unit/config/mge_002_game_profile_test.cpp"
  - "tests/shared/game/events_scheduler_test_fixture.hpp"
  - "tests/shared/imbuements/imbuements_test_fixture.hpp"
  - "vcproj/canary.vcxproj"
validation:
  - command: "revision-bounded payload materialization"
    result: "PASS"
    evidence: "Run 30211701188 verified all payload hashes, synchronized current main, checked exact paths and committed the implementation."
  - command: "exact changed-path audit"
    result: "PASS"
    evidence: "PR 133 lists exactly the thirteen declared implementation, test and documentation paths."
  - command: "CI run 30211805149"
    result: "FAIL"
    evidence: "All compilers and smoke tests passed; Linux debug integration tests exposed fixture reload incompatibility now addressed by explicit scoped test overrides."
  - command: "fixture compatibility regression"
    result: "NOT_RUN"
    evidence: "Pending exact-head CI after this bounded fix."
  - command: "Required exact head"
    result: "NOT_RUN"
    evidence: "Pending the final trusted head produced by this checkpoint update."
blockers: []
next_action: "Run exact-head CI after the fixture compatibility fix, require Required success, audit discussions, reviews, secrets, paths and main drift, then squash merge PR 133 and archive the task."
```
