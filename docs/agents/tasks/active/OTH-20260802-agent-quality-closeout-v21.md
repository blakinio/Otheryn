---
task_id: OTH-20260802-agent-quality-closeout-v21
status: implementing
project_lane: otheryn-governance
policy_version: 2
task_kind: integration
implementation_authorized: false
decomposition_decision: single
context_pressure: medium
context_growth: stable
phase: integrate
session_id: chat-20260802-quality-v21
session_role: coordinator
execution_mode: chat-github
branch: dudantas/agent-quality-closeout-v21
base_branch: main
start_sha: 63a6b9a42a49daf00295f490e18985a276cc8ebd
issue: ""
feature_pr: ""
created: 2026-08-02
updated: 2026-08-02T00:20:00+02:00
lease_expires_at: 2026-08-02T02:20:00+02:00
owned_paths:
  - docs/agents/AGENT_QUALITY_AND_CLOSEOUT.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/tasks/active/OTH-20260802-agent-quality-closeout-v21.md
---

# OTH-20260802 — Agent quality and closeout v2.1

## Goal

Make outcome-based evals, trust boundaries, full-stack vertical slices, independent audit, real E2E, exact-final-head CI, related-PR cleanup, and terminal task archival mandatory for substantial agent work.

## Acceptance

- [x] Add the normative v2.1 contract.
- [x] Make the prompting handover require it.
- [x] Cover all agreed quality and closeout gates.
- [ ] Pass exact-head Required workflow.
- [ ] Merge and archive.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T00:20:00+02:00
head: 63a6b9a42a49daf00295f490e18985a276cc8ebd
branch: dudantas/agent-quality-closeout-v21
pr: none
status: implementing
phase: integrate
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
owned_paths:
  - docs/agents/AGENT_QUALITY_AND_CLOSEOUT.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/tasks/active/OTH-20260802-agent-quality-closeout-v21.md
proven:
  - The v2.1 contract exists and is mandatory in the handover.
derived:
  - Future substantial work must pass the integrated quality and closeout gate.
unknown:
  - Exact-head workflow results and PR number.
conflicts: []
changed_paths:
  - docs/agents/AGENT_QUALITY_AND_CLOSEOUT.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/tasks/active/OTH-20260802-agent-quality-closeout-v21.md
validation: []
blockers: []
next_action: open the governance PR, record its exact identity, and validate the final head
```
