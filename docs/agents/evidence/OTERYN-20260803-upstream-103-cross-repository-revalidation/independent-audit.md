# Independent falsification

Validator: `agent-20260803-cross-revalidation-validator-001`

Scope: generated evidence only plus exact repository/source references named by the producer. The validator did not accept the producer summary as proof.

## Challenges performed

- strict decompression and parsing of both inventories;
- exactly 103 JSON rows, 103 CSV rows and 103 unique canonical keys;
- exact source totals `14 + 60 + 20 + 9`;
- all mandatory fields and allowed enums;
- all 15 proposed `CONFIRMED_OTHERYN_GAP` rows require `otheryn_state=DEFECT_PRESENT`, `evidence_status=PROVEN`, exact target paths and a non-empty static proof;
- all critical/high rows were checked for either direct exact-path proof or an explicit nonclaim/runtime/decision requirement;
- all duplicate families remain independently represented;
- all changed/strengthened classifications have an evidence reason;
- all owner-bucket and evidence-status counts reconcile with report, matrix and decision brief;
- `matrix.md` contains 103 visible item rows;
- `decision-brief.md` contains 103 unique source-item bullets;
- canonical source drift is separated from the fixed 103-row scope;
- no generated evidence claims unchanged Issue comments because reliable comment-delta metadata was unavailable;
- changed-path plan contains only the active audit task and audit evidence directory.

## Material findings

None open.

During validation, the predecessor JSON corruption remained preserved as a conflict rather than silently repaired. Canonical scope recovery is based on the immutable valid CSV companion and does not claim the lost JSON typing.

## Result

`PASS`

Open critical/high findings: `0`.

Runtime E2E: `NOT_APPLICABLE`.

Reason: `Documentation/evidence-only cross-repository audit; no runtime behavior was changed.`
