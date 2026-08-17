# OTBM Atlas — controlled user-distribution preparation

This package prepares the next hosting step without authorizing Internet exposure or public redistribution of the generated Atlas corpus.

The existing Synology package in `deploy/otbm-atlas-synology/` remains the canonical origin/runtime baseline. The generated Atlas remains deployment data and must not be committed, uploaded as a GitHub Actions artifact, placed on GitHub Pages, copied to object storage/CDN, or otherwise redistributed by this package.

## Publication modes

The fail-closed gate in `publication_gate.py` distinguishes three modes:

- `private-local` — private/local serving only; no ATLAS-PR-009 approval is required, but the corpus must be `FULL_RUNTIME_READY`;
- `internet-authenticated` — Internet-facing access restricted to authenticated users; ATLAS-PR-009 approval is mandatory;
- `internet-public` — unrestricted Internet-facing release; a separate exact-scope ATLAS-PR-009 approval is mandatory.

An approval for one Internet mode does not implicitly approve the other.

## Current state

Two independent boundaries remain before real users can receive Atlas access:

1. the already-generated desktop `build/full-map-atlas` corpus must be copied to the verified Synology target `\\Synology\docker\otheryn\atlas\current` and pass the full deployment preflight;
2. ATLAS-PR-009 must be explicitly reviewed and recorded before **any** Internet-facing mode is enabled, including an authenticated beta.

Do not bridge either boundary by rebuilding the world on Synology or by uploading the generated corpus to GitHub/R2/Pages/CDN storage.

## Gate the real verified corpus

The publication gate accepts the **generated Atlas directory**, not a previously written preflight JSON report. On every invocation it directly runs `tools.otbm_atlas.deploy_preflight.deployment_preflight()` with full chunk verification and required environment animations, then evaluates the resulting in-memory report. This prevents a hand-written/stale JSON report from being used as publication evidence.

The fresh preflight must prove:

- `FULL_RUNTIME_READY`;
- canonical Atlas v3 / 128-tile / 3494-chunk identity;
- canonical map SHA-256 and accepted source provenance through the existing deployment preflight;
- current viewer runtime;
- READY spatial data, Tile Inspector, creatures and environment animations;
- successful independent full chunk verification.

Private/local readiness can be checked directly against the corpus with:

```text
python deploy/otbm-atlas-controlled-beta/publication_gate.py \
  build/full-map-atlas \
  --mode private-local
```

Internet-facing modes deliberately fail without a separate approval JSON:

```text
python deploy/otbm-atlas-controlled-beta/publication_gate.py \
  build/full-map-atlas \
  --mode internet-authenticated \
  --approval path/to/reviewed-atlas-pr-009.json
```

`approval.template.json` is intentionally `approved: false`. It is a schema example, not an authorization record. Never change it to `true` merely to make CI or deployment pass.

## Controlled beta architecture after ATLAS-PR-009

The intended first Internet-facing topology is:

```text
approved tester browser
        |
        v
Cloudflare Access policy (deny by default)
        |
        v
Cloudflare Tunnel public hostname
        |
        v
Synology Atlas origin
        |
        v
read-only generated corpus
```

Cloudflare documents Access self-hosted applications as deny-by-default: a user must match an Allow policy before access is granted. Cloudflare Tunnel establishes outbound connections from the origin side, so this path does not require opening an inbound Internet port on the NAS.

Implementation rules for the later activation task:

- create and validate the Access application/policy before enabling the Atlas hostname for testers;
- allow only the explicitly selected identities/group during beta;
- keep the tunnel token in the owner secret store/environment, never in Git or task records;
- preserve the read-only/non-root Atlas origin contract;
- do not add Internet port forwarding to Synology;
- preserve the current origin `Cache-Control: private` policy during the authenticated beta;
- do not enable Cloudflare edge caching of Atlas imagery in this phase;
- do not move the generated corpus to R2, Pages or another public/object-storage origin in this phase;
- run `tools.otbm_atlas.deployed_browser_probe` against the exact tester URL after activation;
- record cold/warm/navigation measurements before making a cache/storage migration decision.

The no-edge-cache rule is intentional for the first authenticated beta. Cloudflare's cache documentation states that responses marked `Cache-Control: private` are not cached at the edge. This keeps the distribution semantics simple while user count is bounded and avoids introducing a second redistribution/storage decision before ATLAS-PR-009 and real browser evidence are complete.

## Public release is a later gate

A successful authenticated beta does **not** authorize `internet-public`. Public release requires an exact `internet-public` ATLAS-PR-009 approval plus a separate decision on public storage/CDN/cache policy.

The current repository boundary remains:

- GitHub Actions may generate bounded/ephemeral Atlas evidence;
- the full generated Atlas corpus is not a repository artifact;
- GitHub Pages is not the full-Atlas host;
- object-storage/CDN publication is not pre-authorized by this package.

## Rollback

The first controlled beta must remain reversible without rebuilding the Atlas:

1. disable/remove the Cloudflare hostname route or Access application;
2. leave the private Synology origin intact;
3. if needed, stop the Atlas Container Manager project;
4. restore/repoint the verified Synology data directory;
5. rerun the publication gate and browser probe before reactivation.

## External reference points

Current Cloudflare behavior used by this design should be re-verified at activation time because service behavior can change:

- Cloudflare One: Publish a self-hosted application to the Internet;
- Cloudflare Tunnel: setup/routing documentation;
- Cloudflare Cache: default cache behavior and Cache-Control documentation.
