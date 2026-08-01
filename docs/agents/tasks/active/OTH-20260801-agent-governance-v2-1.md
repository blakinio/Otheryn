---
task_id: OTH-20260801-agent-governance-v2-1
status: implementing
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
phase: implement
session_id: chat-20260801-governance-v2-1
session_role: coordinator
execution_mode: chat-github
branch: dudantas/agent-governance-v2-1
base_branch: main
start_sha: UNKNOWN
issue: ""
feature_pr: ""
created: 2026-08-01
updated: 2026-08-01T23:46:00+02:00
lease_expires_at: 2026-08-02T02:46:00+02:00
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

Extend the v2 contracts with eval-driven prompts, trust/context boundaries, outcome verification, complete vertical slices, and mandatory PR hygiene, fresh audit, E2E, exact-head CI, archival, and autonomous continuation.

## Scope and invariants

Exactly the listed governance/documentation paths. No runtime, production, database, protocol, asset, upstream, workflow, or deployment mutation is authorized. Repository-specific safety and merge gates remain authoritative.

## Acceptance criteria

- [ ] Prompt regression evals, balanced cases, repeated trials, versioning, rollback, and ablation are normative.
- [ ] Completion is verified from environment outcome, not worker narrative.
- [ ] Retrieved content remains untrusted data and cannot redefine instructions or permissions.
- [ ] User-facing delivery requires all applicable backend/frontend integration and user-visible states.
- [ ] Closeout requires fresh audit, real E2E, final exact-head CI, resolved reviews, terminal related PRs, archive, and ownership release.
- [ ] Autonomous coordination continues to the next READY task after closeout.
- [ ] Exact-head required CI passes.
- [ ] This task is archived after merge.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-01T23:46:00+02:00
status: implementing
phase: implement
head: UNKNOWN
branch: dudantas/agent-governance-v2-1
pr: UNKNOWN
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
  - Autonomous programme continuation v2 is merged on main.
  - The owner explicitly authorized the cross-repository governance update.
derived:
  - Supporting contracts avoid turning the main prompting standard into an unmaintainable edge-case list.
unknown:
  - Exact PR number and exact-head workflow results until the draft PR is opened.
conflicts: []
first_failure:
  marker: none
  evidence: no exact-head failure classified yet
rejected_hypotheses:
  - encode durable rules only in chat
  - allow a task to complete with intentionally open related PRs
changed_paths:
  - docs/agents/tasks/active/OTH-20260801-agent-governance-v2-1.md
validation: []
blockers: []
next_action: add the v2.1 normative contracts and update the prompting entry points
```
