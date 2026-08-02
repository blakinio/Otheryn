---
task_id: OTH-20260802-root-agent-bootstrap-v21
status: implementing
project_lane: otheryn-governance
policy_version: 2
task_kind: documentation
implementation_authorized: false
decomposition_decision: single
context_pressure: low
context_growth: stable
context_score: 2
estimate_confidence: high
phase: implementation
session_id: chat-20260802-root-agent-bootstrap-v21
session_role: coordinator
execution_mode: chat-github
branch: dudantas/root-agent-bootstrap-v21
base_branch: main
start_sha: ""
issue: ""
feature_pr: ""
created: 2026-08-02
updated: 2026-08-02T08:57:00+02:00
lease_expires_at: 2026-08-02T12:00:00+02:00
owned_paths:
  - AGENTS.override.md
  - docs/agents/tasks/active/OTH-20260802-root-agent-bootstrap-v21.md
---

# Root agent bootstrap v2.1

## Goal

Add an automatically loaded root bootstrap that forces every Codex agent to read Otheryn's complete governance stack and makes the short autonomous command sufficient.

## Acceptance

- [x] Add root `AGENTS.override.md` without weakening repository safety.
- [x] Require the root and nested instructions plus delivery and autonomous continuation contracts.
- [x] Define the short Polish autonomous command as authorization for the durable foreground loop.
- [x] Preserve vertical-slice, audit, E2E, exact-head CI, PR closeout and archive requirements.
- [ ] Pass Required workflow.
- [ ] Merge and archive.
