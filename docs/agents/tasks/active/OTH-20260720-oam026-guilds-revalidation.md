---
task_id: OTH-20260720-oam026-guilds-revalidation
status: implementing
branch: dudantas/oam-026-guilds-revalidation
base_branch: main
created: 2026-07-20
updated: 2026-07-20
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260720-oam026-guilds-revalidation.md
  - docs/oam-026-guilds-*.md
  - src/creatures/players/grouping/guild.*
  - src/io/ioguild.*
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
updated_at: 2026-07-20T22:08:00+02:00
head: 1cf38d354b493b4cd9ec8e841ec8f2a6ff322029
branch: dudantas/oam-026-guilds-revalidation
pr: none
status: investigating
context_routes:
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/OTH-20260720-oam026-guilds-revalidation.md
  - docs/oam-026-guilds-*.md
  - src/creatures/players/grouping/guild.*
  - src/io/ioguild.*
proven:
  - The branch was created from exact Otheryn main baseline 1cf38d354b493b4cd9ec8e841ec8f2a6ff322029 and no target PR was open at task start.
  - Canonical guilds depends only on completed character-lifecycle and database-connection contracts.
  - guild.cpp and guild.hpp are blob-identical across the pinned legacy, target and upstream baselines.
  - Target ioguild.cpp and ioguild.hpp differ from legacy/upstream because Otheryn already propagates saveGuild failure as part of the completed OAM-004 persistence contract.
  - Target iologindata_load_player.cpp is blob-identical to upstream while legacy differs; the file is shared with completed character lifecycle and cannot be copied wholesale for guilds.
  - The canonical guild boundary has no maintained-client path and explicitly excludes wire packet compatibility.
derived:
  - OAM-026 must preserve the target-owned OAM-004 IOGuild save-status contract regardless of final guild disposition.
  - Blob identity of the guild core is supporting evidence only and cannot establish REUSE by itself.
unknown:
  - Whether guild-specific legacy history contains a stronger bounded donor or a defect absent from target/upstream.
  - The final migration disposition for guilds.
  - The minimum focused target proof required by the applicable guild ownership and persistence boundaries.
conflicts: []
first_failure:
  marker: none
  evidence: no target-side blocker found at task creation
rejected_hypotheses:
  - copy legacy IOGuild wholesale: it would regress the completed target save-status contract.
changed_paths:
  - docs/agents/tasks/active/OTH-20260720-oam026-guilds-revalidation.md
validation:
  - command: exact task-start baseline and ownership preflight
    result: PASS
    evidence: Otheryn 1cf38d35; Canary 052d9601; upstream 71a0f92b; OTClient a6868920; no target open PR overlap
blockers: []
next_action: Audit exact semantic diffs and relevant history for guild.cpp, guild.hpp, ioguild.cpp, ioguild.hpp and the guild-specific player-load hunk across the pinned baselines, classify applicable boundaries, and decide REUSE, ADAPT or REVALIDATE without changing production code.
```
