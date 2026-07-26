# OTH-20260726 — MGE-001 ownership and dependency inventory

Issue: #127  
Branch: `dudantas/mge-001-ownership-dependency-inventory`  
Pull request: #129  
Target repository: `blakinio/Otheryn`  
Reference repositories: `blakinio/canary`, `opentibiabr/canary`  
Package type: analysis and documentation only

## Objective

Inventory current Otheryn ownership, mutation authority, dependencies, protocol and Lua entry points, persistence boundaries, threading/lifecycle boundaries, Canary differences, and the safest evidence-based candidate for a future vertical extraction.

This task does not implement `ModuleRegistry`, `GameProfile`, dynamic plugins, gameplay changes, protocol changes, Lua API changes, database-schema changes, new persistence behavior, new threading, or MGE-002+.

## Owned paths

- `docs/architecture/current-engine-ownership-and-dependencies.md`
- `docs/agents/tasks/active/OTH-20260726-mge001-ownership-dependency-inventory.md`

## References read

- `AGENTS.md`
- `docs/agents/CONTEXT_HANDOFF.md`
- `docs/architecture/modular-game-engine-and-profiles.md`
- `docs/agents/tasks/archive/OTH-20260726-modular-game-engine-contract.md`
- `docs/architecture/production-resilience-and-recovery.md`
- current source equivalents under `src/config`, `src/lua`, `src/server`, `src/game`, `src/creatures`, `src/items`, `src/io`, `src/database`, `src/map`, and `src/protocol`
- `docs/oam-046-configuration-adapt.md`
- `docs/oam-044-protocol-compatibility-reuse.md`

## Validation contract

Required before merge:

- checkpoint validation
- Markdown structure validation
- repository-relative link/path validation
- exact changed-path audit
- secret scan
- open-PR ownership audit
- discussion, review, and unresolved-thread audit
- target-main drift audit
- exact-head Required status

No analysis tool is added by this package, so tool-test and deterministic-generated-artifact checks are not applicable. The report is validated by exact blob re-read.

## Execution drift note

Draft PR `#128` appeared after the initial baseline. Its exact current changed path is only `docs/agents/tasks/active/OTH-20260726-oam051b-task-shop-adapt.md`; comments, reviews, and review threads are empty. It does not conflict with the two MGE-001 owned paths. Its planned Wheel/Player-storage work is therefore recorded as adjacent future source ownership, not as evidence merged into the MGE-001 baseline.

## Checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-26T14:10:00+02:00"
head: "045bf4e162ef395dbd2c08160dd923ad5ea68f7b"
branch: "dudantas/mge-001-ownership-dependency-inventory"
pr: 129
status: "validation_passed_waiting_for_exact_head_required"
context_routes:
  - "AGENTS.md"
  - "docs/agents/CONTEXT_HANDOFF.md"
  - "docs/architecture/modular-game-engine-and-profiles.md"
  - "docs/agents/tasks/archive/OTH-20260726-modular-game-engine-contract.md"
  - "docs/architecture/production-resilience-and-recovery.md"
  - "docs/oam-046-configuration-adapt.md"
  - "docs/oam-044-protocol-compatibility-reuse.md"
owned_paths:
  - "docs/architecture/current-engine-ownership-and-dependencies.md"
  - "docs/agents/tasks/active/OTH-20260726-mge001-ownership-dependency-inventory.md"
proven:
  - "Game currently aggregates map, player/guild/item registries, world state, gameplay coordination, and an IOWheel owner."
  - "ProtocolGame dispatches packet input and contains validation, gameplay orchestration, concrete IO access, and response formatting."
  - "Lua exposes direct SQL and broad mutable Player APIs."
  - "Player SQL save is transaction-owned; Wheel KV staging occurs after SQL commit as a separate persistence domain."
  - "No pre-existing MGE-001 package existed at baseline."
derived:
  - "Current directory structure is not a dependable module boundary."
  - "Bank is the lowest-risk first vertical gameplay extraction candidate only after adapter contracts are defined."
unknown:
  - "A complete whole-program include graph was not generated."
  - "Runtime frequency of every Lua mutator and SQL function is not established."
  - "End-to-end stale-writer fencing is not proven for every persistence path."
conflicts: []
first_failure: null
rejected_hypotheses:
  - "A subsystem is modular because it has its own directory."
  - "ProtocolGame is only a transport adapter."
  - "A SQL transaction proves SQL/KV crash consistency."
  - "A newer Canary implementation is automatically the correct Otheryn target."
changed_paths:
  - "docs/architecture/current-engine-ownership-and-dependencies.md"
  - "docs/agents/tasks/active/OTH-20260726-mge001-ownership-dependency-inventory.md"
validation:
  checkpoint: "pass"
  markdown: "pass"
  links_and_paths: "pass"
  changed_paths: "pass"
  secret_scan: "pass"
  tools_tests: "not_applicable_no_tools_added"
  deterministic_generation: "not_applicable_no_generated_artifact"
  exact_blob_reread: "pass"
  open_pr_ownership: "pass_including_pr_128_drift"
  discussions: "pass_at_validation_time"
  reviews: "pass_at_validation_time"
  unresolved_threads: "pass_at_validation_time"
  target_main_drift: "pass_main_38bb62192d25984d63f96c2637348b4adc82f6cd"
  exact_head_required: "queued"
blockers: []
next_action: "Confirm Required succeeds on the new checkpoint commit and re-audit PR #129 before merge."
```
