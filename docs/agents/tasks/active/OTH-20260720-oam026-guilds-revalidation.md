---
task_id: OTH-20260720-oam026-guilds-revalidation
status: ready
branch: dudantas/oam-026-guilds-revalidation
base_branch: main
created: 2026-07-20
updated: 2026-07-20
related_pr: "53"
owned_paths:
  - docs/agents/tasks/active/OTH-20260720-oam026-guilds-revalidation.md
  - docs/oam-026-guilds-*.md
  - src/creatures/players/grouping/guild.*
  - src/io/ioguild.*
  - tests/unit/game/oam_026_guilds_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/creatures/players/grouping/guild.*
  - src/io/ioguild.*
  - src/io/functions/iologindata_load_player.cpp
optional_reads:
  - docs/oam-024-sanctions-adapt.md
  - docs/oam-025-chat-communication-adapt.md
---

# OAM-026 guilds revalidation

## Goal

Revalidate exactly one selected canonical package, `guilds`, against immutable task-start legacy, target and upstream baselines; preserve completed target persistence contracts; then choose the smallest evidence-backed migration disposition before any production implementation.

## Immutable task-start baselines

- legacy / governance Canary: `052d96014c805aacaa120ce888b7bed038817a72`
- Otheryn target: `1cf38d354b493b4cd9ec8e841ec8f2a6ff322029`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511` (comparison-only; no canonical guild client path)

Canonical server boundary:

- `src/creatures/players/grouping/guild.*`
- `src/io/ioguild.*`
- guild-specific loading responsibility inside shared `src/io/functions/iologindata_load_player.cpp`

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T22:36:00+02:00
head: 4dfcbb263bb484399679919eb16f9968ef45aa29
branch: dudantas/oam-026-guilds-revalidation
pr: 53
status: ready
context_routes:
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/OTH-20260720-oam026-guilds-revalidation.md
  - docs/oam-026-guilds-*.md
  - src/creatures/players/grouping/guild.*
  - src/io/ioguild.*
  - tests/unit/game/oam_026_guilds_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - The branch was created from exact Otheryn main baseline 1cf38d354b493b4cd9ec8e841ec8f2a6ff322029 and target main still equals that baseline at the pre-ready gate.
  - Canonical guilds depends only on completed character-lifecycle and database-connection contracts.
  - guild.cpp and guild.hpp are blob-identical across the pinned legacy, target and upstream baselines.
  - The guild-specific IOLoginDataLoad::loadPlayerGuild hunk is semantically identical at pinned target and legacy baselines; the shared loader full-file difference is unrelated to guild ownership and is not copied.
  - Target ioguild.cpp and ioguild.hpp intentionally differ from legacy/upstream because completed OAM-004C propagates saveGuild database failure through IOGuild and SaveManager.
  - Otheryn history from bootstrap to task start changes canonical guild paths only for the OAM-004C IOGuild persistence adaptation; no later guild-core donor mutation is present.
  - Reviewed legacy multichannel implementation did not change canonical guild production files; no stronger independent legacy donor for the bounded guild core was identified.
  - Legacy security evidence OTS-ECO-GUILD-001 proves a cross-process stale guild-bank balance double-spend class; OAM-026 does not import that multichannel ownership model and records it as a future multiwriter boundary rather than claiming it solved.
  - The canonical guild boundary has no maintained-client path and explicitly excludes wire packet compatibility.
  - OAM-026 disposition is ADAPT: preserve upstream-compatible guild identity/rank/membership/cache behavior while retaining the target-owned OAM-004C persistence failure-propagation adaptation.
  - PR 53 pre-ready head 4dfcbb263bb484399679919eb16f9968ef45aa29 changed exactly four owned proof paths and no production guild path.
  - PR 53 pre-ready head 4dfcbb263bb484399679919eb16f9968ef45aa29 passed CI run 193 and Required run 174; autofix.ci run 159 was skipped, not failed.
  - PR 53 had no comments, submitted reviews or review threads at the pre-ready gate and was mergeable.
derived:
  - Whole-module REUSE would be inaccurate because copying legacy/upstream IOGuild would regress an established target persistence contract.
  - No new production mutation is required for OAM-026 because the required guild persistence adaptation already exists in the clean target through the completed dependency package.
  - The smallest current proof is documentation plus a focused unit contract test; production guild and IOGuild files remain unchanged.
unknown:
  - Exact-head CI/check results after this ready-state checkpoint commit and ready-for-review transition.
  - Final review/comment/thread state at merge time.
conflicts: []
first_failure:
  marker: none
  evidence: semantic/history/boundary audit and pre-ready exact-head CI found no blocker
rejected_hypotheses:
  - guilds REUSE from blob identity: canonical IOGuild has an intentional target architecture divergence from legacy/upstream.
  - copy legacy or upstream IOGuild wholesale: it would regress completed OAM-004C save failure propagation.
  - import legacy multichannel guild behavior: canonical guild files are not a stronger donor and the multiwriter guild-bank model has a proven stale-balance hazard.
changed_paths:
  - docs/agents/tasks/active/OTH-20260720-oam026-guilds-revalidation.md
  - docs/oam-026-guilds-adapt.md
  - tests/unit/game/oam_026_guilds_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: exact task-start baseline and ownership preflight
    result: PASS
    evidence: Otheryn 1cf38d35; Canary 052d9601; upstream 71a0f92b; OTClient a6868920; no target open PR overlap at task start
  - command: exact canonical guild core and guild-specific loader semantic comparison
    result: PASS
    evidence: guild.cpp/guild.hpp identical across pinned baselines; loadPlayerGuild hunk identical target vs legacy
  - command: OAM-004C persistence compatibility audit
    result: PASS
    evidence: target IOGuild bool save result and SaveManager propagation are deliberate completed target architecture and must be retained
  - command: legacy history and multichannel overlap audit
    result: PASS
    evidence: no stronger canonical guild donor found; OTS-ECO-GUILD-001 retained as future multiwriter limitation
  - command: PR 53 pre-ready exact-head target CI
    result: PASS
    evidence: head 4dfcbb26; CI 193 success; Required 174 success; autofix.ci 159 skipped
  - command: PR 53 changed-file and review gate
    result: PASS
    evidence: exactly four owned proof paths; no production changes; no comments, reviews or review threads; target main unchanged
blockers: []
next_action: Mark PR 53 ready for review, then use the resulting exact PR head for a fresh changed-file, target-main drift, CI/Required, mergeability, comment, review and unresolved-thread gate before squash merge.
```
