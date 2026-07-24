---
task_id: OTH-20260724-oam045-protocol-session-handoff-adapt
status: active
branch: dudantas/oam-045-protocol-session-handoff-adapt
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "b4c65b5d5c76324c247d90584adc7a16aa1fb597"
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-oam045-protocol-session-handoff-adapt.md
  - docs/oam-045-protocol-session-handoff-adapt.md
  - src/server/network/protocol/protocol_session_hint.cpp
  - tests/unit/server/network/protocol/oam_045_protocol_session_handoff_test.cpp
  - tests/unit/server/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - docs/oam-045-protocol-session-handoff-adapt.md
optional_reads: []
---

# OAM-045 protocol session handoff target adaptation

## Final disposition

`ADAPT`.

The inherited state machine remains structurally suitable, but `consumeAndResolveProfile()` ignored the 30-second lease deadline. A stale lease could consume a reusable hint that remains alive for 24 hours. The bounded adaptation rejects expired leases before candidate lookup.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T21:05:00+02:00
head: b4c65b5d5c76324c247d90584adc7a16aa1fb597
branch: dudantas/oam-045-protocol-session-handoff-adapt
pr: none
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - protocol-client
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-oam045-protocol-session-handoff-adapt.md
  - docs/oam-045-protocol-session-handoff-adapt.md
  - src/server/network/protocol/protocol_session_hint.cpp
  - tests/unit/server/network/protocol/oam_045_protocol_session_handoff_test.cpp
  - tests/unit/server/CMakeLists.txt
proven:
  - Canary OAM-045 preflight selected protocol-session-handoff with REVALIDATE and merged as 2798dce948d8bf27f9b1325356d6db4676a8b6ba.
  - Task-start Otheryn main is e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6 and reviewed upstream is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Target, current upstream, legacy Canary and the OAM-006 tested target share header blob 446e7769196fb9a750e13c8402b38c8752243729 and implementation blob 3e57e16649e20121f52c6c4b67b632808b7af363 before adaptation.
  - claimByIp assigns a 30-second lease deadline while reusable hints can live for 24 hours.
  - The inherited consume path did not inspect lease.expiresAt.
  - The adaptation adds one fail-closed lease-deadline guard and changes no TTL, hash, matching, profile, login or transport policy.
  - Focused fixtures cover one-shot and reusable flows, lease expiry, replacement, ambiguity, blocked profiles and capacity eviction.
derived:
  - protocol-session-handoff requires ADAPT rather than REUSE because a package-owned lease invariant was ineffective.
  - A bounded guard is sufficient; no rewrite or ownership expansion is justified.
unknown:
  - Security strength, collision behavior and timing properties of session-hash comparison.
  - Replay resistance and race freedom across complete login-to-game orchestration.
  - Multi-process or distributed behavior.
  - Which hint branches were physically exercised by OAM-006.
  - Physical-client parity for non-current profiles.
conflicts: []
first_failure:
  marker: ignored-lease-expiry
  evidence: consumeAndResolveProfile accepted any structurally valid lease without checking lease.expiresAt, while reusable candidates can outlive the 30-second lease.
rejected_hypotheses:
  - Accept exact source identity as sufficient REUSE proof.
  - Expand the fix into authentication, transport or generic session fencing.
  - Claim cryptographic or replay security from SHA-256 storage, mutex use or TTL enforcement.
  - Extend OAM-006 current-profile physical continuity to every branch and profile.
changed_paths:
  - docs/agents/tasks/active/OTH-20260724-oam045-protocol-session-handoff-adapt.md
  - docs/oam-045-protocol-session-handoff-adapt.md
  - src/server/network/protocol/protocol_session_hint.cpp
  - tests/unit/server/network/protocol/oam_045_protocol_session_handoff_test.cpp
  - tests/unit/server/CMakeLists.txt
validation:
  - command: exact target/upstream/legacy/OAM-006 source review
    result: PASS
    evidence: Baselines and exact pre-adaptation blobs are recorded in docs/oam-045-protocol-session-handoff-adapt.md.
  - command: focused protocol session handoff contract
    result: NOT_RUN
    evidence: The feature PR must compile and execute the registered unit tests.
  - command: Otheryn exact-head gates and audit
    result: NOT_RUN
    evidence: Autofix, CI and Required must pass on the final PR head before merge.
blockers:
  - Otheryn feature PR exact-head validation and merge
next_action: Open the bounded Otheryn feature PR, synchronize exact PR/head metadata, require exact-head Autofix, CI and Required, audit discussions and Otheryn-main drift, then squash-merge with the expected head.
```
