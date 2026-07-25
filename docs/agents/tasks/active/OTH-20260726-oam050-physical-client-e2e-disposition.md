---
task_id: OTH-20260726-oam050-physical-client-e2e-disposition
coordination_id: OAM-050
status: implementing
branch: dudantas/oam-050-physical-client-e2e-disposition
base_branch: main
created: 2026-07-26
updated: 2026-07-26
last_verified_commit: "a9b69bb2ea3b12d2574d8c46c9e4889dd6dcecca"
related_issue: ""
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260726-oam050-physical-client-e2e-disposition.md
  - docs/oam-050-physical-client-e2e-disposition.md
---

# OAM-050 Physical-Client E2E disposition

Final disposition: `physical-client-e2e → DO_NOT_MIGRATE`.

Universal Physical-Client E2E remains the canonical Canary-hosted validation platform. Otheryn consumes exact-revision validation results and does not duplicate the runner, workflow, controlled-client harness, disposable database lifecycle, evidence schemas or cleanup orchestration.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T00:28:00+02:00
head: a9b69bb2ea3b12d2574d8c46c9e4889dd6dcecca
branch: dudantas/oam-050-physical-client-e2e-disposition
pr: null
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - universal-e2e
  - github-actions
owned_paths:
  - docs/agents/tasks/active/OTH-20260726-oam050-physical-client-e2e-disposition.md
  - docs/oam-050-physical-client-e2e-disposition.md
proven:
  - Canary OAM-050 preflight PR 944 merged as 515af061dda97173cb5ac6cc7885b7cdc3c4504f after exact-head Ownership 30176758049 and full CI 30176758136 passed.
  - Otheryn task-start main is 877816a64e31c6d25815ebf6b7543e001648ca52 and no open Otheryn PR owns OAM-050 or physical-client-e2e disposition paths.
  - Canonical physical-client-e2e is platform-tooling whose implementation roots are Canary tools/e2e and tests/e2e; production deployment and duplicate module-specific orchestration are excluded.
  - Universal Agent E2E already accepts blakinio/Otheryn as a controlled server repository with an exact 40-character server_ref.
  - Otheryn therefore needs no target-side adapter, runner, workflow, client harness, evidence schema or database orchestration copy.
  - Canary PR 925 retained nine complete clean login/relog attempts and one failed tenth attempt without a retained result/cleanup artifact; the retention gap is separately owned by the E2E programme.
  - Current comparison heads are opentibiabr/canary@7644bcbcbbad4a09e52a5707ed531e4dd21d8a79 and blakinio/otclient@85bfac8825607a73b475f1267cb3a798da1e717d.
derived:
  - DO_NOT_MIGRATE preserves one canonical validation lifecycle while allowing exact Otheryn revisions to be validated externally.
  - The PR 925 retention defect requires a separate Canary E2E repair task but does not establish a target runtime requirement.
unknown:
  - Complete stability and compatibility outside exact executed scenario/server/client/datapack cells remain unproven.
  - Future feature packages may require new feature-owned scenarios or assertions, but not a duplicate orchestrator.
conflicts: []
first_failure:
  marker: no-target-runtime-responsibility
  evidence: The package validates target revisions externally and has no Otheryn production owner, startup root or runtime consumer.
rejected_hypotheses:
  - Copy the Universal Physical-Client E2E platform into Otheryn.
  - Add an Otheryn-side workflow or adapter solely to invoke the canonical platform.
  - Treat nine retained successes as complete stability proof or hide the failed tenth attempt.
  - Block target disposition on the separately governed failure-retention repair.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-oam050-physical-client-e2e-disposition.md
  - docs/oam-050-physical-client-e2e-disposition.md
validation:
  - command: target root, runtime consumer and dependency review
    result: PASS
    evidence: No target runtime/build/startup consumer requires the platform; protocol and persistence remain separate target responsibilities.
  - command: canonical invocation contract review
    result: PASS
    evidence: Canary Universal Agent E2E accepts blakinio/Otheryn plus an exact server_ref.
  - command: PR 925 evidence ownership reconciliation
    result: PASS
    evidence: Baseline evidence and its retention gap remain separately owned and are not modified by this task.
blockers:
  - exact-head Otheryn Required gate
  - clean discussion and target-main drift audit
next_action: Open the target disposition PR, require exact-head Required, audit discussions and target-main drift, then squash-merge and archive the task before Canary governance reconciliation.
```