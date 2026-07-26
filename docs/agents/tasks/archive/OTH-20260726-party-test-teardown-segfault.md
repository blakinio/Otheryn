# OTH-20260726 — Party unit-test teardown SIGSEGV

Status: **completed and merged**  
Issue: #125 — closed as completed  
Implementation branch: `dudantas/fix-party-test-teardown`  
Implementation pull request: #126  
Final implementation head: `9b65c26c7cb364542beba2f3498bcd04102be6e2`  
Merge SHA: `41c086d3d77b9327aafa6f1375e9531bec3971f2`  
Target repository: `blakinio/Otheryn`

## Objective

Fix the deterministic process-teardown SIGSEGV reported after `PartyTest.GetPlayersAndDisbandHandleNullEntries` completed successfully, without weakening the test or changing production Party, Player, Game, Lua, DI, protocol, persistence, schema or deployment behavior.

## Root cause

Focused ASAN reproduced a heap-use-after-free caused by cross-translation-unit static destruction order:

1. the Party test materialized `Game` and Lua-backed services in a suite-scoped test injector;
2. process teardown destroyed `LuaScriptInterfaceRegistry` first;
3. the static test injector was destroyed later;
4. injector destruction closed `Game`/`Raids` Lua state and constructed `LuaEnvironment`;
5. the new Lua interface attempted to register in the already-freed registry.

The defect belonged to the test fixture lifetime boundary, not to `Party::disband()`, Party membership invariants or Player ownership.

## Delivered change

- `tests/unit/players/party_test.cpp` now owns the test injector with `std::unique_ptr`;
- the injector is created in `SetUpTestSuite()`;
- the global test-container pointer is cleared and the injector is destroyed explicitly in `TearDownTestSuite()` while the Lua registry is still alive;
- the original null-entry setup, full `Party::disband()` execution and every post-disband assertion remain intact;
- `.github/workflows/party-test-sanitizer.yml` retains a focused 25-repeat ASAN/UBSAN regression gate.

## Validation evidence

- original Linux debug failure: run `30197504976`, reproduced twice after 482 of 483 tests passed;
- baseline focused ASAN diagnosis: run `30198967320`, job `89785504123`, heap-use-after-free reproduced after 25 successful repetitions;
- fixed focused ASAN source-head run: `30200053915`, job `89788326340` — success;
- ready-head repository CI: `30200069480` — success, including all 483 Linux debug tests and every platform build;
- ready-head `Required`: `30200069347` — success;
- final main-synchronized focused ASAN: `30201971037`, job `89793343280` — success;
- final main-synchronized CI: `30201971076` — success;
- final main-synchronized `Required`: `30201971029` — success;
- final PR audit: exactly three intended implementation paths, no comments, no reviews or unresolved threads, and zero commits behind `main`;
- merge method: squash with expected-head protection;
- merge SHA: `41c086d3d77b9327aafa6f1375e9531bec3971f2`.

## Lifecycle result

The implementation is on `main`, issue #125 is closed, and the temporary active task is removed by this lifecycle-only package. No runtime or test implementation is changed by the archive PR.

## Next action

Resume PRS-001 PR #123 by integrating the current `main` into `dudantas/prs-001-backup-pitr-foundation`, then rerun its exact-head backup/PITR drill, repository CI and `Required` before deciding whether it is ready for merge.
