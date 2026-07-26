---
task_id: OTH-20260726-oam051b-task-shop-adapt
coordination_id: OAM-051
status: implementing
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-051b-task-shop-adapt
base_branch: main
created: 2026-07-26
updated: 2026-07-26
last_verified_commit: "42011e89fd676b0667d2310fe3a9b63cc631003d"
risk: high
related_issue: ""
related_pr: "128"
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
    - tests/unit/players/oam_051b_task_shop_adapt_test.cpp
    - tests/unit/players/CMakeLists.txt
    - docs/oam-051b-task-shop-adapt.md
    - docs/agents/tasks/active/OTH-20260726-oam051b-task-shop-adapt.md
  shared: []
  read_only:
    - src/creatures/players/player.*
    - src/creatures/players/components/player_storage.*
    - src/io/iologindata.cpp
    - src/io/functions/iologindata_load_player.cpp
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
- Official Wheel payloads report the purchased count in the `GameTaskboard` U16 field after the Monk quest flag.

## Required validation

- Representative costs, cap and display-value offset.
- Wrong offer, malformed, truncated and trailing payload rejection.
- Insufficient balance and replay/duplicate safety.
- Storage-backed load and Wheel extra-point accounting.
- In-memory rollback contract and SQL transaction source boundary.
- Exact outbound Taskboard and Wheel payload fields.
- Existing Bounty and Weekly empty shims remain unchanged.
- Focused tests, applicable repository CI and exact-head Required.

## Exclusions

- No maintained-client Taskboard UI or assets.
- No Bounty, Weekly or other Task Shop offers.
- No Wheel balance, combat effect, spell, stance, area or geometry changes.
- No legacy parser transfer, schema migration, map, deployment or production action.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T15:20:00+02:00
head: 42011e89fd676b0667d2310fe3a9b63cc631003d
branch: dudantas/oam-051b-task-shop-adapt
pr: 128
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
  - protocol
  - player-persistence
  - lua
  - testing
owned_paths:
  - bounded Taskboard, Wheel accounting/payload, storage reservation, tests and lifecycle paths listed in frontmatter
proven:
  - Otheryn task base is 38bb62192d25984d63f96c2637348b4adc82f6cd.
  - No open Otheryn PR or branch owned OAM-051B or the bounded Taskboard/Wheel paths at task start.
  - Canary preflight PR 959 merged as 9e865b68b9197b28450002412ca1720683cf1f64 after exact-head ownership and Required success.
  - Otheryn PlayerStorage and Task Hunting state persist inside one player SQL transaction.
  - Wheel KV is a separate post-commit persistence domain and is excluded.
  - Maintained OTClient parses the exact Bonus Promotion Shop payload and consumes a Task Shop points U16 in the official Wheel payload.
  - Maintained OTClient has no complete shipped Taskboard UI, so no UI claim is made.
  - Focused failing tests were committed before runtime implementation.
  - Storage key 1000006, bounded Taskboard purchase/response logic, Wheel accounting and official Wheel payload reporting are implemented.
  - Both temporary branch-only materialization workflows removed themselves or were deleted before review.
  - Lightweight draft CI 30201733256 succeeded on implementation/test head 1e5d746e1dc94bda571bacaaa4a09a4ec68fcfdf, but affected builds were skipped pending ready-state final validation.
derived:
  - SQL-backed key 1000006 is the smallest schema-free durable counter.
  - Existing generic Lua storage and Task Hunting APIs avoid a new Lua binding and generated API drift.
  - The branch is implementation-complete and ready for exact-head affected final gates.
unknown:
  - Exact final-head affected build/test and Required results after ready-state transition.
  - Physical official-client acceptance result.
conflicts: []
first_failure:
  marker: none
  evidence: No owned implementation or lightweight validation failure remains.
rejected_hypotheses:
  - Copy Canary PR 230 wholesale.
  - Persist purchased points in Wheel KV.
  - Add a new Player Lua binding when existing bounded APIs suffice.
  - Keep sending Monk quest bonus in the official Taskboard points U16.
  - Add maintained-client UI in this package.
  - Expand into other Taskboard or Wheel parity work.
changed_paths:
  - data/XML/storages.xml
  - data/modules/scripts/taskboard/taskboard.lua
  - src/creatures/players/components/wheel/player_wheel.cpp
  - tests/unit/players/oam_051b_task_shop_adapt_test.cpp
  - tests/unit/players/CMakeLists.txt
  - docs/oam-051b-task-shop-adapt.md
  - docs/agents/tasks/active/OTH-20260726-oam051b-task-shop-adapt.md
validation:
  - command: current main and open ownership audit
    result: PASS
    evidence: task base 38bb62192d25984d63f96c2637348b4adc82f6cd; task-start open PRs 123 and 126 did not overlap.
  - command: test-first commit ordering
    result: PASS
    evidence: failing contract tests were committed before storage and Taskboard runtime changes.
  - command: maintained-client source contract
    result: PASS
    evidence: baseline ce4329ee13b39576915240605c2fe6657096c517 parses Shop type/display/cost/status and the official Wheel Task Shop U16.
  - command: temporary helper audit
    result: PASS
    evidence: .github/workflows/oam-051b-materialize.yml is absent from the branch.
  - command: lightweight draft CI
    result: PASS
    evidence: CI run 30201733256 succeeded on 1e5d746e1dc94bda571bacaaa4a09a4ec68fcfdf; heavy affected builds were skipped by draft scope policy.
blockers: []
next_action: Mark PR 128 ready, require exact-final-head affected CI, Repository Audit and Required, resolve any owned failure, then perform clean discussions/path/drift audit before merge.
```
