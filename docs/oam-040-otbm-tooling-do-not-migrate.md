# OAM-040 OTBM tooling target disposition proof

## Final disposition

`otbm-tooling → DO_NOT_MIGRATE`

## Immutable baselines

- Canary OAM-040 preflight merge: `90b5054ebc8b2a19d52cc1bc2731e9dc6f3080f3`
- Otheryn target task-start main: `5eea55ca3dd7689d097fadef3ff92eee84f8c163`
- fresh upstream Canary baseline: `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- maintained OTClient baseline: `1e5305395159142634f182d9e888e5f9164228c6`

## Canonical responsibility

The canonical `otbm-tooling` record is a dependency-free `platform-tooling` module. It owns no server, client or data path. Its recorded scope is the deterministic OTBM analysis/evidence stack used for World Indexing, item/mechanic audit, script resolution, reachability, spawn/NPC evidence, storage graph analysis, semantic diff, geometry audit and factual rendering. The canonical paths point to analysis tests and the OTBM tooling roadmap in the Canary repository.

This is not a gameplay/runtime responsibility that belongs inside Otheryn core.

## Repository-role proof

The Oteryn target architecture contract assigns:

- `blakinio/canary` the roles of legacy laboratory, evidence source, validation environment and migration-source candidate;
- `blakinio/Otheryn` the role of a clean, selectively populated target;
- OTBM/map/content migration the obligation to use the existing deterministic analysis stack rather than creating competing parsers, pathfinders or renderers.

The maintained OTBM tooling roadmap is explicitly repository-scoped to `blakinio/canary`. It records phases 1 through 8 as merged and archived, covering World Index, Quest Map Validator, reachability, spawn/NPC evidence, storage dependency graph, semantic diff, geometry audit and the safe bounded patch writer.

Representative legacy tool `tools/ai-agent/otbm_world_index.py` exists in Canary as blob `d1e23a9df27a070e2d77fd98210b8574f0c9e0bf`. Clean Otheryn and fresh upstream do not contain that representative root or `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`.

## Dependency-impact proof

Canonical `spawns` and `npcs` depend on `otbm-tooling`; canonical `quests` depends on `otbm-tooling` plus `player-persistence`.

Those relationships are evidence-generation dependencies, not target-local runtime/library imports:

1. Future world-content OAM packages may consume pinned Canary tool/report provenance and deterministic outputs as cross-repository evidence.
2. They must not assume that copying the tool suite into Otheryn is required to migrate the resulting gameplay/data responsibility.
3. Each downstream package remains responsible for pinning the exact Canary tool/report version it uses and for proving its own target data/runtime behavior.
4. OAM-040 does not delete, deprecate or freeze the Canary tooling. The maintained evidence stack remains available to those consumers in its established repository role.
5. No identified Otheryn runtime, service, protocol, client, map-loader or production build path imports or requires a target-local OTBM analysis tool module.

Therefore there is no unresolved **target-local** consumer requiring migration of `otbm-tooling` into Otheryn core. Downstream canonical consumers remain satisfied by the explicit cross-repository evidence contract.

## Target exclusion boundary

OAM-040 intentionally introduces no copy of:

- `tools/ai-agent/otbm_*`;
- OTBM analysis test suites;
- OTBM validation workflows;
- `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md`;
- generated `.otbm`, `.widx`, reports, renders or client/map assets.

No production, runtime, protocol, client, data, map, asset, schema, deployment or build path is changed.

This exclusion does not remove `otbm-tooling` from the canonical registry. The registry continues to model the dependency because the analysis/evidence responsibility remains real and maintained in Canary.

## Why not other dispositions

### Not `REUSE`

There is no target-local runtime/product responsibility to transfer. Clean Otheryn and upstream do not contain the tooling roots, and copying the legacy laboratory tool suite would violate the clean-target boundary without adding required target behavior.

### Not `ADAPT` or `REWRITE`

No target incompatibility requires a redesigned OTBM analysis subsystem inside Otheryn. The existing deterministic stack already fulfills the migration evidence role in Canary.

### Not `EXPERIMENTAL_ONLY`

The tooling is not merely experimental. It is an established, maintained deterministic evidence stack with merged and archived delivery phases. The correct target decision is exclusion from Otheryn core while retaining the authoritative laboratory/evidence responsibility in Canary.

## Validation contract

This disposition is proof/documentation-only. The target proof must demonstrate:

- exact repository-role and canonical-module provenance;
- absence of target-local representative tooling roots;
- explicit downstream dependency impact;
- no unresolved target-local consumer;
- zero target production mutation.

The final target PR is expected to change only this proof document and its active task record. Repository `Required` must pass on the exact head, and comments/reviews/threads plus target-main drift must be audited before merge.

## Nonclaims

OAM-040 does not claim OTBM tooling is feature-complete forever, that static map evidence proves live gameplay, that generated reports may be committed to Otheryn, that downstream spawns/NPCs/quests are already correct, or that future world-content packages may skip their own target/runtime validation.
