# DYN-ATLAS-001 — Semantic Thais Z7 Proof worker prompt

ROLE
You are the implementation worker for the first bounded proof of the Oteryn Dynamic Semantic Atlas.

REPOSITORY AND LIVE STATE
Repository: `blakinio/Otheryn`.
Before mutation, read the current root/nested `AGENTS.md` hierarchy and verify live `main`, active task/ownership, related PRs, required checks and the currently running raster Atlas work.

REQUIRED PROJECT READS
- `docs/architecture/oteryn-dynamic-semantic-atlas.md`
- `docs/maps/oteryn-dynamic-semantic-atlas-program.md`
- `docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md`
- `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md`

OBJECTIVE
Implement one non-production vertical proof that discovers a real canonical Thais Z7 bounding box, exports that area as a versioned deterministic semantic package, publishes only the required deduplicated appearance/sprite subset, renders it in a minimal WebGL2 viewer beside the canonical raster oracle, and records parity plus network/decode/runtime evidence.

AUTHORIZATION AND SAFETY BOUNDARIES
- Use a dedicated task, branch and PR.
- Do not modify or interrupt the current production raster run or Synology `current` deployment.
- Do not remove or replace raster Atlas support.
- Do not enable a public route or redistribute the full proprietary generated corpus through GitHub artifacts/object storage.
- Do not invoke owner-funded AI services.
- Do not execute arbitrary legacy Lua/server scripts in the browser.
- Do not add live Game Server mutation, economy, inventory, quest persistence or production protocol changes.
- Treat OTBM/legacy content interpretation as producer-side migration logic; do not establish it as the long-term browser contract.

FEATURE SCOPE
```yaml
feature_scope:
  type: full_stack
  user_facing: true
  backend_required: true
  frontend_required: true
  integration_required: true
  e2e_required: true
  completion_claim: complete_feature
policy_version: 2
prompting_standard_version: 2.1
task_kind: implementation
decomposition_decision: phased
run_scope: single_task
continuation_policy: stop_at_task_boundary
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
```

ACCEPTANCE INVENTORY
1. Discover the exact PoC bounding box and sample entities/interactions from canonical data; do not guess coordinates.
2. Define semantic schema `v1` with world revision, capabilities, producer identity and deterministic content-addressed chunk identity.
3. Keep the current 128-tile grid for this proof unless measured evidence requires a separate architecture decision.
4. Export canonical ground, ordered stack/content references, supported attributes and navigation facts for the selected area.
5. Generate a deduplicated immutable appearance/sprite subset with explicit manifest identity.
6. Re-running the producer on identical input produces byte-identical semantic/package identities.
7. WebGL2 renders the same static world positions and canonical visual ordering as the raster oracle under the approved reference parity method.
8. The browser loads only visible chunks plus a bounded prefetch/cache set; rapid pan/floor/deep-link changes do not cause unbounded requests or stale-state corruption.
9. A semantic Tile Inspector reads X/Y/Z, ground/stack IDs and supported attributes directly from loaded semantic data, never from pixels.
10. Unknown schema/capability, malformed/truncated data and world/appearance revision mismatch fail closed.
11. Record same-journey A/B evidence: cold/warm bytes, request count, first-map timing, chunk decode P50/P95, texture upload, frame timing and memory/cache observations.
12. Keep the production raster viewer/deployment unchanged.
13. Fresh independent audit has zero open material findings, real browser E2E passes, and required exact-head CI is green before merge/closeout.

EXECUTION
1. Verify live state, governance, ownership and overlapping Atlas work.
2. Create the durable task/checkpoint and discover the canonical PoC area.
3. Implement the smallest producer/consumer contract and deterministic validator.
4. Implement the bounded WebGL2 consumer and raster comparison mode.
5. Add focused producer/consumer/negative tests, then component integration validation.
6. Verify the real resulting semantic package and browser behavior rather than relying on worker summaries.
7. Run fresh audit, remediate material findings, run real browser E2E and final exact-head CI.
8. Reconcile all related/superseded PRs, archive/close the task and release ownership according to repository governance.

STOP CONDITIONS
Stop only for a real architecture/authority/safety decision, unavailable required canonical input/environment, exhausted repair/execution budget, or successful terminal task closeout. If physical encoding cannot be selected from the bounded evidence without materially changing the architecture, persist the benchmark and raise that single decision rather than silently locking a format.

FINAL RESPONSE
Report exact branch, final SHA, PR, changed paths, deterministic/parity/performance evidence, audit/E2E/CI state, blockers and the single next action. Do not claim production migration or semantic-default status from this PoC alone.
