# OTBM atlas validation gates

`OTBM Atlas Tests` is the repository-owned validation workflow for changes under `tools/otbm_atlas/`.

Every matching pull request runs:

- the complete `tools/otbm_atlas/tests` unit/runtime suite;
- a real canonical Thais scan against the pinned `world.otbm` fingerprint;
- a real canonical Thais sprite render from the pinned Tibia 15.25 assets.

The expensive full-world validation is additionally enabled when the pull request has the `ci:final-gate` label. That job rebuilds atlas schema/cache version 3 from the canonical map with four workers, requires 3,494 populated chunks across raw Z 0..15, and runs `tools.otbm_atlas.verify` over the generated detailed/overview PNG sets and factual reports. It prints compact statistics rather than uploading the multi-gigabyte rendered atlas.

After any change that affects detailed-render semantics or atlas cache version, previous full-world PNG/checksum evidence is historical only; a fresh full-world gate is required before closeout.
