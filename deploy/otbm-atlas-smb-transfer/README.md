# OTBM Atlas — verified Windows-to-Synology SMB publication

This package closes the remaining deployment-data boundary for the existing private Synology preview. It copies the already-generated desktop Atlas to the verified SMB share, verifies the copied corpus in staging, and only then renames the verified staging directory to `current`.

It does **not** build Atlas on Synology, use SSH, start/stop Container Manager, create DSM Reverse Proxy rules, configure Cloudflare, or expose the Atlas to the Internet.

## Verified destination

The existing project-readiness evidence established:

```text
SMB share:  \\Synology\docker
Atlas root: \\Synology\docker\otheryn\atlas
Current:    \\Synology\docker\otheryn\atlas\current
```

The script assumes the Windows session already has normal SMB access to that share. It does not collect, store or transmit SMB credentials.

## First publication

From the repository root on the Windows machine that already contains `build/full-map-atlas`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File deploy\otbm-atlas-smb-transfer\publish.ps1
```

Use `pwsh` instead of `powershell` if PowerShell 7 is preferred.

Before copying any bytes, the script runs the merged fail-closed publication gate against the local source. The gate itself performs a fresh full Atlas deployment preflight with complete chunk verification and required environment animations.

The transfer then follows:

```text
build/full-map-atlas
        |
        | full local publication gate
        v
\\Synology\docker\otheryn\atlas\incoming-<timestamp>-<id>
        |
        | robocopy over SMB
        | full publication gate over the copied SMB corpus
        v
verified staging
        |
        | current-state drift guard
        | same-share directory rename
        v
\\Synology\docker\otheryn\atlas\current
```

A failed copy or failed remote publication gate is never promoted to `current`.

## Plan-only inspection

To inspect resolved paths without creating directories, copying data or running the full preflight:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File deploy\otbm-atlas-smb-transfer\publish.ps1 -PlanOnly
```

## Existing current Atlas

The default path is deliberately fail-closed if `current` already exists. This prevents an accidental replacement of a preview that may be in use.

For a later deliberate update:

1. stop the private Atlas preview using the normal DSM Container Manager lifecycle;
2. run the script with `-AllowReplaceCurrent`;
3. the script records that `current` exists and fingerprints its `manifest.json` before the long copy;
4. immediately before promotion it requires both the presence state and manifest fingerprint to be unchanged;
5. if another operator/deployment creates, removes or changes `current` while the transfer is running, promotion is refused and the verified `incoming-*` directory is left untouched for inspection;
6. only a stable existing `current` is renamed to `previous-<timestamp>-<id>`;
7. only fully verified staging is renamed to `current`;
8. if the staging rename fails, the script attempts to restore the previous directory back to `current`;
9. keep the previous directory until the new deployment passes browser validation.

Example:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File deploy\otbm-atlas-smb-transfer\publish.ps1 -AllowReplaceCurrent
```

The script never automatically deletes a previous Atlas version.

## Evidence

Local operational evidence is written outside the generated corpus under:

```text
build/atlas-deployment-evidence/<timestamp>-<id>/
```

It contains:

- source publication-gate report;
- SMB-staging publication-gate report;
- robocopy log;
- promotion receipt with the final manifest SHA-256 and exact paths.

No evidence file is inserted into the generated Atlas corpus.

## Copy semantics

The script uses Windows `robocopy` only between the verified local source and a unique, newly-created `incoming-*` directory. `/MIR` is therefore bounded to disposable staging and is never run directly against `current` or `previous-*`.

`robocopy` exit codes `0..7` are accepted according to the tool's success/non-fatal-change convention; `8+` fails the operation and prevents promotion.

The default copy worker count is 16 and can be changed without altering Atlas semantics:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File deploy\otbm-atlas-smb-transfer\publish.ps1 -Threads 8
```

## After successful first publication

The data boundary is then closed, but the private runtime still requires the existing owner-reserved DSM UI actions:

1. Container Manager → import/start `otheryn-atlas-preview` from the already-staged project under `/volume1/docker/otheryn/atlas/project`;
2. confirm the container becomes healthy;
3. create the private DSM Reverse Proxy source whose destination is `HTTP 127.0.0.1:8095 /`;
4. open the resulting private URL in a normal browser;
5. run `tools.otbm_atlas.deployed_browser_probe` against that exact URL for ATLAS-PR-003/004 evidence.

Do not configure any Internet-facing hostname until `ATLAS-PR-009` has been explicitly reviewed and recorded.
