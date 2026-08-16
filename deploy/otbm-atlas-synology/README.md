# OTBM Atlas — private Synology browser preview

This package serves an already-generated OTBM Atlas as read-only static data from Synology Container Manager. It does not build the Atlas on the NAS and it does not integrate with Oteryn Platform.

## Architecture

```text
desktop generated Atlas
        |
        | File Station / SMB / Synology Drive
        v
Synology persistent folder
        |
        | read-only bind mount
        v
unprivileged nginx container :8080
        |
        | host loopback TCP 8095
        v
DSM Reverse Proxy
        |
        v
normal browser
```

The generated Atlas is deployment data. It is deliberately not baked into a multi-gigabyte image.

## Repository baseline

The canonical Atlas contract is schema/Atlas version 3 with a 128-tile chunk size. The certified world contains 3494 detail chunks across Z0..Z15 and uses map SHA-256 `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`.

Accepted asset provenance is either:

- canonical Git bytes: `4c78aa441bc6eed6a614092423a58dc6275cf2c36ea5d4bde13746c9b4ee7ee7`;
- the previously validated Windows worktree representation: `4d11c5be0438c8fa08d079a558fe99f5f28d3db5df0aa742c5a46d4260c905c2`, whose only byte delta was CRLF materialization of one non-render input.

The repository already allocates ports 7171–7175, 8080, 8088 and 9090 in the existing Docker quickstart. No repository service currently allocates 8095. **This does not prove that port 8095 is free on the live NAS.**

## Container contract

The project uses the official nginx unprivileged image pinned by both version and digest:

```text
ghcr.io/nginx/nginx-unprivileged:1.31.3-alpine3.24-slim@sha256:22f839c5fb4007dc24d203a170a9e03fc185d660bfefc34ac6823a7aef085cbc
```

The image is multi-platform, so this project does not guess the Synology CPU architecture. The service:

- runs as the image's non-root user;
- drops all Linux capabilities;
- enables `no-new-privileges`;
- uses a read-only container root filesystem;
- mounts generated Atlas data read-only;
- binds the host port to `127.0.0.1` by default;
- uses `restart: unless-stopped`;
- exposes `/healthz` and a Docker health check;
- writes access/error output to container logs;
- does not use privileged mode or the Docker socket;
- has no database, renderer, OTBM source or Tibia asset dependency at runtime.

## Recommended Synology paths

These are recommendations, not claims about the existing NAS:

```text
RECOMMENDED_PATH project: /volume1/docker/otheryn/atlas/project
RECOMMENDED_PATH data:    /volume1/docker/otheryn/atlas/current
VERIFIED_EXISTING_PATH:   UNKNOWN
```

If the NAS uses a different Synology volume, keep the same logical layout on that volume or set `ATLAS_DATA_DIR` to the real folder.

The default project variables are embedded in `compose.yaml`. `.env.example` documents the values and can be copied to `.env` in the project directory only when an override is needed.

## Recommended host port

```text
RECOMMENDED_HOST_PORT: 8095
RECOMMENDED_BIND: 127.0.0.1
VERIFIED_LIVE_NAS_AVAILABILITY: UNKNOWN until Container Manager binds it
```

If DSM reports 8095 already in use, choose another unused high TCP port and use that same value in the DSM reverse-proxy destination.

## Desktop corpus preflight

Do not rebuild the world merely to deploy it. Against the existing generated output, run:

```text
python -m tools.otbm_atlas.verify build/full-map-atlas --output build/full-map-atlas/verification-deploy.json
python -m tools.otbm_atlas.deploy_preflight build/full-map-atlas --output build/full-map-atlas/deployment-preflight.json
```

For the final full-runtime gate, use:

```text
python -m tools.otbm_atlas.deploy_preflight build/full-map-atlas --require-environment-animations
```

Possible deployment-preflight states are:

- `FULL_RUNTIME_READY` — canonical core corpus plus the final environment-animation index are present;
- `CORE_PREVIEW_READY` — the static Atlas core is valid, but the final environment-animation artifact is absent or incomplete; the preview can be useful but ATLAS-PR-003 must remain partial;
- `NOT_READY` — required viewer/corpus integrity or identity checks failed; do not deploy this directory as the canonical preview.

A missing `data/environment-animations/index.json` is not silently accepted as complete. Do not launch another unbounded environment-animation export merely to satisfy deployment.

## Copy the generated Atlas without SSH

Copy the **contents** of the verified generated Atlas directory into the chosen Synology data folder, for example:

```text
/volume1/docker/otheryn/atlas/current/
  index.html
  viewer-app.js
  viewer-runtime.js
  creature-animation-runtime.js
  manifest.json
  tiles/
  overview/
  overview-low/
  data/
```

Use one of the owner's normal non-SSH mechanisms:

- DSM File Station;
- an SMB/network share;
- Synology Drive.

Do not use `scp`, SSH, `docker exec`, or rsync-over-SSH for this preview.

## Create the Container Manager project

Place these project files in one Synology folder, recommended:

```text
/volume1/docker/otheryn/atlas/project/compose.yaml
/volume1/docker/otheryn/atlas/project/nginx.conf
```

Then in DSM Container Manager create a **Project** using that directory and `compose.yaml`. DSM versions differ slightly in labels, so preserve these invariant values rather than guessing a screen label:

```text
project name: otheryn-atlas-preview
compose/project file: deploy/otbm-atlas-synology/compose.yaml
nginx config: deploy/otbm-atlas-synology/nginx.conf in the same project directory
data mount source: /volume1/docker/otheryn/atlas/current (or the verified real data folder)
data mount target: /usr/share/nginx/html
data mount mode: read-only
host bind: 127.0.0.1
host port: 8095 (or the chosen conflict-free replacement)
container port: 8080
restart policy: unless-stopped
```

If a DSM import screen insists on the conventional Compose filename, copy `compose.yaml` as `docker-compose.yml`; do not change its contents.

Create/start the project and verify in Container Manager that the `atlas` service becomes healthy. Its logs must remain visible in Container Manager. No command shell inside the container is required.

## DSM Reverse Proxy destination

The reverse-proxy **destination** is deterministic once the host port is chosen:

```text
protocol: HTTP
host: 127.0.0.1
port: 8095
path: /
```

If the host port was changed because of a live NAS conflict, substitute the actual chosen port.

On DSM 7 the reverse-proxy editor is under Control Panel → Login Portal → Advanced → Reverse Proxy. The **source** hostname/port is an owner DSM choice. Keep it private/local for this phase: no public DNS, Cloudflare route, Internet port-forward, Oteryn Platform route, or new public exposure.

## HTTP contract

After the project is healthy through the chosen browser URL:

```text
/healthz -> HTTP 200, body: ok
/index.html -> Atlas viewer
/manifest.json -> generated Atlas manifest
```

The server uses standard MIME mappings, including:

```text
.html  text/html
.js    application/javascript
.css   text/css
.json  application/json
.png   image/png
.webp  image/webp
```

Missing resources return 404 rather than the viewer shell. Generated data is mounted read-only.

## Real deployed-browser validation

Repository fixture tests do not close ATLAS-PR-003 or ATLAS-PR-004. After DSM Reverse Proxy is active, use the **same private URL the owner opens**:

```text
python -m pip install --disable-pip-version-check playwright==1.54.0
python -m playwright install chromium
python -m tools.otbm_atlas.deployed_browser_probe https://PRIVATE_ATLAS_URL/
```

The probe records browser identity and durable evidence for initial load, deep links, pan, zoom, floors, coordinate jump, search/details, factual overlays, render modes, overview/detail transitions, creature rendering/animation, environment animation, reload/back/forward, 404 behavior, console/network failures, cold/warm resource measurements and navigation behavior.

The result is written beneath `build/atlas-browser-evidence/` by default. ATLAS-PR-003 and ATLAS-PR-004 remain unverified until this probe runs against the actual DSM URL and its evidence is reviewed.

## Rollback

Rollback does not require mutating a running container:

1. stop the Container Manager project;
2. restore or repoint the Synology Atlas data directory using File Station/SMB/Synology Drive;
3. start the same immutable project;
4. rerun the browser validation against the same DSM URL.

No NAS shell, container shell, database rollback, or Atlas render is required.
