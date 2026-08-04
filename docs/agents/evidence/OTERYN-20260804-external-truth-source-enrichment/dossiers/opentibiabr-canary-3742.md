# Dossier — `opentibiabr/canary#3742`

## Identity

```yaml
canonical_key: opentibiabr/canary#3742
predecessor_row: 24
source_type: issue
prior_bucket: INSUFFICIENT
prior_truth_status: UNPROVEN
family: gamestore-wire-efficiency
research_status: COMPLETE
```

## Source claim

- Current title: `GameStore - Optimization`
- Source URL: `https://github.com/opentibiabr/canary/issues/3742`
- Exact claims:
  1. identical disabled-reason strings are emitted repeatedly instead of once with shared indexes;
  2. the coin-balance packet is emitted twice after an offer purchase.
- Claimed affected version/protocol: modern GameStore packet family; reporter captured output on Linux using an external sniffer, but did not state client build or server revision.
- Claimed expected behavior: the disabled-reason table contains each distinct string once and every offer references its stable index; a successful purchase produces only the balance updates required by the negotiated protocol.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue | `opentibiabr/canary` | Issue `#3742`, open | 2026-08-04 | two packet-efficiency claims and screenshots from an external sniffer | primary claim | raw packet capture and client build are not attached as machine-readable evidence |
| S2 | repository code | `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | 2026-08-04 | `sendShowStoreOffers` inserts disabled reasons as strings but compares `disableTable.reason`, so equal strings never match | primary target evidence | proves duplicate-table construction, not client-visible byte counts for every profile |
| S3 | repository code | upstream/fork lineage | pinned audit revisions | 2026-08-04 | corresponding GameStore sender family exists in inherited code | cross-repository evidence | Crystal uses a different module layout and requires a separate packet trace for exact parity |
| S4 | target code search | `blakinio/Otheryn` | same | 2026-08-04 | balance update sender exists, but the available bounded search did not prove two purchase-path calls | negative/limitation evidence | absence from the searched sender file does not exclude another module or protocol-layer send |

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: disabled-reason strings are deduplicated by value and offers reference the correct zero- or one-based index required by the negotiated client; purchase balance packets are not redundantly duplicated
version_boundary: modern GameStore layout used by the target sender; exact index base and balance sequence require a known-good packet capture per supported profile
evidence_basis:
  - S1
  - S2
conflicts:
  - the code initializes a new reason at `#disableReasons` while Lua arrays are iterated from one, so both failed equality and index-base semantics require packet-level validation
  - the duplicate coin-balance subclaim remains unproven by the bounded source path inspection
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | `data/libs/gamestore/senders.lua`, purchase/player GameStore paths | inherited sender family contains the same string/table mismatch | affected for disabled-reason dedup | high |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | `data/modules/scripts/gamestore/init.lua`, protocol GameStore paths | different module organization; exact duplicate behavior not established | inconclusive | medium-low |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | corresponding GameStore sender paths | inherited implementation family | likely affected | medium-high |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | `data/libs/gamestore/senders.lua` | compares a string value as if it were a table with `.reason`; duplicate strings are appended | affected | high |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | GameStore packet parser family | relevant for index-base and packet-consumption validation; no source evidence establishes official-client byte parity | inconclusive | medium-low |

## Deterministic runtime plan

```yaml
plan_status: NOT_APPLICABLE
system_boundary: deterministic all-owned-mount category -> Otheryn GameStore packet bytes -> decoded reason table, offer indexes
  and balance packet count
preconditions:
- isolated account owning every mount in a small audit-only category
- packet capture/decoder for the negotiated maintained-client profile
- one deterministic successful low-cost purchase fixture
steps:
- request the category with N offers sharing one disabled reason and capture the complete response
- decode reason count, strings and every offer reason index
- repeat with two distinct disabled reasons as an index-order control
- execute one successful purchase and count balance-related opcodes from request through stable post-purchase state
- repeat five times and compare byte-identical results
expected_observations:
- current static defect predicts N repeated strings rather than one shared string for the all-owned category
- purchase path either emits one required balance sequence or reproduces the reported duplicate packet
artifacts:
- category-fixture.lua
- shared-reason.pcap.json
- two-reason-control.pcap.json
- purchase-balance-opcodes.jsonl
- decoder-version.txt
- runtime-feasibility.md
cleanup:
- discard isolated account/category state
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
truth_status: PARTIALLY_PROVEN
static_conclusion: TARGET_AFFECTED
runtime_conclusion: NOT_APPLICABLE
owner_action: OPEN_FIX_PROGRAM
confidence: high
rationale: Otheryn statically contains a value/type mismatch that prevents disabled-reason deduplication; the separate duplicate
  balance-packet claim remains pending packet capture and must not be treated as proven by association Runtime execution is
  not applicable because the pinned static comparison already determines the target disposition.
```

## Drift and unresolved questions

- Drift after pinned revision: final exact-head comparison is still required.
- Unresolved questions:
  - Which index base is required for each supported GameStore profile?
  - Is the purchase balance duplication in Lua, protocol C++, or intentional dual-resource reporting?
  - Can the reason table be made deterministic across Lua table iteration order without changing client semantics?
- Product fixes made by this audit: **none**.
