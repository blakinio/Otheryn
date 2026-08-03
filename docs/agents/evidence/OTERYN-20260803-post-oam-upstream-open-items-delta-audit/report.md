# Post-OAM upstream open-items delta audit

Audit identity: `OTERYN-20260803-post-oam-upstream-open-items-delta-audit`

## 1. Exact baselines

| Repository | Exact pinned head | Authority |
|---|---|---|
| `blakinio/Otheryn` | `ae4373ad396ec6c2a2b6d1f556e2609f4c8e2819` | authoritative target |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | historical governance only |
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | upstream implementation evidence |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | donor/comparison evidence |
| `blakinio/otclient` | task start `4fefec3ab3a1b6401cd3b89b6e0bb1dbcb2ce2a7`; final `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | read-only client correspondence evidence; drift was CI-workflow-only |

Task-start external query: `2026-08-03T17:31:00Z`.
Final inventory and all-open-PR-head re-query represented by this report: `2026-08-03T18:29:39Z`.

## 2. Coverage reconciliation

| Collection | Initial | Final represented | Drift |
|---|---:|---:|---|
| upstream Canary open PRs | 14 | 14 | 0 |
| upstream Canary open Issues | 60 | 60 | 0 |
| CrystalServer open PRs | 20 | 20 | 0 |
| CrystalServer open Issues | 8 | 9 | +1: `zimbadev/crystalserver#535` |
| **Total** | **102** | **103** | **+1** |

Every final live item has exactly one machine-readable row. Issue/PR pairs are normalized through `duplicate_or_superseded_by` and a shared target Issue where applicable.

## 3. Disposition summary

| Disposition | Count |
|---|---:|
| ALREADY_PRESENT | 0 |
| REUSE_CANDIDATE | 1 |
| ADAPT_CANDIDATE | 13 |
| REWRITE_CANDIDATE | 1 |
| DO_NOT_MIGRATE | 20 |
| SUPERSEDED | 1 |
| NEEDS_REVALIDATION | 61 |
| DEFER_BLOCKED | 6 |

Evidence-status totals: `PROVEN_TARGET_GAP=15`, `PROVEN_NOT_APPLICABLE=21`, `PARTIALLY_PROVEN=7`, `UNPROVEN=54`, `BLOCKED=6`.

## 4. Validated migration candidates

| Source item | Evidence | Disposition | Severity | Otheryn Issue | Exact target boundary |
|---|---|---|---|---|---|
| `opentibiabr/canary#4058` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | medium | `#321` | src/game/game.cpp |
| `opentibiabr/canary#4054` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | medium | `#322` | src/creatures/monsters/monster.cpp |
| `opentibiabr/canary#4053` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | medium | `#325` | data-otservbr-global/npc/storkus.lua |
| `opentibiabr/canary#4045` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | medium | `#323` | data/modules/scripts/gamestore/catalog/extras_usefull_things.lua |
| `opentibiabr/canary#4044` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | medium | `#324` | 11 Djinn NPC scripts |
| `opentibiabr/canary#4025` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | medium | `#326` | same two target paths |
| `opentibiabr/canary#3986` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | medium | `#321` | src/game/game.cpp |
| `zimbadev/crystalserver#851` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | high | `#313` | src/creatures/players/player.cpp |
| `zimbadev/crystalserver#850` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | high | `#314` | src/creatures/players/player.cpp |
| `zimbadev/crystalserver#849` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | high | `#315` | src/creatures/players/player.cpp |
| `zimbadev/crystalserver#848` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | high | `#316` | src/creatures/combat/condition.cpp |
| `zimbadev/crystalserver#846` | PROVEN_TARGET_GAP | REUSE_CANDIDATE | medium | `#319` | data/npclib/npc_system/bank_system.lua |
| `zimbadev/crystalserver#845` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | medium | `#317` | data-otservbr-global/scripts/quests/soul_war/soul_war_mechanics.lua |
| `zimbadev/crystalserver#844` | PROVEN_TARGET_GAP | ADAPT_CANDIDATE | medium | `#318` | data-otservbr-global/scripts/globalevents/others/raids_schedule.lua |
| `zimbadev/crystalserver#122` | PROVEN_TARGET_GAP | REWRITE_CANDIDATE | critical | `#320` | src/lua/functions/creatures/npc/npc_functions.cpp |

The two rows for upstream Issue `#3986` and PR `#4058` represent one underlying change and one target Issue (`#321`). Therefore 15 candidate rows produced 14 bounded Otheryn implementation Issues.

## 5. Critical and high findings

- **Critical:** CrystalServer PR `#122` proves that the exact Otheryn NPC-buy path can deliver items before payment succeeds. Donor prevalidation is insufficient as an atomicity contract, so target Issue `#320` requires a rewrite with compensation/fail-closed tests.
- **High:** CrystalServer PR `#851` proves stash quantity can be removed before successful placement and the shortfall lost. Target Issue `#313`.
- **High:** CrystalServer PR `#850` matches an unguarded `exp / rawExp` expression on the exact target. Target Issue `#314`.
- **High:** CrystalServer PR `#849` matches an unguarded null tile dereference in creature update serialization. Target Issue `#315`.
- **High:** CrystalServer PR `#848` matches unbounded serialized condition indexes before array writes. Target Issue `#316`.
- High but not implementation-ready items remain explicitly uncertain or blocked, including map reload/client crash (`#785/#852`), Expert/Open PvP families and multiworld families.

## 6. Uncertain, conflicting or blocked items

| Item | Status | Severity | Required next proof |
|---|---|---|---|
| `opentibiabr/canary#4056` | PARTIALLY_PROVEN / NEEDS_REVALIDATION | medium | perform bounded target proof only if the corresponding target capability is authorized |
| `opentibiabr/canary#4052` | PARTIALLY_PROVEN / NEEDS_REVALIDATION | low | perform bounded target proof only if the corresponding target capability is authorized |
| `opentibiabr/canary#4033` | BLOCKED / DEFER_BLOCKED | high | do not create an implementation Issue until the named architecture decision exists |
| `opentibiabr/canary#2826` | BLOCKED / DEFER_BLOCKED | high | do not create an implementation Issue until the named architecture decision exists |
| `opentibiabr/canary#4057` | PARTIALLY_PROVEN / NEEDS_REVALIDATION | medium | retain partial proof; source-map and exact target tile proof are still required |
| `opentibiabr/canary#3605` | UNPROVEN / NEEDS_REVALIDATION | high | retain as revision-pinned evidence; create no target Issue until exact target proof exists |
| `opentibiabr/canary#3513` | UNPROVEN / NEEDS_REVALIDATION | high | retain as revision-pinned evidence; create no target Issue until exact target proof exists |
| `opentibiabr/canary#3427` | UNPROVEN / NEEDS_REVALIDATION | high | retain as revision-pinned evidence; create no target Issue until exact target proof exists |
| `opentibiabr/canary#3374` | UNPROVEN / NEEDS_REVALIDATION | high | retain as revision-pinned evidence; create no target Issue until exact target proof exists |
| `zimbadev/crystalserver#853` | PARTIALLY_PROVEN / NEEDS_REVALIDATION | medium | retain as revision-pinned evidence; create no target Issue until exact target proof exists |
| `zimbadev/crystalserver#813` | BLOCKED / DEFER_BLOCKED | high | defer without target Issue |
| `zimbadev/crystalserver#785` | PARTIALLY_PROVEN / NEEDS_REVALIDATION | high | retain as revision-pinned evidence; create no target Issue until exact target proof exists |
| `zimbadev/crystalserver#451` | BLOCKED / DEFER_BLOCKED | high | defer without target Issue |
| `zimbadev/crystalserver#445` | BLOCKED / DEFER_BLOCKED | high | defer without target Issue |
| `zimbadev/crystalserver#852` | PARTIALLY_PROVEN / NEEDS_REVALIDATION | high | retain with linked PR evidence; exact target map/lifecycle proof remains required |
| `zimbadev/crystalserver#810` | BLOCKED / DEFER_BLOCKED | high | normalize with the linked PR family; create no target Issue |

All Issue-only allegations without exact target reproduction or static proof remain `UNPROVEN / NEEDS_REVALIDATION`; no speculative Otheryn implementation Issue was created for them.

## 7. Created Otheryn Issues

`#313`, `#314`, `#315`, `#316`, `#317`, `#318`, `#319`, `#320`, `#321`, `#322`, `#323`, `#324`, `#325`, `#326`.

Each Issue pins the external revision and audited Otheryn head, names target-owned paths, acceptance criteria, focused/integration/E2E requirements, non-goals and dependency boundaries.

## 8. Rejected migration hypotheses

- **bulk-content-update:** zimbadev/crystalserver#805, zimbadev/crystalserver#794
- **combat:** zimbadev/crystalserver#847
- **custom-gameplay:** zimbadev/crystalserver#627
- **daily-reward:** zimbadev/crystalserver#742
- **deployment-operations:** opentibiabr/canary#4048
- **monster-datapack:** opentibiabr/canary#4029
- **physical-client-e2e:** zimbadev/crystalserver#826
- **player-persistence:** zimbadev/crystalserver#545
- **protocol-client-feature:** opentibiabr/canary#4038, zimbadev/crystalserver#812
- **unknown:** opentibiabr/canary#4003, opentibiabr/canary#3841, opentibiabr/canary#3470, opentibiabr/canary#3413, opentibiabr/canary#3347, opentibiabr/canary#3310, opentibiabr/canary#3059, opentibiabr/canary#618, opentibiabr/canary#615

Additional explicit rejections:

- no OAM-055 was created;
- the Canary Upstream Intelligence scanner, workflow, registry and report publisher were not duplicated in Otheryn;
- whole-datapack, whole-map, whole-module and generated bulk imports were rejected;
- CrystalServer and upstream Canary text, reviews and CI were treated as evidence claims, not authority;
- temporary OTCR workarounds and MyAAC/deployment-only changes were not imported into the server target.

## 9. OAM reconciliation

The completed OAM-001 through OAM-054 baseline remains terminal. This audit consumed the target architecture and relevant retained boundaries just in time:

- quests/datapack findings are adaptation candidates only when exact target scripts prove the same defect;
- protocol/client findings require maintained-client correspondence and target packet/profile evidence;
- persistence changes cannot cross SQL/KV/lifecycle boundaries by donor similarity;
- deployment operations and physical-client infrastructure remain outside automatic migration;
- Upstream Intelligence remains Canary-owned and is consumed read-only.

No completed OAM package was reopened.

## 10. Open-item drift

CrystalServer Issue `#535` appeared in the live collection after the task-start count. It is represented as `UNPROVEN / NEEDS_REVALIDATION`. Upstream Canary PR `#4025` changed from task-start head `c924fdb05b0e8f6f7fccd248eceeb48ff27c7648` to final head `38878bd04536ef20a7f2560b56d86dc742f28bfa`; the final diff was re-inspected and Otheryn Issue `#326` was updated with the stronger round-state and repeated-dialogue boundary. The OTClient default branch advanced to `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` through merged PR `#239`, which changes only a temporary CI workflow and does not alter protocol/client correspondence for this audit. All 34 final open PR heads were re-fetched; the other 33 were unchanged. No source PR head change or closure was used to remove a row without reconciliation.

## 11. Independent challenge

A fresh falsification pass challenged:

- complete four-collection coverage, the `102 -> 103` item drift, and all 34 final open-PR head revisions;
- every critical/high candidate;
- the sole `REUSE_CANDIDATE` (`#846/#319`);
- the atomicity claim in donor PR `#122`, resulting in `REWRITE_CANDIDATE` rather than reuse;
- representative rejected items: MyAAC Docker, temporary OTCR mount workaround, autoheal/autopotion, bulk monster loot, bulk seasonal content, binary player save and broad C++ daily-reward replacement;
- duplicate families: `#3986/#4058`, `#810/#813/#4033/#445`, `#2826/#451`, `#785/#852`, `#794/#805`;
- conflicts with completed OAM contracts and accidental duplication of Upstream Intelligence.

Material challenge outcomes were incorporated into the final classifications and Issue boundaries.

## 12. Validation and explicit nonclaims

Validated:

- 103 unique rows;
- all 34 live open PR heads re-fetched, with 33 unchanged and `opentibiabr/canary#4025` reconciled at final head `38878bd04536ef20a7f2560b56d86dc742f28bfa`;
- source totals `14 + 60 + 20 + 9`;
- every row has an evidence status and migration disposition;
- every candidate row names exact target evidence and a bounded target Issue;
- 14 distinct target Issues link back to the report inventory;
- duplicate/supersession references resolve to represented items;
- JSON parses and CSV row count matches JSON;
- audit paths contain documentation/evidence only;
- runtime E2E for this audit PR is `NOT_APPLICABLE`.

Metadata nonclaim: the connector's complete bulk Issue query omitted author/created/updated values for most Issue rows. Nulls are retained in the inventory rather than invented. This does not affect item identity, coverage, source revision for PRs, target proof or disposition, but the report does not claim unavailable Issue metadata.

Implementation nonclaims:

- no executable Otheryn behavior was changed;
- no candidate is declared production-ready by this audit;
- no external implementation is declared authoritative;
- no unproven external Issue was converted into a target implementation Issue;
- no protocol, persistence, map or client E2E was performed on behalf of future implementation packages.

## Next action

Merge and archive the documentation-only audit PR after exact-head required CI and review-thread checks pass.
