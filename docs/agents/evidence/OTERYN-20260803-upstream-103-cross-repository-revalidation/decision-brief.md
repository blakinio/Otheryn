# Decision brief — 103 elementy

To są rekomendacje do decyzji właściciela. Żadna pozycja nie autoryzuje implementacji.

## Potwierdzone luki Otheryn (15)

- `opentibiabr/canary#4058` — The same spell-suppression defect is statically present in Otheryn and CrystalServer. blakinio/canary already contains the correction. Adapt the narrow behavior only after owner approval.
- `opentibiabr/canary#4054` — All compared server lines share the client-cache refresh weakness; Otheryn has a proven gap.
- `opentibiabr/canary#4053` — Otheryn shares the exact upstream defect. CrystalServer is not a portable drop-in because its storage model differs.
- `opentibiabr/canary#4045` — The exact Otheryn catalog has the pricing/count gap; CrystalServer is not structurally equivalent.
- `opentibiabr/canary#4044` — Otheryn shares the same greeting-state defect; the bounded eleven-script adaptation remains supported.
- `opentibiabr/canary#4025` — Otheryn has the same two-path Barbarian Test defect; CrystalServer uses a different quest implementation.
- `opentibiabr/canary#3986` — The issue and PR #4058 describe one proven defect family. Otheryn is affected; blakinio/canary is already fixed.
- `zimbadev/crystalserver#851` — A statically proven item-loss path exists in all compared server lines, including Otheryn.
- `zimbadev/crystalserver#850` — The divide-by-zero/undefined behavior path is shared and statically proven in Otheryn.
- `zimbadev/crystalserver#849` — The null-dereference path is shared and statically proven in Otheryn.
- `zimbadev/crystalserver#848` — The malformed-persistence out-of-bounds write risk is shared and statically proven in Otheryn.
- `zimbadev/crystalserver#846` — The exact one-line guild-deposit defect is shared and statically proven in Otheryn.
- `zimbadev/crystalserver#845` — The nil-attacker crash path is shared and statically proven in Otheryn.
- `zimbadev/crystalserver#844` — The recurring raid scheduler state defect is shared and statically proven in Otheryn.
- `zimbadev/crystalserver#122` — Otheryn has a proven currency/item atomicity gap. The donor patch is evidence, not a safe reusable solution; a fail-closed rewrite remains required.

## Już naprawione w Otheryn (0)

- Brak.

## Brak działania w Otheryn (21)

- `opentibiabr/canary#4055` — The PR only advances a vcpkg baseline and was already superseded; dependency refresh is not an upstream gameplay migration unit.
- `opentibiabr/canary#4048` — The change is MyAAC/Docker frontend deployment work and is outside the Otheryn server target.
- `opentibiabr/canary#4038` — The PR is a broad custom viewport/Idle Hunt client-product package, not an Otheryn defect correction.
- `opentibiabr/canary#4029` — The PR is a generated bulk monster-loot import with no bounded provenance-safe target proof.
- `opentibiabr/canary#4003` — The issue requests arm64 image publication; this is deployment/product scope, not a server defect migration.
- `opentibiabr/canary#3841` — The issue requests a broad Summer Update content package, not a bounded defect.
- `opentibiabr/canary#3470` — The issue asks for a new Lua spell-casting API; it is a feature proposal, not a proven target defect.
- `opentibiabr/canary#3413` — The issue requests changed NPC product semantics for used rings/amulets; owner product policy is not inferred from upstream.
- `opentibiabr/canary#3347` — The issue describes custom imbuement behavior and configuration, outside the canonical target product contract.
- `opentibiabr/canary#3310` — The issue concerns extreme custom experience/reset rates and edited creatures, not the supported target profile.
- `opentibiabr/canary#3059` — The issue proposes an admin command implementation that writes spawn XML; it is custom tooling, not target behavior.
- `opentibiabr/canary#618` — The issue is a bulk historical quest backlog and cannot be migrated as one bounded unit.
- `opentibiabr/canary#615` — The issue is a bulk boss/raid backlog and cannot be migrated as one bounded unit.
- `zimbadev/crystalserver#847` — The PR changes a donor-specific Agony damage mapping with no matching target contract; previous rejection remains supported.
- `zimbadev/crystalserver#826` — The PR is an explicit temporary OTCR client workaround and is not maintained-client/server target behavior.
- `zimbadev/crystalserver#805` — The PR is an under-construction bulk Summer Update content package; bulk import is forbidden.
- `zimbadev/crystalserver#742` — The PR replaces the daily reward system wholesale with a donor-native C++ architecture; it is not a bounded correction.
- `zimbadev/crystalserver#627` — The PR adds custom autohealing/autopotion gameplay; it is a product proposal outside Otheryn scope.
- `zimbadev/crystalserver#545` — The draft replaces player persistence with binary blobs; Otheryn persistence architecture cannot be replaced by donor similarity.
- `zimbadev/crystalserver#812` — The issue proposes a large reverse-engineered Discovery/Donations system and generated geometry; it is a separate product/architecture programme.
- `zimbadev/crystalserver#794` — The issue is only a placeholder for Summer Update 2026 and is normalized with PR #805.

## Wymagana reprodukcja runtime (49)

- `opentibiabr/canary#4057` — The source claim is plausible but not proven in exact Otheryn. The issue contains precise map coordinates and two script floor claims, but the binary source-map and exact target tiles were not independently opened; a map/runtime proof is required.
- `opentibiabr/canary#4013` — The source claim is plausible but not proven in exact Otheryn. The scheduled-save warning/console claim was not tied to an exact target execution trace; run a controlled scheduled save and inspect messages and persistence.
- `opentibiabr/canary#3875` — The source claim is plausible but not proven in exact Otheryn. Both upstreams contain Pale Worm assets and entry/death scripts, but no complete Hunger/Greed/Weak Spot mechanic equivalence was proven.
- `opentibiabr/canary#3803` — The source claim is plausible but not proven in exact Otheryn. The issue names missing spawn areas, but semantic searches did not establish exact target spawn definitions or map coverage.
- `opentibiabr/canary#3770` — The source claim is plausible but not proven in exact Otheryn. Quest catalog evidence exists, but no exact action/position path proving the western mast interaction was found.
- `opentibiabr/canary#3745` — The source claim is plausible but not proven in exact Otheryn. No exact server equip/quick-access path or maintained-client trace was established for quiver switching.
- `opentibiabr/canary#3724` — The source claim is plausible but not proven in exact Otheryn. No exact wheel dismantle persistence path or logout/relog fixture was established.
- `opentibiabr/canary#3645` — The source claim is plausible but not proven in exact Otheryn. The wand/Cyclopedia crash crosses protocol and client rendering; exact packet reproduction is required.
- `opentibiabr/canary#3605` — The source claim is plausible but not proven in exact Otheryn. The allegation combines quest state, map swap and client crash; exact target map and maintained-client reproduction are required.
- `opentibiabr/canary#3584` — The source claim is plausible but not proven in exact Otheryn. The field-rune initial-damage allegation lacks an exact target combat trace; reproduce with deterministic rune/monster fixtures.
- `opentibiabr/canary#3549` — The source claim is plausible but not proven in exact Otheryn. The hazard allegation spans zone membership, monster tags and scripts; exact target runtime state must be measured.
- `opentibiabr/canary#3534` — The source claim is plausible but not proven in exact Otheryn. Quest catalog presence does not prove pickaxe action wiring or map destination; reproduce on exact target coordinates.
- `opentibiabr/canary#3513` — The source claim is plausible but not proven in exact Otheryn. The claimed Zone::afterEnter/changeSpeed crash is client-state sensitive and needs maintained-client login/relog reproduction.
- `opentibiabr/canary#3506` — The source claim is plausible but not proven in exact Otheryn. Boss files or names alone cannot prove mechanics; execute each Grave Danger encounter with scripted assertions.
- `opentibiabr/canary#3500` — The source claim is plausible but not proven in exact Otheryn. The issue alleges four distinct Soul War boss mechanic failures; each needs a bounded scenario and storage/state trace.
- `opentibiabr/canary#3485` — The source claim is plausible but not proven in exact Otheryn. Hireling customization is a protocol/UI boundary; exact server packet and maintained-client behavior must be reproduced.
- `opentibiabr/canary#3479` — The source claim is plausible but not proven in exact Otheryn. The Brain Head encounter start path was not statically proven from the issue; reproduce the entry trigger and spawned entities.
- `opentibiabr/canary#3478` — The source claim is plausible but not proven in exact Otheryn. Freequest storage values and consumer thresholds may differ; run one exact grant-and-access scenario.
- `opentibiabr/canary#3458` — The source claim is plausible but not proven in exact Otheryn. Soulpit wave completion depends on creature ownership/filtering; reproduce with and without summons.
- `opentibiabr/canary#3453` — The source claim is plausible but not proven in exact Otheryn. The issue supplies a script snippet but not authoritative target map/action state; reproduce the lever, transform and walk path.
- `opentibiabr/canary#3447` — The source claim is plausible but not proven in exact Otheryn. NPC keyword/topic behavior needs an exact Wyrdin conversation transcript on Otheryn.
- `opentibiabr/canary#3438` — The source claim is plausible but not proven in exact Otheryn. The Lion's Rock claim needs exact tile/action IDs and a deterministic gem-use test.
- `opentibiabr/canary#3428` — The source claim is plausible but not proven in exact Otheryn. House bed wrapping spans item definitions and client/server interactions; reproduce both bed halves.
- `opentibiabr/canary#3426` — The source claim is plausible but not proven in exact Otheryn. Monster bomb-field damage requires a deterministic combat-field scenario and immunity trace.
- `opentibiabr/canary#3424` — The source claim is plausible but not proven in exact Otheryn. Soul War taint reset/reacquisition needs storage and boss-kill lifecycle reproduction.
- `opentibiabr/canary#3414` — The source claim is plausible but not proven in exact Otheryn. Concoction amplification needs deterministic damage sampling and Cyclopedia packet/client verification.
- `opentibiabr/canary#3345` — The source claim is plausible but not proven in exact Otheryn. Reflection behavior varies by damage origin; reproduce melee, elemental weapon, spells and runes with controlled targets.
- `opentibiabr/canary#3329` — The source claim is plausible but not proven in exact Otheryn. Wall-lamp diagonal use needs exact positions, item IDs and interaction-range reproduction.
- `opentibiabr/canary#3288` — The source claim is plausible but not proven in exact Otheryn. Wheel spell area requires a controlled wheel allocation and target-position assertion.
- `opentibiabr/canary#3259` — The source claim is plausible but not proven in exact Otheryn. The Secret Library forcefield claim needs exact storage preconditions and tile traversal reproduction.
- `opentibiabr/canary#3251` — The source claim is plausible but not proven in exact Otheryn. Forge transfer rules are product-sensitive; reproduce normal versus convergence transfer with class/slot fixtures.
- `opentibiabr/canary#3180` — The source claim is plausible but not proven in exact Otheryn. Corpse access depends on tile stack and client browse-field behavior; reproduce on the exact map tile.
- `opentibiabr/canary#3160` — The source claim is plausible but not proven in exact Otheryn. Chain targeting needs deterministic mixed creature/NPC fixtures and effect-recipient assertions.
- `opentibiabr/canary#2730` — The source claim is plausible but not proven in exact Otheryn. The Snapper task lifecycle needs exact storages before/after kill and Grizzly Adams dialogue replay.
- `opentibiabr/canary#2639` — The source claim is plausible but not proven in exact Otheryn. Distance liquid use depends on queued walking and item state; reproduce with position trace.
- `opentibiabr/canary#2553` — The source claim is plausible but not proven in exact Otheryn. Primal Pods/Patriarch spawn depends on hazard counters and zone state; measure exact kill thresholds and spawns.
- `opentibiabr/canary#2542` — The source claim is plausible but not proven in exact Otheryn. Rune targeting with hotkeyAimbotEnabled needs party/non-party maintained-client scenarios.
- `opentibiabr/canary#2396` — The source claim is plausible but not proven in exact Otheryn. Offline training requires elapsed-time, vocation and skill fixtures across bed and statue paths.
- `opentibiabr/canary#2083` — The source claim is plausible but not proven in exact Otheryn. Cyclopedia market pricing crosses persistence and client display; capture exact market data and packets.
- `opentibiabr/canary#2066` — The source claim is plausible but not proven in exact Otheryn. Barkless access and Leiden heal are separate claims; each needs storage/dialogue and boss-combat reproduction.
- `opentibiabr/canary#1919` — The source claim is plausible but not proven in exact Otheryn. Diamond-arrow imbuement damage split needs deterministic combat and target resistance assertions.
- `zimbadev/crystalserver#853` — The source claim is plausible but not proven in exact Otheryn. The donor PR changes Hot Cuisine quest behavior; compare each touched script and run the affected recipe/action flow.
- `zimbadev/crystalserver#785` — The source claim is plausible but not proven in exact Otheryn. The donor PR explicitly calls its clearArea solution incomplete. Reproduce repeated map swaps, memory/tile cache behavior and client movement.
- `zimbadev/crystalserver#852` — The source claim is plausible but not proven in exact Otheryn. The issue links the map-swap crash to PR #785, but exact Otheryn map replacement and maintained-client crash were not reproduced.
- `zimbadev/crystalserver#837` — The source claim is plausible but not proven in exact Otheryn. The freequest grant and consumers use differing thresholds; reproduce one NPC, teleport and door access after grant.
- `zimbadev/crystalserver#647` — The source claim is plausible but not proven in exact Otheryn. Missing library books is map/content evidence; inspect exact tiles against an accepted content source and runtime map.
- `zimbadev/crystalserver#564` — The source claim is plausible but not proven in exact Otheryn. The greasy-oil lever interaction needs exact item/action IDs and storage-state reproduction.
- `zimbadev/crystalserver#561` — The source claim is plausible but not proven in exact Otheryn. Boss absence needs accepted product/content scope plus exact map/spawn/quest evidence.
- `zimbadev/crystalserver#535` — The source claim is plausible but not proven in exact Otheryn. The Goroma mini-world-change activation needs schedule/global-state inspection across restart and server-save boundaries.

## Wymagana decyzja architektoniczna (4)

- `opentibiabr/canary#4033` — This is not a portable bug fix. Otheryn needs an explicit PvP world-type and protocol architecture decision before row-level implementation can be evaluated.
- `zimbadev/crystalserver#813` — This is not a portable bug fix. Otheryn needs an explicit PvP world-type and protocol architecture decision before row-level implementation can be evaluated.
- `zimbadev/crystalserver#445` — This is not a portable bug fix. Otheryn needs an explicit PvP world-type and protocol architecture decision before row-level implementation can be evaluated.
- `zimbadev/crystalserver#810` — This is not a portable bug fix. Otheryn needs an explicit PvP world-type and protocol architecture decision before row-level implementation can be evaluated.

## Wymagana decyzja produktowa (0)

- Brak.

## Wymagana decyzja klient/protokół (1)

- `opentibiabr/canary#4056` — Server-side similarity is insufficient. Owner must decide the supported effect-source and virtue notification contract for the maintained client/protocol profile.

## Wymagana decyzja persistence/migracja (2)

- `opentibiabr/canary#2826` — The two source rows are one lineage family, but neither can be migrated until Otheryn defines world identity, schema ownership, account/character routing and operational topology.
- `zimbadev/crystalserver#451` — The two source rows are one lineage family, but neither can be migrated until Otheryn defines world identity, schema ownership, account/character routing and operational topology.

## Wymagana decyzja deploymentowa (0)

- Brak.

## Niewystarczające dowody (11)

- `opentibiabr/canary#4052` — Source evidence is insufficient for a semantic four-repository conclusion. The PR pins build registries/tools, but no exact Otheryn build failure or dependency need is proven.
- `opentibiabr/canary#3742` — Source evidence is insufficient for a semantic four-repository conclusion. The issue reports GameStore payload inefficiency and duplicate balance packets, but no exact target packet capture or semantic path was proven.
- `opentibiabr/canary#3599` — Source evidence is insufficient for a semantic four-repository conclusion. The issue supplies a tuning anecdote for one raid host; no target trace, benchmark or exact affected raid files were established.
- `opentibiabr/canary#3430` — Source evidence is insufficient for a semantic four-repository conclusion. The issue's proposed login-condition analysis is speculative and no failing exact-version target handshake was established.
- `opentibiabr/canary#3427` — Source evidence is insufficient for a semantic four-repository conclusion. The issue provides only a video-level movement symptom; no packet, map, server trace or deterministic target reproduction is available.
- `opentibiabr/canary#3407` — Source evidence is insufficient for a semantic four-repository conclusion. The issue states monster vision is too large without a reference contract, exact monster, coordinates or target comparison.
- `opentibiabr/canary#3374` — Source evidence is insufficient for a semantic four-repository conclusion. The issue says a large withdrawal may crash but provides no amount, stack trace, path or reproduction.
- `opentibiabr/canary#2272` — Source evidence is insufficient for a semantic four-repository conclusion. The combat-balance allegation lacks deterministic equipment, formulas, random seed and target comparison evidence.
- `opentibiabr/canary#917` — Source evidence is insufficient for a semantic four-repository conclusion. The broad low-level combat allegation relies on external videos and does not isolate target code or a deterministic test.
- `opentibiabr/canary#560` — Source evidence is insufficient for a semantic four-repository conclusion. IPv6 is a feature request without an accepted Otheryn networking/product requirement.
- `zimbadev/crystalserver#206` — Source evidence is insufficient for a semantic four-repository conclusion. The scheduler PR is broad and old; no exact Otheryn scheduler defect or workload is tied to it.
