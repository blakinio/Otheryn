# OTH-20260726 — MGE-001 ownership and dependency inventory

Status: **completed and merged**  
Issue: #127  
Implementation branch: `dudantas/mge-001-ownership-dependency-inventory`  
Implementation pull request: #129  
Final implementation head: `a9e9415a6f3a74eea9ef4d1042cebf5095c78500`  
Required run: `30201411760` — success  
Merge SHA: `0b01222d3a257cef593d296b22f7280fbce74b4b`  
Target repository: `blakinio/Otheryn`  
Reference repositories: `blakinio/canary`, `opentibiabr/canary`  
Package type: analysis and documentation only

## Objective

Inventory current Otheryn ownership, mutation authority, dependencies, protocol and Lua entry points, persistence boundaries, threading/lifecycle boundaries, Canary differences, and the safest evidence-based candidate for a future vertical extraction.

The package did not implement `ModuleRegistry`, `GameProfile`, dynamic plugins, gameplay changes, protocol changes, Lua API changes, database-schema changes, new persistence behavior, new threading, or MGE-002+.

## Delivered paths

- `docs/architecture/current-engine-ownership-and-dependencies.md`
- this archived lifecycle record

## Evidence baseline

- Otheryn source-analysis revision: `38bb62192d25984d63f96c2637348b4adc82f6cd`
- Canary fork revision: `ec0d815570415a4c7ca7217e3e2aca41f6023dab`
- Canary upstream revision: `7644bcbcbbad4a09e52a5707ed531e4dd21d8a79`

## Result

The merged report documents:

- actual bootstrap, readiness, shutdown and service-locator composition;
- globals, singleton-like accessors, registries and mutation authority;
- state ownership for world, map, players, sessions, items, gameplay features, configuration and protocol capabilities;
- compile-time and runtime dependency edges and manually validated cycles;
- ProtocolGame application/domain/persistence responsibilities;
- Lua query, mutation, persistence and administrative authority;
- persistence, threading, callback, stale-writer and lifecycle gaps;
- current subsystem-boundary classifications;
- revision-pinned Canary dispositions;
- Bank operations as the first future vertical extraction candidate after bounded protocol/Lua adapter contracts;
- Party, Market and Wheel as rejected first candidates;
- a recommended continuation order moving adapter-interface definition before the first extraction implementation.

No runtime source was changed.

## Execution drift note

Draft PR `#128` appeared after the initial baseline. At the final implementation audit it changed only `docs/agents/tasks/active/OTH-20260726-oam051b-task-shop-adapt.md`, with no comments, reviews, or review threads. It did not overlap the MGE-001 owned paths.

## Final validation

- checkpoint validation: pass
- Markdown structure: pass
- repository-relative links/paths: pass
- exact implementation changed paths: pass
- secret scan: pass
- analysis-tool tests: not applicable; no tools added
- deterministic generation: not applicable; no generated artifact
- exact report blob reread: pass
- open-PR ownership audit: pass, including PR #128 drift
- implementation PR comments: empty
- implementation PR reviews: empty
- implementation PR unresolved threads: empty
- target-main drift before merge: none; `main` remained `38bb62192d25984d63f96c2637348b4adc82f6cd`
- Required exact head: success on `a9e9415a6f3a74eea9ef4d1042cebf5095c78500`
- Required run: `30201411760`
- merge method: squash
- expected head SHA enforced: `a9e9415a6f3a74eea9ef4d1042cebf5095c78500`
- merge SHA: `0b01222d3a257cef593d296b22f7280fbce74b4b`

## Checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-26T14:20:00+02:00"
head: "a9e9415a6f3a74eea9ef4d1042cebf5095c78500"
branch: "dudantas/mge-001-ownership-dependency-inventory"
pr: 129
status: "completed_merged_lifecycle_archive_pending"
context_routes:
  - "docs/architecture/current-engine-ownership-and-dependencies.md"
  - "docs/architecture/modular-game-engine-and-profiles.md"
  - "docs/architecture/production-resilience-and-recovery.md"
owned_paths:
  - "docs/agents/tasks/active/OTH-20260726-mge001-ownership-dependency-inventory.md"
  - "docs/agents/tasks/archive/OTH-20260726-mge001-ownership-dependency-inventory.md"
proven:
  - "Implementation PR #129 merged from exact head a9e9415a6f3a74eea9ef4d1042cebf5095c78500."
  - "Required run 30201411760 succeeded on the exact implementation head."
  - "Merge SHA is 0b01222d3a257cef593d296b22f7280fbce74b4b."
  - "The implementation PR changed only the report and active task."
derived:
  - "MGE-001 completed only the architecture inventory contract; it did not implement modular runtime behavior."
unknown:
  - "The continuation package owner and start revision are not selected by this lifecycle PR."
conflicts: []
first_failure: null
rejected_hypotheses:
  - "A successful MGE-001 report means the modular engine is implemented."
  - "Bank is already an isolated module."
changed_paths:
  - "docs/agents/tasks/active/OTH-20260726-mge001-ownership-dependency-inventory.md"
  - "docs/agents/tasks/archive/OTH-20260726-mge001-ownership-dependency-inventory.md"
validation:
  implementation_required: "pass_run_30201411760"
  implementation_merge: "pass_0b01222d3a257cef593d296b22f7280fbce74b4b"
  lifecycle_changed_paths: "pending"
  lifecycle_markdown: "pending"
  lifecycle_secret_scan: "pending"
  lifecycle_discussions: "pending"
  lifecycle_reviews: "pending"
  lifecycle_unresolved_threads: "pending"
  lifecycle_main_drift: "pending"
  lifecycle_exact_head_required: "pending"
blockers: []
next_action: "Validate and merge the lifecycle-only archive pull request without changing the architecture report."
```
