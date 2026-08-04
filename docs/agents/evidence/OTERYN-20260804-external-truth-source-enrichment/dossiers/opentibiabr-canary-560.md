# Dossier — `opentibiabr/canary#560`

## Identity

```yaml
canonical_key: opentibiabr/canary#560
predecessor_row: 74
source_type: issue
prior_bucket: INSUFFICIENT
prior_truth_status: UNPROVEN
family: network-listener-ipv6
research_status: COMPLETE
```

## Source claim

- Current title: `[Feature] IPV6 Support`
- Source URL: `https://github.com/opentibiabr/canary/issues/560`
- Exact claim: the server does not support accepting game-service connections over IPv6.
- Claimed affected version/protocol: not specified by the reporter; the Issue was opened on 2022-10-30 and remains open.
- Claimed reproduction: none.
- Claimed expected behavior: a configured server endpoint can listen on an IPv6 address and accept an IPv6 TCP connection.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue | `opentibiabr/canary` | Issue `#560`, open | 2026-08-04 | requests IPv6 connection support | primary claim | one-sentence report; no reproduction or version boundary |
| S2 | network standard | RFC Editor / IETF | RFC 3493, section 5.3 | 2026-08-04 | AF_INET6 sockets and `IPV6_V6ONLY` define IPv6-only/dual-stack listener behavior | primary specification | operating-system defaults may differ despite the RFC default |
| S3 | library documentation | Boost.Asio | current `ip::v6_only` reference | 2026-08-04 | Asio exposes `IPPROTO_IPV6/IPV6_V6ONLY` and IPv6 TCP endpoints | primary library documentation | current documentation, while the audited repositories may pin an earlier compatible Asio version |
| S4 | repository code | `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | 2026-08-04 | `ServicePort::open` parses only `address_v4` and binds only IPv4 endpoints | primary target evidence | static evidence; no exact-head runtime execution yet |
| S5 | repository code | `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | 2026-08-04 | donor line accepts IPv4, IPv6 or hostname and chooses `address_v6::any()` when appropriate | corroborating implementation | does not itself prove production portability on every OS |
| S6 | repository code | `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | 2026-08-04 | client uses protocol-independent TCP resolution/connect, but `getIp()` converts the peer address to IPv4 | client compatibility evidence | suggests partial rather than fully proven end-to-end IPv6 support |

External source locations:

- RFC 3493: `https://www.rfc-editor.org/info/rfc3493/`
- Boost.Asio `ip::v6_only`: `https://www.boost.org/doc/libs/latest/doc/html/boost_asio/reference/ip__v6_only.html`

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: when configured with a valid IPv6 literal or hostname resolving to IPv6, each public TCP service can create an IPv6 listener and accept an IPv6 connection without falling into the bind-retry path
version_boundary: protocol-independent transport requirement; application packet protocol is unchanged, but client and operating-system dual-stack behavior must be validated separately
evidence_basis:
  - S2
  - S3
conflicts:
  - RFC 3493 describes IPV6_V6ONLY default as off, but platform defaults and policy may differ; an implementation must choose and test its desired IPv4/IPv6 coexistence behavior explicitly
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | `src/server/server.cpp`, `ServicePort::open` | `address_v4::from_string(IP)` and `address_v4(INADDR_ANY)` are the only listener endpoints | affected | high |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | `src/server/server.cpp`, `ServicePort::open` | parses IPv4, then IPv6, then resolves a hostname; chooses v4/v6 wildcard from the resolved family | fixed/different implementation | high |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | `src/server/server.cpp`, `ServicePort::open` | listener path remains IPv4-only despite unrelated Platform session additions | affected | high |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | `src/server/server.cpp`, `ServicePort::open` | listener path is byte-for-byte equivalent to upstream Canary for endpoint construction and accepts only IPv4 | affected | high |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | `src/framework/net/connection.cpp`, resolver/connect and `getIp()` | resolver and socket connect are address-family agnostic; post-connect `getIp()` forces `to_v4()` | inconclusive/partial client support | medium |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: isolated Otheryn configuration with IPv6 loopback input -> ServicePort listener creation -> observable IPv6 TCP connection or bind-retry failure
preconditions:
  - Linux GitHub Actions runner with IPv6 loopback enabled
  - disposable Otheryn configuration and database/services required for startup
  - exact audited Otheryn head or a recorded later drift head
steps:
  - verify `::1` is present and create an isolated configuration with IP set to `::1` and bindOnlyGlobalAddress enabled
  - start Otheryn under a finite timeout and capture structured startup logs
  - inspect the game/login ports with `ss -lnt6`
  - attempt a TCP connection to `[::1]:<configured-port>` with an IPv6-capable probe
  - repeat the control case on `127.0.0.1` using otherwise identical configuration
expected_observations:
  - current target rejects or fails to parse `::1`, schedules the 15-second acceptor retry and exposes no IPv6 listener
  - IPv4 control binds and accepts the TCP probe
artifacts:
  - ipv6-loopback.txt
  - otheryn-ipv6-startup.log
  - listeners-ipv6.txt
  - ipv6-probe.txt
  - ipv4-control.txt
cleanup:
  - terminate the isolated process and remove disposable configuration/database state
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: none; runtime harness has not yet been executed in this audit
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
static_conclusion: TARGET_AFFECTED
runtime_conclusion: PENDING
owner_action: OPEN_FIX_PROGRAM
confidence: high
rationale: the target constructs only IPv4 addresses and wildcard endpoints, while the transport standard and Asio explicitly support IPv6 endpoints and the pinned CrystalServer line contains a concrete IPv6-aware listener implementation; an isolated runtime run remains required to complete the audit gate and characterize platform/client behavior
```

## Drift and unresolved questions

- Drift after pinned revision: not yet inspected beyond the task-start target snapshot; final aggregation must verify the exact final Otheryn head.
- Unresolved questions:
  - Should Otheryn use one dual-stack IPv6 listener, separate v4/v6 listeners, or an explicit configuration mode?
  - Must ban/rate-limit address storage be generalized from the current IPv4-sized representation before public IPv6 support is safe?
  - The maintained OTClient resolver can receive IPv6 endpoints, but `Connection::getIp()` assumes IPv4 and requires a separate client compatibility decision or fix verification.
- Product fixes made by this audit: **none**.
