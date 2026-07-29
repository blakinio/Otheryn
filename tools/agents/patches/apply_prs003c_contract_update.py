from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


path = Path("docs/architecture/prs-003-database-outage-state-machine-contract.md")
text = path.read_text(encoding="utf-8")

text = replace_once(
    text,
    "`PRS-003 database-outage handling → SLICE B IMPLEMENTED`",
    "`PRS-003 database-outage handling → SLICE C LIVE PROTOCOL ADMISSION IMPLEMENTED`",
    "disposition",
)
text = replace_once(
    text,
    "The discovery milestone records the live startup and runtime database-failure behavior and accepts one bounded fail-closed state-machine contract. PRS-003A implements the database-independent pure state object. PRS-003B now classifies direct runtime database failures and publishes deterministic events to one process-level state owner while preserving existing caller-visible results. It does not add protocol or gameplay admission, draining orchestration, recovery probes, reconnect, query replay, schema changes or production deployment.",
    "The discovery milestone records the live startup and runtime database-failure behavior and accepts one bounded fail-closed state-machine contract. PRS-003A implements the database-independent pure state object. PRS-003B classifies direct runtime database failures and publishes deterministic events to one process-level state owner while preserving existing caller-visible results. PRS-003C now consumes immutable snapshots at live account-login, game-login and existing-session/channel-handoff boundaries and exposes a separately named staff-diagnostic evaluator with an explicit capability. It does not add durable-mutation admission, draining orchestration, recovery probes, reconnect, query replay, schema changes or production deployment.",
    "opening scope",
)
text = replace_once(
    text,
    "- no runtime database path reconnects, replays an arbitrary query, starts a retry loop, changes `GameState_t`, blocks admission or starts a drain.",
    "- no runtime database path reconnects, replays an arbitrary query, starts a retry loop, changes `GameState_t` or starts a drain; the live protocol adapter only rejects the explicitly classified account-login, game-login and handoff operations.",
    "runtime boundary",
)
text = replace_once(
    text,
    "- no login gate reads a database-health snapshot yet;",
    "- account login reads one immutable outage snapshot after the existing startup/maintenance gates and before IP-ban, account load or authentication work;\n- ordinary game login reads one immutable outage snapshot after the existing startup/maintenance gates and before IP-ban/world authentication, then rechecks before player loading;\n- existing-session/channel handoff reads one immutable outage snapshot before old-client disconnect, replacement scheduling and final player/client ownership assignment;\n- the separately named staff-diagnostic evaluator requires its own explicit capability, performs no database I/O and is not selected by ordinary login or handoff paths;",
    "live gates",
)
text = replace_once(
    text,
    "Runtime database failures now create one deterministic shared outage signal, but the signal is not yet consumed by login, handoff, mutation or drain paths. Other sessions and gameplay paths can therefore continue accepting work after the owner has entered `DEGRADED` or `DRAINING`. A later query succeeding does not establish whether an earlier write committed, and reconnecting or replaying that write could duplicate value. Continuing indefinitely can accumulate unpersistable RAM state; disconnecting everyone immediately on the first error can also discard state before bounded final checkpoint attempts are made.\n\nPRS-003A and PRS-003B provide deterministic policy state plus runtime failure publication only. No admission gate, scheduled deadline transition, drain guarantee, recovery probe, automatic recovery or production RTO/RPO claim is accepted from the current integration.",
    "Runtime database failures create one deterministic shared outage signal, and PRS-003C now closes new account-login, ordinary game-login and existing-session/channel-handoff admission from that signal. Durable gameplay mutations and drain scheduling still do not consume it, so already admitted sessions can continue persistence-relevant work after the owner has entered `DEGRADED` or `DRAINING`. A later query succeeding does not establish whether an earlier write committed, and reconnecting or replaying that write could duplicate value. Continuing indefinitely can accumulate unpersistable RAM state; disconnecting everyone immediately on the first error can also discard state before bounded final checkpoint attempts are made.\n\nPRS-003A, PRS-003B and PRS-003C provide deterministic policy state, runtime failure publication and live login/handoff admission. No durable-mutation gate, scheduled deadline transition, drain guarantee, recovery probe, automatic recovery or production RTO/RPO claim is accepted from the current integration.",
    "risk statement",
)
text = replace_once(
    text,
    "Until a call site has an explicit operation classification, the fail-closed classification is persistence-relevant mutation. PRS-003A and PRS-003B do not enforce this table; Slice C and Slice D own that integration.",
    "Until a call site has an explicit operation classification, the fail-closed classification is persistence-relevant mutation. PRS-003C enforces the account-login, game-login and channel-handoff rows. Slice D still owns durable-mutation classification, admission and bounded draining.",
    "admission enforcement",
)
text = replace_once(
    text,
    "PRS-003A records the drain deadline and terminal reason only. PRS-003B may enter draining by publishing an unknown-outcome failure, but it does not schedule the deadline, disconnect players or orchestrate final saves.",
    "PRS-003A records the drain deadline and terminal reason only. PRS-003B may enter draining by publishing an unknown-outcome failure. PRS-003C closes newly classified login and handoff admission but does not schedule the deadline, disconnect the online population or orchestrate final saves.",
    "drain boundary",
)
text = replace_once(
    text,
    "Logs must include state, fixed reason and transition time. They must not include credentials, full SQL statements, player-private payloads or unbounded labels. PRS-003B exposes the immutable process snapshot and deterministic publication results but does not add metrics or new log labels.",
    "Logs must include state, fixed reason and transition time. They must not include credentials, full SQL statements, player-private payloads or unbounded labels. PRS-003B exposes the immutable process snapshot and deterministic publication results. PRS-003C maps admission reasons to fixed bounded protocol messages and adds no high-cardinality metric or log labels.",
    "observability boundary",
)
text = replace_once(
    text,
    "### Slice C — login and handoff admission\n\nGate account/game login and channel-switch entry points from immutable outage snapshots. Keep existing staff/lifecycle behavior explicit and tested.",
    "### Slice C — login and handoff admission — implemented\n\n`src/server/network/protocol/database_outage_protocol_admission.hpp` adapts one immutable PRS-003B snapshot into the accepted PRS-003C-A policy and fixed bounded caller messages. `ProtocolLogin` evaluates account-login admission before IP-ban/account database work. `ProtocolGame` evaluates ordinary game-login admission before world authentication and again before player loading. Existing-session handoff is evaluated before the old client is disconnected, before replacement is scheduled and before `player->client` ownership is assigned.\n\nThe adapter preserves existing startup, maintenance, closing and closed messages, defers the ordinary game-login closing/closed decision until the existing player capability is available, and supplies `CanAlwaysLogin` only from the existing player at handoff. Its separately named staff-diagnostic evaluator requires a dedicated diagnostic capability, does no I/O and is not reachable through the ordinary login/handoff helpers. No new network opcode or universal staff bypass is introduced.\n\n`tests/unit/server/network/protocol/database_outage_protocol_admission_test.cpp` deterministically proves the healthy/degraded/draining/maintenance table for each live operation, closing/closed deferral, handoff capability behavior, explicit diagnostic capability, unknown-value fail-closed handling, bounded messages and immutable deterministic evaluation.",
    "slice C implementation",
)
text = replace_once(
    text,
    "Current deterministic Slice A and Slice B evidence proves:",
    "Current deterministic Slice A, Slice B and Slice C evidence proves:",
    "evidence heading",
)
text = replace_once(
    text,
    "- no reconnect, query replay or retry loop is introduced.\n\nFuture integration evidence must still prove:",
    "- no reconnect, query replay or retry loop is introduced;\n- account login, ordinary game login and existing-session handoff consume immutable outage snapshots and reject degraded, draining and maintenance admission;\n- handoff is rechecked before old-client disconnect, replacement scheduling and final ownership mutation;\n- `CanAlwaysLogin` never overrides an outage rejection and diagnostic capability remains separate;\n- caller messages are fixed, bounded and contain no SQL text, player identifier or unbounded exception data.\n\nFuture integration evidence must still prove:",
    "slice C evidence",
)
text = replace_once(
    text,
    "- protocols and mutations enforce the admission table;",
    "- durable gameplay mutations enforce the remaining admission table and cannot create an unbounded drain;",
    "future evidence",
)
text = replace_once(
    text,
    "- protocol, login, handoff or gameplay mutation admission;",
    "- durable gameplay-mutation admission beyond the implemented account-login, game-login and handoff gates;",
    "non-goal",
)

path.write_text(text, encoding="utf-8")
