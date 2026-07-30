---
task_id: OTH-20260730-prs-program-coordination
status: active
branch: dudantas/prs-program-coordination
base_branch: main
start_sha: 30ad4f41987481219faf43fdab51596a0bec4732
created: 2026-07-30
updated: 2026-07-30
related_issue: "233"
related_pr: "239"
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/agents/tasks/archive/OTH-20260730-prs003d-mutation-admission-policy.md
  - docs/agents/tasks/archive/OTH-20260730-prs003d-runtime-bank-mutation-gate.md
  - docs/agents/tasks/archive/OTH-20260730-prs003d-bounded-draining.md
  - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
search_first:
  - open PRS issues
  - open PRS pull requests
  - docs/agents/tasks/active/
  - docs/agents/tasks/archive/
  - matching dudantas/prs branches
---

# PRS program coordination — PRS-003D through PRS-008

## Mission

Coordinate the complete terminal lifecycle of PRS-003D, PRS-003E, durable PRS-004, PRS-005, PRS-006, PRS-007, PRS-008, the independent final audit and closure of #233 and #116. This record owns coordination evidence only and never authorizes feature, schema, migration, runtime, save, handoff or deployment implementation by the coordinator.

## Live baseline

- current audited `main`: `b7cb8fdbb90fafcab0c77ff594abb20619e6a98c`;
- coordination issue: #233, open;
- parent resilience tracker: #116, open;
- coordinator PR: #239, refreshed to current main and restricted to this file;
- PRS-003D-A/B/C: terminal;
- PRS-003E-A: terminal through feature #238, lifecycle #258, finalizer #259 and evidence #260;
- duplicate PR #261: closed without merge;
- stale PRS-003E-A refs: neutralized to current main;
- PRS-003E-B issue #262: open, dependency gate open, branch/task/owned paths not yet created;
- PRS-003E-C and PRS-004+ feature gates: closed.

## Dependency graph

```text
terminal PRS-003C-B
  ├─> terminal PRS-003D-A
  │     └─> terminal PRS-003D-B
  │           └─> terminal PRS-003D-C
  │
  └─> terminal PRS-003E-A
          └─> active PRS-003E-B
                  └─> PRS-003E-C

terminal PRS-003D + terminal PRS-003E
  └─> PRS-004B
        └─> PRS-004C
              └─> PRS-004D
                    └─> PRS-004E
                          └─> PRS-004F

terminal durable PRS-004
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
    pr: 236
    base_sha: 35b1a3f5ffe775d2973df6f996f2a966e7d4d761
    head_sha: 24b8bd872382b48f81c717ed98a8d0e3266dbe5d
    owned_paths:
      - docs/architecture/prs-003d-mutation-admission-policy.md
      - src/game/database_outage_mutation_admission_policy.hpp
      - tests/unit/game/database_outage_mutation_admission_policy_test.cpp
      - tests/unit/game/CMakeLists.txt
    actual_changed_paths: same_as_owned_paths
    gate_state: terminal
    ci: PASS:30523296793
    required: PASS:30523296740
    autofix: PASS:30523296602
    dedicated_checks: deterministic mutation-admission policy tests PASS
    discussion_state: clean
    freshness: behind_by=0 at merge
    merge_state: merged:7e7f3b65751a2348146286018454e428f7732c53
    lifecycle_pr: 244
    finalizer_pr: 245
    terminal: true
    blockers: []
    next_action: none

  - package: PRS-003D
    slice: PRS-003D-B
    issue: 248
    branch: dudantas/prs-003d-b
    task_record: docs/agents/tasks/archive/OTH-20260730-prs003d-runtime-bank-mutation-gate.md
    pr: 249
    base_sha: 704405c625278c7ec4d197ebd03e4c3d829c76ef
    head_sha: c963aef818ff2fcf034cf9f979b2d2f415b26a15
    owned_paths:
      - docs/architecture/prs-003d-runtime-bank-mutation-gate.md
      - src/game/database_outage_mutation_gate.hpp
      - src/game/bank/bank.cpp
      - tests/unit/game/database_outage_mutation_gate_test.cpp
      - tests/unit/game/CMakeLists.txt
    actual_changed_paths: same_as_owned_paths
    gate_state: terminal
    ci: PASS:30529636790
    required: PASS:30529636278
    autofix: PASS:30529636233
    dedicated_checks: live bank mutation-gate tests PASS
    discussion_state: clean
    freshness: behind_by=0 at merge
    merge_state: merged:e18467d1f79e5388ec3bb824815dd8ecd0103c06
    lifecycle_pr: 250
    finalizer_pr: 251
    terminal: true
    blockers: []
    next_action: none

  - package: PRS-003D
    slice: PRS-003D-C
    issue: 253
    branch: dudantas/prs-003d-c
    task_record: docs/agents/tasks/archive/OTH-20260730-prs003d-bounded-draining.md
    pr: 254
    base_sha: b66241361d2cd1d97ee9c5a3fc28ee0677f39b8b
    head_sha: 8745ffdcd14bc6e99f99e712ba030162d32094e3
    owned_paths:
      - docs/architecture/prs-003d-bounded-draining.md
      - src/database/database_failure_classification.hpp
      - src/database/database.cpp
      - src/game/database_outage_drain_orchestrator.hpp
      - src/game/scheduling/save_manager.hpp
      - src/game/scheduling/save_manager.cpp
      - tests/unit/database/database_failure_classification_test.cpp
      - tests/unit/game/database_outage_drain_orchestrator_test.cpp
      - tests/unit/game/CMakeLists.txt
      - docs/agents/tasks/archive/OTH-20260730-prs003d-bounded-draining.md
    actual_changed_paths: exact ten-path feature scope plus archive lifecycle path
    gate_state: terminal
    ci: PASS:30537779771
    required: PASS:30537779602
    autofix: PASS:30537779604
    dedicated_checks: full CTest and bounded-drain evidence PASS
    discussion_state: clean
    freshness: behind_by=0 at merge
    merge_state: merged:db059bfa6a92f23922b236e0463ee457f1a27179
    lifecycle_pr: 255
    finalizer_pr: 256
    terminal: true
    blockers: []
    next_action: none

  - package: PRS-003E
    slice: PRS-003E-A
    issue: 232
    branch: dudantas/prs-003e-a
    task_record: docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
    pr: 238
    base_sha: 732b8d76cb3a6e344f3503f6cb7b003a7e0d72b1
    head_sha: 91f90c9325cbabcfd67d16e09317daa4aea1b47b
    owned_paths:
      - .github/workflows/prs-003e-database-outage.yml
      - tests/integration/prs_003e/database_outage_injector.cpp
      - tests/integration/prs_003e/run_disposable_mariadb_outage.sh
      - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
    actual_changed_paths: exact four-path feature scope; one-file terminal archive evidence
    gate_state: terminal
    ci: PASS:30578360728
    required: PASS:30578360313
    autofix: PASS:30578360325
    dedicated_checks: PASS:30578360334
    discussion_state: clean
    freshness: behind_by=0 at feature/lifecycle/finalizer/evidence merges
    merge_state: merged:09297920ffa15feea2a05b24909d58b8e2a33e2a
    lifecycle_pr: 258
    finalizer_pr: 259
    terminal: true
    blockers: []
    next_action: none

  - package: PRS-003E
    slice: PRS-003E-B
    issue: 262
    branch: null
    task_record: docs/agents/tasks/active/OTH-20260730-prs003e-b-recovery-evidence.md
    pr: null
    base_sha: b7cb8fdbb90fafcab0c77ff594abb20619e6a98c
    head_sha: null
    owned_paths: []
    actual_changed_paths: []
    gate_state: open_for_live_discovery_and_exact_ownership_freeze
    ci: NOT_RUN
    required: NOT_RUN
    autofix: NOT_RUN
    dedicated_checks: NOT_RUN
    discussion_state: issue_created_no_pr
    freshness: must_start_from_current_main
    merge_state: not_started
    lifecycle_pr: null
    finalizer_pr: null
    terminal: false
    blockers:
      - exact owned_paths and feature branch must be created by the execution agent after live conflict audit
    next_action: create the canonical branch and one active task record, freeze disjoint owned_paths, then implement only bounded recovery evidence/probes

  - package: PRS-003E
    slice: PRS-003E-C
    issue: null
    branch: null
    task_record: null
    pr: null
    base_sha: null
    head_sha: null
    owned_paths: []
    actual_changed_paths: []
    gate_state: closed_until_terminal_PRS-003E-B
    ci: NOT_RUN
    required: NOT_RUN
    autofix: NOT_RUN
    dedicated_checks: NOT_RUN
    discussion_state: none
    freshness: not_applicable
    merge_state: blocked
    lifecycle_pr: null
    finalizer_pr: null
    terminal: false
    blockers:
      - PRS-003E-B issue 262 is not terminal
    next_action: none_until_gate_opens

  - package: PRS-004
    slice: PRS-004B-through-PRS-004F
    issue: 235
    branch: null
    task_record: null
    pr: null
    base_sha: null
    head_sha: null
    owned_paths: []
    actual_changed_paths: []
    gate_state: closed_until_terminal_PRS-003E-C
    ci: NOT_RUN
    required: NOT_RUN
    autofix: NOT_RUN
    dedicated_checks: NOT_RUN
    discussion_state: package_issue_only
    freshness: not_applicable
    merge_state: blocked
    lifecycle_pr: null
    finalizer_pr: null
    terminal: false
    blockers:
      - PRS-003E is not terminal
    next_action: read_only_discovery_only

  - package: PRS-005
    slice: one-critical-operation
    issue: 237
    branch: null
    task_record: null
    pr: null
    base_sha: null
    head_sha: null
    owned_paths: []
    actual_changed_paths: []
    gate_state: closed_until_terminal_durable_PRS-004
    ci: NOT_RUN
    required: NOT_RUN
    autofix: NOT_RUN
    dedicated_checks: NOT_RUN
    discussion_state: package_issue_only
    freshness: not_applicable
    merge_state: blocked
    lifecycle_pr: null
    finalizer_pr: null
    terminal: false
    blockers:
      - durable PRS-004 is not terminal
    next_action: read_only_discovery_only

  - package: PRS-006
    slice: one-SQL-KV-domain
    issue: 240
    branch: null
    task_record: null
    pr: null
    base_sha: null
    head_sha: null
    owned_paths: []
    actual_changed_paths: []
    gate_state: closed_until_terminal_PRS-005
    ci: NOT_RUN
    required: NOT_RUN
    autofix: NOT_RUN
    dedicated_checks: NOT_RUN
    discussion_state: package_issue_only
    freshness: not_applicable
    merge_state: blocked
    lifecycle_pr: null
    finalizer_pr: null
    terminal: false
    blockers:
      - PRS-005 is not terminal
    next_action: read_only_discovery_only

  - package: PRS-007
    slice: manual-replica-failover
    issue: 241
    branch: null
    task_record: null
    pr: null
    base_sha: null
    head_sha: null
    owned_paths: []
    actual_changed_paths: []
    gate_state: closed_until_terminal_PRS-006
    ci: NOT_RUN
    required: NOT_RUN
    autofix: NOT_RUN
    dedicated_checks: NOT_RUN
    discussion_state: package_issue_only
    freshness: not_applicable
    merge_state: blocked
    lifecycle_pr: null
    finalizer_pr: null
    terminal: false
    blockers:
      - PRS-006 is not terminal
    next_action: read_only_discovery_only

  - package: PRS-008
    slice: production-compose-hardening
    issue: 242
    branch: null
    task_record: null
    pr: null
    base_sha: null
    head_sha: null
    owned_paths: []
    actual_changed_paths: []
    gate_state: closed_until_terminal_PRS-007
    ci: NOT_RUN
    required: NOT_RUN
    autofix: NOT_RUN
    dedicated_checks: NOT_RUN
    discussion_state: package_issue_only
    freshness: not_applicable
    merge_state: blocked
    lifecycle_pr: null
    finalizer_pr: null
    terminal: false
    blockers:
      - PRS-007 is not terminal
    next_action: read_only_discovery_only

  - package: FINAL-AUDIT
    slice: independent-terminal-audit
    issue: 243
    branch: null
    task_record: null
    pr: null
    base_sha: null
    head_sha: null
    owned_paths: []
    actual_changed_paths: []
    gate_state: closed_until_terminal_PRS-003D-through-PRS-008
    ci: NOT_RUN
    required: NOT_RUN
    autofix: NOT_RUN
    dedicated_checks: NOT_RUN
    discussion_state: audit_issue_only
    freshness: not_applicable
    merge_state: blocked
    lifecycle_pr: null
    finalizer_pr: null
    terminal: false
    blockers:
      - PRS-003E-B through PRS-008 are not terminal
    next_action: read_only_discovery_only
```

## Conflict and safety controls

- one active owner per path;
- later packages remain read-only while gated;
- duplicate implementation or metadata PRs close without merge after canonical patch comparison;
- every merge requires exact-head successful checks, clean discussion, exact changed paths, mergeable state and `behind_by=0`;
- all merges use squash with `expected_head_sha`;
- no reconnect, ping recovery, arbitrary SQL replay, unknown-outcome write retry, unbounded retry/drain, automatic resume, automatic promotion, automatic rollback, Redis-only writer authority, success before durable commit, production credentials/data or unsupported RPO/RTO claims.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T23:08:00+02:00
head: b7cb8fdbb90fafcab0c77ff594abb20619e6a98c
head_scope: current main after terminal PRS-003E-A; this coordinator-only commit refreshes registry and opens PRS-003E-B governance
branch: dudantas/prs-program-coordination
pr: 239
status: active
context_routes:
  - production-resilience
  - coordination
  - database-persistence
  - ci
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
proven:
  - PRS-003D-A/B/C are terminal with full feature, lifecycle and finalizer evidence.
  - PRS-003E-A is terminal through PRs 238, 258, 259 and 260.
  - Duplicate PR 261 is closed without merge and stale E-A refs are neutralized.
  - Issue 262 is the only PRS-003E-B issue and no E-B branch or PR existed at issue creation.
  - PRS-003E-C and PRS-004+ feature gates remain closed.
derived:
  - PRS-003E-B may now create one branch/task and exact disjoint ownership.
unknown:
  - PRS-003E-B exact owned paths and implementation head.
conflicts: []
first_failure:
  marker: duplicate-finalizer-evidence-pr-261
  result: CONTAINED
  evidence: canonical PR 260 merged; duplicate 261 closed without merge and its branch was neutralized
rejected_hypotheses:
  - merge duplicate metadata patches
  - reserve PRS-003E-C or PRS-004 source paths before their gates open
  - automatic reconnect, replay or maintenance resume
changed_paths:
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
validation:
  - command: live GitHub preflight and terminal archive audit
    result: PASS
    evidence: main, issues, PRs, branches, task archives, exact checks and lifecycle merges were re-audited
  - command: coordinator changed-path audit
    result: PASS
    evidence: PR 239 is restricted to this one coordinator-owned path after branch refresh
  - command: exact-head Required and coordinator merge audit
    result: NOT_RUN
    evidence: this refreshed coordinator head requires replacement checks before merge
blockers: []
next_action: validate exact-head PR 239, then monitor issue 262 for one canonical branch, task record and disjoint owned_paths
```
