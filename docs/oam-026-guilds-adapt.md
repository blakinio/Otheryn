# OAM-026 — Guilds adaptation proof

## Disposition

```text
guilds → ADAPT
```

The disposition describes the canonical package in the target, not the amount of new production code required by this PR. OAM-026 preserves the upstream-compatible guild core while retaining the deliberate target persistence adaptation already delivered by OAM-004C.

## Immutable task-start baselines

- legacy / governance Canary: `052d96014c805aacaa120ce888b7bed038817a72`
- Otheryn target: `1cf38d354b493b4cd9ec8e841ec8f2a6ff322029`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511` (comparison-only)

## Canonical boundary

OAM-026 revalidates only canonical `guilds`:

- `src/creatures/players/grouping/guild.*`;
- `src/io/ioguild.*`;
- the guild-specific `IOLoginDataLoad::loadPlayerGuild` responsibility in shared `src/io/functions/iologindata_load_player.cpp`.

The package depends on completed `character-lifecycle` and `database-connection` contracts and interacts with `chat-communication`, `protocol` and `world-persistence`. Guild chat delivery, wire compatibility, party lifecycle, website/account-management flows and proof of generic durable transaction correctness remain outside this package.

## Evidence-driven classification

The bounded guild core is exact-identical across the immutable legacy, target and upstream baselines:

- `guild.cpp`: `346bfc562275a5835fd81f146eb235048ce9d45b`;
- `guild.hpp`: `0e4c53a615d5df90e561cc211da002a89c72a413`.

The guild-specific `IOLoginDataLoad::loadPlayerGuild` hunk is also semantically identical across the pinned target and legacy baselines. The whole shared loader is not identical because it contains unrelated responsibilities; therefore OAM-026 does not copy or claim ownership of that file.

Whole-module `REUSE` is rejected because the canonical persistence handoff is intentionally different in Otheryn. Legacy and fresh upstream `IOGuild::saveGuild()` discard the database write result and return `void`. Otheryn's completed OAM-004C adaptation changes this boundary to `bool`, propagates the database result through `SaveManager::saveGuild()`, and includes guild-save failure in aggregate server-save status. Replacing `IOGuild` from legacy or upstream would regress an established target persistence contract.

No stronger independent legacy donor for the canonical guild core was identified. The reviewed legacy multichannel implementation did not change canonical guild production files; its later security audit instead proves a cross-process guild-bank hazard that must not be imported as target architecture.

## Boundary classification

| Boundary | Classification | Evidence / decision |
|---|---|---|
| ownership/lifecycle | applicable | `Game` owns the process-local guild cache; player guild loading populates it; `Guild::removeMember` removes an empty online-member cache entry through `Game::removeGuild`. |
| build/toolchain | applicable | Existing guild production targets remain unchanged; OAM-026 adds only focused unit proof to the existing unit-test target. |
| configuration | not-applicable | No canonical guild configuration key is introduced or changed. |
| service/API | applicable | Preserve `Guild`, `IOGuild` and `Game` guild-cache interfaces; no new public API is introduced. |
| scheduling/concurrency | applicable | Current target is a single authoritative game process for this package; OAM-026 does not introduce cross-process guild ownership. Save orchestration remains under the existing `SaveManager` contract. |
| persistence | applicable | Preserve OAM-004C `IOGuild::saveGuild() -> bool` failure propagation. Generic cross-domain atomicity remains explicitly unclaimed. |
| protocol/session | not-applicable | The canonical registry has no client path and excludes wire compatibility. |
| identifiers/assets | not-applicable | No IDs, assets or external data are added or repurposed. |
| world/map | not-applicable | No map, OTBM or world-content path is changed. |
| runtime | applicable | Online-member and process-local guild-cache lifecycle are retained unchanged; no new distributed runtime claim is made. |
| tests | applicable | Focused proof covers stable guild identity/rank/balance state and compile-time preservation of the OAM-004C `bool` save contract; full target CI remains authoritative. |
| physical-client E2E | not-applicable | No protocol/UI behavior is changed; OAM-026 does not claim guild UI or guild-chat E2E closure. |
| operations | applicable | Existing aggregate save failure visibility is retained; no deployment or rollback mechanism changes. |
| security/privacy | applicable | Guild bank is durable economic state. The legacy multichannel audit finding is recorded as a future multiwriter boundary, not as permission to import the legacy multichannel design. |

## Target adaptation retained

OAM-026 makes no new production mutation. It deliberately retains the already-merged target adaptation:

1. `IOGuild::saveGuild()` returns the underlying database update status.
2. `SaveManager::saveGuild()` propagates and logs failure.
3. `SaveManager::saveAll()` aggregates guild failure while continuing independent save domains best-effort.
4. Guild identity, ranks, membership projection, war-list loading and process-local online-member cache remain on the upstream-compatible implementation.

This is the smallest architecture-correct outcome: preserve the functional guild behavior while refusing to regress the target-owned persistence failure contract merely to obtain source identity with legacy/upstream.

## Multichannel guild-bank boundary

Legacy security evidence `OTS-ECO-GUILD-001` proves that a multiwriter deployment can double-spend a global guild balance when each process authorizes against a stale process-local `Guild::bankBalance` snapshot and later performs an absolute save.

That proof is not promoted into a claim that the current Otheryn target has the same multi-authority runtime: OAM-026 does not adopt the legacy multichannel architecture. It also does not claim the generic problem is solved. Any future Otheryn move to multiple authoritative guild writers must introduce a separate durable ownership/atomic-debit contract before enabling concurrent guild-bank mutation.

## Focused proof

`Oam026GuildsAdaptTest` verifies the bounded target contract without a production DB mutation:

- stable guild identity and empty initial state;
- rank registration and lookup by id, name and level;
- bank balance and member-count state accessors used by the persistence projection;
- the target `IOGuild::saveGuild` signature remains `bool(const std::shared_ptr<Guild>&)`, preventing accidental regression to the legacy/upstream fire-and-forget persistence API.

Exact-head target CI is required before the disposition is final.

## Package manifest

```text
package_id: OAM-026
module_id: guilds
legacy_repository: blakinio/canary
legacy_sha: 052d96014c805aacaa120ce888b7bed038817a72
legacy_source_paths: src/creatures/players/grouping/guild.*; src/io/ioguild.*; guild-specific hunk in src/io/functions/iologindata_load_player.cpp
target_repository: blakinio/Otheryn
target_base_sha: 1cf38d354b493b4cd9ec8e841ec8f2a6ff322029
target_head_sha: PENDING_EXACT_HEAD_GATE
upstream_repository: opentibiabr/canary
upstream_baseline_sha: 71a0f92b4da3f550b292fa7536a0e35c2769f1ae
target_paths: src/creatures/players/grouping/guild.*; src/io/ioguild.*; focused proof/docs only in OAM-026
depends_on: character-lifecycle; database-connection
interacts_with: chat-communication; protocol; world-persistence
migration_disposition: ADAPT
disposition_rationale: retain upstream-compatible guild core while preserving the target-owned OAM-004C save-failure propagation adaptation
runtime_evidence: no new guild-specific runtime claim; current process-local lifecycle retained and exact-head CI required
physical_client_e2e_evidence: not-applicable; no wire/UI behavior changed
known_gaps: generic crash/restart and cross-domain atomicity are unproven; future multiwriter guild-bank safety requires a separate ownership/atomic-debit contract; no guild-specific physical-client E2E claim
rollback_plan: revert OAM-026 proof-only files; do not revert the pre-existing OAM-004C IOGuild/SaveManager persistence contract
provenance_notes: canonical guild core is identical at pinned baselines; target IOGuild divergence is intentional OAM-004C target architecture, not legacy drift
```

The exact final target head is recorded by the task checkpoint and PR exact-head merge gate after all proof commits are complete; it is intentionally not guessed in this document before that gate exists.
