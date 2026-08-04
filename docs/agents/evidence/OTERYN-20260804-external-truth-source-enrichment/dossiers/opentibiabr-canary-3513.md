# Dossier — `opentibiabr/canary#3513`

## Identity

```yaml
canonical_key: opentibiabr/canary#3513
predecessor_row: 32
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: zone-login-client-state
research_status: COMPLETE
```

## Source claim

- Current title: `Client crash login Zone::afterEnter`
- Source URL: `https://github.com/opentibiabr/canary/issues/3513`
- Exact claim: when a player logs in while already inside a zone whose `ZoneEvent.afterEnter` calls `Player:changeSpeed()`, the official 13.40 client crashes; the reporter reproduced this five times.
- Claimed affected version/protocol: Canary through `19bf3e1dfec65ab7d656966a32428642fd11dec1`, official client 13.40, Windows.
- Claimed reproduction: create a zone, register the supplied `afterEnter` callback, enter the zone, log out and log in again.
- Claimed expected behavior: login completes without a client crash and the speed state is applied or safely deferred.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue | `opentibiabr/canary` | Issue `#3513`, open, `Status: Pending Test` | 2026-08-04 | exact script and 5/5 reported crashes on client 13.40 | primary claim | no client crash dump, packet capture or independent reproduction |
| S2 | repository code | four server lines | pinned audit revisions | 2026-08-04 | `ZoneEvent.afterEnter` directly invokes the Lua callback after the zone-enter event | primary static evidence | callback timing relative to login packet ordering is not proven statically by this file alone |
| S3 | repository code | `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | 2026-08-04 | `sendChangeSpeed` emits opcode `0x8F`, creature ID, base speed and speed immediately to the output buffer | target packet evidence | does not establish whether the creature is already known to a specific client at that point |
| S4 | repository code | `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | 2026-08-04 | maintained client parses creature-speed packets and returns safely when the creature ID is not known | client comparison | not the proprietary 13.40 client named by the reporter |

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: a zone-enter callback invoked during login must not produce a packet sequence that crashes the negotiated client; the speed update must be ordered after creature introduction or safely ignored/deferred by the client
version_boundary: source claim is explicitly official client 13.40; applicability to Otheryn current protocol profiles and maintained OTClient is unproven
evidence_basis:
  - S1
  - S3
  - S4
conflicts:
  - maintained OTClient explicitly tolerates an unknown creature in `parseCreatureSpeed`, so a crash there is not statically implied
  - no official 13.40 packet capture or crash trace establishes the exact malformed/order-sensitive sequence
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | `data/libs/systems/zones.lua`, `ZoneEvent:register` | `afterEnter` callback is still invoked directly | inconclusive | high for shared path, low for crash |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | `data/libs/systems/zones.lua`, `ZoneEvent:register` | file blob is identical to upstream Canary | inconclusive | high for shared path, low for crash |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | `data/libs/systems/zones.lua`, `ZoneEvent:register` | file blob is identical to upstream Canary | inconclusive | high for shared path, low for crash |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | `data/libs/systems/zones.lua`; `src/server/network/protocol/protocolgame.cpp::sendChangeSpeed` | direct callback remains; speed packet is written immediately using opcode `0x8F` | inconclusive, target path present | medium |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | `src/client/protocolgameparse.cpp::parseCreatureSpeed` | parser reads creature ID/base speed/speed; unknown creature logs and returns instead of dereferencing | not statically affected by the claimed unknown-creature failure mode | medium |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: isolated zone/login script input -> Otheryn login packet sequence -> observable client completion, disconnect or crash
preconditions:
  - disposable Otheryn world containing a small named zone
  - test player positioned inside the zone
  - audit-only Lua callback exactly matching Issue 3513
  - maintained OTClient build at the pinned revision
  - official 13.40 client only if a lawful reproducible test artifact and automation path are available
steps:
  - start Otheryn with packet-level debug capture limited to the test connection
  - log in outside the zone, enter it, log out and log in again five times with the callback enabled
  - repeat five times with the callback disabled as control
  - record ordering of creature introduction/map packets and opcode 0x8F
  - execute the same matrix with maintained OTClient; execute official 13.40 only when the client artifact and crash collection are available
expected_observations:
  - callback-enabled login either completes safely or produces a reproducible disconnect/crash correlated with the 0x8F ordering
  - disabled control completes without the correlated failure
artifacts:
  - zone-after-enter.lua
  - server-packet-order.log
  - maintained-otclient-5x.json
  - control-5x.json
  - official-1340-5x.json
  - client-crash-artifacts/
cleanup:
  - remove the audit-only zone script and disposable player/world state
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: exact official 13.40 reproduction depends on a lawful automatable client artifact; maintained OTClient control remains feasible
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
truth_status: PARTIALLY_PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: PENDING
owner_action: RESEARCH_REQUIRED
confidence: medium
rationale: the exact callback and immediate speed-packet path exist in all server lines, but static code does not prove the packet is emitted before client creature registration; maintained OTClient safely handles an unknown creature, while the reported official 13.40 crash lacks a packet capture or dump
```

## Drift and unresolved questions

- Drift after pinned revision: the Issue remains open and labelled pending test; later exact-head code must be compared before final aggregation.
- Unresolved questions:
  - Which login packet precedes opcode `0x8F` in the failing official-client trace?
  - Is the crash specific to official client 13.40, to a base-speed field/version mismatch, or to an earlier server revision?
  - Should zone callbacks be delayed until protocol login initialization completes, or should the protocol suppress updates for not-yet-known creatures?
- Product fixes made by this audit: **none**.
