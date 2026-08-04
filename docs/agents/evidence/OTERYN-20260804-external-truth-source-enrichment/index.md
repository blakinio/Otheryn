# Evidence index — external truth-source enrichment

Task: `OTERYN-20260804-external-truth-source-enrichment`

## Canonical scope

- total unique keys: **60**;
- predecessor `REPRO`: **49**;
- predecessor `INSUFFICIENT`: **11**;
- upstream Canary: **51** items, including one pull request;
- CrystalServer: **9** items, including three pull requests;
- duplicates: **0**.

The scope is the immutable 60-row subset inherited from the completed 103-item cross-repository revalidation. Live source discovery did not expand it.

## Final coverage

| Gate | Result |
|---|---:|
| Canonical keys recovered | 60/60 |
| Unique keys | 60/60 |
| Source titles and types resolved | 60/60 |
| Pinned source revisions recorded | 60/60 |
| Per-item dossiers | 60/60 |
| Five-repository comparisons | 60/60 |
| Expected-behavior conclusions | 60/60 |
| Runtime plans or explicit terminal blockers | 60/60 |
| Final item decisions | 60/60 |
| `INSUFFICIENT` rows researched | 11/11 |
| `REPRO` rows researched | 49/49 |
| Canonical gameplay/client executions | 0/60 |
| Product/runtime paths changed | 0 |

## Evidence-stage conclusions

### Truth status

- `PROVEN`: **31**;
- `PARTIALLY_PROVEN`: **24**;
- `UNKNOWN`: **5**.

### Static target conclusion

- `TARGET_AFFECTED`: **9**;
- `TARGET_NOT_AFFECTED`: **2**;
- `TARGET_PATH_ABSENT`: **2**;
- `STATIC_INCONCLUSIVE`: **47**.

### Runtime disposition

- `NOT_APPLICABLE`: **13** — pinned static evidence already determines the target disposition;
- `NOT_RUN_REFERENCE_INSUFFICIENT`: **5** — no deterministic expected result is supported;
- `NOT_RUN_INFEASIBLE`: **42** — the repository lacks a deterministic game-protocol/client driver and isolated scenario fixtures, and building them is outside audit-only authority.

No canonical gameplay/client scenario was executed. `runtime-feasibility.md` records the exact existing Docker/login boundary and why it cannot truthfully execute these 42 scenarios.

### Owner action

- `OPEN_FIX_PROGRAM`: **8**;
- `OPEN_ARCHITECTURE_DECISION`: **3**;
- `OPEN_PROTOCOL_DECISION`: **2**;
- `NO_ACTION`: **2**;
- `RESEARCH_REQUIRED`: **45**.

These are evidence-stage recommendations only. No row authorizes implementation.

## Durable artifacts

- `canonical-scope.json` — exact canonical identity and predecessor metadata;
- `source-policy.md` — source hierarchy, version discipline and conclusion contracts;
- `dossier-template.md` — normalized evidence schema;
- `dossiers/` — 60 complete per-item records;
- `source-registry.json.gz` and `source-registry.csv.gz` — normalized 60-row registries with matching identities and dispositions;
- `expected-behavior-matrix.md` — exact 60-key expected-behavior aggregation;
- `reproduction-matrix.md` — exact 60-key terminal runtime disposition aggregation;
- `decision-matrix.md` — exact 60-key truth/static/runtime/owner-action aggregation;
- `runtime-feasibility.md` — executable-boundary and authority closeout;
- `validate_evidence.py` — deterministic primary invariant validator;
- `independent_falsification.py` — separate falsification implementation;
- `validation.txt` and `validation.json` — persisted primary validation result;
- `independent-audit.md` and `independent-audit.json` — persisted fresh independent result.

## Scope integrity

Authoritative predecessor evidence:

- predecessor matrix blob SHA: `006a790c143ea16acaaaefe09a8a2a2ea526b2d8`;
- predecessor task: `docs/agents/tasks/archive/OTERYN-20260803-upstream-103-cross-repository-revalidation.md`;
- predecessor valid inventory CSV blob: `8ae3ddb89cebe581d236fcd0d4c6c74420bd9b30`;
- predecessor JSON corruption remains an explicit historic conflict and was not used to redefine scope.

## Validation

- deterministic primary validation: **PASS** on evidence head `1cf8d74d10805156bc63c26416ce0a6d2bce0154`, workflow run `30932195423`;
- independent falsification: **PASS**, zero open material findings on evidence head `ab8ea10db6bab03a7bc611c5cde1c8dcdfc29a8f`, workflow run `30932913247`;
- exact-final-head Required CI: pending;
- runtime E2E: item-level terminal dispositions recorded above; no product behavior changed.
