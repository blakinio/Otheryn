---
task_id: OTH-20260802-agent-governance-sync
status: waiting
branch: dudantas/OTH-20260802-agent-governance-sync
base_branch: main
created: 2026-08-02
updated: 2026-08-02
related_pr: "309"
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

- [x] Shared status, task-budget, audit and exact-head rules are consistent.
- [x] Future branch naming uses the repository owner or task policy instead of a stale external username.
- [x] Checkpoint validation accepts waiting/completed and NOT_APPLICABLE.
- [x] Required workflow passed on verified head `33d69eadf1f39513a99bcf3a74267ba096e73afd`.
- [ ] Coordinated Canary dependency is terminal and this PR is revalidated on its final metadata head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-02T13:52:00Z
head: 33d69eadf1f39513a99bcf3a74267ba096e73afd
branch: dudantas/OTH-20260802-agent-governance-sync
pr: 309
status: waiting
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
  - The root policy and task template use an owner-neutral task branch rule.
  - The portable contract accepts waiting, completed and NOT_APPLICABLE.
  - Task status is separated from terminal invocation result.
  - Required workflow run 30749324153 passed on head 33d69eadf1f39513a99bcf3a74267ba096e73afd.
  - PR 309 has zero unresolved review threads and changes only governance and task-record paths.
derived:
  - The stale identity dependency and shared contract contradictions are repaired without invalidating checkpoint version 1 records.
unknown:
  - Exact-head Required workflow conclusion after this durable checkpoint update.
conflicts: []
first_failure:
  marker: coordinated Canary dependency
  evidence: Canary PR 1063 is blocked until isolation PR 1064 completes through normal branch protection
rejected_hypotheses:
  - Game code or asset validation is required; this PR changes governance records only.
changed_paths:
  - AGENTS.md
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/GOVERNANCE_CONTRACT.json
  - docs/agents/tasks/TASK_TEMPLATE.md
  - docs/agents/tasks/active/OTH-20260802-agent-governance-sync.md
validation:
  - command: Required workflow run 30749324153
    result: PASS
    evidence: exact verified head 33d69eadf1f39513a99bcf3a74267ba096e73afd
  - command: review-thread audit
    result: PASS
    evidence: zero unresolved threads on PR 309
blockers:
  - Canary PR 1063 must complete after lifecycle isolation PR 1064.
next_action: after Canary PR 1063 is terminal, verify Required on the current PR 309 head and merge through normal protections
```
