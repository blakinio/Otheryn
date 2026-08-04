# Evidence index — external truth-source enrichment

Task: `OTERYN-20260804-external-truth-source-enrichment`

## Canonical scope

- total unique keys: **60**;
- predecessor `REPRO`: **49**;
- predecessor `INSUFFICIENT`: **11**;
- upstream Canary: **51** items, including one pull request;
- CrystalServer: **9** items, including three pull requests;
- duplicates: **0**.

The scope was recovered from the predecessor 103-row matrix and refreshed with the live source titles of every canonical Issue and pull request. The source type is preserved so pull requests are not silently treated as Issues.

## Evidence files

- `canonical-scope.json` — exact 60-key scope, predecessor row, live source title, prior bucket/status/reason, source URL and pinned source revision;
- `source-policy.md` — provenance hierarchy, version discipline, conclusion enums, five-repository comparison and runtime gate;
- `dossier-template.md` — normalized per-item evidence schema;
- `dossiers/` — completed per-item research and reproduction records;
- `source-registry.json.gz` and `source-registry.csv.gz` — final normalized source records, not yet generated;
- `expected-behavior-matrix.md` — pending final aggregation;
- `reproduction-matrix.md` — pending final aggregation;
- `decision-matrix.md` — pending final aggregation;
- `validation.txt` — pending;
- `independent-audit.md` — pending.

## Current coverage

| Gate | Result |
|---|---:|
| Canonical keys recovered | 60/60 |
| Unique keys | 60/60 |
| Source titles resolved | 60/60 |
| Pinned source revisions recorded | 60/60 |
| Per-item dossiers | 14/60 |
| Five-repository comparisons | 14/60 |
| Expected-behavior conclusions | 14/60 |
| Runtime plans or explicit reference blockers | 14/60 |
| Runtime executions | 0/60 |
| Final item decisions | 14/60 |
| `INSUFFICIENT` rows fully researched | 11/11 |
| `REPRO` rows fully researched | 3/49 |

## Completed insufficient-evidence dispositions

| Item | Truth | Static | Runtime | Owner action |
|---|---|---|---|---|
| `opentibiabr/canary#4052` | PARTIALLY_PROVEN | TARGET_AFFECTED | NOT_APPLICABLE | OPEN_ARCHITECTURE_DECISION |
| `opentibiabr/canary#3742` | PARTIALLY_PROVEN | TARGET_AFFECTED | PENDING | OPEN_FIX_PROGRAM |
| `opentibiabr/canary#3599` | PARTIALLY_PROVEN | STATIC_INCONCLUSIVE | PENDING | RESEARCH_REQUIRED |
| `opentibiabr/canary#3430` | PROVEN | TARGET_NOT_AFFECTED | PENDING | NO_ACTION |
| `opentibiabr/canary#3427` | UNKNOWN | STATIC_INCONCLUSIVE | NOT_RUN_REFERENCE_INSUFFICIENT | RESEARCH_REQUIRED |
| `opentibiabr/canary#3407` | UNKNOWN | STATIC_INCONCLUSIVE | NOT_RUN_REFERENCE_INSUFFICIENT | RESEARCH_REQUIRED |
| `opentibiabr/canary#3374` | PROVEN | TARGET_AFFECTED | PENDING | OPEN_FIX_PROGRAM |
| `opentibiabr/canary#2272` | UNKNOWN | STATIC_INCONCLUSIVE | NOT_RUN_REFERENCE_INSUFFICIENT | RESEARCH_REQUIRED |
| `opentibiabr/canary#917` | UNKNOWN | STATIC_INCONCLUSIVE | NOT_RUN_REFERENCE_INSUFFICIENT | RESEARCH_REQUIRED |
| `opentibiabr/canary#560` | PROVEN | TARGET_AFFECTED | PENDING | OPEN_FIX_PROGRAM |
| `zimbadev/crystalserver#206` | PARTIALLY_PROVEN | STATIC_INCONCLUSIVE | PENDING | OPEN_ARCHITECTURE_DECISION |

## Completed reproduction-row research

- `opentibiabr/canary#3513` — official-client zone-login speed crash: source path present, maintained client is tolerant, deterministic packet-order reproduction pending;
- `zimbadev/crystalserver#785` — live map cache retention: architecture present, quantitative swap soak pending;
- `zimbadev/crystalserver#852` — occupied live map swap/client crash: exact script path present, deterministic map/client reproduction pending.

## Scope integrity

Authoritative predecessor evidence:

- matrix blob SHA: `006a790c143ea16acaaaefe09a8a2a2ea526b2d8`;
- predecessor task: `docs/agents/tasks/archive/OTERYN-20260803-upstream-103-cross-repository-revalidation.md`;
- predecessor valid inventory CSV blob: `8ae3ddb89cebe581d236fcd0d4c6c74420bd9b30`;
- predecessor JSON corruption remains a recorded historic conflict and is not used to redefine scope.

## Next bounded phase

Research the remaining 46 `REPRO` rows in coherent behavior families. Prioritize rows with exact source steps and shared quest/map/protocol paths, then build runtime harnesses only after expected behavior and safety boundaries are complete.
