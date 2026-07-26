---
task_id: OTH-20260726-oam051b-task-shop-adapt
coordination_id: OAM-051
status: implementing
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-051b-task-shop-adapt
base_branch: main
created: 2026-07-26
updated: 2026-07-26
last_verified_commit: "38bb62192d25984d63f96c2637348b4adc82f6cd"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - Canary OAM-051B preflight PR 959 merged as 9e865b68b9197b28450002412ca1720683cf1f64
  - OAM-051A lifecycle completed as bd0b58a362d89e449a6863ba299d1c50ad4e6685
blocks:
  - OAM-051 final lifecycle and durable reconciliation
  - OAM-052 start
owned_paths:
  exclusive:
    - data/XML/storages.xml
    - data/modules/scripts/taskboard/taskboard.lua
    - src/creatures/players/components/wheel/player_wheel.cpp
    - src/creatures/players/components/wheel/player_wheel.hpp
    - src/io/functions/iologindata_load_player.cpp
    - src/lua/functions/creatures/player/player_functions.cpp
    - tests/unit/players/oam_051b_task_shop_adapt_test.cpp
    - tests/unit/players/CMakeLists.txt
    - docs/oam-051b-task-shop-adapt.md
    - docs/agents/tasks/active/OTH-20260726-oam051b-task-shop-adapt.md
  shared: []
  read_only:
    - src/creatures/players/player.*
    - src/creatures/players/components/player_storage.*
    - src/io/iologindata.cpp
    - src/io/functions/iologindata_save_player.cpp
    - docs/oam-051-wheel-safety-adapt.md
    - blakinio/canary
    - blakinio/otclient
---

# OAM-051B Hunting Task Shop adaptation

Implement the single bounded Hunting Task Shop Bonus Promotion offer authorized by Canary OAM-051B preflight without importing Wheel KV persistence, maintained-client UI, other Taskboard offers or unrelated Wheel parity changes.

## Accepted contract

- Offer id `0`; offer type `4`.
- Purchased points `0..50`; displayed value is purchased points plus one.
- Next-point cost for point `n` is `100 * (1 + n * (n - 1) / 2)`.
- Status `0` means available, `2` insufficient Hunting Task Points and `4` bought/capped.
- Purchased count persists as SQL-backed PlayerStorage key `1000006`, named `wheel.hunting_task_shop_points`.
- Hunting Task Point balance and purchased count are validated and mutated together; Wheel KV is not used.
- Purchased points load before persisted Wheel allocation validation and contribute to Wheel extra points.
- Shop action and Shop Buy packet parsing remain exact and fail closed.

## Required validation

- Representative costs, cap and display-value offset.
- Wrong offer, malformed, truncated and trailing payload rejection.
- Insufficient balance and replay/duplicate safety.
- Storage-backed load and Wheel extra-point accounting.
- In-memory rollback contract and SQL transaction source boundary.
- Exact outbound payload fields and statuses.
- Existing Bounty and Weekly empty shims remain unchanged.
- Focused tests, applicable repository CI and exact-head Required.

## Exclusions

- No maintained-client Taskboard UI or assets.
- No Bounty, Weekly or other shop offers.
- No Wheel balance, combat effect, spell, stance, area or geometry changes.
- No legacy parser transfer, schema migration, map, deployment or production action.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T14:55:00+02:00
head: 38bb62192d25984d63f96c2637348b4adc82f6cd
branch: dudantas/oam-051b-task-shop-adapt
pr: null
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
  - protocol
  - player-persistence
  - lua
  - testing
owned_paths:
  - bounded Taskboard, Wheel load/accounting, storage reservation, Lua binding, tests and lifecycle paths listed in frontmatter
proven:
  - Otheryn current main is 38bb62192d25984d63f96c2637348b4adc82f6cd.
  - No open Otheryn PR or branch owns OAM-051B or the bounded Taskboard/Wheel paths.
  - Canary preflight PR 959 merged as 9e865b68b9197b28450002412ca1720683cf1f64 after exact-head ownership and Required success.
  - Otheryn PlayerStorage and Task Hunting state persist inside one player SQL transaction.
  - Wheel KV is a separate post-commit persistence domain and is excluded.
  - Maintained OTClient already parses the exact Bonus Promotion payload but has no complete shipped Taskboard UI.
derived:
  - SQL-backed key 1000006 is the smallest schema-free durable counter.
  - The target can ship server-first packet compatibility without a client UI claim.
unknown:
  - Exact implementation shape after focused failing tests.
  - Physical official-client acceptance result.
conflicts: []
first_failure:
  marker: none
  evidence: Preflight and ownership gates authorize the bounded target package.
rejected_hypotheses:
  - Copy Canary PR 230 wholesale.
  - Persist purchased points in Wheel KV.
  - Add maintained-client UI in this package.
  - Expand into other Taskboard or Wheel parity work.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-oam051b-task-shop-adapt.md
validation:
  - command: current main and open ownership audit
    result: PASS
    evidence: main 38bb62192d25984d63f96c2637348b4adc82f6cd; open PRs 123 and 126 do not overlap.
blockers: []
next_action: Open a draft PR, add focused failing tests first, implement the bounded server contract, then run focused and exact-head final validation.
```
