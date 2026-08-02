---
task_id: OTH-20260802-github-only-execution-v1
status: validating
project_lane: otheryn-governance
policy_version: 2
task_kind: documentation
implementation_authorized: false
branch: docs/github-only-execution-v1-20260802
base_branch: main
created: 2026-08-02
updated: 2026-08-02T12:05:00+02:00
feature_pr: "307"
owned_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/tasks/active/OTH-20260802-github-only-execution-v1.md
---

# GitHub-only execution v1

## Goal

Make the GitHub connection and GitHub Actions the mandatory fallback execution path when Codex or a local terminal is unavailable, while allowing gated autonomous merge or auto-merge and preserving separate production and protected-asset authorization.

## Acceptance

- [x] Add the normative GitHub-only execution contract.
- [x] Require it from the automatically loaded root bootstrap.
- [x] Route local agent execution through it.
- [x] Preserve bounded validation, asset safety, merge, auto-merge, secret, and production restrictions.
- [ ] Pass exact-head Required workflow.
- [ ] Complete autonomous merge and archival.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T12:05:00+02:00
head: 23cd1734d2f53aaf082454651cb87efeee3fb064
branch: docs/github-only-execution-v1-20260802
pr: 307
status: validating
phase: validate
session_id: chat-20260802-github-only-execution-v1
session_role: coordinator
execution_mode: chat-github
run_scope: coordinated_governance_rollout
continuation_policy: continue_until_real_stop
task_completion_policy: complete_merge_and_archive
user_communication: low_noise
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/tasks/active/OTH-20260802-github-only-execution-v1.md
proven:
  - Root and local routing require bounded GitHub-only execution when Codex or a local terminal is unavailable.
  - The owner durably authorizes gated autonomous merge or auto-merge of the current task PR.
  - Production deployment, protected assets, secrets, and protected environments remain separately unauthorized.
derived:
  - Missing Codex or a local terminal cannot justify stopping at a plan when GitHub execution is available.
unknown:
  - Exact-head Required workflow result after the auto-merge authorization update.
conflicts: []
first_failure:
  marker: none
  evidence: no validation failure observed
rejected_hypotheses:
  - GitHub-only execution authorizes protected asset changes
  - merge authority is equivalent to production-deployment authority
changed_paths:
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/tasks/active/OTH-20260802-github-only-execution-v1.md
validation: []
blockers: []
invocation_started_at: 2026-08-02T11:43:00+02:00
last_progress_at: 2026-08-02T12:05:00+02:00
runtime_limit_minutes: 60
no_progress_minutes: 15
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
context_reconstruction_attempts: 0
stall_warnings: 0
next_action: verify exact-head Required workflow, mark PR 307 ready, enable auto-merge, and archive after merge
```
