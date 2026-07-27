# OTH-20260727 — MGE-004 composition root lifecycle

Status: **completed and merged**

Issue: `#161` — closed
Implementation branch: `dudantas/mge-004-composition-root-lifecycle`
Implementation pull request: `#162`
Final implementation head: `3470e125870fd59578ccbe094433f396221ae609`
Synchronized target main: `41bc0562c263781df85c2f6855295fefa201db0a`
Implementation merge SHA: `a2186277f42b5250253af1c7faf952f553164459`
Lifecycle branch: `dudantas/mge-004-lifecycle-archive`
Target repository: `blakinio/Otheryn`

## Result

Otheryn now has a bounded module composition root that:

- consumes the validated MGE-003 dependency-first module order;
- starts explicitly registered participants in dependency order;
- publishes readiness only after successful startup;
- rolls back successful starts and stops normally in exact reverse order;
- records stop errors without preventing remaining participants from stopping;
- keeps separate root instances isolated;
- transfers only `MonsterComputeService` into explicit lifecycle ownership under `Creatures` while preserving its configuration, startup phase and diagnostics;
- leaves unregistered legacy systems under their existing ownership.

## Final implementation validation

- final changed paths: exactly 7 declared paths;
- comments, reviews and inline threads: empty;
- target drift: branch behind by 0 at merge;
- autofix run `30259175893`: success;
- full CI run `30259176170`: success;
- Required run `30259175890`: success;
- Windows CMake compilation, MariaDB installation and Canary runtime smoke: success;
- Linux debug compilation, Canary runtime smoke, schema import and full tests: success;
- Linux release Canary and Global runtime smoke: success;
- macOS compilation and Canary runtime smoke: success;
- expected-head merge protection: enforced on `3470e125870fd59578ccbe094433f396221ae609`;
- squash merge SHA: `a2186277f42b5250253af1c7faf952f553164459`;
- issue `#161`: closed as completed.

## Checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-27T13:05:20+02:00"
head: "a2186277f42b5250253af1c7faf952f553164459"
branch: "main"
pr: 162
status: "completed_merged_lifecycle_archive_pending"
context_routes:
  - "docs/architecture/modular-game-engine-and-profiles.md"
  - "docs/architecture/current-engine-ownership-and-dependencies.md"
  - "docs/architecture/module-registry-and-profile-validation.md"
  - "docs/architecture/module-composition-root-and-lifecycle.md"
proven:
  - "MGE-004 merged from exact head 3470e125870fd59578ccbe094433f396221ae609."
  - "CI 30259176170, autofix 30259175893 and Required 30259175890 succeeded on the exact head."
  - "The implementation changed exactly seven declared paths."
  - "The final audit found no comments, reviews or review threads and no target drift."
  - "Issue #161 closed as completed after squash merge a2186277f42b5250253af1c7faf952f553164459."
derived:
  - "MGE-006 can define bounded command/query protocol and Lua adapter interfaces before the first MGE-005 gameplay extraction."
unknown: []
conflicts: []
validation:
  implementation_ci: "pass_run_30259176170"
  implementation_autofix: "pass_run_30259175893"
  implementation_required: "pass_run_30259175890"
  implementation_merge: "pass_a2186277f42b5250253af1c7faf952f553164459"
  lifecycle_required: "pending"
blockers: []
next_action: "Validate and merge this lifecycle-only archive PR, then begin the next bounded MGE package from a fresh preflight."
```
