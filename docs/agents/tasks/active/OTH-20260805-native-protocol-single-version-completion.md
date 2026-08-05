---
task_id: OTH-20260805-native-protocol-single-version-completion
coordination_id: OTS-20260804-native-protocol-selection
status: waiting
agent: ChatGPT
branch: agents/ots-native-selection-otheryn-correction-20260804
base_branch: main
created: 2026-08-05T13:05:00+02:00
updated: 2026-08-05T13:05:00+02:00
risk: high
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
execution_mode: github-only
implementation_authorized: true
production_activation_authorized: false
related_pr: none
owned_paths:
  - docs/agents/tasks/active/OTH-20260805-native-protocol-single-version-completion.md
  - docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CORRESPONDENCE.md
modules_touched:
  - native-protocol-correspondence
cross_repo_tasks:
  - blakinio/Oteryn-Platform#540
  - OTC2-20260805-native-protocol-single-version-completion
required_reads:
  - AGENTS.md
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CORRESPONDENCE.md
  - docs/architecture/oteryn-native-gameplay-protocol.md
search_first:
  - live Platform correction PR and exact merged canonical commit
  - active Otheryn ownership, shared-path leases and open PRs
optional_reads: []
---

# OTH-20260805-native-protocol-single-version-completion

## Goal

Adopt the corrected canonical Platform contract with exactly `family = oteryn`, `native_protocol_version = 1`, no native profile dimension, and then implement the separately disabled Otheryn Game Session v2/native TLS-ASIO producer after correspondence merges.

## Acceptance criteria

- [ ] Correspondence pins the exact merged canonical Platform correction and corrected schema SHA-256.
- [ ] Correspondence contains no native profile field/value/catalogue/selection and preserves isolated Canary compatibility profiles.
- [ ] Correspondence exact-head CI and independent audit pass and the PR merges before runtime work.
- [ ] A later runtime branch implements Game Session v2, readiness, TLS/ALPN, parser, authoritative commands, snapshot/deltas and tests while disabled.
- [ ] Runtime exact-head CI, Canary regression, independent audits, merge, archive and ownership release complete.

## Ownership

```yaml
owned_paths:
  - docs/agents/tasks/active/OTH-20260805-native-protocol-single-version-completion.md
  - docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CORRESPONDENCE.md
modules:
  - native-protocol-correspondence
dependencies:
  - blakinio/Oteryn-Platform#540 merged with exact canonical schema digest
blockers:
  - canonical Platform correction is not yet merged
cross_repository_tasks:
  - OTERYN-20260805-native-protocol-single-version-completion
  - OTC2-20260805-native-protocol-single-version-completion
```

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-05T13:05:00+02:00
head: e9eb10a72f7b711c809eea19fcd280154fddebe1
branch: agents/ots-native-selection-otheryn-correction-20260804
pr: none
status: waiting
context_routes:
  - architecture
  - canary-integration
  - security
  - testing
owned_paths:
  - docs/agents/tasks/active/OTH-20260805-native-protocol-single-version-completion.md
  - docs/contracts/OTERYN_NATIVE_GAMEPLAY_PROTOCOL_CORRESPONDENCE.md
proven:
  - Current correspondence still pins the superseded profile-oriented Platform contract.
  - No active Otheryn task owns native protocol implementation paths.
  - Open PR #339 touches legacy protocolgame.cpp, so later native runtime must remain isolated or re-preflight after that PR becomes terminal.
  - Production activation is not authorized.
derived:
  - Correspondence cannot be finalized until Platform PR #540 merges and exposes an immutable canonical commit and schema digest.
unknown:
  - Exact corrected Platform merge commit and schema SHA-256.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Reuse protocol_profile.hpp as a native profile catalogue.
  - Implement native traffic inside the Canary listener or parser.
changed_paths:
  - docs/agents/tasks/active/OTH-20260805-native-protocol-single-version-completion.md
validation:
  - command: live ownership and open-PR preflight
    result: PASS
    evidence: native correspondence path is free; runtime overlap is documented for later re-preflight
blockers:
  - Platform PR #540 must merge first
next_action: After Platform PR #540 merges, update correspondence to its exact merge commit and corrected schema digest.
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 1
  session_id: OTS-20260805T1305+0200-otheryn-correspondence
  session_started_at: 2026-08-05T13:05:00+02:00
  checkpointed_at: 2026-08-05T13:05:00+02:00
  last_progress_at: 2026-08-05T13:05:00+02:00
  phase: wait-for-platform-contract-merge
  exact_head: e9eb10a72f7b711c809eea19fcd280154fddebe1
  pull_request: none
  active_operation: none
  external_run_ids: []
  operation_started_at: null
  wait_deadline_at: null
  check_generation: draft
  checks_used: 0
  status: waiting
  safe_to_resume: true
  resume_condition: Platform PR #540 is merged and exact canonical schema evidence is available
  next_action: Update Otheryn correspondence to the exact merged Platform correction.
```
