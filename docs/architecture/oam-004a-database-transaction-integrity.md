# OAM-004A — Database transaction integrity

Status: implementation slice

Parent coordination: `OAM-004` in `blakinio/canary#420`

Task issue: `blakinio/Otheryn#7`

Pinned target task-start:

```text
blakinio/Otheryn@a9c7fabc9f4b9bbeca9fed4ab73c36309cd04e2d
```

Evidence baselines:

```text
opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01
```

## Goal

Make database statement failure and transaction failure semantics fail closed so Oteryn persistence code cannot silently continue after an automatic reconnect has discarded server-side transaction state.

## Proven risk

The current DB core enables `MYSQL_OPT_RECONNECT` and automatically retries recoverable query errors. MySQL documents that automatic reconnect can resend a statement while resetting session state and rolling back active transactions. Therefore a caller holding a local `DBTransaction` can otherwise continue after the server-side transaction has disappeared.

The current `DBTransaction::executeWithinTransaction()` also commits when its callback returns `false`.

## Bounded implementation

1. Disable MySQL automatic reconnect for the process connection.
2. Remove automatic retry/resend of arbitrary SQL statements from normal query execution paths.
3. Make query failure return immediately to the owning operation so it can fail/rollback explicitly.
4. Make `DBTransaction::executeWithinTransaction()` roll back when the callback returns `false`.
5. Keep the explicitly named rollback-on-failure helper compatible while avoiding divergent semantics.
6. Preserve the existing recursive database serialization lock and transaction begin/commit/rollback ownership.

## Explicit non-goals

- no connection pool;
- no distributed transaction or session fencing;
- no automatic operation-level retry framework;
- no schema migration changes;
- no player/world serializer changes;
- no production database access.

## Safety rule

After this slice, a dropped connection causes the current DB operation to fail rather than silently reconnect and replay an arbitrary statement. Higher-level bounded operations may implement explicit retry only when their idempotence and transaction boundary are proven.

## Validation

- exact-head C++ build and runtime smoke matrix;
- temporary MariaDB integration through existing CI;
- focused transaction semantics tests if the existing test harness exposes a safe DB fixture;
- no persistence-domain call-site refactor in this slice.
