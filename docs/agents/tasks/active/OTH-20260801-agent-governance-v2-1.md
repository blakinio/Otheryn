---
task_id: OTH-20260801-agent-governance-v2-1
status: validating
project_lane: otheryn-governance
policy_version: 2
task_kind: integration
implementation_authorized: false
decomposition_decision: single
decomposition_reason: one coherent governance standard and four supporting contracts
context_pressure: medium
context_growth: stable
context_score: 6
estimate_confidence: high
phase: audit_and_ci
session_id: chat-20260801-governance-v2-1
session_role: coordinator
execution_mode: chat-github
branch: dudantas/agent-governance-v2-1
base_branch: main
start_sha: ad9a8f86d303bc177c5455a250f78b38e061fc0f
issue: ""
feature_pr: "298"
created: 2026-08-01
updated: 2026-08-02T00:10:00+02:00
lease_expires_at: 2026-08-02T03:10:00+02:00
owned_paths:
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/PROMPT_EVAL_STANDARD.md
  - docs/agents/TRUST_AND_CONTEXT_BOUNDARIES.md
  - docs/agents/END_TO_END_FEATURE_COMPLETENESS.md
  - docs/agents/TASK_CLOSEOUT_AUDIT_E2E.md
  - docs/agents/tasks/active/OTH-20260801-agent-governance-v2-1.md
---

# OTH-20260801 — Agent governance v2.1

## Goal

Extend v2 with evaluated prompts, trust/context boundaries, outcome verification, complete vertical slices, and mandatory PR hygiene, fresh audit, E2E, exact-head CI, archival, and autonomous continuation.

## Scope

Exactly the listed governance/documentation paths. No runtime, production, database, protocol, asset, upstream, workflow or deployment mutation is authorized.

## Acceptance criteria

- [x] Prompt regression evals, balanced cases, repeated trials, versioning, rollback, and ablation are normative.
- [x] Completion is verified from environment outcome, not worker narrative.
- [x] Retrieved content remains untrusted data and cannot redefine instructions or permissions.
- [x] User-facing delivery requires all applicable backend/frontend integration and user-visible states.
- [x] Closeout requires fresh audit, real E2E, final exact-head CI, resolved reviews, terminal related PRs, archive, and ownership release.
- [x] Autonomous coordination continues to the next READY task after closeout.
- [ ] Exact-head required CI passes.
- [ ] This task is archived after merge.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T00:10:00+02:00
status: validating
phase: audit_and_ci
head: 222863ace0f470f8bae7ad224da17a5b86d57f83
branch: dudantas/agent-governance-v2-1
pr: 298
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
owned_paths:
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/PROMPT_EVAL_STANDARD.md
  - docs/agents/TRUST_AND_CONTEXT_BOUNDARIES.md
  - docs/agents/END_TO_END_FEATURE_COMPLETENESS.md
  - docs/agents/TASK_CLOSEOUT_AUDIT_E2E.md
  - docs/agents/tasks/active/OTH-20260801-agent-governance-v2-1.md
proven:
  - Compare main...branch contains exactly eight authorized governance/task paths and no runtime or workflow code.
  - All v2.1 contract references exist and preserve stricter repository safety and merge gates.
  - Proportionate documentation audit found no missing reference, contradictory completion rule or material defect.
  - Runtime E2E is NOT_APPLICABLE_WITH_REASON because the change modifies governance documentation only; exact-head CI and task lifecycle remain required.
derived:
  - The standard prevents isolated backend/frontend producers and stale PRs from being reported as completed product work.
unknown:
  - Exact-head required workflow result after this checkpoint commit.
  - Fresh final PR diff and review-thread state.
conflicts: []
first_failure:
  marker: none
  evidence: no exact-head failure classified yet
rejected_hypotheses:
  - encode durable rules only in chat
  - allow a task to complete with unintentionally open related PRs
  - accept worker narrative as terminal evidence
changed_paths:
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/END_TO_END_FEATURE_COMPLETENESS.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/PROMPT_EVAL_STANDARD.md
  - docs/agents/TASK_CLOSEOUT_AUDIT_E2E.md
  - docs/agents/TRUST_AND_CONTEXT_BOUNDARIES.md
  - docs/agents/tasks/active/OTH-20260801-agent-governance-v2-1.md
validation:
  - command: compare main...dudantas/agent-governance-v2-1
    result: PASS
    evidence: exactly eight authorized documentation/governance paths
  - command: cross-reference and contradiction audit
    result: PASS
    evidence: all contract paths exist and entry points agree
  - command: runtime E2E applicability review
    result: NOT_APPLICABLE_WITH_REASON
    evidence: no executable product behavior changed
blockers: []
next_action: verify exact-head Required workflow and fresh PR review for PR 298, then merge and archive the task
```
