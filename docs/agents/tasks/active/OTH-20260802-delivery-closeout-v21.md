---
task_id: OTH-20260802-delivery-closeout-v21
status: validating
project_lane: otheryn-governance
policy_version: 2
task_kind: integration
implementation_authorized: false
decomposition_decision: single
context_pressure: low
context_growth: stable
context_score: 3
estimate_confidence: high
phase: validate
session_id: chat-20260802-delivery-closeout-v21
session_role: coordinator
execution_mode: chat-github
branch: dudantas/agent-closeout-vertical-slice-v21
base_branch: main
start_sha: f5c2a2b5cfebfce8da7d4fd06159c4398c126725
issue: ""
feature_pr: "301"
created: 2026-08-02
updated: 2026-08-02T00:24:00+02:00
lease_expires_at: 2026-08-02T03:00:00+02:00
owned_paths:
  - docs/agents/AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
  - docs/agents/tasks/active/OTH-20260802-delivery-closeout-v21.md
---

# Delivery completeness and closeout v2.1

## Goal

Require complete producer/consumer delivery, independent audit, real E2E, exact-head validation and terminal PR hygiene before substantial work is completed.

## Acceptance

- [x] Add and route the normative closeout contract.
- [x] Prevent backend-only completion claims for user-facing work with missing frontend/client consumers.
- [x] Require prompt eval discipline and trust boundaries.
- [x] Require audit, E2E and terminal related PRs.
- [ ] Pass Required workflow.
- [ ] Merge and archive.
