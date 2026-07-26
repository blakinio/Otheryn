# Otheryn Production Deployment Boundary

Status: **architecture placeholder; not a runnable production stack**

The local quickstart under `docker/` is intentionally separate. Production deployment files belong under this directory only after the corresponding bounded `PRS-*` package proves them.

Required reads:

- `docs/architecture/production-resilience-and-recovery.md`
- `docs/operations/backup-and-pitr-policy.md`
- `docs/operations/production-recovery-runbook.md`
- `docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md`

## Intended future layout

```text
deploy/production/
  README.md
  compose.yml                         # PRS-008, not created yet
  compose.override.example.yml        # site-specific non-secret example
  env.example                         # names only, no credentials
  mariadb/
    99-resilience.cnf.example         # design input, not auto-mounted
  backup/
    backup.sh                         # PRS-001
    prepare-and-verify.sh             # PRS-001
    restore-pitr.sh                   # PRS-001
  monitoring/
    alerts.yml                        # package-owned alerts
  runbooks/
    site-specific.md                  # operator endpoints and contacts
```

## Production rules

- pin every image to an immutable digest or exact approved release;
- do not use rolling `latest` tags;
- do not commit passwords, tokens, private keys or production endpoints;
- do not publish MariaDB or Redis ports publicly;
- use explicit persistent volume ownership;
- mount map/datapack inputs read-only;
- keep database backup credentials separate from runtime credentials;
- treat `restart: unless-stopped` as process availability only;
- use health checks for readiness, not as proof of data integrity;
- require controlled `SIGTERM` shutdown and measured stop grace periods;
- require off-host backups before claiming disaster recovery;
- validate production files against the exact Docker Compose and MariaDB versions selected by the package;
- do not replace or broaden `docker/docker-compose.yml` while implementing production deployment.

## Package ownership

- `PRS-001` may add backup, prepare, verification and PITR files.
- `PRS-007` may add replica/manual-failover configuration after fencing is proven.
- `PRS-008` may add the production Compose stack and hardening.
- Gameplay or OAM feature packages must not opportunistically add production deployment behavior.

## Entry gate for new files

A future file may be added here only when its task record states:

- exact target and tool/image versions;
- owned paths;
- runtime/deployment responsibility;
- secret handling;
- failure injection;
- rollback/removal procedure;
- exact validation command or controlled drill;
- explicit nonclaims.

The example MariaDB option file in this directory is design input only. It is not loaded by the current quickstart or by any production service.
