# OTH-20260726 — MGE-002 typed profile snapshot

Status: **synchronized current main; final exact-head validation pending**

Issue: `#132`
Branch: `dudantas/mge-002-typed-profile-snapshot`
Pull request: `#133`
Target repository: `blakinio/Otheryn`
Synchronized main: `7ba0ac1ae6450378ad2fb4f85ccc9026309f902e`
Validated code head before synchronization: `953a0af93e7df64309dd524ada31ebdedefdac06`
Synchronization merge head: `d7d20458d002f003cc7c9c8a86c846fab9643875`
Previous CI run: `30213109871` — success
Previous Required run: `30213109809` — success

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
updated_at: "2026-07-26T20:52:00+02:00"
head: "d7d20458d002f003cc7c9c8a86c846fab9643875"
branch: "dudantas/mge-002-typed-profile-snapshot"
pr: 133
status: "synchronized_final_exact_head_validation_pending"
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
  - "The branch is synchronized through main 7ba0ac1ae6450378ad2fb4f85ccc9026309f902e."
  - "The eight commits added after the previous baseline changed persistence scheduling and unrelated lifecycle/evidence paths only; they did not overlap MGE-002 ownership."
  - "The one-shot synchronization workflow removed itself before the synchronization merge head d7d20458d002f003cc7c9c8a86c846fab9643875."
  - "The implementation publishes shared_ptr<const GameProfile> only after successful validation."
  - "ConfigManager reload preserves the startup-only snapshot and selected compatibility values."
  - "Explicit test fixture overrides do not mutate or republish the immutable startup GameProfile."
  - "CI run 30213109871 succeeded on pre-sync code head 953a0af93e7df64309dd524ada31ebdedefdac06."
  - "Required run 30213109809 succeeded on the same pre-sync code head."
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
    evidence: "Run 30211701188 verified payload hashes, synchronized the earlier main, checked exact paths and committed the implementation."
  - command: "pre-sync full repository CI"
    result: "PASS"
    evidence: "Run 30213109871 passed fast checks, Lua tests, Linux debug/release, macOS, Windows, Docker, runtime smoke tests and the full Linux debug test suite."
  - command: "pre-sync Required exact code head"
    result: "PASS"
    evidence: "Run 30213109809 succeeded on 953a0af93e7df64309dd524ada31ebdedefdac06."
  - command: "exact changed-path audit after current-main synchronization"
    result: "PASS"
    evidence: "PR 133 lists exactly fifteen declared paths and no temporary payload, workflow or script."
  - command: "discussion and review audit"
    result: "PASS"
    evidence: "Comments, submitted reviews and inline review threads are empty."
  - command: "secret-pattern scan"
    result: "PASS"
    evidence: "Final unified diff contains no credential, token, private-key or secret assignment material."
  - command: "current-main synchronization audit"
    result: "PASS"
    evidence: "Branch contains main 7ba0ac1ae6450378ad2fb4f85ccc9026309f902e and remains exactly fifteen paths ahead."
  - command: "trusted checkpoint exact-head CI and Required"
    result: "PENDING"
    evidence: "This trusted checkpoint commit follows the bot-authored synchronization merge and triggers the final exact-head workflows."
blockers: []
next_action: "Require exact-head CI, autofix and Required success on this trusted checkpoint commit, re-audit live PR state and main drift, then squash merge PR 133 with expected_head_sha and archive the lifecycle task."
```
