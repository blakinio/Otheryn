---
task_id: OTH-20260817-atlas-controlled-distribution-prep
status: completed
owner: none
branch: feat/OTH-20260817-atlas-controlled-distribution-prep
base_branch: main
created: "2026-08-17T10:23:00+02:00"
completed: "2026-08-17T10:34:31+02:00"
updated: "2026-08-17T10:34:31+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "431"
ownership_released: true
---

# OTBM Atlas controlled distribution preparation — completed

## Outcome

A fail-closed user-distribution preparation layer is merged without activating Internet exposure or publishing the generated Atlas corpus.

Implementation PR: `blakinio/Otheryn#431`

Final implementation head:

`782e56eddbf71ccc9827559549c88f2cc8e31060`

Merge commit on `main`:

`76da15d02598d38fb00852df866a14ce094c37b9`

## Delivered

- explicit `private-local`, `internet-authenticated` and `internet-public` publication modes;
- publication gate accepts the real Atlas directory and always recomputes a fresh full deployment preflight in-process;
- full preflight uses chunk verification and requires environment animations;
- publication requires `FULL_RUNTIME_READY`, canonical v3/128/3494 world identity, current viewer/runtime layers and successful independent verification;
- every Internet-facing mode remains blocked without an exact-scope `ATLAS-PR-009` approval record;
- committed approval template is deliberately `approved: false`;
- authenticated-beta design preserves the existing read-only Synology origin and current private cache policy;
- this task does not authorize GitHub Pages, R2/CDN/object-storage publication, public DNS, Internet port forwarding or a Synology full-world build;
- eight focused publication-gate tests and a dedicated lightweight workflow are present on `main`.

## Fresh audit and remediation

Fresh diff audit found one material issue before merge: the first revision accepted an already-written deployment-preflight JSON file, which could be stale or hand-written.

Remediation changed the gate to accept the generated Atlas directory itself and invoke `tools.otbm_atlas.deploy_preflight.deployment_preflight()` directly with:

```text
verify_chunks=true
require_environment_animations=true
```

A regression test proves that the gate calls the fresh full preflight against the supplied Atlas root. Open material findings after remediation: `0`.

PR review hygiene at final audit:

- review threads: `0`;
- submitted reviews: `0`;
- no unresolved material findings.

## Exact-head validation

Final head `782e56eddbf71ccc9827559549c88f2cc8e31060`:

- `OTBM Atlas Controlled Distribution` run `32010846498` — SUCCESS;
- `CI` run `32010846655` — SUCCESS;
- `Required` run `32010846431` — SUCCESS;
- `autofix.ci` run `32010846467` — SUCCESS;
- Lua Tests — SUCCESS;
- Fast Checks — SUCCESS;
- Linux/Docker heavy build jobs — correctly SKIPPED because the final paths are deployment tooling/docs/workflow only and do not affect engine/Docker runtime build inputs.

## Remaining broader product-readiness boundary

This bounded preparation task does not close `OTH-20260815-otbm-atlas-product-readiness`.

The real next deployment boundary remains:

1. reuse the already-generated desktop `build/full-map-atlas` corpus;
2. transfer it via the verified SMB path to `\\Synology\docker\otheryn\atlas\current`;
3. run the full publication/deployment preflight against the copied real corpus;
4. start the already-staged private Synology project and obtain the private DSM URL;
5. run the deployed Chromium E2E/performance probe;
6. do not activate any Internet-facing route until `ATLAS-PR-009` is explicitly reviewed and recorded.

No full-world rebuild on Synology is authorized as a substitute for the desktop corpus transfer.

## Closeout

```yaml
closeout:
  implementation_complete: true
  outcome_verified: true
  audit:
    result: PASS
    findings_found: 1
    findings_remediated: 1
    findings_open_material: 0
  tests:
    focused_publication_gate: PASS
    focused_test_count: 8
    ci: PASS
    required: PASS
    autofix: PASS
  implementation:
    pull_request: 431
    final_head: 782e56eddbf71ccc9827559549c88f2cc8e31060
    merge_commit: 76da15d02598d38fb00852df866a14ce094c37b9
  safety_boundaries:
    internet_exposure_activated: false
    corpus_uploaded_to_github: false
    corpus_uploaded_to_object_storage: false
    synology_full_build_started: false
    atlas_pr_009_bypassed: false
  task_archived_or_terminal: true
  ownership_released: true
```
