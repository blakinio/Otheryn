---
task_id: OTH-20260724-oam043-quests-adapt
status: completed
branch: dudantas/oam-043-quests-target-proof
base_branch: main
created: 2026-07-24
updated: 2026-07-24
completed: 2026-07-24T14:24:00+02:00
last_verified_commit: "6512d78004ae2540784b3e67592a92a903554cf6"
related_pr: "98"
owned_paths:
  - docs/agents/tasks/archive/OTH-20260724-oam043-quests-adapt.md
  - data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua
  - data-otservbr-global/scripts/quests/soulpit/soulpit_fight.lua
  - data-otservbr-global/scripts/quests/the_ancient_tombs/actions_oasis_lever_door.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua
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

Exact three-way inventory, complete source scanning and configured-map correlation isolated six bounded target gaps: three corrections in existing quest scripts and three map-backed legacy-only `The Beginning` handlers. No bulk quest-tree copy, map mutation, protocol/client change, schema change or deployment change was included.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T14:24:00+02:00
head: 6512d78004ae2540784b3e67592a92a903554cf6
branch: main
pr: 98
status: completed
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - docs/agents/tasks/archive/OTH-20260724-oam043-quests-adapt.md
  - data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua
  - data-otservbr-global/scripts/quests/soulpit/soulpit_fight.lua
  - data-otservbr-global/scripts/quests/the_ancient_tombs/actions_oasis_lever_door.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua
  - data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua
  - docs/oam-043-quests-adapt.md
  - tests/unit/game/oam_043_quests_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Canary PR 866 selected canonical quests with REVALIDATE; post-preflight handoff PR 872 merged as 13ec3077babba0ac81bb1e30e79f0ea4827ae2fe.
  - Exact baselines were Otheryn 3a37f3d5e4c01ddf4469f1c71461c40ca749142f, upstream 7323503b3dc61ed86bf1f04a611b2d0aec64b35a and legacy 13ec3077babba0ac81bb1e30e79f0ea4827ae2fe.
  - Inventory manifest 391e38d963b1a791e4fd59edf8ce6adbb4a75dfc8e8a34da351c50f080267925 records target/upstream 978 files, legacy 981, 973 all-identical, five target/upstream-identical divergences and three legacy-only paths.
  - Complete source scan digest a97442a2e77aee6cd02ba094a8158965a1da9681d0426114c7cd1c3546e3ef40 covers 978 files and 12027 evidence entries.
  - The source scan preserves 1045 dynamic expressions as unresolved, including 593 storage, 266 position, 182 item and four unique-ID findings.
  - Configured map SHA a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 produced World Index SHA 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a with zero unknown tails.
  - Complete map correlation records 8860 confirmed, 484 script-only, 2683 unresolved, zero map-only and zero conflicting findings.
  - Hero of Rathleton used an unregistered achievement spelling; target catalogue proved The Professor's Nut is canonical.
  - Soulpit onUse referenced undefined creature; generic target Encounter countMonsters already existed and rejected the wider legacy override.
  - Ancient Tomb donor proved timed door closure, while AID 12108 was script-only with zero configured-map placements and was rejected.
  - Three legacy-only The Beginning handlers produced 47 confirmed and zero script-only map findings, proving bounded restoration was required.
  - Target had no hasAccountQuestAccess or unlockAccountQuestAccess API, so Ape City and Wrath account-access donor changes were rejected.
  - Final source-contract scope repaired three existing files, added exactly three map-backed handlers and left the final quest inventory at 981 files.
  - Ready head 7a783c65e83a9fead651e38f336b10cbffe7a19b passed autofix 30090686762, CI 30090686923, Required 30090686740 and Repository Audit 30090564163 across Fast Checks, Lua, Linux debug/release with full tests, Windows CMake/Solution and macOS.
  - Validation-only sync head 333b7047f8ecc660a84b215e9a4149b10d083c35 passed autofix 30091648723, CI 30091648878, Required 30091648720 and Repository Audit 30091648732.
  - PR 98 had no comments, reviews or review threads and Otheryn main had no drift from task-start baseline before merge.
  - PR 98 squash-merged as 6512d78004ae2540784b3e67592a92a903554cf6.
derived:
  - Canonical quests required bounded ADAPT rather than REUSE because concrete source defects and map-backed missing handlers were proven.
  - The remaining shared script-only and dynamic findings are evidence boundaries, not authorization for broad remediation.
  - No maintained-client, protocol, map, schema or deployment mutation was justified by the accepted package.
unknown:
  - Exact gameplay impact and ownership of each of the 484 shared target/upstream script-only findings.
  - Runtime values and execution paths of the 1045 unresolved dynamic expressions.
  - Exhaustive stage ordering, reachability and scope for all 2016 storage references.
  - Full factual correctness of every quest family, reward, NPC/spawn dependency and access gate.
  - Physical-client and production gameplay parity.
conflicts: []
first_failure:
  marker: candidate donor AID 12108
  evidence: Run 30089559964 rejected the legacy dual registration; preserved diagnostics in run 30089658579 classified AID 12108 as script-only with map count zero.
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
  - docs/agents/tasks/archive/OTH-20260724-oam043-quests-adapt.md
  - docs/oam-043-quests-adapt.md
  - tests/unit/game/oam_043_quests_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: exact inventory, complete source scan and configured-map correlation
    result: PASS
    evidence: Otheryn run 30089008736; evidence artifact digest sha256:2272eea7e77e3c04a4ed6e8ddf30e75dcdf18f115a1dcf8f624d00e9f7191f76.
  - command: bounded legacy-only and candidate donor map correlation
    result: PASS
    evidence: Runs 30089339771 and 30089658579 proved the three The Beginning handlers and rejected AID 12108.
  - command: exact target prerequisite symbol search
    result: PASS
    evidence: Run 30089254012 proved the achievement catalogue, generic Encounter counter and absent account-wide quest APIs.
  - command: feature exact-head gates
    result: PASS
    evidence: Ready head 7a783c65e83a9fead651e38f336b10cbffe7a19b and sync head 333b7047f8ecc660a84b215e9a4149b10d083c35 passed all required gates.
  - command: feature merge and lifecycle readiness
    result: PASS
    evidence: PR 98 merged as 6512d78004ae2540784b3e67592a92a903554cf6 after clean discussion audit and zero target-main drift.
blockers: []
next_action: Complete the separate Otheryn lifecycle archive PR, then hand the exact feature and lifecycle evidence to Canary governance without starting OAM-044.
```
