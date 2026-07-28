# OTH-20260727 — MGE-004 composition root lifecycle

Status: **completed and merged**

Issue: `#161` — closed
Implementation branch: `dudantas/mge-004-composition-root-lifecycle`
Implementation pull request: `#162`
Final implementation head: `3470e125870fd59578ccbe094433f396221ae609`
Synchronized target main: `41bc0562c263781df85c2f6855295fefa201db0a`
Implementation merge SHA: `a2186277f42b5250253af1c7faf952f553164459`
Lifecycle branch: `dudantas/mge-004-lifecycle-archive`
Lifecycle pull request: `#175`
Lifecycle merge SHA: `8b40cf8ba1cc23b9144c01f62c70b21f35abc7a1`
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

## Final validation and lifecycle closure

- final implementation changed exactly 7 declared paths;
- comments, reviews and inline threads were empty;
- target drift was zero at implementation merge;
- autofix run `30259175893`: success;
- full CI run `30259176170`: success;
- Required run `30259175890`: success;
- Windows CMake compilation, MariaDB installation and Canary runtime smoke: success;
- Linux debug compilation, Canary runtime smoke, schema import and full tests: success;
- Linux release Canary and Global runtime smoke: success;
- macOS compilation and Canary runtime smoke: success;
- expected-head merge protection was enforced on `3470e125870fd59578ccbe094433f396221ae609`;
- implementation squash merge SHA: `a2186277f42b5250253af1c7faf952f553164459`;
- issue `#161` closed as completed;
- lifecycle PR `#175` changed only the active/archive task pair, passed Required run `30260635496`, and squash-merged as `8b40cf8ba1cc23b9144c01f62c70b21f35abc7a1`;
- the active task record is absent from `main`, the archive record is present, and no `mge-004` branches remain.

## Final checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-28T22:05:16+02:00"
head: "8b40cf8ba1cc23b9144c01f62c70b21f35abc7a1"
head_scope: "final lifecycle archive merge on main; later unrelated main commits do not alter MGE-004 completion evidence"
branch: "main"
pr: 175
status: "completed"
context_routes:
  - "docs/architecture/modular-game-engine-and-profiles.md"
  - "docs/architecture/current-engine-ownership-and-dependencies.md"
  - "docs/architecture/module-registry-and-profile-validation.md"
  - "docs/architecture/module-composition-root-and-lifecycle.md"
owned_paths:
  - "docs/agents/tasks/archive/OTH-20260727-mge004-composition-root-lifecycle.md"
proven:
  - "MGE-004 implementation PR #162 squash-merged from exact head 3470e125870fd59578ccbe094433f396221ae609 as a2186277f42b5250253af1c7faf952f553164459."
  - "CI 30259176170, autofix 30259175893 and Required 30259175890 succeeded on the exact implementation head."
  - "The implementation changed exactly seven declared paths and passed all applicable platform builds, runtime smoke checks, schema import and full Linux tests."
  - "The final implementation audit found no comments, reviews, review threads or target drift."
  - "Issue #161 closed as completed."
  - "Lifecycle PR #175 changed only the active/archive task pair, passed Required 30260635496 and squash-merged as 8b40cf8ba1cc23b9144c01f62c70b21f35abc7a1."
  - "The active task record is absent from main, the archive record is present and no mge-004 branches remain."
derived:
  - "MGE-004 requires no further implementation, validation, merge, archive or branch-cleanup action."
  - "A later MGE package must begin as a separately scoped task with a fresh ownership preflight."
unknown: []
conflicts: []
first_failure:
  marker: "CI 30247921486 attempt 1 / macOS job 89919380421 / Smoke test Canary datapack runtime"
  result: "RESOLVED"
  evidence: "The server reached readiness and shut down cleanly; the unchanged head passed on rerun, and later exact heads passed macOS without rerun."
rejected_hypotheses:
  - "Move all singleton services into the root in one package."
  - "Treat every MGE-003 descriptor as lifecycle-owned."
  - "Combine lifecycle foundation with Bank gameplay extraction."
  - "Change MGE-004 code to suppress a one-off hosted-runner queue-latency warning."
changed_paths:
  - "docs/agents/tasks/active/OTH-20260727-mge004-composition-root-lifecycle.md"
  - "docs/agents/tasks/archive/OTH-20260727-mge004-composition-root-lifecycle.md"
validation:
  - command: "implementation exact-head CI/autofix/Required"
    result: "PASS"
    evidence: "CI 30259176170, autofix 30259175893 and Required 30259175890 succeeded on 3470e125870fd59578ccbe094433f396221ae609."
  - command: "implementation final audit and expected-head merge"
    result: "PASS"
    evidence: "Exactly seven declared paths, behind_by zero, no discussion or review items, and squash merge a2186277f42b5250253af1c7faf952f553164459."
  - command: "lifecycle archive PR #175"
    result: "PASS"
    evidence: "Exactly the active/archive task pair changed; Required 30260635496 succeeded and expected-head squash merge produced 8b40cf8ba1cc23b9144c01f62c70b21f35abc7a1."
  - command: "final repository-state audit"
    result: "PASS"
    evidence: "Issue closed, both PRs merged, active record absent, archive record present and no mge-004 branches remain."
blockers: []
next_action: "No further action is required for MGE-004; start any subsequent MGE package only as a separately scoped task with a fresh preflight."
```
