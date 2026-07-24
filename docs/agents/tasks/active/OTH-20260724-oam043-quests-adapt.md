---
task_id: OTH-20260724-oam043-quests-adapt
status: review
branch: dudantas/oam-043-quests-target-proof
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "7a783c65e83a9fead651e38f336b10cbffe7a19b"
related_pr: "98"
owned_paths:
  - data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua
  - data-otservbr-global/scripts/quests/soulpit/soulpit_fight.lua
  - data-otservbr-global/scripts/quests/the_ancient_tombs/actions_oasis_lever_door.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua
  - docs/agents/tasks/active/OTH-20260724-oam043-quests-adapt.md
  - docs/oam-043-quests-adapt.md
  - tests/unit/game/oam_043_quests_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - docs/oam-043-quests-adapt.md
optional_reads: []
---

# OAM-043 quests target adaptation

## Final disposition

`ADAPT` with explicit evidence boundaries.

Exact three-way inventory, complete source scanning and configured-map correlation isolate six bounded target gaps: three corrections in existing quest scripts and three map-backed legacy-only `The Beginning` handlers. No bulk quest-tree copy, map mutation, protocol/client change, schema change or deployment change is included.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T14:01:00+02:00
head: 7a783c65e83a9fead651e38f336b10cbffe7a19b
branch: dudantas/oam-043-quests-target-proof
pr: 98
status: validating
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua
  - data-otservbr-global/scripts/quests/soulpit/soulpit_fight.lua
  - data-otservbr-global/scripts/quests/the_ancient_tombs/actions_oasis_lever_door.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua
  - docs/agents/tasks/active/OTH-20260724-oam043-quests-adapt.md
  - docs/oam-043-quests-adapt.md
  - tests/unit/game/oam_043_quests_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Canary PR 866 selected canonical quests with REVALIDATE; post-preflight handoff PR 872 merged as 13ec3077babba0ac81bb1e30e79f0ea4827ae2fe.
  - Exact baselines are Otheryn 3a37f3d5e4c01ddf4469f1c71461c40ca749142f, upstream 7323503b3dc61ed86bf1f04a611b2d0aec64b35a and legacy 13ec3077babba0ac81bb1e30e79f0ea4827ae2fe.
  - Inventory manifest 391e38d963b1a791e4fd59edf8ce6adbb4a75dfc8e8a34da351c50f080267925 records target/upstream 978 files, legacy 981, 973 all-identical, five target/upstream-identical divergences and three legacy-only paths.
  - Complete source scan digest a97442a2e77aee6cd02ba094a8158965a1da9681d0426114c7cd1c3546e3ef40 covers 978 files and 12027 evidence entries.
  - The source scan preserves 1045 dynamic expressions as unresolved, including 593 storage, 266 position, 182 item and four unique-ID findings.
  - Configured map SHA a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 produced World Index SHA 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a with zero unknown tails.
  - Complete map correlation records 8860 confirmed, 484 script-only, 2683 unresolved, zero map-only and zero conflicting findings.
  - Hero of Rathleton uses an unregistered achievement spelling; target catalogue proves The Professor's Nut is canonical.
  - Soulpit onUse references undefined creature; generic target Encounter countMonsters already exists and rejects the wider legacy override.
  - Ancient Tomb donor proves timed door closure, while AID 12108 is script-only with zero configured-map placements and is rejected.
  - Three legacy-only The Beginning handlers produce 47 confirmed and zero script-only map findings, proving bounded restoration is required.
  - Target has no hasAccountQuestAccess or unlockAccountQuestAccess API, so Ape City and Wrath account-access donor changes are rejected.
  - Final source-contract scope repairs three existing files, adds exactly three map-backed handlers and leaves final quest inventory at 981 files.
derived:
  - Canonical quests requires bounded ADAPT rather than REUSE because concrete source defects and map-backed missing handlers are proven.
  - The remaining shared script-only and dynamic findings are evidence boundaries, not authorization for broad remediation.
  - No maintained-client, protocol, map, schema or deployment mutation is justified by the accepted package.
unknown:
  - Exact gameplay impact and ownership of each of the 484 shared target/upstream script-only findings.
  - Runtime values and execution paths of the 1045 unresolved dynamic expressions.
  - Exhaustive stage ordering, reachability and scope for all 2016 storage references.
  - Full factual correctness of every quest family, reward, NPC/spawn dependency and access gate.
  - Physical-client and production gameplay parity.
conflicts: []
first_failure:
  marker: candidate donor AID 12108
  evidence: Run 30089559964 rejected the legacy dual registration; preserved diagnostics in run 30089658579 classify AID 12108 as script-only with map count zero.
rejected_hypotheses:
  - Finalize quests as REUSE from target/upstream inventory identity alone.
  - Bulk-copy the legacy quest tree or all five divergent legacy variants.
  - Import account-wide quest-access calls without the prerequisite target API.
  - Restore the redundant Soulpit-local countMonsters override.
  - Register Ancient Tomb AID 12108 despite zero configured-map placements.
  - Treat unresolved dynamic expressions or lexical storage references as proven runtime progression.
changed_paths:
  - data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua
  - data-otservbr-global/scripts/quests/soulpit/soulpit_fight.lua
  - data-otservbr-global/scripts/quests/the_ancient_tombs/actions_oasis_lever_door.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua
  - docs/agents/tasks/active/OTH-20260724-oam043-quests-adapt.md
  - docs/oam-043-quests-adapt.md
  - tests/unit/game/oam_043_quests_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: exact inventory, complete source scan and configured-map correlation
    result: PASS
    evidence: Otheryn run 30089008736; evidence artifact digest sha256:2272eea7e77e3c04a4ed6e8ddf30e75dcdf18f115a1dcf8f624d00e9f7191f76.
  - command: bounded legacy-only and candidate donor map correlation
    result: PASS
    evidence: Runs 30089339771 and 30089658579 prove the three The Beginning handlers and reject AID 12108.
  - command: exact target prerequisite symbol search
    result: PASS
    evidence: Run 30089254012 proves the achievement catalogue, generic Encounter counter and absent account-wide quest APIs.
  - command: final exact-head CI, Required and repository audit
    result: PASS
    evidence: Head 7a783c65e83a9fead651e38f336b10cbffe7a19b passed autofix 30090686762, CI 30090686923, Required 30090686740 and Repository Audit 30090564163 across Fast Checks, Lua, Linux debug/release with full tests, Windows CMake/Solution and macOS.
blockers: []
next_action: Require exact-head gates on this validation-only synchronization commit, audit comments/reviews/threads and target-main drift, then squash-merge PR 98 with the expected head.
```
