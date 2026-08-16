# OTBM Atlas environment-animation resume evidence

Status: implementation under exact-head validation.

The full-world environment-animation phase now uses per-chunk spool fingerprints, atomic assets/shards/checkpoints, content-addressed underlay/overdraw deduplication, deterministic completed/total progress and resumable restart semantics. Existing schema-2 browser records remain the runtime contract. Focused validation covers clean export, interrupted finalization, identical restart reuse, stale-spool invalidation and deterministic clean rebuild.

Fresh audit additionally found a per-chunk invalidation edge case: if an animated chunk became static, the prior shard and now-unreferenced payload files could survive. Head `2f24b1f492754c533ba975ec4db776cef8ec498a` removes the stale shard, tracks all live payload references across reused and rebuilt checkpoints, garbage-collects unreferenced frame/underlay/overdraw files only after the complete pass, and adds focused regression coverage for animated-to-static invalidation.

The bot-authored remediation generation produced GitHub `action_required` checks, so this repository-authored evidence commit intentionally starts a fresh exact-head CI/E2E generation without changing the implementation. This record does not claim the canonical full-world export complete. Final acceptance still requires exact-head CI plus a bounded canonical run on the persisted Synology Atlas spool, followed by deployed Chromium validation.
