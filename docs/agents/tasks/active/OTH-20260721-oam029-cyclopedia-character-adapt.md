---
task_id: OTH-20260721-oam029-cyclopedia-character-adapt
status: implementing
branch: dudantas/oam-029-cyclopedia-character-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260721-oam029-cyclopedia-character-adapt.md
  - docs/oam-029-cyclopedia-character-adapt.md
  - src/creatures/players/components/player_cyclopedia.cpp
  - tests/unit/game/oam_029_cyclopedia_character_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/creatures/players/components/player_cyclopedia.cpp
optional_reads: []
---

# OAM-029 cyclopedia-character target adaptation

## Goal

Apply only the reviewed legacy PR #188 recent-PvP count-window correction to the clean target Cyclopedia Character component and add focused proof without importing Bestiary, Bosstiary, Charms, Titles or maintained-client changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T06:29:00Z
head: 1521906ffa8bd83ff2b35b0feadab4a44ea6df05
branch: dudantas/oam-029-cyclopedia-character-adapt
pr: none
status: implementing
context_routes:
  - docs/agents/tasks/active/OTH-20260721-oam029-cyclopedia-character-adapt.md
  - docs/oam-029-cyclopedia-character-adapt.md
owned_paths:
  - docs/agents/tasks/active/OTH-20260721-oam029-cyclopedia-character-adapt.md
  - docs/oam-029-cyclopedia-character-adapt.md
  - src/creatures/players/components/player_cyclopedia.cpp
  - tests/unit/game/oam_029_cyclopedia_character_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 1521906ffa8bd83ff2b35b0feadab4a44ea6df05.
  - Target and fresh upstream share player_cyclopedia.cpp blob 91a3235e53e5f7ca4da22649bff6bad34cf44e3a.
  - Merged legacy PR 188 changes exactly one cyclopedia-character production site in PlayerCyclopedia::loadRecentKills.
  - The returned recent-PvP rows are restricted to 70 days while the count subquery is not, so computed pages can include stale historical kills.
  - The accepted donor adds the identical 70-day predicate to the count subquery and changes no request shape, persistence schema, child subsystem or maintained client.
  - Whole-file legacy copy is unnecessary and rejected because OAM-029 owns only the isolated reviewed SQL hunk.
derived:
  - OAM-029 target disposition is cyclopedia-character ADAPT with one production SQL correction plus focused proof.
unknown:
  - Exact CI outcome until the target PR runs.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Import the entire legacy PR 188 package.
  - Change maintained OTClient pagination behavior instead of correcting the server-side count/list mismatch.
changed_paths:
  - docs/agents/tasks/active/OTH-20260721-oam029-cyclopedia-character-adapt.md
validation:
  - command: exact donor/context preflight
    result: PASS
    evidence: PR 188 has one isolated player_cyclopedia.cpp hunk that applies to the exact target/upstream query
blockers: []
next_action: Materialize the exact PR 188 70-day count-window correction in PlayerCyclopedia::loadRecentKills, add focused OAM-029 proof, register it, remove temporary materialization paths, and open the target PR for exact-head CI.
```
