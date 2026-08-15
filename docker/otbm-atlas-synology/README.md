# OTBM Atlas — private Synology browser preview

This project serves an already-generated OTBM Atlas as static files from Synology Container Manager. It does not build the Atlas on the NAS and it does not bake the multi-gigabyte Atlas corpus into the container image.

## Deployment contract

- Container image: `ghcr.io/nginx/nginx-unprivileged:1.30.4-alpine3.24-slim` pinned by digest in `docker-compose.yml`.
- Container HTTP port: `8080`.
- Generated Atlas mount: `/usr/share/nginx/html`, read-only.
- Container root filesystem: read-only.
- Linux capabilities: all dropped.
- `no-new-privileges`: enabled.
- Restart policy: `unless-stopped`.
- Deterministic health endpoint: `GET /__health` -> `200 ok`.
- No database, renderer, OTBM source, Tibia source assets, Docker socket or privileged mode is required at runtime.
- Atlas is bound to host loopback by default so DSM Reverse Proxy, rather than a new LAN/public listener, is the intended browser entry point.

## Recommended values — not verified existing NAS state

Repository history already uses `/volume1/docker/oteryn/...` for another Synology operational path. The Atlas paths below follow that convention, but this document does **not** claim that either directory currently exists on the NAS.

```text
RECOMMENDED_PROJECT_PATH=/volume1/docker/oteryn/atlas-project
RECOMMENDED_ATLAS_DATA_PATH=/volume1/docker/oteryn/atlas/current
RECOMMENDED_HOST_PORT=18088
```

`18088` avoids the repository quickstart's existing `8080` and `8088` host-port conventions. It is still **UNVERIFIED on the NAS** until DSM confirms that the port is unused. If the NAS uses another volume or the port is occupied, copy `.env.example` to `.env` in the project directory and change only `ATLAS_DATA_DIR` and/or `ATLAS_HTTP_PORT`.

## 1. Verify the desktop corpus before transfer

From a repository checkout that can see the generated Atlas directory, run the read-only preflight. It does not build or modify the Atlas:

```text
python -m tools.otbm_atlas.preview_corpus_check build/full-map-atlas --require-browser-core --require-environment
```

For the canonical current-v3 corpus the default preflight requires:

- Atlas schema/version 3;
- canonical map SHA-256;
- 3,494 manifest chunks across Z0..Z15;
- every detailed, overview and low-overview manifest path;
- every corresponding manifest checksum;
- final viewer files;
- factual/search/spatial browser data;
- NPC and monster static sprite indexes/assets;
- referenced creature-animation manifests/frames;
- `data/environment-animations/index.json`, its shard count and all referenced environment-animation assets.

A report with `browserCoreReady: true` but `environmentAnimations.ready: false` is useful only as an explicitly partial preview. It does **not** satisfy full browser E2E acceptance. The environment-animation dependency remains tracked by `docs/agents/tasks/active/OTH-20260815-atlas-environment-animation-export-performance.md`.

`--skip-checksums` exists only for a faster diagnostic pass. Do not use a skipped-checksum run as final transfer evidence.

## 2. Copy files to Synology without SSH

Use DSM File Station, SMB or Synology Drive. Do not use SSH, SCP, an SSH tunnel or `docker exec`.

1. Create or choose the project directory corresponding to `RECOMMENDED_PROJECT_PATH`.
2. Put `docker-compose.yml` and `nginx.conf` from this directory into that project directory. Add `.env` only if overriding the recommended data path or host port.
3. Create or choose the persistent Atlas data directory corresponding to `RECOMMENDED_ATLAS_DATA_PATH`.
4. Copy the **contents of the exact preflight-verified generated Atlas directory** into the Atlas data directory so that `manifest.json` and `index.html` are directly below that directory.

Do not copy the source OTBM or Tibia asset input corpus merely to run the preview; the static server does not consume them.

## 3. Create the Container Manager project

DSM wording differs between Container Manager versions, so use the Project feature rather than relying on a version-specific screenshot or menu label.

Invariant configuration:

```text
Project name: otheryn-otbm-atlas
Working/project path: RECOMMENDED_PROJECT_PATH (or the owner-confirmed equivalent)
Compose source: docker-compose.yml in that path
Atlas source mount: ATLAS_DATA_DIR -> /usr/share/nginx/html (read-only)
Host port: 127.0.0.1:ATLAS_HTTP_PORT -> container 8080
Restart policy: unless-stopped
```

In Container Manager, create/import a **Project** from the project directory/Compose file, review the rendered Compose configuration, then build/create/start the project. No image build is expected; Container Manager only pulls the pinned server image and mounts the static Atlas directory.

After start, Container Manager must show the `otheryn-otbm-atlas` container running and healthy. Its logs should show normal nginx access/error output. If the project is not healthy, use the Container Manager UI/log viewer; NAS shell access is not part of this deployment contract.

## 4. DSM Reverse Proxy target

The owner chooses the private source hostname/HTTPS certificate and whether the URL is local-only. Do not create public DNS, Cloudflare exposure or an Internet-facing port for this preview.

The destination side of the DSM Reverse Proxy rule is:

```text
protocol: HTTP
host: 127.0.0.1
port: 18088                 # or the owner-confirmed ATLAS_HTTP_PORT override
path: /
```

Depending on DSM generation, Reverse Proxy is under Control Panel's login/application portal advanced settings. Use the DSM Reverse Proxy UI and the destination values above; do not add nginx/Traefik/Caddy as a second external proxy layer.

## 5. Runtime acceptance boundary

A healthy container or a successful `curl` is not product completion. After the DSM rule exists, validation must use real Chromium against the same private URL the owner opens and must record the browser/E2E and performance evidence required by the active OTBM Atlas product-readiness task.

The PNG -> lossless-WebP migration remains unauthorized until the separate owner decision gate. This static server intentionally supports both MIME types without changing the canonical Atlas manifest or image format.
