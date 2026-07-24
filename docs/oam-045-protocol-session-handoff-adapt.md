# OAM-045 protocol session handoff target adaptation

## Final disposition

`protocol-session-handoff → ADAPT`.

The inherited state machine is retained, but one target-owned correctness defect requires a bounded production guard: a `ProtocolSessionHintLease` carries a 30-second `expiresAt` value that was not checked during consumption. This allowed an expired lease to consume a reusable hint whose independent lifetime can extend to 24 hours.

## Exact baselines

- Canary OAM-045 preflight merge: `2798dce948d8bf27f9b1325356d6db4676a8b6ba`
- Otheryn task-start main: `e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6`
- reviewed current upstream: `opentibiabr/canary@7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- live legacy Canary preflight baseline: `blakinio/canary@92c550b41d0f7d1c8c71f4b85dfa81dfb6488f4f`
- physically tested OAM-006 Otheryn revision: `c547d8ad70ef1252624c255476e6cb83fa125e14`

Before adaptation, target, current upstream, legacy Canary and the OAM-006 tested target revision share exact blobs:

- `src/server/network/protocol/protocol_session_hint.hpp`: `446e7769196fb9a750e13c8402b38c8752243729`
- `src/server/network/protocol/protocol_session_hint.cpp`: `3e57e16649e20121f52c6c4b67b632808b7af363`

Source identity is continuity evidence, not proof that every state transition or security property is correct.

## Canonical responsibility

This package owns the bounded in-process protocol-profile hint state machine:

- hint registration by remote IP, profile, session and character set;
- profile-allowance filtering;
- bounded capacity and oldest-entry eviction;
- overlapping-character replacement;
- lease selection by IP and optional wire behavior;
- ambiguous mixed-wire rejection;
- session hash, character and client-version matching;
- one-shot consumption;
- reusable hint refresh and explicit cleanup;
- hint and lease expiry enforcement.

It does not own account authentication, secure login-token issuance/redemption, transport framing/checksum/sequence/XTEA/compression, login packet serialization, game-world player ownership, generic distributed fencing or physical-client orchestration.

## Isolated defect

`claimByIp()` sets `lease.expiresAt = now + 30 seconds`. Reusable hints can remain valid for 24 hours. The inherited `consumeAndResolveProfile()` checked only whether the lease object was structurally non-empty and then searched the still-valid hint collection; it never rejected `lease.expiresAt <= now`.

Consequently, a stale lease could remain usable long after its claim window, provided its candidate reusable hint still existed. The lease deadline field was therefore semantically ineffective.

## Bounded adaptation

`consumeAndResolveProfile()` now obtains the current steady-clock time and fails closed before locking or examining hint candidates when the lease deadline has passed:

```cpp
const auto now = std::chrono::steady_clock::now();
if (lease.expiresAt <= now) {
    return std::nullopt;
}
```

No TTL duration, hash representation, capacity policy, matching rule, reusable policy, profile registry, login flow or transport behavior is changed.

## Focused target contract

`tests/unit/server/network/protocol/oam_045_protocol_session_handoff_test.cpp` covers:

- exact session, case-insensitive character and client-version matching;
- one-shot consumption and removal;
- reusable reclaim, refresh and explicit behavior-scoped cleanup;
- rejection of an expired lease while preserving the independently valid reusable hint;
- overlapping-character replacement by a newer registration;
- fail-closed mixed-wire ambiguity and explicit behavior filtering;
- blocked-profile registration rejection;
- the 512-entry capacity boundary and oldest-entry eviction.

The fixture uses local store instances and the existing unit-test target. It does not add a second harness or a production test seam.

## Evidence classification

### Confirmed

- Public state transitions above are exercised by focused deterministic fixtures.
- Current-profile hints are one-shot under the reviewed registry.
- Tibia 11.00 hints are reusable under the reviewed non-modern initial wire behavior.
- Blocked OTCv8 registration fails closed.
- Expired leases fail closed after the adaptation.

### Source-only

- Hint TTL is 30 seconds for modern behavior and 24 hours for reusable behavior.
- Session values are stored as SHA-256 strings rather than plaintext.
- A process-local mutex serializes each store operation.

### Unresolved or explicitly unclaimed

- Cryptographic strength, collision handling or constant-time comparison of the session hash.
- Replay resistance across the complete login-to-game flow.
- Race freedom outside the reviewed process-local mutex boundary.
- Multi-process or distributed consistency.
- Which hint branches were exercised by OAM-006 physical login/relog.
- Physical-client parity for Tibia 11.00, CipSoft 8.60 or OTCv8.

## Conclusion

The exact inherited implementation cannot be accepted unchanged because the lease deadline was not enforced. A single package-owned guard plus focused deterministic fixtures supports bounded `ADAPT`; no broader rewrite or ownership expansion is justified.
