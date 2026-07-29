---
task_id: OTH-20260729-prs002i-checkpoint-operational-metrics
status: active
branch: dudantas/prs-002i-checkpoint-operational-metrics
base_branch: main
start_sha: d36ad9a5bfd8970ab1a108e6017945b91a4683e6
created: 2026-07-29
updated: 2026-07-29
related_issue: "187"
related_pr: null
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/lib/metrics/metrics.hpp
  - src/lib/metrics/metrics.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/player_checkpoint_attempt_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260729-prs002i-checkpoint-operational-metrics.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/lib/metrics/metrics.hpp
  - src/lib/metrics/metrics.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/player_checkpoint_attempt_test.cpp
---

# PRS-002I checkpoint operational metrics

## Goal

Expose bounded, low-cardinality operational metrics for the generation-aware asynchronous player checkpoint path without changing its queue, retry or persistence semantics.

## Accepted target contract

- exact-owner dirty timestamp begins once for one continuous dirty interval;
- newer mutations, queue rejection and failed/thrown attempts preserve that timestamp;
- exact-owner success clears the timestamp only when no newer generation remains;
- current queue capacity/outstanding work, dirty-owner count and oldest dirty timestamp are gauges;
- requests, attempts, successes, failures, thrown attempts, queue rejections and submission failures are monotonic counters;
- metric labels are fixed and low cardinality, with no player, GUID or generation identity;
- oldest dirty age is derived continuously in Prometheus as `time() - player_checkpoint_oldest_dirty_timestamp_seconds`.

## Implementation plan

- add optional caller-supplied dirty timestamp ownership to `PlayerPersistenceState`;
- add deterministic atomic `PlayerCheckpointTelemetry` counters and a gauge-summary helper;
- add `Metrics::setGauge` backed by an OpenTelemetry integer up/down counter and reset instrument state on shutdown;
- instrument `SaveManager` transitions and release callbacks without changing admission behavior;
- reuse the existing method-latency histogram for player checkpoint duration;
- add state, telemetry, concurrency and source-contract tests;
- document metric names, PromQL age derivation and explicit non-goals.

## Failure-injection plan

Focused tests inject queue rejection, save failure, thrown save, newer mutation during success, stale timestamp ownership and concurrent counter updates. No real database failure or production exporter is required because this package observes already-proven boundaries.

## Rollback plan

Revert the feature merge. No schema, database data, KV data, credentials, deployment state or generated assets are changed.

## Explicit non-goals

- no alert thresholds, Grafana dashboards or production deployment;
- no claimed checkpoint SLO or RPO;
- no retry timer, backoff or queue-policy change;
- no high-cardinality identity labels;
- no PRS-003, PRS-004, PRS-005 or PRS-006 implementation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T08:12:00+02:00
head: d36ad9a5bfd8970ab1a108e6017945b91a4683e6
branch: dudantas/prs-002i-checkpoint-operational-metrics
pr: null
status: implementing
context_routes:
  - production-resilience
  - player-persistence
  - metrics
  - prometheus
  - concurrency
  - testing
  - agent-governance
owned_paths:
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/lib/metrics/metrics.hpp
  - src/lib/metrics/metrics.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/player_checkpoint_attempt_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/active/OTH-20260729-prs002i-checkpoint-operational-metrics.md
proven:
  - PRS-002H is merged and terminally archived.
  - The repository already provides OpenTelemetry Counter and UpDownCounter instruments.
  - The checkpoint queue exposes exact capacity and outstanding values but does not export them.
  - Exact-owner state has generations and failure count but no dirty timestamp.
  - No open PR owns the selected paths.
derived:
  - A caller-supplied timestamp plus low-cardinality counters and delta-set gauges is the smallest package that closes the PRS-002 observability gap without adding scheduler policy.
unknown:
  - Exact-head compile, exporter compatibility and focused test results.
conflicts: []
first_failure: null
rejected_hypotheses:
  - add player names, GUIDs or generations as labels
  - add dashboards or alert thresholds
  - add an observable-gauge callback with process-lifetime ownership complexity
  - alter queue capacity, retry or persistence policy
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs002i-checkpoint-operational-metrics.md
validation:
  - command: governance, source and conflict preflight
    result: PASS
    evidence: Main d36ad9a5bfd8970ab1a108e6017945b91a4683e6; no open PR and no existing PRS-002I issue or branch.
blockers: []
next_action: Implement exact-owner timestamp ownership, deterministic telemetry, gauge export, SaveManager wiring and focused tests.
```
