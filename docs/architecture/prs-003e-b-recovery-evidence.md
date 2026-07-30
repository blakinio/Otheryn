# PRS-003E-B bounded recovery evidence

## Disposition

`PRS-003E-B recovery evidence -> VALIDATED PENDING FINAL REPLACEMENT CHECKS`

This slice adds one bounded, database-independent recovery-evidence tracker plus disposable MariaDB evidence. It does not reconnect a failed gameplay handle, replay an operation, resume the game automatically or change production database wiring.

## Existing state-owner boundary

The accepted PRS-003 state owner already exposes `recoveryEvidenceAccepted(sequence, now)` from `DEGRADED` or `MAINTENANCE`. Acceptance sets one eligibility flag without changing outage state. A later qualifying runtime failure clears that flag. Explicit `operatorResume` remains a separate PRS-003E-C action.

PRS-003E-B does not modify the state owner. It supplies the bounded evidence decision required before the existing method may be called.

## Bounded tracker contract

`DatabaseOutageRecoveryEvidence` receives finite constructor inputs:

- required consecutive successful probe attempts;
- maximum total attempts;
- one positive candidate window.

`begin(now)` fixes one saturating deadline. Neither a failed attempt nor a later successful attempt extends it. The tracker has no clock, thread, scheduler, database connection or background loop; callers provide deterministic monotonic time.

One successful probe attempt requires all five observations:

1. read probe succeeded;
2. transaction begin succeeded;
3. isolated test write succeeded;
4. rollback succeeded;
5. the probe object remained unchanged after rollback.

Failure classification is fixed and ordered: read, begin, write, rollback, changed object. A failure resets the consecutive-success count, increments one low-cardinality counter and preserves the original deadline. Attempt exhaustion or deadline expiry stops the candidate.

After the required consecutive window, the tracker emits exactly one `PublishRecoveryEvidenceAccepted` decision. `publishIfReady` consumes that pending decision once and calls only `DatabaseOutageStateMachine::recoveryEvidenceAccepted`. It never calls `operatorResume`. A qualifying later failure invalidates local evidence; the existing state owner independently invalidates its accepted flag when the corresponding runtime failure is published.

## Dedicated-session probe contract

Every controlled probe attempt opens a new dedicated MariaDB session. It never revives or reuses the failed gameplay session. Every SQL phase is attempted once.

The disposable harness owns only `prs003e_b_recovery_probe` inside a loopback-only temporary MariaDB database. The table is test evidence, not a migration or gameplay schema. A successful attempt inserts one unique marker inside a transaction, rolls it back and verifies that the marker count is unchanged using a separate audit session.

Controlled evidence covers:

- read failure against a missing disposable table;
- transaction-begin failure after killing the dedicated probe session;
- deterministic transaction-write failure through a duplicate test marker followed by rollback;
- rollback failure after killing a session with an uncommitted test marker;
- successful read/write/rollback attempts leaving no committed marker;
- one success being insufficient;
- failure resetting consecutive successes without deadline extension;
- finite attempt exhaustion and exact deadline expiry;
- exact-once accepted-evidence publication from degraded and maintenance;
- no automatic state change after evidence acceptance;
- later qualifying failure invalidating accepted evidence;
- an unknown-outcome gameplay mutation and commit each attempted once, never replayed.

## Observability

The tracker exposes only bounded counters and fixed reasons:

- attempts and consecutive successes;
- read, begin, write, rollback and changed-object failures;
- qualifying failures;
- publication attempts and accepted publications;
- candidate, pending, accepted, deadline-expired and budget-exhausted flags.

No SQL text, credentials, hostnames, account/player identifiers or arbitrary exception strings are used as labels.

## Safety boundaries

- no `MYSQL_OPT_RECONNECT`, `mysql_ping`, reconnect or implicit session revival;
- no retry or replay of a failed or unknown-outcome operation;
- no production `Database` integration, connection pool or scheduler;
- no automatic transition to `HEALTHY` and no operator command/API/UI;
- no login, handoff, mutation, drain or final-save change;
- no migration, gameplay schema, production credentials or deployment change;
- no PRS-004+ implementation and no production RPO/RTO claim.

## Exact-head validation

Exact implementation/autofix head `e0930e3fca423bbb7f2f5b8e626a2fe088b35cec` passed the complete applicable evidence set:

- dedicated PRS-003E-B Recovery Evidence run `30586300932`;
- regression PRS-003E MariaDB Outage Evidence run `30586300777`;
- autofix run `30586301018`;
- full CI run `30586300959`, including fast checks, Lua, Linux debug with tests, Linux release, Windows CMake and solution, macOS, Docker and quickstart smoke;
- Required run `30586300723`.

The first autofix attempt found only missing final newlines in the two new C++ files. Bot head `e0930e3fca423bbb7f2f5b8e626a2fe088b35cec` contained that formatting-only correction and passed every gate above.

This evidence update creates a new governance-only final head. It must receive replacement exact-head CI, Required, autofix and dedicated workflow success before merge.

## Rollback

Revert the feature merge. All implementation, test, workflow and documentation paths in this package are new; no production database state or schema rollback is required.
