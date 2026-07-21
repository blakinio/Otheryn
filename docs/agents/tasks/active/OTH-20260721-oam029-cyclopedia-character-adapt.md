---
task_id: OTH-20260721-oam029-cyclopedia-character-adapt
status: ready
branch: dudantas/oam-029-cyclopedia-character-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: "59"
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
updated_at: 2026-07-21T06:33:00Z
head: e24c3d58cbae5d19102e8b048e744fc6ec88908a
branch: dudantas/oam-029-cyclopedia-character-adapt
pr: 59
status: ready
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
  - The accepted donor adds the existing 70-day predicate to the count subquery so page count and returned rows use one window.
  - The production file after adaptation has blob b2b6d0f3283380f450b3c79874d5ce38ac2734a0, matching current reviewed legacy at this path.
  - PR 59 changes exactly five intended paths and contains no temporary materialization helper/workflow.
  - Draft CI 208 and Required 192 passed on head e24c3d58cbae5d19102e8b048e744fc6ec88908a; autofix 171 was skipped, not failed.
derived:
  - OAM-029 target disposition is cyclopedia-character ADAPT with one production SQL correction plus focused proof.
unknown:
  - Final ready-state exact-head CI outcome.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Import the entire legacy PR 188 package.
  - Change maintained OTClient pagination behavior instead of correcting the server-side count/list mismatch.
changed_paths:
  - docs/agents/tasks/active/OTH-20260721-oam029-cyclopedia-character-adapt.md
  - docs/oam-029-cyclopedia-character-adapt.md
  - src/creatures/players/components/player_cyclopedia.cpp
  - tests/unit/game/oam_029_cyclopedia_character_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: exact donor/context preflight
    result: PASS
    evidence: PR 188 has one isolated player_cyclopedia.cpp hunk that applies to the exact target/upstream query
  - command: draft target CI 208 and Required 192
    result: PASS
    evidence: exact head e24c3d58cbae5d19102e8b048e744fc6ec88908a
blockers: []
next_action: Mark PR 59 ready, require CI and Required success on the resulting exact final head, verify the focused OAM-029 proof executes in Linux debug, audit five-file scope plus comments/reviews/threads and target-main drift, then expected-head squash merge if all gates remain clean.
```
