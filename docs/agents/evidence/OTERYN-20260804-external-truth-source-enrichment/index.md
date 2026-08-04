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
- `dossiers/` — per-item research and reproduction records, to be populated;
- `source-registry.json.gz` and `source-registry.csv.gz` — final normalized source records, not yet generated;
- `expected-behavior-matrix.md` — pending;
- `reproduction-matrix.md` — pending;
- `decision-matrix.md` — pending;
- `validation.txt` — pending;
- `independent-audit.md` — pending.

## Current coverage

| Gate | Result |
|---|---:|
| Canonical keys recovered | 60/60 |
| Unique keys | 60/60 |
| Source titles resolved | 60/60 |
| Pinned source revisions recorded | 60/60 |
| Per-item dossiers | 0/60 |
| Five-repository comparisons | 0/60 |
| Runtime plans | 0/60 |
| Runtime executions | 0/60 |
| Final decisions | 0/60 |

## Scope integrity

Authoritative predecessor evidence:

- matrix blob SHA: `006a790c143ea16acaaaefe09a8a2a2ea526b2d8`;
- predecessor task: `docs/agents/tasks/archive/OTERYN-20260803-upstream-103-cross-repository-revalidation.md`;
- predecessor valid inventory CSV blob: `8ae3ddb89cebe581d236fcd0d4c6c74420bd9b30`;
- predecessor JSON corruption remains a recorded historic conflict and is not used to redefine scope.

## Next bounded phase

Create the normalized dossier template and complete the first coherent research batch, prioritizing items with deterministic source steps or shared map-runtime/protocol families. Persist source provenance and static comparison before attempting any runtime reproduction.
