---
task_id: OTH-20260730-prs-program-coordination
status: active
branch: dudantas/prs-program-coordination
base_branch: main
start_sha: 30ad4f41987481219faf43fdab51596a0bec4732
created: 2026-07-30
updated: 2026-07-31
related_issue: "233"
related_pr: null
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
required_reads:
  - AGENTS.md
  - docs/agents/EXECUTION_PROTOCOL.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
search_first:
  - live main head
  - open PRS issues and pull requests
  - active task records
  - matching dudantas/prs branches
  - terminal archives
---

# PRS program coordination — PRS-003D through PRS-008

## Mission

Coordinate the terminal lifecycle of PRS-003D, PRS-003E, durable PRS-004, PRS-005, PRS-006, PRS-007, PRS-008, the independent final audit and closure of #233 and #116.

This record owns coordination evidence only. The coordinator does not implement feature, schema, migration, runtime, save, handoff or deployment code and does not claim feature paths.

## Live baseline

- audited `main`: `d5cea84e9e8c526ae7e0aaa30d78d91d0b668c22`;
- coordination issue #233: open;
- parent resilience tracker #116: open;
- PRS-003D-A/B/C: terminal;
- PRS-003E-A/B/C: terminal;
- duplicate E-C lifecycle PR #273: closed without merge;
- no open pull request at the PRS-004B gate audit;
- `schema.sql` still declares `db_version = 58`;
- PRS-004B execution issue #276: open, gate open, no branch/task/feature ownership yet;
- PRS-004C+ and PRS-005+ gates: closed.

## Dependency graph

```text
terminal PRS-003D + terminal PRS-003E
  └─> open PRS-004B
        └─> PRS-004C
              └─> PRS-004D
                    └─> PRS-004E
                          └─> PRS-004F
                                └─> PRS-005
                                      └─> PRS-006
                                            └─> PRS-007
                                                  └─> PRS-008
                                                        └─> independent audit
                                                              └─> close #233 and #116
```

## Ownership registry

```yaml
packages:
  - package: PRS-003D
    slice: PRS-003D-A
    issue: 231
    branch: dudantas/prs-003d-a
    task_record: docs/agents/tasks/archive/OTH-20260730-prs003d-mutation-admission-policy.md
    feature_pr: 236
    feature_head: 24b8bd872382b48f81c717ed98a8d0e3266dbe5d
    feature_merge: 7e7f3b65751a2348146286018454e428f7732c53
    ci: PASS:30523296793
    required: PASS:30523296740
    autofix: PASS:30523296602
    lifecycle_pr: 244
    finalizer_pr: 245
    terminal_evidence_pr: 247
    gate_state: terminal
    terminal: true
    blockers: []
    next_action: none

  - package: PRS-003D
    slice: PRS-003D-B
    issue: 248
    branch: dudantas/prs-003d-b
    task_record: docs/agents/tasks/archive/OTH-20260730-prs003d-runtime-bank-mutation-gate.md
    feature_pr: 249
    feature_head: c963aef818ff2fcf034cf9f979b2d2f415b26a15
    feature_merge: e18467d1f79e5388ec3bb824815dd8ecd0103c06
    ci: PASS:30529636790
    required: PASS:30529636278
    autofix: PASS:30529636233
    lifecycle_pr: 250
    finalizer_pr: 251
    terminal_evidence_pr: 252
    gate_state: terminal
    terminal: true
    blockers: []
    next_action: none

  - package: PRS-003D
    slice: PRS-003D-C
    issue: 253
    branch: dudantas/prs-003d-c
    task_record: docs/agents/tasks/archive/OTH-20260730-prs003d-bounded-draining.md
    feature_pr: 254
    feature_head: 8745ffdcd14bc6e99f99e712ba030162d32094e3
    feature_merge: db059bfa6a92f23922b236e0463ee457f1a27179
    ci: PASS:30537779771
    required: PASS:30537779602
    autofix: PASS:30537779604
    lifecycle_pr: 255
    finalizer_pr: 256
    terminal_evidence_pr: 257
    gate_state: terminal
    terminal: true
    blockers: []
    next_action: none

  - package: PRS-003E
    slice: PRS-003E-A
    issue: 232
    branch: dudantas/prs-003e-a-outage-injector
    task_record: docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
    feature_pr: 238
    feature_head: 91f90c9325cbabcfd67d16e09317daa4aea1b47b
    feature_merge: 09297920ffa15feea2a05b24909d58b8e2a33e2a
    ci: PASS:30578360728
    required: PASS:30578360313
    autofix: PASS:30578360325
    dedicated: PASS:30578360334
    lifecycle_pr: 258
    finalizer_pr: 259
    terminal_evidence_pr: 260
    gate_state: terminal
    terminal: true
    blockers: []
    next_action: none

  - package: PRS-003E
    slice: PRS-003E-B
    issue: 262
    branch: dudantas/prs-003e-b-recovery-evidence
    task_record: docs/agents/tasks/archive/OTH-20260730-prs003e-b-recovery-evidence.md
    feature_pr: 264
    feature_head: 34e6d4c3e812231174f7e55c4864d6fe73446197
    feature_merge: 79fd8e7218432bbd73cb0a19e8c581e4e885831c
    ci: PASS:30588063392
    required: PASS:30588063257
    autofix: PASS:30588063233
    dedicated: PASS:30588063252
    regression: PASS:30588063222
    lifecycle_pr: 265
    finalizer_pr: 267
    terminal_evidence_pr: 268
    gate_state: terminal
    terminal: true
    blockers: []
    next_action: none

  - package: PRS-003E
    slice: PRS-003E-C
    issue: 269
    branch: dudantas/prs-003e-c-operator-resume
    task_record: docs/agents/tasks/archive/OTH-20260731-prs003e-c-operator-resume.md
    feature_pr: 270
    feature_head: 29d80dd126fde49287f1e8a24b8937867cf17d85
    feature_merge: b967f07b98a36d4e7399bab4a0f409f8ac720e06
    ci: PASS:30613479213
    required: PASS:30613478930
    autofix: PASS:30613479017
    dedicated: PASS:30613478900
    regression: PASS:30613478901
    lifecycle_pr: 272
    lifecycle_head: cb25c6f5e46d25e711e16ebe434c4720fb6fc0c2
    lifecycle_required: PASS:30615112481
    lifecycle_merge: 360af9d42577b3ed088a084410fa56dbd51e32ca
    finalizer_pr: 274
    finalizer_head: eaba4ddf7971a56eda829e24d8611c91c8bffdfc
    finalizer_required: PASS:30615377548
    finalizer_merge: 07a21d0ae7ce4a4bcf8a1d0017525a2d6f721d08
    terminal_evidence_pr: 275
    terminal_evidence_head: 5cd0093b9ac2e9f31e18b13d4aaf7e4be111d7ed
    terminal_evidence_required: PASS:30615781267
    terminal_evidence_merge: d5cea84e9e8c526ae7e0aaa30d78d91d0b668c22
    duplicate_prs_closed_without_merge:
      - 273
    gate_state: terminal
    terminal: true
    blockers: []
    next_action: none

  - package: PRS-004
    slice: PRS-004B-durable-schema
    issue: 276
    canonical_branch: dudantas/prs-004b-durable-fence-schema
    task_record: docs/agents/tasks/active/OTH-20260731-prs004b-durable-fence-schema.md
    feature_pr: null
    base_sha: d5cea84e9e8c526ae7e0aaa30d78d91d0b668c22
    head_sha: null
    owned_paths: []
    actual_changed_paths: []
    gate_state: open_for_live_discovery_and_exact_ownership_freeze
    ci: NOT_RUN
    required: NOT_RUN
    autofix: NOT_RUN
    discussion_state: issue_created_no_pr
    freshness: must_start_from_current_main
    merge_state: not_started
    terminal: false
    blockers:
      - no authorized feature execution agent has created the canonical branch, active task or frozen owned_paths
    next_action: execution agent must run live source/conflict audit, freeze exact disjoint owned_paths and implement only the version-58 durable schema slice

  - package: PRS-004
    slice: PRS-004C-through-PRS-004F
    issue: 235
    gate_state: closed_until_terminal_PRS-004B_then_strictly_serialized
    terminal: false
    blockers:
      - PRS-004B issue 276 is not terminal
    next_action: read_only_discovery_only

  - package: PRS-005
    issue: 237
    gate_state: closed_until_terminal_durable_PRS-004
    terminal: false
    blockers:
      - PRS-004B-through-PRS-004F are not terminal
    next_action: read_only_discovery_only

  - package: PRS-006
    issue: 240
    gate_state: closed_until_terminal_PRS-005
    terminal: false
    blockers:
      - PRS-005 is not terminal
    next_action: read_only_discovery_only

  - package: PRS-007
    issue: 241
    gate_state: closed_until_terminal_PRS-006
    terminal: false
    blockers:
      - PRS-006 is not terminal
    next_action: read_only_discovery_only

  - package: PRS-008
    issue: 242
    gate_state: closed_until_terminal_PRS-007
    terminal: false
    blockers:
      - PRS-007 is not terminal
    next_action: read_only_discovery_only

  - package: FINAL-AUDIT
    issue: 243
    gate_state: closed_until_terminal_PRS-003D-through-PRS-008
    terminal: false
    blockers:
      - PRS-004B through PRS-008 are not terminal
    next_action: read_only_discovery_only
```

## Conflict and safety controls

- one active owner per feature path;
- later slices remain read-only while gated;
- duplicate implementation or lifecycle PRs close without merge after canonical patch comparison;
- every accepted merge requires exact-head successful checks, clean discussion, exact changed paths, mergeability and a final freshness audit;
- feature and lifecycle merges use repository-standard squash with expected-head protection;
- preserve no reconnect, ping recovery, arbitrary SQL replay, unknown-outcome write retry, unbounded retry/drain, automatic maintenance resume, automatic promotion, automatic rollback, Redis-only durable authority, success before durable commit, production credentials/data or unsupported RPO/RTO claims.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T10:25:00+02:00
phase: coordinate
execution_mode: chat-github
head: d5cea84e9e8c526ae7e0aaa30d78d91d0b668c22
branch: dudantas/prs-program-coordination
status: active
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
proven:
  - PRS-003D-A/B/C and PRS-003E-A/B/C are terminal
  - PRS-003E-C terminal evidence PR 275 merged as d5cea84e9e8c526ae7e0aaa30d78d91d0b668c22
  - no open PR existed at the PRS-004B gate audit
  - no prs-004b branch existed at the gate audit
  - schema.sql remains at version 58
  - issue 276 is the unique authorized PRS-004B execution issue
unknown:
  - PRS-004B exact owned_paths, implementation branch head and validation evidence
conflicts: []
first_failure:
  marker: concurrent-independent-main-advances-during-PRS-003E-C-lifecycle
  result: CONTAINED
  evidence: canonical lifecycle and finalizer completed; duplicate PR 273 closed without merge; terminal archive records exact evidence
blockers:
  - no authorized feature execution agent has started PRS-004B issue 276
last_completed_step: terminal PRS-003E-C recorded and PRS-004B gate opened with unique issue 276
next_action: authorized PRS-004B execution agent creates the canonical branch and active task, freezes exact disjoint owned_paths and implements only durable schema scope
```
