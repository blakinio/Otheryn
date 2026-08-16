# OTBM Atlas private release/update pipeline

This is the canonical local/private release path for the browser Atlas. It satisfies the repeatability and rollback requirements without creating a public redistribution channel.

## Release invariant

A release is an immutable generated Atlas directory produced from one pinned map/assets fingerprint and one repository head. It is not promoted merely because generation completed.

Required sequence:

1. **Fingerprint/source gate** — record repository head plus `manifest.json` map/assets/version identity. A changed map or asset fingerprint creates a new release candidate; do not overwrite the active release.
2. **Build** — build/resume into a staging directory. Detail chunk cache and environment-animation checkpoints may be reused only under their validated fingerprints.
3. **Independent preflight** — run `python -m tools.otbm_atlas.deploy_preflight <staging> --require-environment-animations`. A nonzero exit cannot be promoted.
4. **Full-world certification when source identity changes** — preserve Z0..Z15 / chunk-count / missing-sprite evidence. Existing certification may be reused only when the exact certified source identity remains unchanged and no producer affecting the certified bytes changed.
5. **Preview/staging** — serve the candidate through the private Synology preview boundary before promotion.
6. **Real Chromium gates** — run both `deployed_browser_probe` and `product_acceptance_probe` against the exact staged URL. Any required failure blocks promotion.
7. **Immutable release copy** — copy the verified candidate into `/volume1/docker/otheryn/atlas/releases/<release-id>/`. Never mutate an already promoted release directory.
8. **Atomic pointer promotion** — use `python -m tools.otbm_atlas.release_pointer /atlas --promote <release-id>` in a helper container that mounts `/volume1/docker/otheryn/atlas` at `/atlas`. Recreate the static web container so Docker resolves the new `current` symlink target.
9. **Post-promotion smoke** — verify `/healthz`, `index.html`, `manifest.json`, deterministic 404, then repeat the critical deployed browser smoke against the owner URL.
10. **Rollback** — if the post-promotion smoke fails, run `python -m tools.otbm_atlas.release_pointer /atlas --rollback`, recreate the web container and verify the same URL. Do not delete the failed release until evidence has been retained.

## Browser/server boundaries

- Generated Atlas directories are mounted read-only.
- The nginx container root filesystem is read-only, runs unprivileged, drops all capabilities and uses `no-new-privileges`.
- Host serving remains loopback-only behind DSM Reverse Proxy for the private phase.
- No SSH tunnel is part of runtime or validation.
- Missing resources return 404 rather than the viewer shell.
- Logs remain available from Container Manager/Docker without changing the generated corpus.

## Versioned directory shape

```text
/volume1/docker/otheryn/atlas/
  releases/
    <release-id>/
      index.html
      manifest.json
      viewer-*.js
      data/
      tiles/
      overview/
      overview-low/
  current -> releases/<release-id>
  previous -> releases/<previous-release-id>
  project/
    docker-compose.yml
    nginx.conf
```

The `current` and `previous` links are runtime pointers only. The immutable release directories are the rollback source of truth.

## What does not trigger a full rerender

A viewer-only change may reuse certified detail PNG/overview bytes when `deploy_preflight` proves the same canonical manifest and the release procedure regenerates only affected derived viewer/data artifacts. A producer change that affects map rendering, chunk geometry, overview generation or source identity requires the corresponding certification gate before promotion.

## Public-release gate

This runbook is **private/local only**. `ATLAS-PR-009` remains `NOT_APPLICABLE_WITH_REASON` while the Atlas is not Internet-facing. Any future public release must add an explicit legal/licensing review and a separate public-delivery decision before exposure.
