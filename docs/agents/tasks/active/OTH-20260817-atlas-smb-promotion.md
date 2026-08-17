---
task_id: OTH-20260817-atlas-smb-promotion
status: in_progress
owner: chat-github-atlas-smb-promotion
branch: feat/OTH-20260817-atlas-smb-promotion
base_branch: main
created: "2026-08-17T10:35:00+02:00"
updated: "2026-08-17T10:35:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: none
ownership_released: false
owned_paths:
  - deploy/otbm-atlas-smb-transfer/**
  - .github/workflows/otbm-atlas-smb-transfer.yml
  - docs/agents/tasks/active/OTH-20260817-atlas-smb-promotion.md
---

# OTBM Atlas verified SMB promotion

## Goal

Reduce the remaining external desktop-corpus deployment boundary to one safe Windows command: validate the already-generated `build/full-map-atlas`, copy it over the already-verified Synology SMB share into isolated staging, fully verify the copied corpus over SMB, then promote only verified staging to `current`.

This is a bounded implementation subtask of `OTH-20260815-otbm-atlas-product-readiness`; it does not replace or duplicate that broader task.

## Boundaries

- live implementation base: `76da15d02598d38fb00852df866a14ce094c37b9`;
- existing generated desktop corpus must be reused; no full-world build on Synology;
- verified destination root: `\\Synology\docker\otheryn\atlas`;
- no SSH, SCP, Docker exec, rclone, Internet route, Cloudflare activation or public/object-storage upload;
- script does not collect or store SMB credentials;
- `current` replacement is fail-closed unless `-AllowReplaceCurrent` is explicitly supplied;
- `/MIR` is used only against a unique disposable `incoming-*` directory, never directly against `current` or `previous-*`;
- remote staging must pass the merged fresh-corpus publication gate before rename to `current`;
- previous current is preserved on deliberate replacement and rollback is attempted if promotion fails;
- no owner-funded Codex/OpenAI/paid AI quota is used.

## Implementation

- Windows-compatible PowerShell `publish.ps1`;
- local full publication gate before any SMB write;
- bounded `robocopy` retries and configurable worker count;
- unique `incoming-<timestamp>-<id>` staging;
- full remote publication gate against the copied UNC directory;
- same-share rename promotion;
- explicit replacement guard and previous-version preservation;
- local evidence package with both gate reports, robocopy log and promotion receipt;
- `-PlanOnly` mode with zero destination side effects;
- Linux GitHub-hosted syntax/plan/safety contract validation via PowerShell Core, with no Windows/macOS build runner.

## Acceptance

- [ ] PowerShell syntax validation PASS;
- [ ] PlanOnly creates no destination directory and reports fail-closed defaults;
- [ ] focused safety contract PASS;
- [ ] exact-head CI/Required applicable gates PASS;
- [ ] fresh diff audit has zero material findings;
- [ ] implementation merged to main;
- [ ] task archived and ownership released;
- [ ] broader product-readiness task continues to wait only on actual owner desktop execution and DSM UI/runtime browser evidence.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-17T10:35:00+02:00
head: 3f6ec0f85b227da6e99a4cecbd99ff101fb53e51
base: 76da15d02598d38fb00852df866a14ce094c37b9
status: in_progress
phase: exact-head-validation
proven:
  - Synology SMB destination was previously verified as \\Synology\docker\otheryn\atlas\current
  - no reusable full Atlas corpus exists on Synology
  - the merged publication gate verifies the real corpus directly and remains fail-closed
  - no duplicate open Atlas SMB transfer PR existed at admission
blockers:
  - actual 10+ GB transfer cannot be executed from the GitHub connector because the source corpus is on the owner's Windows desktop
next_action: open the bounded implementation PR, run focused syntax/plan/safety validation and applicable repository gates, audit and merge if green, then give the owner the single execution command for the physical transfer
```
