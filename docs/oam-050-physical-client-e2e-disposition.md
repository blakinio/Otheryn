# OAM-050 Physical-Client E2E disposition

## Final disposition

```text
physical-client-e2e → DO_NOT_MIGRATE
```

Universal Physical-Client E2E remains the canonical validation platform in `blakinio/canary`. It owns disposable database bootstrap, exact controlled server and maintained-client selection, physical OTClient automation, scenario execution, retained logs/screenshots/SQL/result evidence and cleanup. It is development and release-validation tooling, not Otheryn production-server runtime.

Otheryn must not duplicate the runner, workflow, scenario registry, controlled-client harness, disposable database lifecycle, evidence schemas or cleanup orchestration. The existing Canary workflow already accepts `blakinio/Otheryn` as a controlled server repository with an exact 40-character `server_ref`, so target revisions can be validated without adding an Otheryn-side adapter or invocation layer.

## Proven boundary

- Canary OAM-050 preflight PR #944 merged as `515af061dda97173cb5ac6cc7885b7cdc3c4504f` after exact-head Ownership run `30176758049` and full CI run `30176758136` passed.
- The canonical registry classifies `physical-client-e2e` as `platform-tooling`; its implementation paths are `tools/e2e/**` and `tests/e2e/**`, while production deployment and module-specific duplicate orchestration are explicitly excluded.
- Universal E2E feature tasks own scenario definitions and assertions; generic lifecycle or orchestration changes remain separately governed Canary platform tasks.
- Canary draft PR #925 owns the first login/relog repeated-run baseline evidence. It retained nine clean complete attempts; the tenth failed without a retained result envelope or cleanup certification, proving a separate failure-retention gap rather than a target migration requirement.
- Current target baseline is `blakinio/Otheryn@877816a64e31c6d25815ebf6b7543e001648ca52`; current upstream comparison head is `opentibiabr/canary@7644bcbcbbad4a09e52a5707ed531e4dd21d8a79`; current maintained-client head is `blakinio/otclient@85bfac8825607a73b475f1267cb3a798da1e717d`.

## Target effect

This package adds no Otheryn runtime, build entry, startup hook, workflow, test runner, client automation, scenario registry, evidence schema, database fixture system or deployment component. Future Otheryn feature packages may request bounded physical-client validation by invoking the canonical Canary workflow against an exact target SHA and by supplying feature-owned scenarios/assertions through separately governed work when needed.

## Dependency impact

Protocol and player-persistence remain target responsibilities already handled through their own OAM packages. Physical E2E consumes those target behaviors as evidence inputs; it does not own them. No unresolved Otheryn runtime consumer requires the orchestration platform to be copied into the target.

The failure/cancellation evidence-retention gap observed by PR #925 remains a Canary E2E-platform concern. It must be repaired in a separate bounded E2E task before repeating that ten-attempt stability baseline, but it does not block this target disposition.

## Nonclaims

This disposition does not claim complete gameplay coverage, general stability, compatibility with every client/server/datapack cell, successful retention of all failures, production deployment readiness, or that static/unit evidence can replace a real exact-revision physical-client run.