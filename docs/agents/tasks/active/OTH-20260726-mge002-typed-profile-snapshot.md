# OTH-20260726 — MGE-002 typed profile snapshot

Status: **implementation ready for exact-head validation**

Issue: `#132`
Branch: `dudantas/mge-002-typed-profile-snapshot`
Pull request: `#133`
Target repository: `blakinio/Otheryn`
Base main before final implementation: `db10096f0ebb484f05883dbde4dd895744fbe8c6`

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
updated_at: "2026-07-26T18:45:00+02:00"
head: "db10096f0ebb484f05883dbde4dd895744fbe8c6"
branch: "dudantas/mge-002-typed-profile-snapshot"
pr: 133
issue: 132
base_main: "db10096f0ebb484f05883dbde4dd895744fbe8c6"
status: "implementation_ready_for_validation"
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
  - "MGE-001 inventory and modular-engine architecture contract are merged on main."
  - "Main drift after task start does not overlap MGE-002 implementation paths."
  - "The implementation publishes a shared_ptr<const GameProfile> only after validation."
derived:
  - "Snapshot-backed compatibility getters keep selected legacy consumers on the startup contract without a broad caller migration."
unknown:
  - "Module dependencies and lifecycle remain future MGE packages."
conflicts: []
first_failure: null
rejected_hypotheses:
  - "A typed profile snapshot is equivalent to a ModuleRegistry."
  - "Selecting an existing legacy protocol as the primary profile is authorized by MGE-002."
validation:
  local_structure: "pass"
  focused_tests: "pending_ci"
  required_exact_head: "pending"
  changed_paths: "pending"
  secret_scan: "pending"
  discussions: "pending"
  reviews: "pending"
  main_drift: "pending"
blockers: []
next_action: "Run focused and Required validation on the exact final head, then squash merge and archive this lifecycle record."
```
