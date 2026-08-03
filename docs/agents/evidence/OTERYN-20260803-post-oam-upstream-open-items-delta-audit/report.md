# Post-OAM upstream open-items delta audit

Audit identity: `OTERYN-20260803-post-oam-upstream-open-items-delta-audit`

## 1. Exact baselines

| Repository | Exact pinned head | Authority |
|---|---|---|
| `blakinio/Otheryn` | `ae4373ad396ec6c2a2b6d1f556e2609f4c8e2819` | authoritative target |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | historical governance only |
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | upstream implementation evidence |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | donor/comparison evidence |
| `blakinio/otclient` | `4fefec3ab3a1b6401cd3b89b6e0bb1dbcb2ce2a7` | read-only client correspondence evidence |

Task-start external query: `2026-08-03T17:31:00Z`.
Final inventory query represented by this report: `2026-08-03T18:00:30Z`.

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
| `opentibiabr/canary#2826` | BLOCKEDQ‘T—Ğ“ĞÒÑQYÚÈ›İÜ™X]H[ˆ[\[Y[][Ûˆ\ÜİYH[[H˜[YY\˜Ú]Xİ\™HXÚ\Ú[Ûˆ^\İÈŸÜ[XšXXœ‹ØØ[˜\HÍMØT•PSWÔ“Õ‘SˆÈ‘QQ×Ô‘USQUSÓˆYY][H™]Z[ˆ\X[›ÛÙÈÛİ\˜ÙK[X\[™^Xİ\™Ù][H›ÛÙˆ\™Hİ[™\]Z\™YŸÜ[XšXXœ‹ØØ[˜\HÌÍŒXS”“Õ‘SˆÈ‘QQ×Ô‘USQUSÓˆYÚ™]Z[ˆ\È™]š\Ú[Û‹\[›™Y]šY[˜ÙNÈÜ™X]H›È\™Ù]\ÜİYH[[^Xİ\™Ù]›ÛÙˆ^\İÈŸÜ[XšXXœ‹ØØ[˜\HÌÍLLØS”“Õ‘SˆÈ‘QQ×Ô‘USQUSÓˆYÚ™]Z[ˆ\È™]š\Ú[Û‹\[›™Y]šY[˜ÙNÈÜ™X]H›È\™Ù]\ÜİYH[[^Xİ\™Ù]›ÛÙˆ^\İÈŸÜ[XšXXœ‹ØØ[˜\HÌÍØS”“Õ‘SˆÈ‘QQ×Ô‘USQUSÓˆYÚ™]Z[ˆ\È™]š\Ú[Û‹\[›™Y]šY[˜ÙNÈÜ™X]H›È\™Ù]\ÜİYH[[^Xİ\™Ù]›ÛÙˆ^\İÈŸÜ[XšXXœ‹ØØ[˜\HÌÌÍÍS”“Õ‘SˆÈ‘QQ×Ô‘USQUSÓˆYÚ™]Z[ˆ\È™]š\Ú[Û‹\[›™Y]šY[˜ÙNÈÜ™X]H›È\™Ù]\ÜİYH[[^Xİ\™Ù]›ÛÙˆ^\İÈŸš[X˜Y]‹ØÜ\İ[Ù\™\ˆÎLØT•PSWÔ“Õ‘SˆÈ‘QQ×Ô‘USQUSÓˆYY][H™]Z[ˆ\È™]š\Ú[Û‹\[›™Y]šY[˜ÙNÈÜ™X]H›È\™Ù]\ÜİYH[[^Xİ\™Ù]›ÛÙˆ^\İÈŸš[X˜Y]‹ØÜ\İ[Ù\™\ˆÎLØ“ĞÒÑQÈQ‘T—Ğ“ĞÒÑQYÚY™\ˆÚ]İ]\™Ù]\ÜİYHŸš[X˜Y]‹ØÜ\İ[Ù\™\ˆÍÎXT•PSWÔ“Õ‘SˆÈ‘QQ×Ô‘USQUSÓˆYÚ™]Z[ˆ\È™]š\Ú[Û‹\[›™Y]šY[˜ÙNÈÜ™X]H›È\™Ù]\ÜİYH[[^Xİ\™Ù]›ÛÙˆ^\İÈŸš[X˜Y]‹ØÜ\İ[Ù\™\ˆÍLX“ĞÒÑQÈQ‘T—Ğ“ĞÒÑQYÚY™\ˆÚ]İ]\™Ù]\ÜİYHŸš[X˜Y]‹ØÜ\İ[Ù\™\ˆÍX“ĞÒÑQÈQ‘T—Ğ“ĞÒÑQYÚY™\ˆÚ]İ]\™Ù]\ÜİYHŸš[X˜Y]‹ØÜ\İ[Ù\™\ˆÎL˜T•PSWÔ“Õ‘SˆÈ‘QQ×Ô‘USQUSÓˆYÚ™]Z[ˆÚ][šÙYˆ]šY[˜ÙNÈ^Xİ\™Ù]X\ÛY™XŞXÛH›ÛÙˆ™[XZ[œÈ™\]Z\™YŸš[X˜Y]‹ØÜ\İ[Ù\™\ˆÎL“ĞÒÑQÈQ‘T—Ğ“ĞÒÑQYÚ›Ü›X[^™HÚ]H[šÙYˆ˜[Z[NÈÜ™X]H›È\™Ù]\ÜİYH‚[\ÜİYK[Û›H[YØ][ÛœÈÚ]İ]^Xİ\™Ù]™\›ÙXİ[ÛˆÜˆİ]XÈ›ÛÙˆ™[XZ[ˆS”“Õ‘SˆÈ‘QQ×Ô‘USQUSÓ˜È›ÈÜXİ[]]™Hİ\[ˆ[\[Y[][Ûˆ\ÜİYHØ\ÈÜ™X]Y›Üˆ[K‚‚ˆÈÈËˆÜ™X]Yİ\[ˆ\ÜİY\Â‚˜ÌÌLØÌÌMÌÌMXÌÌM˜ÌÌMØÌÌNÌÌNXÌÌŒÌÌŒXÌÌŒ˜ÌÌŒØÌÌÌÌXÌÌ˜‚‚‘XXÚ\ÜİYH[œÈH^\›˜[™]š\Ú[Ûˆ[™]Y]Yİ\[ˆXY˜[Y\È\™Ù][İÛ™Y]ËXØÙ\[˜ÙHÜš]\šXK›Øİ\ÙYÚ[YÜ˜][Û‹ÑL‘H™\]Z\™[Y[Ë›Û‹YÛØ[È[™\[™[˜ŞH›İ[™\šY\Ë‚‚ˆÈÈˆ™Z™XİYZYÜ˜][Ûˆ\İ\Ù\Â‚‹H
Š˜[ËXÛÛ[]\]NŠŠˆš[X˜Y]‹ØÜ\İ[Ù\™\ˆÎKš[X˜Y]‹ØÜ\İ[Ù\™\ˆÍÎM‹H
Š˜ÛÛX˜]ŠŠˆš[X˜Y]‹ØÜ\İ[Ù\™\ˆÎÂ‹H
Š˜İ\İÛKYØ[Y\^NŠŠˆš[X˜Y]‹ØÜ\İ[Ù\™\ˆÍŒÂ‹H
Š™Z[K\™]Ø\™ŠŠˆš[X˜Y]‹ØÜ\İ[Ù\™\ˆÍÍ‚‹H
Š™\Ş[Y[[Ü\˜][ÛœÎŠŠˆÜ[XšXXœ‹ØØ[˜\HÍ‹H
Š›[Ûœİ\‹Y]\^ÎŠŠˆÜ[XšXXœ‹ØØ[˜\HÍB‹H
Šœ\ÚXØ[XÛY[YL™NŠŠˆš[X˜Y]‹ØÜ\İ[Ù\™\ˆÎ‚‹H
Šœ^Y\‹\\œÚ\İ[˜ÙNŠŠˆš[X˜Y]‹ØÜ\İ[Ù\™\ˆÍMB‹H
Šœ›İØÛÛXÛY[Y™X]\™NŠŠˆÜ[XšXXœ‹ØØ[˜\HÍÎš[X˜Y]‹ØÜ\İ[Ù\™\ˆÎL‚‹H
Š[šÛ›İÛŠŠˆÜ[XšXXœ‹ØØ[˜\HÍËÜ[XšXXœ‹ØØ[˜\HÌÎKÜ[XšXXœ‹ØØ[˜\HÌÍÌÜ[XšXXœ‹ØØ[˜\HÌÍLËÜ[XšXXœ‹ØØ[˜\HÌÌÍËÜ[XšXXœ‹ØØ[˜\HÌÌÌLÜ[XšXXœ‹ØØ[˜\HÌÌNKÜ[XšXXœ‹ØØ[˜\HÍŒNÜ[XšXXœ‹ØØ[˜\HÍŒMB‚Y][Û˜[^XÚ]™Z™Xİ[ÛœÎ‚‚‹H›ÈĞSKLMHØ\ÈÜ™X]YÂ‹HHØ[˜\H\İ™X[H[[YÙ[˜ÙHØØ[›™\‹ÛÜšÙ›İË™YÚ\İH[™™\ÜX›\Ú\ˆÙ\™H›İ\XØ]Y[ˆİ\[Â‹HÚÛKY]\XÚËÚÛK[X\ÚÛK[[Ù[H[™Ù[™\˜]Y[È[\ÜÈÙ\™H™Z™XİYÂ‹HÜ\İ[Ù\™\ˆ[™\İ™X[HØ[˜\H^™]šY]ÜÈ[™ÒHÙ\™H™X]Y\È]šY[˜ÙHÛZ[\Ë›İ]]Üš]NÂ‹H[\Ü˜\HÕÔˆÛÜšØ\›İ[™È[™^PPPËÙ\Ş[Y[[Û›HÚ[™Ù\ÈÙ\™H›İ[\ÜY[ÈHÙ\™\ˆ\™Ù]‚‚ˆÈÈKˆĞSH™XÛÛ˜Ú[X][Û‚‚•HÛÛ\]YĞSKLH›İYÚĞSKLM˜\Ù[[™H™[XZ[œÈ\›Z[˜[ˆ\È]Y]ÛÛœİ[YYH\™Ù]\˜Ú]Xİ\™H[™™[]˜[™]Z[™Y›İ[™\šY\È\İ[ˆ[YN‚‚‹H]Y\İËÙ]\XÚÈš[™[™ÜÈ\™HY\][ÛˆØ[™Y]\ÈÛ›HÚ[ˆ^Xİ\™Ù]ØÜš\È›İ™HHØ[YHY™XİÂ‹H›İØÛÛØÛY[š[™[™ÜÈ™\]Z\™HXZ[Z[™YXÛY[ÛÜœ™\ÜÛ™[˜ÙH[™\™Ù]XÚÙ]Ü›Ùš[H]šY[˜ÙNÂ‹H\œÚ\İ[˜ÙHÚ[™Ù\ÈØ[››İÜ›ÜÜÈÔSÒÕ‹ÛY™XŞXÛH›İ[™\šY\ÈHÛ›ÜˆÚ[Z[\š]NÂ‹H\Ş[Y[Ü\˜][ÛœÈ[™\ÚXØ[XÛY[[™œ˜\İXİ\™H™[XZ[ˆİ]ÚYH]]ÛX]XÈZYÜ˜][ÛÂ‹H\İ™X[H[[YÙ[˜ÙH™[XZ[œÈØ[˜\K[İÛ™Y[™\ÈÛÛœİ[YY™XY[Û›K‚‚“›ÈÛÛ\]YĞSHXÚØYÙHØ\È™[Ü[™Y‚‚ˆÈÈLˆÜ[‹Z][HšY‚Ü\İ[Ù\™\ˆ\ÜİYHÍLÍX\X\™Y[ˆH]™HÛÛXİ[ÛˆY\ˆH\ÚË\İ\Ûİ[ˆ]\È™\™\Ù[Y\ÈS”“Õ‘SˆÈ‘QQ×Ô‘USQUSÓ˜ˆ›ÈÛİ\˜ÙHˆXYÚ[™ÙHÜˆÛÜİ\™HØ\È\ÙYÈ™[[İ™HH›İÈÚ]İ]™XÛÛ˜Ú[X][Û‹‚‚ˆÈÈLKˆ[™\[™[Ú[[™ÙB‚Hœ™\Ú˜[ÚYšXØ][Ûˆ\ÜÈÚ[[™ÙY‚‚‹HÛÛ\]H›İ\‹XÛÛXİ[ÛˆÛİ™\˜YÙH[™HLˆOˆLØšYÂ‹H]™\HÜš]XØ[ÚYÚØ[™Y]NÂ‹HHÛÛH‘UTÑWĞĞS‘QUX
Î‹ÈÌÌNX
NÂ‹HH]ÛZXÚ]HÛZ[H[ˆÛ›ÜˆˆÌLŒ˜™\İ[[™È[ˆ‘UÔ’UWĞĞS‘QUX˜]\ˆ[ˆ™]\ÙNÂ‹H™\™\Ù[]]™H™Z™XİY][\Îˆ^PPPÈØÚÙ\‹[\Ü˜\HÕÔˆ[İ[ÛÜšØ\›İ[™]]ÚX[Ø]]Üİ[Û‹[È[Ûœİ\ˆÛİ[ÈÙX\ÛÛ˜[ÛÛ[š[˜\H^Y\ˆØ]™H[™œ›ØYÊÊÈZ[K\™]Ø\™™\XÙ[Y[Â‹H\XØ]H˜[Z[Y\ÎˆÌÎN‹ÈÍNÎLÈÎLËÈÍÌËÈÍXÌ‹ÈÍLXÍÎKÈÎL˜ÍÎMÈÎXÂ‹HÛÛ™›XİÈÚ]ÛÛ\]YĞSHÛÛ˜XİÈ[™XØÚY[[\XØ][ÛˆÙˆ\İ™X[H[[YÙ[˜ÙK‚‚“X]\šX[Ú[[™ÙHİ]ÛÛY\ÈÙ\™H[˜ÛÜœÜ˜]Y[ÈHš[˜[Û\ÜÚYšXØ][ÛœÈ[™\ÜİYH›İ[™\šY\Ë‚‚ˆÈÈL‹ˆ˜[Y][Ûˆ[™^XÚ]›Û˜ÛZ[\Â‚•˜[Y]Y‚‚‹HLÈ[š\]YH›İÜÎÂ‹HÛİ\˜ÙHİ[ÈM
ÈŒ
ÈŒ
ÈXÂ‹H]™\H›İÈ\È[ˆ]šY[˜ÙHİ]\È[™ZYÜ˜][Ûˆ\ÜÜÚ][ÛÂ‹H]™\HØ[™Y]H›İÈ˜[Y\È^Xİ\™Ù]]šY[˜ÙH[™H›İ[™Y\™Ù]\ÜİYNÂ‹HM\İ[˜İ\™Ù]\ÜİY\È[šÈ˜XÚÈÈH™\Ü[™[ÜNÂ‹H\XØ]KÜİ\\œÙ\ÜÚ[Ûˆ™Y™\™[˜Ù\È™\ÛÛ™HÈ™\™\Ù[Y][\ÎÂ‹H”ÓÓˆ\œÙ\È[™ÔÕˆ›İÈÛİ[X]Ú\È”ÓÓÂ‹H]Y]]ÈÛÛZ[ˆØİ[Y[][Û‹Ù]šY[˜ÙHÛ›NÂ‹H[[YHL‘H›Üˆ\È]Y]ˆ\È“ÕĞTPĞP“X‚‚“Y]Y]H›Û˜ÛZ[NˆHÛÛ›™XİÜ‰ÜÈÛÛ\]H[È\ÜİYH]Y\HÛZ]Y]]Ü‹ØÜ™X]Yİ\]Y˜[Y\È›Üˆ[Üİ\ÜİYH›İÜËˆ[È\™H™]Z[™Y[ˆH[™[ÜH˜]\ˆ[ˆ[™[Yˆ\ÈÙ\È›İY™™Xİ][HY[]KÛİ™\˜YÙKÛİ\˜ÙH™]š\Ú[Ûˆ›ÜˆœË\™Ù]›ÛÙˆÜˆ\ÜÜÚ][Û‹]H™\ÜÙ\È›İÛZ[H[˜]˜Z[X›H\ÜİYHY]Y]K‚‚’[\[Y[][Ûˆ›Û˜ÛZ[\Î‚‚‹H›È^Xİ]X›Hİ\[ˆ™Z]š[ÜˆØ\ÈÚ[™ÙYÂ‹H›ÈØ[™Y]H\ÈXÛ\™Y›ÙXİ[Û‹\™XYHH\È]Y]Â‹H›È^\›˜[[\[Y[][Ûˆ\ÈXÛ\™Y]]Üš]]]™NÂ‹H›È[œ›İ™[ˆ^\›˜[\ÜİYHØ\ÈÛÛ™\Y[ÈH\™Ù][\[Y[][Ûˆ\ÜİYNÂ‹H›È›İØÛÛ\œÚ\İ[˜ÙKX\ÜˆÛY[L‘HØ\È\™›Ü›YYÛˆ™Z[ˆÙˆ]\™H[\[Y[][ÛˆXÚØYÙ\Ë‚‚ˆÈÈ™^Xİ[Û‚‚“Y\™ÙH[™\˜Ú]™HHØİ[Y[][Û‹[Û›H]Y]ˆY\ˆ^XİZXY™\]Z\™YÒH[™™]šY]Ë]™XYÚXÚÜÈ\ÜË‚