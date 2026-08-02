---
task_id: OTH-20260802-agent-governance-sync
status: implementing
branch: dudantas/OTH-20260802-agent-governance-sync
base_branch: main
created: 2026-08-02
updated: 2026-08-02
related_pr: ""
owned_paths:
  - AGENTS.md
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/GOVERNANCE_CONTRACT.json
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/tasks/TASK_TEMPLATE.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
search_first: []
optional_reads: []
---

# Synchronize shared agent governance

## Goal

Apply the shared governance correction and remove the stale mandatory `dudantas/` branch-prefix rule for future tasks.

## Acceptance criteria

- Shared status, task-budget, audit and exact-head rules are consistent.
- Future branch naming uses the repository owner or task policy instead of a stale external username.
- Checkpoint validation accepts waiting/completed and NOT_APPLICABLE.
- Governance checks pass on the final PR head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-02T12:33:00Z
head: UNKNOWN
branch: dudantas/OTH-20260802-agent-governance-sync
pr: none
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.md
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/GOVERNANCE_CONTRACT.json
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/tasks/TASK_TEMPLATE.md
proven:
  - The current root policy and task template require a dudantas branch prefix in a blakinio-owned repository.
  - The checkpoint contract rejects waiting and completed states.
derived:
  - A repository-owner-neutral branch rule removes the stale identity dependency.
unknown:
  - Exact governance workflow results on the future PR head.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses: []
changed_paths:
  - docs/agents/tasks/active/OTH-20260802-agent-governance-sync.md
validation:
  - command: Agent Governance workflow
    result: NOT_RUN
    evidence: PR not yet opened
blockers: []
next_action: update the shared governance documents and stale branch-prefix policy
```
