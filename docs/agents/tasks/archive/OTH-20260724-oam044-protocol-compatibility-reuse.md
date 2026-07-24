---
task_id: OTH-20260724-oam044-protocol-compatibility-reuse
status: completed
branch: dudantas/oam-044-protocol-compatibility-reuse
base_branch: main
created: 2026-07-24
updated: 2026-07-24
completed: 2026-07-24T19:19:00+02:00
last_verified_commit: "5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca"
related_pr: "100"
owned_paths:
  - docs/agents/tasks/archive/OTH-20260724-oam044-protocol-compatibility-reuse.md
  - docs/oam-044-protocol-compatibility-reuse.md
  - tests/unit/server/network/protocol/oam_044_protocol_compatibility_test.cpp
  - tests/unit/server/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - docs/oam-044-protocol-compatibility-reuse.md
optional_reads: []
---

# OAM-044 protocol compatibility target reuse proof

## Final disposition

`REUSE` with explicit server/client evidence boundaries.

Exact target/current-upstream registry identity, maintained-client feature inventory, unchanged OAM-006 physically tested current-profile roots and focused target fixtures support reuse without production mutation. Tibia 11.00/8.60 physical parity, exhaustive feature mapping and transport/login/session-handoff behavior remain explicit nonclaims.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T19:19:00+02:00
head: 5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca
branch: main
pr: 100
status: completed
context_routes:
  - agent-governance
  - cross-repo
  - protocol-client
owned_paths:
  - docs/agents/tasks/archive/OTH-20260724-oam044-protocol-compatibility-reuse.md
  - docs/oam-044-protocol-compatibility-reuse.md
  - tests/unit/server/network/protocol/oam_044_protocol_compatibility_test.cpp
  - tests/unit/server/CMakeLists.txt
proven:
  - Canary OAM-044 preflight selected protocol-compatibility with REVALIDATE and merged as 47611c10be8a2262d66421c9da65de6cc5c7264d.
  - Exact baselines were Otheryn 3f3c15917610e45430aa3902d110806dd25e10a8, upstream 7323503b3dc61ed86bf1f04a611b2d0aec64b35a, legacy Canary a5cafe1b7ce148af59c64d1382963ac6ac633334 and maintained client b3bcea2a95959bb4e92cc0b80cd49f36b63699b2.
  - Target and reviewed current-upstream share protocol_profile.hpp blob b9f1eec01e1ba348c22315be43ccefe74b210e45 and protocol_profile.cpp blob 5405c343cfa2c2d75a173d6678ecf8afc7690120.
  - Maintained-client modules/game_features/features.lua blob is 8b458b864ad765185fd856414f2c097d565a5a22.
  - Legacy Canary diverges at the server registry roots and includes transport-owned hardening rejected from this package.
  - OAM-006 physical run 29531221365 passed two protocol-1525 login/relog cycles against Otheryn c547d8ad70ef1252624c255476e6cb83fa125e14 and client 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f.
  - The OAM-006 tested server header, server implementation and client feature roots are byte-identical to the current OAM-044 roots.
  - The server registry exposes six explicit profiles: current, Tibia 11.00, three CipSoft 8.60 variants and blocked OTCv8 8.60.
  - The focused target contract covers the complete profile manifest, support/mapper states, selected current server/client feature pairs and bounded current/1100/860 login metadata.
  - Ready head 29d196e1b7d084813e24d368bd9e70329e16d0b3 passed Autofix 30106675779, CI 30106676001 and Required 30106675816.
  - Final synchronization head 62a42372e2225b71aaa0066cc934f684e830913c passed Autofix 30111297337, CI 30111297597 and Required 30111297475.
  - PR 100 had no comments, reviews or review threads; Otheryn main remained 3f3c15917610e45430aa3902d110806dd25e10a8 before merge.
  - PR 100 squash-merged as 5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca.
  - No production server, maintained-client, transport, login, session-handoff, packet, asset, schema or deployment path changed.
derived:
  - protocol-compatibility supports bounded REUSE because no target-owned defect was isolated and the selected current roots retain exact physical continuity.
  - Tibia 11.00 and 8.60 remain source-fixture boundaries rather than physical parity claims.
  - Legacy transport-profile differences remain assigned to network-transport and login-protocol.
unknown:
  - Exhaustive one-to-one or many-to-one correspondence between every ProtocolFeature and GameFeature.
  - Byte-level compatibility for every packet and registered profile.
  - Provenance and factual correctness of every proprietary asset signature.
  - Physical-client login/world-entry parity for Tibia 11.00 and CipSoft 8.60 variants.
  - OTCv8 8.60 readiness.
  - Production gameplay parity.
conflicts: []
first_failure:
  marker: none
  evidence: No protocol-compatibility-owned target defect was isolated.
rejected_hypotheses:
  - Import legacy transport-profile splitting into protocol-compatibility.
  - Infer semantic compatibility from similar feature names.
  - Extend the OAM-006 current-profile physical result to all legacy profiles.
  - Absorb network transport, login authentication or session-handoff behavior.
changed_paths:
  - docs/agents/tasks/archive/OTH-20260724-oam044-protocol-compatibility-reuse.md
  - docs/oam-044-protocol-compatibility-reuse.md
  - tests/unit/server/network/protocol/oam_044_protocol_compatibility_test.cpp
  - tests/unit/server/CMakeLists.txt
validation:
  - command: exact target/upstream/legacy/client source review
    result: PASS
    evidence: Exact blobs and bounded ownership classification are recorded in docs/oam-044-protocol-compatibility-reuse.md.
  - command: focused target protocol compatibility contract
    result: PASS
    evidence: CI runs 30106676001 and 30111297597 compiled and executed the registered unit-test matrix successfully.
  - command: feature exact-head gates
    result: PASS
    evidence: Ready head 29d196e1b7d084813e24d368bd9e70329e16d0b3 and final sync head 62a42372e2225b71aaa0066cc934f684e830913c passed all required gates.
  - command: feature merge and lifecycle readiness
    result: PASS
    evidence: PR 100 merged as 5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca after clean discussion audit and zero target-main drift.
blockers: []
next_action: Complete the separate Otheryn lifecycle archive PR, then hand the exact feature and lifecycle evidence to Canary governance without starting OAM-045.
```
