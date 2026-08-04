# Dossier — `opentibiabr/canary#2542`

## Identity

```yaml
canonical_key: opentibiabr/canary#2542
predecessor_row: 65
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: rune-manual-target-hotkey-policy
research_status: COMPLETE
```

## Source claim

With `hotkeyAimbotEnabled` disabled, manually using Ultimate Healing or another rune on a player/party member is incorrectly rejected. A tested one-line change removes `creature->getPlayer()` from the hotkey restriction and leaves only `isHotkey`.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: the anti-hotkey setting blocks automatic/hotkey creature targeting only; explicit manual use-with on an eligible player or party member is validated by normal rune/PvP rules and remains allowed
version_boundary: audited game use-with/hotkey policy
evidence_basis: [opentibiabr/canary#2542, issue workaround]
conflicts:
  - community one-line fix must be checked against hostile manual runes, secure mode and protection zones
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | exact boolean predicate and tested correction supplied |
| CrystalServer | pinned | related use-with path | inconclusive |
| `blakinio/canary` | pinned | inherited source | potentially affected |
| Otheryn | pinned | bounded exact search did not find the historic literal; current equivalent policy requires path inspection/runtime | inconclusive |
| OTClient | pinned | distinguishes manual use versus hotkey request | protocol-critical control |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: manual/hotkey rune request + config/party/PvP state -> validation -> heal/damage/item consumption
preconditions: [two players in party and hostile/control states]
steps:
  - use UH and offensive runes manually and by hotkey with setting on/off
  - test self, party, neutral, hostile, summon and protection-zone targets
  - record request mode, return reason, effect and rune consumption
expected_observations:
  - manual eligible use works independently of hotkey restriction; hotkey targeting obeys configuration and all normal combat rules remain intact
artifacts: [rune-target-policy-matrix.json, use-packets.jsonl, combat-events.jsonl]
cleanup: [restore/discard actors/items]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: none
```

## Runtime execution

```yaml
execution_status: NOT_RUN
exact_otheryn_head: not applicable
run_ids: []
observations: []
artifacts: []
cleanup_result: not run
```

## Conclusions

```yaml
truth_status: PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: PENDING
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: source identifies the precise policy conflation and a successful correction; target behavior must be matrix-tested because its current code may have drifted from the literal predicate
```

## Drift and unresolved questions

- Preserve secure-mode and hostile-target protections while separating request origin from target type.
- Product fixes made by this audit: **none**.
