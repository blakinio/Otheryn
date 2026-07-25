# OAM-048 Gameplay Analytics target disposition

## Final disposition

`gameplay-analytics → EXPERIMENTAL_ONLY`

## Exact baselines

- Canary preflight merge: `4d47714756b67cd632aeedd6c405a7fc8dba4a79`
- Otheryn task-start main: `68e2b233b02356a79a03422ed51d757b85915bc5`
- reviewed upstream: `7644bcbcbbad4a09e52a5707ed531e4dd21d8a79`
- legacy Gameplay Analytics config blob: `939b8b8b51fdf0c1157afb7df8af5cccf1d3ebdf`
- legacy loader blob: `86f6ae164077ce616e87f278e553475225a52f8a`

## Target responsibility conclusion

Gameplay Analytics is optional laboratory telemetry, not a required Otheryn core server responsibility. The canonical package owns disabled-by-default Global datapack configuration, telemetry session collection, buffering/retry/dead-letter behavior, optional analytics persistence, dry-run tooling, maintenance and aggregate-report discovery. It explicitly excludes gameplay formula correctness, complete coverage, production stability, privacy assurance and retention assurance.

At the pinned target head:

- the representative `data-otservbr-global/scripts/config/gameplay_analytics.lua` path is absent;
- repository search finds no `GameplayAnalytics` or `gameplay_analytics` target consumer;
- Otheryn startup, build and runtime roots do not require a target-local analytics implementation;
- no canonical dependent module requires Gameplay Analytics.

The legacy config sets `enabled = false` and `anonymizePlayers = false`. Existing dry-run and MariaDB-backed tests prove selected laboratory contracts only; they do not establish privacy, retention, schema migration, deletion, realistic load behavior or production operations for Otheryn.

## Isolation contract

The package may remain useful in Canary or a separately authorized experimental target branch only when all of these boundaries hold:

- disabled by default and never required for core startup or gameplay;
- no target core module depends on analytics globals, schema or workflows;
- no automatic copy of legacy Lua, tools, workflows or database surfaces;
- no production activation without a separately reviewed product, privacy, retention, deletion, schema-migration, capacity and operations contract;
- no claim that collected metrics are complete, anonymous, authoritative or safe for AI/security use;
- failures remain isolated from gameplay and persistence correctness.

## Dependency impact

`lua-runtime` remains completed independently. Combat, parties, database connection, player persistence and world-map runtime do not depend on Gameplay Analytics. Excluding analytics from Otheryn core therefore removes no required runtime consumer and introduces no dependency gap.

## Rejected alternatives

- `REUSE`: target ownership, privacy and production criteria are not established.
- `ADAPT`: no bounded core target need exists to justify importing or adapting the legacy stack.
- `REWRITE`: the responsibility is not required in core and no target product contract exists.
- `DO_NOT_MIGRATE`: too strong because the telemetry remains useful as an isolated laboratory/experimental capability.

## Nonclaims

This disposition does not prove production privacy, anonymization, retention, deletion, schema migration, aggregation correctness, complete telemetry coverage, failure isolation under load, performance, security analytics suitability, AI investigation suitability, physical-client behavior or production readiness.

## Rollback

No target runtime path is added. Rollback is removal of this disposition document/task record. Any future experimental implementation must use its own bounded task and may be abandoned without affecting Otheryn core.
