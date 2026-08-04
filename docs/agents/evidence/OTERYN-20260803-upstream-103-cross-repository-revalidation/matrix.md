# Macierz 103 elementów

`C`=upstream Canary, `R`=CrystalServer, `F`=blakinio/canary, `O`=Otheryn, `K`=OTClient. Stany: `D` defect, `X` fix, `I` inna implementacja, `P` feature, `A` poza architekturą, `N` poza produktem, `?` nieudowodnione, `-` nieistotne.

|#|Źródło|Konkluzja|C|R|F|O|K|Dowód|Decyzja|
|---:|---|---|:--:|:--:|:--:|:--:|:--:|---|---|
|1|`opentibiabr/canary#4058`|Otheryn+Crystal defect; fork fixed.|D|D|X|D|-|PROVEN|GAP|
|2|`opentibiabr/canary#4056`|Effect-source/virtue packet contract needs maintained-client proof.|P|I|I|I|?|PARTIALLY_PROVEN|CLIENT-DECISION|
|3|`opentibiabr/canary#4055`|Superseded dependency baseline; no target migration.|P|N|N|N|-|PROVEN|NO-ACTION|
|4|`opentibiabr/canary#4054`|Same rename-refresh defect in all server lines.|D|D|D|D|-|PROVEN|GAP|
|5|`opentibiabr/canary#4053`|Otheryn/fork exact defect; Crystal differs.|D|I|D|D|-|PROVEN|GAP|
|6|`opentibiabr/canary#4052`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|-|PARTIALLY_PROVEN|INSUFFICIENT|
|7|`opentibiabr/canary#4048`|MyAAC/Docker deployment; outside server target.|P|N|N|N|-|PROVEN|NO-ACTION|
|8|`opentibiabr/canary#4045`|Otheryn/fork wrong bundle values; Crystal differs.|D|I|D|D|-|PROVEN|GAP|
|9|`opentibiabr/canary#4044`|Same Djinn greeting defect in all server lines.|D|D|D|D|-|PROVEN|GAP|
|10|`opentibiabr/canary#4038`|Custom viewport/Idle Hunt product package.|P|N|N|N|?|PROVEN|NO-ACTION|
|11|`opentibiabr/canary#4033`|Expert/Open PvP implementations differ; target contract required.|I|P|I|A|?|BLOCKED_BY_DECISION|ARCH-DECISION|
|12|`opentibiabr/canary#4029`|Unreviewed generated bulk loot import.|P|N|N|N|-|PROVEN|NO-ACTION|
|13|`opentibiabr/canary#4025`|Otheryn/fork old mead-state defect; Crystal differs.|D|I|D|D|-|PROVEN|GAP|
|14|`opentibiabr/canary#2826`|Multiworld lineage shared; target schema/routing contract required.|P|P|I|A|-|BLOCKED_BY_DECISION|PERSIST-DECISION|
|15|`opentibiabr/canary#4057`|quests-map: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|?|PARTIALLY_PROVEN|REPRO|
|16|`opentibiabr/canary#4013`|server-save: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|17|`opentibiabr/canary#4003`|arm64 image publication request.|?|N|N|N|-|PROVEN|NO-ACTION|
|18|`opentibiabr/canary#3986`|Same family as PR #4058; Otheryn affected, fork fixed.|D|D|X|D|-|PROVEN|GAP|
|19|`opentibiabr/canary#3875`|feaster-of-souls: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|20|`opentibiabr/canary#3841`|Broad Summer Update content request.|?|N|N|N|-|PROVEN|NO-ACTION|
|21|`opentibiabr/canary#3803`|monster-spawns: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|22|`opentibiabr/canary#3770`|ice-islands-quest: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|23|`opentibiabr/canary#3745`|equipment-quiver: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|?|UNPROVEN|REPRO|
|24|`opentibiabr/canary#3742`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|?|UNPROVEN|INSUFFICIENT|
|25|`opentibiabr/canary#3724`|wheel-persistence: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|26|`opentibiabr/canary#3645`|weapon-protocol: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|?|UNPROVEN|REPRO|
|27|`opentibiabr/canary#3605`|cults-of-tibia-client-map: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|?|UNPROVEN|REPRO|
|28|`opentibiabr/canary#3599`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|-|UNPROVEN|INSUFFICIENT|
|29|`opentibiabr/canary#3584`|combat-fields: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|30|`opentibiabr/canary#3549`|hazard-system: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|31|`opentibiabr/canary#3534`|beregar-quest: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|32|`opentibiabr/canary#3513`|zones-client-state: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|?|UNPROVEN|REPRO|
|33|`opentibiabr/canary#3506`|grave-danger: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|34|`opentibiabr/canary#3500`|soul-war: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|35|`opentibiabr/canary#3485`|hirelings-protocol: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|?|UNPROVEN|REPRO|
|36|`opentibiabr/canary#3479`|encounter-system: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|37|`opentibiabr/canary#3478`|freequest-storage: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|38|`opentibiabr/canary#3470`|New Lua API feature proposal.|?|N|N|N|-|PROVEN|NO-ACTION|
|39|`opentibiabr/canary#3458`|soulpit: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|40|`opentibiabr/canary#3453`|quest-door: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|41|`opentibiabr/canary#3447`|npc-dialogue: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|42|`opentibiabr/canary#3438`|lions-rock: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|43|`opentibiabr/canary#3430`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|?|UNPROVEN|INSUFFICIENT|
|44|`opentibiabr/canary#3428`|houses-decoration: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|45|`opentibiabr/canary#3427`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|?|UNPROVEN|INSUFFICIENT|
|46|`opentibiabr/canary#3426`|combat-fields: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|47|`opentibiabr/canary#3424`|soul-war-storage: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|48|`opentibiabr/canary#3414`|concoction-drome: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|49|`opentibiabr/canary#3413`|Custom NPC trade product semantics.|?|N|N|N|-|PROVEN|NO-ACTION|
|50|`opentibiabr/canary#3407`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|-|UNPROVEN|INSUFFICIENT|
|51|`opentibiabr/canary#3374`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|-|UNPROVEN|INSUFFICIENT|
|52|`opentibiabr/canary#3347`|Custom imbuement configuration behavior.|?|N|N|N|-|PROVEN|NO-ACTION|
|53|`opentibiabr/canary#3345`|combat-reflection: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|54|`opentibiabr/canary#3329`|item-use: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|55|`opentibiabr/canary#3310`|Extreme custom-rate performance profile.|?|N|N|N|-|PROVEN|NO-ACTION|
|56|`opentibiabr/canary#3288`|wheel-spells: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|57|`opentibiabr/canary#3259`|secret-library: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|58|`opentibiabr/canary#3251`|forge: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|59|`opentibiabr/canary#3180`|corpse-map-stack: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|60|`opentibiabr/canary#3160`|chain-combat: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|61|`opentibiabr/canary#3059`|Custom admin/XML-writing command.|?|N|N|N|-|PROVEN|NO-ACTION|
|62|`opentibiabr/canary#2730`|killing-in-name-of: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|63|`opentibiabr/canary#2639`|item-use-movement: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|64|`opentibiabr/canary#2553`|hazard-system: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|65|`opentibiabr/canary#2542`|rune-targeting: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|66|`opentibiabr/canary#2396`|offline-training: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|67|`opentibiabr/canary#2272`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|-|UNPROVEN|INSUFFICIENT|
|68|`opentibiabr/canary#2083`|cyclopedia-market: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|?|UNPROVEN|REPRO|
|69|`opentibiabr/canary#2066`|cults-of-tibia: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|70|`opentibiabr/canary#1919`|ammo-imbuement: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|?|UNPROVEN|REPRO|
|71|`opentibiabr/canary#917`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|-|UNPROVEN|INSUFFICIENT|
|72|`opentibiabr/canary#618`|Bulk historical quest backlog.|?|N|N|N|-|PROVEN|NO-ACTION|
|73|`opentibiabr/canary#615`|Bulk boss/raid backlog.|?|N|N|N|-|PROVEN|NO-ACTION|
|74|`opentibiabr/canary#560`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|-|UNPROVEN|INSUFFICIENT|
|75|`zimbadev/crystalserver#853`|quests: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|PARTIALLY_PROVEN|REPRO|
|76|`zimbadev/crystalserver#851`|Stash shortfall can be lost in all server lines.|D|D|D|D|-|PROVEN|GAP|
|77|`zimbadev/crystalserver#850`|Unguarded rawExp division in all server lines.|D|D|D|D|-|PROVEN|GAP|
|78|`zimbadev/crystalserver#849`|Null tile dereference in all server lines.|D|D|D|D|-|PROVEN|GAP|
|79|`zimbadev/crystalserver#848`|Unbounded condition indexes in all server lines.|D|D|D|D|-|PROVEN|GAP|
|80|`zimbadev/crystalserver#847`|Donor-specific Agony mapping without target contract.|N|P|N|N|-|PROVEN|NO-ACTION|
|81|`zimbadev/crystalserver#846`|Inverted guild balance check in all server lines.|D|D|D|D|-|PROVEN|GAP|
|82|`zimbadev/crystalserver#845`|Nil attacker crash in inherited SoulCage script.|D|D|D|D|-|PROVEN|GAP|
|83|`zimbadev/crystalserver#844`|Recurring raid execution state defect in inherited script.|D|D|D|D|-|PROVEN|GAP|
|84|`zimbadev/crystalserver#826`|Temporary OTCR client workaround.|N|P|N|N|?|PROVEN|NO-ACTION|
|85|`zimbadev/crystalserver#813`|Expert/Open PvP implementations differ; target contract required.|I|P|I|A|?|BLOCKED_BY_DECISION|ARCH-DECISION|
|86|`zimbadev/crystalserver#805`|Under-construction bulk Summer Update package.|N|P|N|N|-|PROVEN|NO-ACTION|
|87|`zimbadev/crystalserver#785`|map-runtime: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|?|PARTIALLY_PROVEN|REPRO|
|88|`zimbadev/crystalserver#742`|Whole daily-reward architecture replacement.|A|P|A|A|-|PROVEN|NO-ACTION|
|89|`zimbadev/crystalserver#627`|Custom autoheal/autopotion product feature.|N|P|N|N|-|PROVEN|NO-ACTION|
|90|`zimbadev/crystalserver#545`|Binary persistence architecture replacement.|A|P|A|A|-|PROVEN|NO-ACTION|
|91|`zimbadev/crystalserver#451`|Multiworld lineage shared; target schema/routing contract required.|P|P|I|A|-|BLOCKED_BY_DECISION|PERSIST-DECISION|
|92|`zimbadev/crystalserver#445`|Expert/Open PvP implementations differ; target contract required.|I|P|I|A|?|BLOCKED_BY_DECISION|ARCH-DECISION|
|93|`zimbadev/crystalserver#206`|No exact target path or deterministic proof; evidence insufficient.|?|?|?|?|-|PARTIALLY_PROVEN|INSUFFICIENT|
|94|`zimbadev/crystalserver#122`|Items delivered before payment; donor fix not atomic.|D|D|D|D|-|PROVEN|GAP|
|95|`zimbadev/crystalserver#852`|map-runtime: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|?|PARTIALLY_PROVEN|REPRO|
|96|`zimbadev/crystalserver#837`|freequest-storage: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|97|`zimbadev/crystalserver#812`|Separate Discovery/Donations product programme.|A|?|A|A|?|PROVEN|NO-ACTION|
|98|`zimbadev/crystalserver#810`|Expert/Open PvP implementations differ; target contract required.|I|P|I|A|?|BLOCKED_BY_DECISION|ARCH-DECISION|
|99|`zimbadev/crystalserver#794`|Placeholder normalized with PR #805.|N|?|N|N|-|PROVEN|NO-ACTION|
|100|`zimbadev/crystalserver#647`|map-content-books: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|101|`zimbadev/crystalserver#564`|children-of-the-revolution: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|102|`zimbadev/crystalserver#561`|kusuma-content: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|
|103|`zimbadev/crystalserver#535`|mini-world-change: not proven across repos; exact Otheryn runtime reproduction required.|?|?|?|?|-|UNPROVEN|REPRO|

Pełne ścieżki, rewizje, brakujące dowody i następne kroki: `inventory.json.gz`, `inventory.csv.gz`, `decision-brief.md`.
