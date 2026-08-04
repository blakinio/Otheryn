# Dossier — `zimbadev/crystalserver#206`

## Identity

```yaml
canonical_key: zimbadev/crystalserver#206
predecessor_row: 93
source_type: pull_request
prior_bucket: INSUFFICIENT
prior_truth_status: PARTIALLY_PROVEN
family: player-update-coalescing
research_status: COMPLETE
```

## Source claim

- Current title: `feat: scheduler update`
- Source URL: `https://github.com/zimbadev/crystalserver/pull/206`
- Exact inferred claim: frequently repeated player stats/skills/inventory/light/weight sends can be coalesced into a scheduled bitmask and emitted once per update cycle, reducing redundant work and packets.
- Claimed affected version/protocol: CrystalServer base `ffe4db548371c44ce01dfc280af0209318272292`; no packet-version boundary or performance target stated.
- Claimed validation: none in the PR body; the PR is draft, open, non-mergeable, has 10 commits and includes an unrelated group-flag change.
- Claimed expected behavior: coalescing preserves all externally observable player state updates while reducing duplicate sends and bounded update latency.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream PR | `zimbadev/crystalserver` | PR `#206`, head `ee5606edf587c2ae3065163b8cf46618678063ef` | 2026-08-04 | proposes scheduled update aggregation | primary claim | body only credits another author and supplies no problem statement, benchmark or tests |
| S2 | PR patch | same | same head | 2026-08-04 | replaces many immediate `sendStats`/`sendSkills` calls with `addScheduledUpdates` bit flags across player, conditions, mounts and outfits | exact change evidence | patch is broad, draft and contains unrelated changes; truncated review still shows lifecycle-sensitive modifications |
| S3 | bounded repository search | four server repositories | pinned audit revisions | 2026-08-04 | `addScheduledUpdates`/`PlayerUpdate_*` model is absent from the pinned compared lines | applicability evidence | absence does not prove redundant packet volume is material |
| S4 | client boundary | `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | 2026-08-04 | client consumes the resulting stats/skills/inventory updates | protocol-observation evidence | client cannot establish whether coalescing preserves timing-sensitive UI behavior |

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: multiple state mutations within one bounded server update window produce the minimal required packet set, with final values equivalent to immediate sends and no missed update on logout, death, relog, condition end or protocol flush
version_boundary: server-side update scheduling; packet layouts remain profile-dependent, while acceptable delay depends on game-loop interval and lifecycle ordering
evidence_basis:
  - S1
  - S2
  - S3
conflicts:
  - PR lacks a defined flush point contract and tests proving updates are not cleared before callbacks or disconnect
  - the patch resets scheduling fields inside `Player::onThink`, which is ordering-sensitive and cannot be accepted from diff intent alone
  - unrelated `hasnoexhaustion` group change violates narrow applicability
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | player/condition/mount/outfit update sends and scheduling types | immediate-send model; no PR 206 scheduler API | architecture candidate only | high |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | same paths | pinned base lacks draft PR; candidate head spans 14 files | unproven draft improvement | high |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | same update paths | immediate-send model with project-specific drift | architecture candidate only | medium-high |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | player stats/skills/inventory/light/weight sends; think/lifecycle paths | no bitmask coalescing model; no evidence yet that current packet volume breaches a budget | static performance impact inconclusive | high |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | parsers/UI updates for stats, skills and inventory | suitable for packet-count and final-state comparison | relevant validation target | high |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: scripted burst of player state mutations -> emitted packet sequence and client final state -> latency/packet/work
  comparison
preconditions:
- isolated Otheryn and maintained OTClient
- deterministic scenarios for condition add/remove, damage/mana, skill/level gain, equipment/imbuement, mount/outfit, death/relog
  and logout-before-next-think
- audit-only packet decoder and server counters
steps:
- run each scenario on pinned immediate-send target and record packet counts/order, CPU and final server/client state
- build the donor PR head separately and run the same matrix without copying it into Otheryn
- compare final state equivalence and maximum update latency
- stress repeated mutations within one tick and lifecycle boundaries where deferred updates may be lost
expected_observations:
- candidate is beneficial only if packet/work reduction is material and every final state/lifecycle assertion is equivalent
  within an accepted latency budget
- any missing pre-disconnect/death/callback update rejects direct adoption
artifacts:
- scenario-matrix.json
- immediate-packets.jsonl
- donor-scheduled-packets.jsonl
- final-state-diff.json
- update-latency.csv
- server-work-counters.csv
- runtime-feasibility.md
cleanup:
- terminate isolated builds and discard test state
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: the repository can start the server and validate the seeded HTTP login response, but it has no deterministic game-protocol/client
  driver and no isolated per-scenario world fixture for map, quest, combat, store, boss, persistence or client-rendering actions;
  adding that infrastructure would be implementation outside this audit-only authorization
```

## Runtime execution

```yaml
execution_status: BLOCKED
exact_otheryn_head: not applicable
run_ids: []
observations:
- Docker quickstart validates server startup and the seeded HTTP login response only
- no deterministic game-protocol/client driver or per-scenario world fixture exists in the repository
artifacts:
- runtime-feasibility.md
cleanup_result: not started; no state created
```

## Conclusions

```yaml
truth_status: PARTIALLY_PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: NOT_RUN_INFEASIBLE
owner_action: OPEN_ARCHITECTURE_DECISION
confidence: high
rationale: 'the draft demonstrates a concrete coalescing design but supplies no benchmark, correctness suite or clean scope,
  and Otheryn has no proven packet-volume breach; evaluate the concept through an independent architecture/benchmark programme
  rather than migrate the PR Runtime execution is infrastructure-blocked: the repository has no deterministic game/client
  driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Drift after pinned revision: PR remains draft/open/non-mergeable and is not an accepted CrystalServer contract.
- Unresolved questions:
  - What is the exact coalescing/flush window and which updates must remain immediate?
  - How are disconnect, death, teleport, callback and exception paths flushed?
  - Should Otheryn solve packet coalescing at player state, protocol output buffering or event transaction boundaries?
  - What packet/work reduction justifies added state-machine complexity?
- Product fixes made by this audit: **none**.
