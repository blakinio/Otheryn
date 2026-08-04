# Dossier — `opentibiabr/canary#3160`

## Identity

```yaml
canonical_key: opentibiabr/canary#3160
predecessor_row: 60
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: chain-combat-target-filter
research_status: COMPLETE
```

## Source claim

Chain combat selects NPCs and protection-zone creatures as visual chain hops even though damage is not applied. Discussion identifies the script `CHAINPICKER` callback and supplies a tested C++ filter excluding NPCs, caster, protection-zone actors and secure-mode-ineligible players/summons.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: every chain hop passes both spell-specific picker rules and global combat legality before effects are emitted; NPCs, caster, protected/ineligible actors and disallowed summons never consume a hop or display a false impact
version_boundary: audited chain-combat framework
evidence_basis: [opentibiabr/canary#3160, issue discussion]
conflicts:
  - community C++ patch is broad and may duplicate or override spell-specific picker policy
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | failure and tested workaround reported |
| CrystalServer | pinned | related chain combat path | inconclusive |
| `blakinio/canary` | pinned | inherited source | potentially affected |
| Otheryn | pinned | bounded search did not prove equivalent global legality filtering before visual/effect emission | potentially affected |
| OTClient | pinned | displays the chain packets/effects | end-to-end observer |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: caster/spell picker + spectator set -> ordered chain targets/effects/damage
preconditions:
- fixture containing monsters, NPC, caster, players, player/monster summons and protection-zone boundaries
steps:
- cast player and monster chain spells with secure mode on/off
- vary spell-specific picker callbacks and maximum hops
- record considered, accepted and emitted targets plus damage/effects
- test deterministic ordering and no-target termination
expected_observations:
- only legal picker-approved targets receive a hop/effect and no invalid actor shortens the chain
artifacts:
- chain-target-matrix.jsonl
- effect-packets.jsonl
- combat-events.jsonl
- runtime-feasibility.md
cleanup:
- discard actors/fixtures
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
truth_status: PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: NOT_RUN_INFEASIBLE
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: 'source and successful workaround prove a target-selection legality gap, but implementation must preserve spell
  callbacks and deterministic chain ordering rather than copy the broad patch blindly Runtime execution is infrastructure-blocked:
  the repository has no deterministic game/client driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Decide which legality belongs in the generic engine versus each `CHAINPICKER` callback.
- Product fixes made by this audit: **none**.
