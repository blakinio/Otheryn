---
task_id: OTH-20260721-oam029-cyclopedia-character-adapt
status: completed
branch: dudantas/oam-029-cyclopedia-character-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
completed: 2026-07-21
related_pr: "59"
---

# OAM-029 cyclopedia-character target task archive

Final disposition:

```text
cyclopedia-character → ADAPT
```

Immutable task-start target baseline:

```text
1521906ffa8bd83ff2b35b0feadab4a44ea6df05
```

Final target PR head:

```text
5f8f629ca78bcaf8636e2751ef60ae5ce9ab9a85
```

Target squash merge:

```text
908834adc7d7e7e4ced7404391c7966b1c961b18
```

OAM-029 adapted only the reviewed legacy PR #188 Cyclopedia Character hunk in `PlayerCyclopedia::loadRecentKills`: the recent-PvP `count(*)` subquery now uses the same 70-day window as the returned rows. Bestiary, Bosstiary, Charms, Titles, protocol and maintained-client changes were excluded.

The exact final head passed autofix.ci #173. Linux debug full `Run Tests` passed. CI #210 initially failed only in Docker Quickstart Smoke; a failed-job retry passed on the unchanged exact head, after which CI #210 concluded success. Required #194 was rerun to evaluate the recovered CI and concluded success. Test-log artifact `8486265013` has digest `sha256:c4eb1f8815e77b3cb7fb243beea00d3e17d2c7a66183ad057b28d1fad59dbb47`.

Target comments/reviews/threads were empty and target `main` had no task-start drift before expected-head squash merge. Canary governance, authoritative lifecycle and durable program reconciliation subsequently completed separately; durable reconciliation merged as `9b8ea0b297010a8055357c94d09e874808d57a9a`.

This archive replaces the stale `tasks/active` checkpoint so future `tools/agents/resume.py` use cannot incorrectly resume completed OAM-029 target work.
