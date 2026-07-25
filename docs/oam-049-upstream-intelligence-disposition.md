# OAM-049 Upstream Intelligence disposition

## Final disposition

```text
upstream-intelligence → DO_NOT_MIGRATE
```

Upstream Intelligence remains an active, useful capability in `blakinio/canary`. It watches selected upstream and donor repositories read-only, inventories bounded changes, maps source-policy-eligible paths to canonical modules and publishes candidates for reviewed triage. This disposition does not disable, remove or weaken that monitoring.

Otheryn is the production server target. It must not duplicate Canary's GitHub scanner, source registry, path mapper, report-issue publisher, scheduled workflow or reviewed-decision store. Otheryn may receive a specific correction only after the external signal is re-fetched, reviewed against current local behavior, pinned to an exact revision and delivered through a separate bounded task with normal tests and merge gates.

## Proven boundary

- The canonical package is platform tooling with no dependency and no Otheryn implementation root, startup hook, build root or runtime consumer.
- Watched repositories remain read-only; no automatic cherry-pick, implementation branch, gameplay/protocol conclusion or semantic-equivalence claim is authorized.
- The only automated write belongs to the stable report issue in `blakinio/canary`.
- Candidate signals can raise review priority but cannot establish that Otheryn is wrong, incomplete or behind.
- Operational verification of the next production scan and report issue remains the separate Canary UI-002 responsibility.

## Target effect

This package adds no Otheryn runtime, workflow, source registry, scanner, mapper, report issue, data schema, test harness or deployment path. `DO_NOT_MIGRATE` means the governance system stays where it is useful—Canary—while reviewed fixes may still flow into Otheryn through normal package work.

## Nonclaims

This disposition does not claim that every upstream change is detected, that candidates are correct, that exact ancestry proves semantic equivalence, that donor behavior is official Tibia behavior, or that the scheduled production scan has completed UI-002 operational verification.
