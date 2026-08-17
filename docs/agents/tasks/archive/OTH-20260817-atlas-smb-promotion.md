---
task_id: OTH-20260817-atlas-smb-promotion
status: completed
owner: none
branch: feat/OTH-20260817-atlas-smb-promotion
base_branch: main
created: "2026-08-17T10:35:00+02:00"
completed: "2026-08-17T10:44:25+02:00"
updated: "2026-08-17T10:44:25+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: "433"
ownership_released: true
---

# OTBM Atlas verified SMB promotion — completed

## Outcome

A fail-closed Windows-to-Synology publication helper is merged. It reduces the remaining physical deployment-data boundary to one owner-side Windows command while preserving the existing prohibition on NAS full-world builds and Internet exposure.

Implementation PR: `blakinio/Otheryn#433`

Final implementation head:

`e0d848235469b45e3f8a361d76348f9983bf44fa`

Merge commit on `main`:

`845510abdc8ad0291e559586efd03addd17e13ea`

## Delivered

- `deploy/otbm-atlas-smb-transfer/publish.ps1`;
- `deploy/otbm-atlas-smb-transfer/transfer_contract.psm1`;
- local full publication gate before any SMB write;
- unique `incoming-<timestamp>-<id>` staging under `\\Synology\docker\otheryn\atlas`;
- bounded `robocopy` transfer with `/MIR` restricted to disposable staging;
- full publication gate repeated against the copied UNC staging corpus;
- same-share rename promotion only after successful remote verification;
- default refusal to replace an existing `current` without explicit `-AllowReplaceCurrent`;
- current-state drift guard binding initial presence plus `manifest.json` SHA-256 across the long copy;
- preservation of stable replaced `current` as `previous-*` and rollback attempt if final staging rename fails;
- local evidence package with source gate, remote gate, robocopy log and promotion receipt;
- `-PlanOnly` mode with zero destination side effects;
- focused PowerShell syntax/plan/drift/safety validation on `ubuntu-latest` with no Windows/macOS build runner.

## Fresh audit and remediation

Fresh diff audit found one material race before merge: `current` was initially checked before the long copy but could appear, disappear or change before promotion.

The final implementation records the initial `current` presence and, for an explicitly authorized replacement, the initial `manifest.json` SHA-256. Immediately before any rename it verifies both are unchanged. A new/missing `current` or manifest drift aborts promotion and leaves the verified `incoming-*` directory for inspection.

Focused regressions prove:

- a `current` directory appearing during transfer blocks promotion;
- a stable existing `current` is accepted when its manifest fingerprint is unchanged;
- a manifest mutation during transfer blocks promotion.

Open material findings after remediation: `0`.

Final review hygiene:

- review threads: `0`;
- submitted reviews: `0`.

## Exact-head validation

Final head `e0d848235469b45e3f8a361d76348f9983bf44fa`:

- `OTBM Atlas SMB Transfer` run `32011599746` — SUCCESS;
- `CI` run `32011599883` — SUCCESS;
- `Required` run `32011599742` — SUCCESS;
- `autofix.ci` run `32011599756` — SUCCESS;
- Lua Tests — SUCCESS;
- Fast Checks — SUCCESS;
- Linux/Docker/Quickstart heavy jobs — correctly SKIPPED because the final paths are deployment scripts/docs/workflow only.

## Post-merge verification

- `main` points to `845510abdc8ad0291e559586efd03addd17e13ea`;
- `publish.ps1` and `transfer_contract.psm1` were reread from `main`;
- the implementation branch was automatically deleted after merge.

## Remaining broader product-readiness boundary

This bounded task does not claim the 10+ GB corpus was physically transferred. The GitHub connector cannot read the owner's Windows desktop filesystem or LAN SMB session.

The exact next owner-side command, from the repository root on the Windows machine that already contains `build/full-map-atlas`, is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File deploy\otbm-atlas-smb-transfer\publish.ps1
```

That command validates the local corpus, copies it to isolated SMB staging, validates the copied corpus over SMB, and promotes only verified staging to `\\Synology\docker\otheryn\atlas\current`.

After successful physical transfer the broader product-readiness task still requires the already-reserved DSM UI actions and real browser evidence. No Internet-facing route may be enabled until `ATLAS-PR-009` is explicitly reviewed and recorded.

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
    focused_smb_transfer: PASS
    ci: PASS
    required: PASS
    autofix: PASS
  implementation:
    pull_request: 433
    final_head: e0d848235469b45e3f8a361d76348f9983bf44fa
    merge_commit: 845510abdc8ad0291e559586efd03addd17e13ea
  safety_boundaries:
    physical_transfer_claimed_complete: false
    internet_exposure_activated: false
    corpus_uploaded_to_github: false
    corpus_uploaded_to_object_storage: false
    synology_full_build_started: false
    windows_macos_builds_reintroduced: false
  task_archived_or_terminal: true
  ownership_released: true
```
