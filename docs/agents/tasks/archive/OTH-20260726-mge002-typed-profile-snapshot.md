# OTH-20260726 — MGE-002 typed profile snapshot

Status: **completed and merged**

Issue: `#132` — closed
Implementation branch: `dudantas/mge-002-typed-profile-snapshot`
Implementation pull request: `#133`
Final implementation head: `8ee421132b46d7d17ade2a91316caf45ebfd16bb`
Synchronized target main: `7ba0ac1ae6450378ad2fb4f85ccc9026309f902e`
Implementation merge SHA: `1c38b1245e24549d057cf713a03ea4914d13e987`
Lifecycle branch: `dudantas/mge-002-lifecycle-archive`
Lifecycle pull request: `#153`
Target repository: `blakinio/Otheryn`

## Objective

Deliver the bounded MGE-002 implementation: one immutable, validated and atomically published startup `GameProfile` snapshot, reload immutability, selected bootstrap/content/protocol consumer migration and focused tests.

## Result

Otheryn now:

- reads backward-compatible profile identity and protocol selection from `config.lua`;
- copies startup-only identity, protocol, rules, content and effective ports into `shared_ptr<const GameProfile>`;
- validates profile identifiers, registered primary protocol, world type, content identifiers and port conflicts before readiness;
- publishes the snapshot only after complete successful validation;
- keeps startup-only profile state stable across normal `ConfigManager::reload()`;
- uses typed snapshot values for selected bootstrap and protocol-port decisions;
- supports scoped fixture-only startup string overrides without mutating or republishing the production snapshot;
- includes focused tests covering defaults, invalid input, effective legacy ports, recovery, atomic publication and reload immutability.

The package did not implement `ModuleRegistry`, dependency graphs, module lifecycle, dynamic plugins, historical primary-profile enablement, protocol wire changes, gameplay, Lua bindings, persistence, schema, map, datapack, deployment, runtime profile hot reload or MGE-003+.

## Delivered paths

- `config.lua.dist`
- `src/config/game_profile.hpp`
- `src/config/configmanager.hpp`
- `src/config/configmanager.cpp`
- `src/canary_server.cpp`
- `src/server/network/protocol/protocol_profile.hpp`
- `src/server/network/protocol/protocol_profile.cpp`
- `src/server/network/protocol/protocol_port_utils.hpp`
- `tests/shared/game/events_scheduler_test_fixture.hpp`
- `tests/shared/imbuements/imbuements_test_fixture.hpp`
- `tests/unit/config/CMakeLists.txt`
- `tests/unit/config/mge_002_game_profile_test.cpp`
- `vcproj/canary.vcxproj`
- `docs/architecture/typed-game-profile-snapshot.md`
- this archived lifecycle record

## Final implementation validation

- exact implementation changed paths: **PASS**, exactly 15 declared paths;
- temporary workflow/payload audit: **PASS**, none in final diff;
- comments: **empty**;
- submitted reviews: **empty**;
- inline review threads: **empty**;
- secret-pattern scan: **PASS**;
- main drift: **PASS**, branch behind by 0 at merge;
- `autofix.ci` run `30219796930`: **success**;
- full `CI` run `30219796971`: **success**;
- exact-head `Required` run `30219796911`: **success**;
- expected-head merge protection: **enforced** on `8ee421132b46d7d17ade2a91316caf45ebfd16bb`;
- squash merge: **PASS**, SHA `1c38b1245e24549d057cf713a03ea4914d13e987`;
- issue `#132`: **closed as completed**.

## Checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-26T23:12:00+02:00"
head: "1c38b1245e24549d057cf713a03ea4914d13e987"
branch: "main"
pr: 133
lifecycle_pr: 153
status: "completed_merged_lifecycle_validation_pending"
context_routes:
  - "docs/architecture/modular-game-engine-and-profiles.md"
  - "docs/architecture/current-engine-ownership-and-dependencies.md"
  - "docs/architecture/typed-game-profile-snapshot.md"
proven:
  - "PR 133 merged from exact head 8ee421132b46d7d17ade2a91316caf45ebfd16bb."
  - "Full CI run 30219796971 succeeded on the exact implementation head."
  - "Required run 30219796911 succeeded on the exact implementation head."
  - "Implementation merge SHA is 1c38b1245e24549d057cf713a03ea4914d13e987."
  - "The implementation changed exactly fifteen declared paths."
  - "The final implementation audit found no comments, reviews or review threads."
  - "Issue 132 is closed as completed."
  - "Lifecycle PR 153 changes only the active and archive task paths."
derived:
  - "MGE-002 establishes typed immutable startup profile state but does not establish module composition or lifecycle."
unknown:
  - "The owner and exact start revision for MGE-003 are not selected by this lifecycle PR."
conflicts: []
first_failure:
  marker: "linux-debug-fixture-reload"
  result: "RESOLVED"
  evidence: "Earlier CI exposed fixture reload failures; scoped test-only startup string overrides fixed the boundary, and final exact-head CI passed."
rejected_hypotheses:
  - "A GameProfile snapshot is equivalent to a ModuleRegistry."
  - "MGE-002 authorizes historical primary protocol enablement."
changed_paths:
  - "docs/agents/tasks/active/OTH-20260726-mge002-typed-profile-snapshot.md"
  - "docs/agents/tasks/archive/OTH-20260726-mge002-typed-profile-snapshot.md"
validation:
  implementation_ci: "pass_run_30219796971"
  implementation_autofix: "pass_run_30219796930"
  implementation_required: "pass_run_30219796911"
  implementation_merge: "pass_1c38b1245e24549d057cf713a03ea4914d13e987"
  lifecycle_changed_paths: "pending"
  lifecycle_comments: "pending"
  lifecycle_reviews: "pending"
  lifecycle_threads: "pending"
  lifecycle_main_drift: "pending"
  lifecycle_required: "pending"
blockers: []
next_action: "Validate and merge lifecycle PR 153, then start MGE-003 only after a fresh ownership and dependency preflight."
```
