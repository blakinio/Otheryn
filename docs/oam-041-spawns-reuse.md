# OAM-041 spawns reuse proof

## Disposition

`spawns → REUSE`

The clean Otheryn target already contains the bounded canonical spawn runtime required by OAM-041. Deterministic source, map-index, reachability and placement-correlation evidence did not isolate a concrete `spawns`-owned target defect requiring production, datapack or map repair.

This result is intentionally narrower than full gameplay parity. Static evidence does not prove live spawn timing under load, player-state behavior, dynamic Lua execution, raid lifecycle, exact Real Tibia placement parity or physical-client gameplay.

## Target and source contract

Target task-start `main` was `9369b0719ff94997a9cf5a2d62853939744e6338`.

The reviewed canonical runtime roots are:

- `src/creatures/monsters/spawns/spawn_monster.cpp`, blob `4c82217631ddf479faa5443025d43f99a0c927d1`;
- `src/creatures/npcs/spawns/spawn_npc.cpp`, blob `21718ad80827a16e9a1b29bc9d649ad603bcf216`.

The bounded semantic review confirms:

- monster and NPC spawn XML load/startup/clear lifecycle;
- center coordinates plus child `x`/`y` offsets with runtime `z = centerz`;
- monster default respawn fallback, rate/event/boost scaling and one-second-to-one-day clamping;
- NPC one-second-to-one-day interval validation;
- player-presence blocking for configured respawns;
- removed monster/NPC cleanup and respawn timestamp reset;
- maintenance-lane periodic checks and delayed non-blockable respawn scheduling;
- monster spawn-block boss exclusivity;
- weighted monster selection.

The older legacy Canary runtime is not used as a whole-module donor. The reviewed target runtime matches the fresh upstream roots recorded by Canary OAM-041 governance and retains `DispatcherLane::Maintenance` scheduling on the relevant periodic and delayed paths.

Raid registry scheduling, ordered raid-event execution and raid lifecycle remain owned by canonical `raids` and the completed OAM-037 proof. OAM-041 does not duplicate that ownership.

## Deterministic external OTBM evidence

OAM-040 established OTBM tooling as an external Canary evidence responsibility. OAM-041 therefore consumed the pinned toolchain without copying it into Otheryn.

Pinned Canary evidence revision:

`d1ad83056ec7930f067986909f66b8f20f1a1f44`

Pinned Phase 4 tool blobs:

- `otbm_spawn_npc.py`: `4339e94f5875f4d7fd443c2359c15d10f205004f`;
- `otbm_spawn_npc_validation.py`: `7f66f74b68b66e9acabe1ea1a5cbd404b1637e9b`;
- `otbm_spawn_npc_tool.py`: `481c163d8048298900b33648b08b1fac5b60fefe`.

Explicit target inputs:

- active datapack: `data-otservbr-global`;
- monster spawn XML: `world/otservbr-monster.xml`;
- NPC spawn XML: `world/otservbr-npc.xml`;
- configured map: `otservbr`, downloaded from the target-configured Canary v3.6.1 release URL;
- map SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- appearances SHA-256: `aa44a154f30c7ed59acc25f246286396e4043851ef0b54ef3cf3951e46d1ce50`.

The generated World Index remained outside Git. Its deterministic manifest recorded:

- index SHA-256: `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`;
- index size: `842280592` bytes;
- `17972761` tiles;
- `23359571` item placements;
- `9339` mechanic placements;
- `0` unknown attribute tails.

The exact successful proof workflow run was Otheryn Actions run `30049543113` on head `38bf8dcb4d401fa4053e350af052cc2e9c8da4bd`. The generated proof artifact digest was `sha256:24997761f2140054606abf116b277f7af0ddeceefa7a59fcffb434ea31375be8`.

Artifact SHA-256 provenance:

- source evidence: `edb27ac204a2924fc5009310cad25eb10538c281036676d59817f43e77007ef4`;
- reachability report: `1c8237545f42d7974623baebb733f982e8b3611ab09e0ef1e1fa2b8b1f841b3f`;
- spawn/NPC validation: `6845eee1322706cdbd1bea542067d567198a54ef00108c5e462cde2afa02965d`;
- World Index manifest: `efc33fc73c23a6c884135619e88d3fc45d5db99a8afb2b223e560f7d3a261e72`.

Generated `.widx` and JSON reports were workflow artifacts only and are not committed.

## Full active-datapack source scan

The exact current Otheryn active-datapack scan produced:

- `2692` definition files and `2688` resolved definitions;
- `52903` spawn groups;
- `84294` static placements: `83286` monsters and `1008` NPCs;
- `1769` dynamic-source files;
- `461` dynamic creation calls: `151` literal and `310` unresolved;
- `318` findings: `2` errors and `316` warnings;
- no truncation.

The two errors are one pre-existing ambiguous NPC-definition condition, not a newly isolated target runtime defect: canonical `harlow` is defined by both `npc/harlow.lua` and `npc/harlow_trade.lua`, making the static `Harlow` placement at `32836,31364,7` ambiguous. OAM-041 does not guess which definition should win and does not delete or rewrite either source.

The `310` non-literal dynamic creation calls remain explicitly unresolved. Dynamic Lua was not executed and unresolved calls were not promoted to handled.

## Bounded map and reachability correlation

The final complete proof region was:

- from `32824,31275,7`;
- to `32873,31324,7`;
- origin `32849,31300,7`.

Reachability diagnostics were complete and untruncated:

- `0` error-severity findings;
- `0` warning-severity findings;
- `1115` informational tile diagnostics;
- `829` strictly reachable tiles from the selected origin;
- `940` optimistically reachable tiles.

Spawn/NPC correlation produced:

- `34/34` selected spawn groups `confirmed`;
- `39/39` selected static placements `confirmed`;
- `0` validation findings;
- no `reachability_diagnostics_truncated` failure;
- `310` globally unpositioned dynamic calls retained as `unresolved` rather than guessed.

An earlier deliberately fail-closed run used an over-broad 16-floor region and correctly produced `reachability_diagnostics_truncated`. That result was rejected as incomplete evidence. A second attempt exposed the reachability tool's default diagnostic sample limit of `200`; the final run raised the bound to `10000` and required non-truncated diagnostics before accepting the correlation.

## Conclusion and boundaries

The evidence supports `spawns → REUSE` without production mutation. The target runtime already preserves the bounded canonical spawn lifecycle, the explicit active global source inventory is deterministically scanned, and the completed bounded map/reachability correlation confirms every selected group and placement.

No OTBM binary, generated World Index, generated report, map asset, runtime source, datapack source, protocol, client, schema or deployment path is changed by this package.

OAM-041 does not claim:

- execution or correctness of unresolved dynamic Lua creation calls;
- exhaustive validation of every one of the `84294` static placements against live gameplay;
- exact Real Tibia spawn population, timing or placement parity;
- scheduler fairness or timing under production load;
- raid lifecycle correctness beyond consuming already-separated raid placement evidence;
- physical-client spawn/NPC gameplay E2E closure.
