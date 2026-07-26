# Otheryn Production Deployment Boundary

Status: **non-runnable production boundary with disposable PRS-001 validation tooling**

The local quickstart under `docker/` is intentionally separate. Production deployment files belong under this directory only after the corresponding bounded `PRS-*` package proves them.

Required reads:

- `docs/architecture/production-resilience-and-recovery.md`
- `docs/operations/backup-and-pitr-policy.md`
- `docs/operations/production-recovery-runbook.md`
- `docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md`

## Current layout

```text
deploy/production/
  README.md
  mariadb/
    99-resilience.cnf.example         # design input; not auto-mounted
  backup/
    README.md                          # PRS-001 boundaries and operator gate
    versions.env                      # exact disposable MariaDB pin
    take-full-backup.sh               # physical full-backup step
    publish-recovery-set.sh            # encrypted atomic publication
    verify-recovery-set.sh             # checksum/decryption verification
    restore-pitr.sh                    # isolated prepare/restore/PITR step
```

The `backup/` files are executable only when an operator or CI supplies explicit disposable resources. They do not define a scheduler, production database endpoint, object-store account, credential, retention service or automatic restore path.

## Intended future layout

```text
deploy/production/
  compose.yml                         # PRS-008, not created yet
  compose.override.example.yml        # site-specific non-secret example
  env.example                         # names only, no credentials
  monitoring/
    alerts.yml                        # package-owned alerts
  runbooks/
    site-specific.md                  # operator endpoints and contacts
```

## PRS-001 evidence boundary

PRS-001 may prove the mechanics of:

- an exact MariaDB image and conservative durability options;
- a physical full backup with binlog coordinates;
- encrypted recovery-set publication to a filesystem boundary that models off-host storage;
- checksum verification, prepare, isolated startup and exact-time binlog replay;
- deterministic failure injection without deleting a previous known-good recovery set.

That disposable proof is not evidence that a real production backup exists. Production readiness still requires a separately configured off-host immutable/versioned store, protected credentials and keys, scheduling, monitoring, capacity measurements and repeated isolated drills with production-shaped data.

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

- `PRS-001` owns the bounded backup, verification and PITR proof. It does not own a production scheduler or deployment.
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

The MariaDB option example remains design input. It is not loaded by the local quickstart or by any production service.
