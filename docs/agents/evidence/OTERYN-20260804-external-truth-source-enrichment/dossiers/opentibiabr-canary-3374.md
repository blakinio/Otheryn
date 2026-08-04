# Dossier — `opentibiabr/canary#3374`

## Identity

```yaml
canonical_key: opentibiabr/canary#3374
predecessor_row: 51
source_type: issue
prior_bucket: INSUFFICIENT
prior_truth_status: UNPROVEN
family: bank-withdrawal-resource-exhaustion
research_status: COMPLETE
```

## Source claim

- Current title: `Withdrawing a lot of money crash`
- Source URL: `https://github.com/opentibiabr/canary/issues/3374`
- Exact refined claim: after crediting `10,000,000,000` gold, `!withdraw 10000000000` causes the server console to become unresponsive until interrupted; large money delivery performs excessive per-stack item work and can ignore practical delivery limits.
- Claimed affected environment: Windows for the original report; a reproducer and debugger log were later supplied, but the attachment was not normalized into the predecessor evidence.
- Claimed expected behavior: withdrawal validates a bounded deliverable amount, performs finite work, debits only the amount actually delivered and refunds/retains the remainder atomically.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue/comments | `opentibiabr/canary#3374` | open | 2026-08-04 | exact 10B command reproducer, unresponsive server symptom and per-stack hypothesis | primary claim | attached debugger log was not parsed; “crash” is described as a long-running freeze |
| S2 | maintainer discussion | same | comments | 2026-08-04 | identifies repeated stack insertion/search/status updates and missing practical limits | corroborating mechanism | comments include speculative mitigations and are not a benchmark |
| S3 | merged upstream PR | `opentibiabr/canary#3692` | merge `0c2f3e3cd6baa85291afa5f9af982465cc53c453` | 2026-08-04 | later implements actual-delivery accounting/refunds and integration tests for bank money handling | accepted upstream remediation evidence | merged after the pinned audit revision and does not by itself prove Otheryn state |
| S4 | target talkaction | `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | 2026-08-04 | `!withdraw` accepts any positive numeric amount and calls `Bank.withdraw` without a maximum or preflight | primary target evidence | underlying C++/Lua money delivery determines exact runtime cost |
| S5 | target NPC bank | `blakinio/Otheryn` | same | 2026-08-04 | NPC path computes coin piles and requires capacity/free backpack slots before withdrawal | partial mitigation evidence | does not protect the independent `!withdraw` talkaction path |

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: an arbitrarily large requested amount is rejected, bounded or partially delivered within a declared time/resource budget; bank debit equals actual delivered value and undelivered value remains/refunds without blocking the game loop
version_boundary: all player-accessible bank withdrawal entry points and the audited money-delivery API
evidence_basis:
  - S1
  - S3
  - S4
  - S5
conflicts:
  - the source calls the event a crash, while reproduced console behavior is an apparent synchronous resource-exhaustion freeze
  - a simple one-million limit mitigates the command but does not establish the correct systemic money-delivery contract
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | `data/scripts/talkactions/player/bank.lua`, bank/money delivery, tile insertion | source reproducer targets an unbounded command path; later PR 3692 indicates accepted remediation need | affected at pinned revision | high |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | same bank talkaction/API family | inherited unbounded command architecture | likely affected | medium-high |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | bank talkaction/API family | requires exact-head check for post-3692 backport | inconclusive at pinned snapshot | medium |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | `data/scripts/talkactions/player/bank.lua`, `data/npclib/npc_system/bank_system.lua`, player bank wrappers | `!withdraw` remains unbounded; NPC path has pile/slot preflight | affected through talkaction | high |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | client command/chat and inventory updates | client can initiate command but resource exhaustion is server-side | not a direct fix target | high |

## Deterministic runtime plan

```yaml
plan_status: NOT_APPLICABLE
system_boundary: isolated bank balance and withdrawal request -> money delivery work/game-loop responsiveness -> actual inventory/bank
  accounting
preconditions:
- isolated Otheryn account with disposable balance above 10B
- empty and constrained inventory variants
- game-loop/scheduler watchdog and item-allocation counters
steps:
- establish baseline for 100, 10k, 1M, 100M and 10B withdrawals through talkaction and NPC paths
- enforce a finite timeout and capture CPU, allocations, scheduler delay, delivered money and final bank balance
- repeat with no inventory slots, limited capacity and ground-drop conditions
- verify conservation: initial bank plus inventory/ground money equals final totals
- compare pinned target with the accepted upstream PR 3692 behavior in an isolated donor build
expected_observations:
- current talkaction is affected if work/time grows pathologically or blocks the scheduler for very large requests
- all failure/partial-delivery cases preserve money and return bounded feedback
artifacts:
- withdrawal-latency.csv
- scheduler-watchdog.jsonl
- allocation-counts.csv
- money-conservation.json
- server-stack-or-timeout.txt
- upstream-3692-control.json
- runtime-feasibility.md
cleanup:
- discard account/database/world state and generated coins
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: 'not applicable: pinned static evidence already reaches a target disposition; runtime execution would not change
  the audit decision'
```

## Runtime execution

```yaml
execution_status: NOT_RUN
exact_otheryn_head: not applicable
run_ids: []
observations:
- static comparison is sufficient for the target disposition; no game-world state was created
artifacts:
- runtime-feasibility.md
cleanup_result: not applicable
```

## Conclusions

```yaml
truth_status: PROVEN
static_conclusion: TARGET_AFFECTED
runtime_conclusion: NOT_APPLICABLE
owner_action: OPEN_FIX_PROGRAM
confidence: high
rationale: the source now contains a deterministic 10B reproducer and an accepted upstream remediation, while Otheryn's player
  talkaction still forwards an unbounded amount directly to bank delivery; quantitative bounded execution remains required
  before implementation Runtime execution is not applicable because the pinned static comparison already determines the target
  disposition.
```

## Drift and unresolved questions

- Drift after pinned revision: upstream PR `#3692` merged on 2026-05-21 and is authoritative drift evidence for the final repair programme.
- Unresolved questions:
  - Should Otheryn retain `!withdraw`, cap it, or route all entry points through one preflight/partial-delivery API?
  - What maximum synchronous work budget and coin representation should apply?
  - Does the final target head already contain any partial backport outside the pinned paths?
- Product fixes made by this audit: **none**.
