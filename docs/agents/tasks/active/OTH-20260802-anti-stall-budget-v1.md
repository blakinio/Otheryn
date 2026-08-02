---
task_id: OTH-20260802-anti-stall-budget-v1
status: validating
project_lane: otheryn-governance
policy_version: 2
task_kind: documentation
implementation_authorized: false
branch: docs/anti-stall-budget-v1-20260802
base_branch: main
created: 2026-08-02
updated: 2026-08-02T10:42:00+02:00
feature_pr: "305"
owned_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/tasks/active/OTH-20260802-anti-stall-budget-v1.md
---

# Anti-stall and execution budget v1

## Goal

Prevent autonomous agents from becoming unbounded polling, retry, repair, or task-selection loops while preserving durable repository state.

## Acceptance

- [x] Add the normative anti-stall contract.
- [x] Require it from the automatically loaded root bootstrap.
- [x] Route local execution through it.
- [x] Limit CI checks, unchanged states, identical failures, repair cycles, context reconstruction, command duration, runtime and no-progress time.
- [ ] Pass exact-head Required workflow.
- [ ] Merge and archive.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T10:42:00+02:00
head: 7150e3a00a004cd76d738c53dce8c8b062c5574d
branch: docs/anti-stall-budget-v1-20260802
pr: 305
status: validating
phase: validate
session_id: chat-20260802-anti-stall-budget-v1
session_role: coordinator
execution_mode: chat-github
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/tasks/active/OTH-20260802-anti-stall-budget-v1.md
proven:
  - Required workflow 851 passed on the implementation head before this durable checkpoint update.
  - Root and local routing require bounded autonomous execution.
derived:
  - Agents must stop instead of polling indefinitely after budget or no-progress exhaustion.
unknown:
  - Exact-head Required result after this checkpoint update.
conflicts: []
first_failure:
  marker: none
  evidence: no implementation-gate failure observed
rejected_hypotheses:
  - autonomous continuation should permit unbounded overnight execution
changed_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/tasks/active/OTH-20260802-anti-stall-budget-v1.md
validation:
  - Required workflow 851 passed on head 7150e3a00a004cd76d738c53dce8c8b062c5574d
blockers: []
invocation_started_at: 2026-08-02T10:29:00+02:00
last_progress_at: 2026-08-02T10:42:00+02:00
runtime_limit_minutes: 60
no_progress_minutes: 15
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 0
stall_warnings: 0
next_action: verify exact-head Required workflow for PR 305
```
