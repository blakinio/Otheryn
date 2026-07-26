# OTH-20260726 — MGE-002 typed profile snapshot

Status: **implementation validated; final documentation head pending Required**

Issue: `#132`
Branch: `dudantas/mge-002-typed-profile-snapshot`
Pull request: `#133`
Target repository: `blakinio/Otheryn`
Synchronized main: `d585c1b8120973d50a3e846fb9e3b063ef3019ff`
Validated code head: `953a0af93e7df64309dd524ada31ebdedefdac06`
CI run: `30213109871` — success
Required run: `30213109809` — success

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
updated_at: "2026-07-26T19:56:00+02:00"
head: "953a0af93e7df64309dd524ada31ebdedefdac06"
branch: "dudantas/mge-002-typed-profile-snapshot"
pr: 133
status: "implementation_validated_final_docs_required_pending"
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
  - "Explicit test fixture overrides do not mutate or republish the immutable startup GameProfile."
  - "CI run 30213109871 succeeded on code head 953a0af93e7df64309dd524ada31ebdedefdac06."
  - "Required run 30213109809 succeeded on the same code head."
  - "PR 133 contains exactly fifteen declared implementation, fixture, test and documentation paths."
derived:
  - "Snapshot-backed compatibility getters keep selected legacy consumers on the startup contract without a broad caller migration."
unknown:
  - "Module dependency graphs and lifecycle remain future MGE packages."
conflicts: []
first_failure:
  marker: "linux-debug-fixture-reload"
  evidence: "CI run 30211805149 exposed five fixture reload failures; scoped test-only startup string overrides fixed the boundary, and CI run 30213109871 then passed the full Linux debug test suite."
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
    evidence: "Run 30211701188 verified payload hashes, synchronized current main, checked exact paths and committed the implementation."
  - command: "full repository CI"
    result: "PASS"
    evidence: "Run 30213109871 passed fast checks, Lua tests, Linux debug/release, macOS, Windows, Docker, runtime smoke tests and the full Linux debug test suite."
  - command: "Required exact code head"
    result: "PASS"
    evidence: "Run 30213109809 succeeded on 953a0af93e7df64309dd524ada31ebdedefdac06."
  - command: "exact changed-path audit"
    result: "PASS"
    evidence: "PR 133 lists exactly fifteen declared paths and no temporary payload, workflow or script."
  - command: "discussion and review audit"
    result: "PASS"
    evidence: "Comments, submitted reviews and inline review threads are empty."
  - command: "secret-pattern scan"
    result: "PASS"
    evidence: "Final unified diff contains no credential, token, private-key or secret assignment material."
  - command: "main drift audit"
    result: "PASS"
    evidence: "Main remains d585c1b8120973d50a3e846fb9e3b063ef3019ff, matching the PR base."
  - command: "final documentation head Required"
    result: "NOT_RUN"
    evidence: "This documentation-only checkpoint commit triggers the last exact-head Required run."
blockers: []
next_action: "Require success on the final documentation head, re-audit live PR state, then squash merge PR 133 with expected_head_sha and archive the lifecycle task."
```
