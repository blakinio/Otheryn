---
task_id: OTH-20260815-otbm-atlas-creature-animation
status: waiting
owner: none
branch: feat/otbm-atlas-creature-animation
base_branch: main
created: 2026-08-15T10:47:00+02:00
updated: 2026-08-15T11:49:00+02:00
project_lane: otheryn-content
execution_mode: chat-github
execution_reason: GitHub connector plus isolated GitHub Actions provide all repository writes, pinned-data validation and Chromium E2E without owner-funded Codex quota.
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-creature-animation-tests.yml
  - .github/workflows/otbm-creature-animation-audit.yml
  - docs/maps/otbm-atlas-completion-audit-20260814.md
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-creature-animation.md
required_reads:
  - AGENTS.md
  - docs/agents/AGENTS.md
  - docs/agents/EXECUTION_PROTOCOL.md
  - docs/agents/ANTI_STALL_AND_EXECUTION_BUDGET.md
  - docs/agents/GITHUB_ONLY_EXECUTION.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
---

# Canonical OTBM Atlas creature animation

## Goal

Close the remaining verified runtime gap in the OTBM Atlas by extending the existing canonical NPC/monster sprite pipeline with bounded, time-based creature animation derived only from the pinned Tibia appearance data already vendored under `vendor/map-analysis/**`.

The atlas does not simulate world movement or invent server state. Static spawn positions remain factual; animation presents canonical appearance frame groups and direction semantics at those positions.

## Delivery classification

```yaml
feature_scope:
  type: full_stack
  user_facing: true
  backend_required: false
  frontend_required: true
  integration_required: true
  e2e_required: true
```

## Acceptance criteria

- Preserve canonical creature frame-group identity and phase metadata.
- Export renderable NPC/monster phases with exact pinned sprites, outfit recolouring and addons.
- Preserve canonical cardinal direction patterns without inventing unsupported direction meanings.
- Honor canonical phase duration, synchronization, default-start, random-start and loop metadata conservatively.
- Never mutate factual spawn positions or simulate creature pathing.
- Keep browser animation viewport/zoom bounded with bounded caches and static canonical fallback.
- Keep canonical inputs restricted to `vendor/map-analysis/**`.
- Real pinned-data integration must cover a canonical NPC and monster.
- Real Chromium E2E must prove time-varying phases for the same NPC and same monster in the production viewer.
- Independent clean-runner audit must have zero material findings.
- Existing atlas/factual/environment/static-creature regressions and exact-head Required/CI must pass before merge.

## Context checkpoint

```yaml
policy_version: 2
checkpoint_version: 2
phase: validate
task_kind: implementation
implementation_authorized: true
session_id: chat-github-20260815-atlas-creature-animation
session_role: validator
execution_mode: chat-github
execution_reason: GitHub connector and GitHub Actions are sufficient; no Codex or owner-funded AI quota is used.
updated_at: 2026-08-15T11:49:00+02:00
invocation_started_at: 2026-08-15T10:47:00+02:00
last_progress_at: 2026-08-15T11:49:00+02:00
lease_expires_at: null
context_pressure: medium
context_growth: stable
context_score: 7
estimate_confidence: high
decomposition_decision: phased
decomposition_reason: one cohesive atlas feature moved through implementation, repair, independent audit and E2E on one branch/PR.
validation_level: full
session_rotation_count: 0
heavy_validation_runs: 5
stale_takeover_count: 0
human_interruptions: 0
ci_checks_for_current_head: 3
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 3
context_reconstruction_attempts: 0
stall_warnings: 1
base_main: 75e121478beadbe12d4c77343f693f74887f489d
pr: 399
validated_runtime_head: 780e2dd94bfd44d05c158ce134200582af9584c6
validated_audit_head: b7d9c6079a5f0f84c9976ef2fddfe1343fc885e6
checkpoint_commit_scope: documentation-only durable-state correction; runtime implementation is unchanged
proven:
  - current main remained 75e121478beadbe12d4c77343f693f74887f489d during feature validation
  - canonical Tibia protobuf frame groups are preserved as idle/moving rather than flattened
  - canonical N/E/S/W direction patterns and all renderable phases are exported without invented path movement
  - asynchronous non-random animations use a bounded per-spawn first-seen clock so defaultStartPhase is honored
  - random per-spawn offset is applied only when canonical randomStartPhase metadata permits it
  - static canonical sprite/dot fallbacks remain conservative
  - browser work is bounded to enabled creature layers and visible chunks with bounded image, shard, descriptor and start-clock LRUs
  - real pinned-data NPC Tanyt lookType 1199 resolves from vendor/map-analysis/crystalserver/data-global/npc/tanyt.lua
  - real pinned-data monster Silver Rabbit lookType 262 resolves from vendor/map-analysis/crystalserver/data-global/monster/mammals/silver_rabbit.lua
  - both prove 8 distinct south phase images at 300 ms per phase and canonical north/east/south/west directions
  - real Chromium creature-animation E2E run 31876770535 on exact runtime head 780e2dd94bfd44d05c158ce134200582af9584c6 completed SUCCESS; job 94993568366
  - prior human-viewable production artifact run 31876571280 completed SUCCESS and uploaded otbm-creature-animation-showcase artifact 9245078739
  - independent clean-runner audit run 31877436007 on head b7d9c6079a5f0f84c9976ef2fddfe1343fc885e6 completed SUCCESS with materialFindings=0; job 94995134683
  - exact-head Required run 31877435952 on b7d9c6079a5f0f84c9976ef2fddfe1343fc885e6 completed SUCCESS
  - exact-head CI run 31877436065 on b7d9c6079a5f0f84c9976ef2fddfe1343fc885e6 completed SUCCESS
  - exact-head autofix run 31877435954 on b7d9c6079a5f0f84c9976ef2fddfe1343fc885e6 completed SUCCESS
  - exact-head factual-layer audit run 31877435998 completed SUCCESS
  - exact-head factual-layer integration run 31877435971 completed SUCCESS
  - exact-head extended item animation browser E2E job 94995134580 completed SUCCESS
  - PR 399 is mergeable and all known review threads are resolved
pending:
  - final-head creature-animation E2E run 31877435955 is still running
  - final-head canonical static creature showcase run 31877435947 is still running
  - final-head environment-animation canonical build job 94995134637 is still running
  - final-head OTBM Atlas Tests run 31877435956 is queued
constraints:
  - do not merge PR 399 before every required final gate is terminal PASS
  - do not deploy or mutate any protected/live environment
  - do not simulate creature movement beyond canonical appearance phase playback
  - do not use owner-funded Codex/OpenAI quota
blockers: []
status: waiting
next_action: inspect each pending final-head workflow once when terminal; if all required gates PASS and review remains clean, enable/perform protected expected-head squash merge of PR 399, then archive this task and perform the single permitted atlas lifecycle closeout/cleanup task in a fresh session only if the new invocation budget permits it
```

## Anti-stall stop reason

The foreground invocation reached the repository's normal 60-minute runtime budget while required final-head workflows were still pending. Further polling in the same invocation is forbidden by `ANTI_STALL_AND_EXECUTION_BUDGET.md`; durable state is therefore `waiting`, with no active owner/lease.
