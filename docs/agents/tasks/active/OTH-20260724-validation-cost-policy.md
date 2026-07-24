---
task_id: OTH-20260724-validation-cost-policy
status: implementing
branch: dudantas/validation-cost-policy
base_branch: main
created: 2026-07-24
updated: 2026-07-24
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-validation-cost-policy.md
  - AGENTS.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - AGENTS.md
optional_reads: []
---

# Risk-based validation policy

## Goal

Make compilation and test scope proportional to the changed paths and risk. Avoid builds for documentation-only and clearly non-build-affecting changes while preserving focused and full builds where compilation, ABI, dependencies, toolchains or platform behavior may change.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T08:00:00+02:00
branch: dudantas/validation-cost-policy
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-validation-cost-policy.md
  - AGENTS.md
proven:
  - AGENTS.md already permits skipping builds for small documentation, script and clearly non-build-affecting changes.
derived:
  - A more explicit decision table will reduce unnecessary full builds and prevent agents from treating every PR identically.
unknown: []
conflicts: []
changed_paths:
  - docs/agents/tasks/active/OTH-20260724-validation-cost-policy.md
validation: []
blockers: []
next_action: Strengthen the Build Policy in AGENTS.md and inspect the exact branch diff.
```
