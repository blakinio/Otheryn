# OTBM Atlas environment-animation resume evidence

Status: implementation under exact-head validation.

The full-world environment-animation phase uses per-chunk spool fingerprints, atomic assets/shards/checkpoints, content-addressed underlay/overdraw deduplication, deterministic completed/total progress and resumable restart semantics. Existing schema-2 browser records remain the runtime contract. Focused validation covers clean export, interrupted finalization, identical restart reuse, stale-spool invalidation and deterministic clean rebuild.

Fresh audit found two restart-integrity edge cases and both are now remediated:

- animated-to-static chunk invalidation could leave a stale shard and unreferenced payload files; head `2f24b1f492754c533ba975ec4db776cef8ec498a` removes stale shards, tracks all live payload references and garbage-collects only unreachable frame/underlay/overdraw files after the complete pass;
- checkpoint reuse previously proved referenced paths existed but did not prove their bytes remained intact. Head `4d8ef26ce24fbc50fc649d4b2b124a2491f9953c` advances the exporter contract version, records SHA-256 for each referenced asset and shard, rejects any byte mismatch, atomically repairs corrupted payloads during rebuild, and adds corruption regressions for both a frame and a shard.

This repository-authored evidence commit intentionally starts a fresh exact-head CI/E2E generation after the bot-authored remediation. It does not claim the canonical full-world export complete. Final acceptance still requires green exact-head gates plus a bounded canonical run on the persisted Synology Atlas spool, followed by deployed Chromium validation.
