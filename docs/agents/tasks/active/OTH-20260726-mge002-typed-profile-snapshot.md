# OTH-20260726 — MGE-002 typed profile snapshot

Status: **validating exact final head**

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
  - "vcproj/canary.vcxproj"
  - "docs/architecture/typed-game-profile-snapshot.md"
  - "docs/agents/tasks/active/OTH-20260726-mge002-typed-profile-snapshot.md"
proven:
  - "MGE-001 inventory and the modular-engine architecture contract are merged on main."
  - "The branch is synchronized through main d585c1b8120973d50a3e846fb9e3b063ef3019ff."
  - "The implementation publishes shared_ptr<const GameProfile> only after successful validation."
  - "ConfigManager reload preserves the startup-only snapshot and selected compatibility values."
  - "The PR diff contains exactly the thirteen declared MGE-002 paths and no transport workflow or payload."
derived:
  - "Snapshot-backed compatibility getters keep selected legacy consumers on the startup contract without a broad caller migration."
unknown:
  - "Module dependency graphs and lifecycle remain future MGE packages."
conflicts: []
first_failure:
  marker: "resolved-checkpoint-contract"
  evidence: "The staged task used an obsolete checkpoint shape; this commit converts it to the current portable checkpoint contract before final validation."
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
  - "vcproj/canary.vcxproj"
validation:
  - command: "revision-bounded payload materialization"
    result: "PASS"
    evidence: "Run 30211701188 verified all payload hashes, synchronized current main, checked exact paths and committed the implementation."
  - command: "exact changed-path audit"
    result: "PASS"
    evidence: "PR 133 lists exactly the thirteen declared implementation, test and documentation paths."
  - command: "focused and repository CI"
    result: "NOT_RUN"
    evidence: "A trusted checkpoint commit is triggering final exact-head workflows."
  - command: "Required exact head"
    result: "NOT_RUN"
    evidence: "Pending the final trusted head produced by this checkpoint update."
blockers: []
next_action: "Require exact-head CI and Required success, audit discussions, reviews, secrets, paths and main drift, then squash merge PR 133 and archive the task."
```
