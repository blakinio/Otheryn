---
task_id: OTH-20260729-prs002i-checkpoint-operational-metrics
status: review
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

## Implemented behavior

- `PlayerPersistenceState` owns one optional Unix timestamp for a continuous dirty interval and can backfill one previously unmeasured interval exactly once;
- exact-generation success clears the timestamp only when the owner becomes clean, while failure and abandonment preserve it;
- `PlayerCheckpointTelemetry` provides atomic deterministic event counters and `summarizePlayerCheckpointGauges` provides current queue/dirty values;
- `Metrics::setGauge` publishes label-free current integer values through delta updates to OpenTelemetry up/down counters;
- `SaveManager` publishes queue capacity/outstanding, dirty owners and oldest dirty timestamp at relevant transitions;
- requests, attempts, successes, fixed-reason failures, thrown attempts, queue rejections and submission failures are exported as counters;
- the existing `method_latency` histogram records checkpoint duration with fixed method value `player_checkpoint_save`;
- release observers are best-effort and cannot turn a successful admission release into a persistence failure;
- focused tests cover timestamp ownership, retry/rejection preservation, gauge summaries, release observation and concurrent counters.

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
updated_at: 2026-07-29T08:27:00+02:00
head: 97d03a83ff8622df3e820210eed7597482b62dd5
branch: dudantas/prs-002i-checkpoint-operational-metrics
pr: null
status: validating
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
  - Dirty timestamp ownership is exact-generation safe and deterministic.
  - Queue and event telemetry uses only atomic process-level state and fixed low-cardinality labels.
  - Gauge export uses a retained absolute value and emits only the OpenTelemetry up/down-counter delta.
  - SaveManager wiring covers request, admission, queue rejection, worker release, attempt, success, failure, thrown attempt and submission failure transitions.
  - Focused tests cover continuous dirty timestamps, backfill, rejection/failure preservation, gauge summaries, observer single-fire and concurrent counter safety.
  - The branch is behind_by zero and changes exactly eleven owned paths.
derived:
  - Prometheus can derive a continuously increasing oldest dirty age from its own scrape time without adding a game-thread timer.
unknown:
  - Exact-head compile, OpenTelemetry API compatibility, focused runtime tests and full platform CI results.
conflicts: []
first_failure: null
rejected_hypotheses:
  - add player names, GUIDs or generations as labels
  - add dashboards or alert thresholds
  - add an observable-gauge callback with process-lifetime ownership complexity
  - alter queue capacity, retry or persistence policy
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs002i-checkpoint-operational-metrics.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - src/game/scheduling/player_checkpoint_attempt.hpp
  - src/game/scheduling/player_persistence_state.hpp
  - src/game/scheduling/save_manager.cpp
  - src/game/scheduling/save_manager.hpp
  - src/lib/metrics/metrics.cpp
  - src/lib/metrics/metrics.hpp
  - tests/unit/game/player_checkpoint_attempt_test.cpp
  - tests/unit/game/player_persistence_state_test.cpp
  - tests/unit/game/prs_002_dirty_player_checkpoint_contract_test.cpp
validation:
  - command: governance, source and conflict preflight
    result: PASS
    evidence: Main d36ad9a5bfd8970ab1a108e6017945b91a4683e6; no open PR and no existing PRS-002I issue or branch.
  - command: deterministic source and metric-cardinality audit
    result: PASS
    evidence: Exact-owner timestamp, atomic counters, label-free gauges, four fixed failure reasons and release-before-follow-up publication are present.
  - command: changed-path audit
    result: PASS
    evidence: Branch is behind_by zero and changes exactly eleven declared paths.
blockers: []
next_action: Open the feature PR, record its number, and run full exact-head CI, Required and autofix validation.
```
