---
task_id: OTH-20260724-oam042-npcs-reuse
status: validating
branch: dudantas/oam-042-npcs-reuse-proof
base_branch: main
created: 2026-07-24
updated: 2026-07-24
related_pr: "96"
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-oam042-npcs-reuse.md
  - docs/oam-042-npcs-reuse.md
  - tests/unit/game/oam_042_npcs_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/creatures/npcs/npcs.cpp
  - src/creatures/npcs/npc.cpp
  - src/lua/functions/creatures/npc/npc_functions.cpp
  - data/npclib/load.lua
  - data/npclib/npc_system/modules.lua
  - data-otservbr-global/npc/harlow.lua
  - data-otservbr-global/npc/rashid.lua
  - data-otservbr-global/world/otservbr-npc.xml
optional_reads: []
---

# OAM-042 NPC target reuse proof

## Goal

Prove the bounded canonical `npcs` package is already represented correctly in the clean Otheryn target. Cover NPC definition/registration, callback loading, dialogue state, shops, travel, quest hooks and placement evidence without copying Canary OTBM tooling into Otheryn or mutating production runtime, datapack, map, binary assets, protocol, client, schema or deployment paths unless proof isolates a concrete NPC-owned target defect.

## Acceptance criteria

- Target NPC loader, callback and case-insensitive registration contracts are source-covered.
- Core npclib dialogue, shop and travel behavior is source-covered.
- Representative Harlow travel/storage and Rashid quest/shop contracts are source-covered.
- Exact target/current-upstream blob identity is recorded for the reviewed core and representative data paths.
- OAM-041 deterministic placement evidence is reused only for placement/definition correlation.
- Duplicate Harlow and nonliteral dynamic creation findings remain unresolved unless exact active-root evidence resolves them.
- Final disposition is evidence-backed `REUSE`, `ADAPT` or `REWRITE`; no guessed repair is allowed.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T09:56:00+02:00
head: 0db56ac77b55f028a19487702c34cd91163097f3
branch: dudantas/oam-042-npcs-reuse-proof
pr: 96
status: validating
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-oam042-npcs-reuse.md
  - docs/oam-042-npcs-reuse.md
  - tests/unit/game/oam_042_npcs_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Canary OAM-042 preflight PR 859 merged as c86e805910d87dc8db9a212b18645e27c28c779c and selected canonical npcs for REVALIDATE with REUSE as the leading bounded hypothesis.
  - Fresh Otheryn task-start main is 7c54172adfa612fa143d11630f5a341ff4c82338.
  - No open Otheryn OAM-042 PR or branch existed before this branch was created.
  - Canonical npcs includes definitions/registration, dialogue state, shops, travel, quest hooks and placement evidence and depends only on completed external otbm-tooling.
  - Target and current opentibiabr/canary have identical reviewed blobs for src/creatures/npcs/npcs.cpp 5a5d37d4085c9b564936f721469c831b12fee6a4, src/creatures/npcs/npc.cpp 2aee02b7b0ff6b69c868365ac4ba102b5b115f40, data/npclib/load.lua ad7cb718531212facdca6b842cbf03e63945f379, data/npclib/npc_system/modules.lua 40a58c2ca7c74e28c51565604390ad80dcdb30af, data-otservbr-global/npc/harlow.lua c8eae6fe74881ab4c08305cd383e92517d14feae, data-otservbr-global/npc/rashid.lua b1f8b022e07f83cbe401c410efb3efa10f3ec697 and data-otservbr-global/world/otservbr-npc.xml 0a72085b7bbdfca73b794e631cc2bab790d8fcef.
  - Target NPC loader loads core npclib then the active datapack npc folder and stores NPC types case-insensitively.
  - Target callback loading covers think, appear, disappear, move, say, buy, sell, item inspection and channel close events.
  - Target Lua NPC surface exposes interaction, shop-window, speech, movement and sell-item behavior and initializes ShopFunctions plus NpcTypeFunctions.
  - Target StdModule.travel enforces interaction, premium, level, PZ lock, cost, cooldown and destination teleport semantics.
  - Target Harlow preserves the Blood Brothers VengothAccess storage gate, 100-gold fare and destination Position(32858, 31549, 7).
  - Target Rashid preserves multi-step travelling-trader storage transitions, gated trade callback and explicit shop catalogue.
  - OAM-041 external deterministic evidence already covered static NPC placement/definition correlation and retained duplicate Harlow plus nonliteral dynamic creation calls as explicit boundaries.
  - The coherent OAM-042 package now contains one proof document, one target-local source-contract test and one existing-test-target CMake registration with no production path mutation.
  - Draft-head workflows 30076953442 and 30076953153 completed successfully; build jobs were intentionally skipped because PR 96 remained draft.
derived:
  - Core NPC runtime and the reviewed representative dialogue/shop/travel/quest-hook sources are exact current-upstream reuse candidates.
  - A target-local source-contract test protects the reviewed semantics without copying or rebuilding the external OTBM scanner.
  - Candidate final disposition is npcs REUSE if the exact ready-for-review head passes full CI and Required.
unknown:
  - Full factual completeness of every individual NPC conversation remains outside this bounded source-contract proof.
  - Whether both Harlow definitions reported by the external scanner are active under the exact target configuration remains unresolved.
  - Exact NPC-owned subset of nonliteral dynamic creation and quest-hook calls remains unresolved.
  - Production gameplay parity is not claimed by this package.
conflicts: []
first_failure:
  marker: none
  evidence: No concrete NPC-owned target defect has been isolated; draft workflows passed their applicable gates.
rejected_hypotheses:
  - Treat OAM-041 placement evidence as proof of dialogue, shop, travel or quest-hook correctness.
  - Resolve duplicate Harlow or nonliteral calls by guessing which source wins.
  - Copy Canary OTBM tooling into Otheryn.
  - Start the broader quests package before the smaller NPC boundary is resolved.
  - Treat skipped draft build jobs as final compilation evidence.
changed_paths:
  - docs/agents/tasks/active/OTH-20260724-oam042-npcs-reuse.md
  - docs/oam-042-npcs-reuse.md
  - tests/unit/game/oam_042_npcs_reuse_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: fresh preflight, ownership and branch overlap review
    result: PASS
    evidence: Canary preflight merged; no Otheryn OAM-042 owner existed; branch starts from current main 7c54172adfa612fa143d11630f5a341ff4c82338.
  - command: exact reviewed target/upstream blob comparison
    result: PASS
    evidence: seven reviewed core, representative data and placement files have identical Git blobs.
  - command: exact PR patch audit
    result: PASS
    evidence: PR 96 changes only the task record, proof document, focused source-contract test and test-target registration.
  - command: draft-head CI 30076953442 and Required 30076953153
    result: PASS
    evidence: workflow orchestration and Required succeeded; heavy build jobs were correctly skipped while draft.
blockers: []
next_action: Mark PR 96 ready for review, require full exact-head CI and Required, then audit comments reviews threads and main drift before expected-head squash merge.
```
