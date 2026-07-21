# OAM-030 Bosstiary Adaptation

Final disposition: `bosstiary → ADAPT`.

Immutable target base: `68d48deea999990b1eab30858f3a85fc9fef7067`.
Legacy/governance task-start baseline: `419d0848448c641561e7bc06392a4b17b95213b2`.
Fresh upstream: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`.
Maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`.

Canonical `bosstiary` owns `src/io/io_bosstiary.*` and depends on completed `cyclopedia` and `player-persistence`. Task-start Otheryn and fresh upstream shared exact `io_bosstiary.cpp` blob `8e89ce79316e5c193e918661c50278f50d476c83`.

Merged legacy PR #188 contains one isolated Bosstiary production correction. The target/upstream implementation returned immediately when the `boosted_boss` query had no row, making its later `if (!result)` recovery branch unreachable. OAM-030 removes that early return and initializes the missing singleton row before selecting and persisting a new boosted boss.

Later legacy multichannel leader-election changes are deliberately not imported by this bounded donor. Bestiary, Charms, monster-data, protocol and maintained-client changes are also excluded.

Focused proof guards that exactly one missing-result branch remains, the stale early error path is absent, and the deterministic missing-row insert plus failure handling are present.

This package does not claim exhaustive Bosstiary parity, boosted-boss cluster-singleton correctness, boss slot persistence, point/loot arithmetic parity, schema migration correctness, packet compatibility, maintained-client rendering, physical-client Bosstiary E2E closure or full Real Tibia parity.
