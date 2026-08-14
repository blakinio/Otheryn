# OTBM Atlas environment animation

The atlas treats cyclic appearance animation and server-driven object state as separate systems.

Cyclic animations such as flames, lamps and other objects with multiple sprite phases come only from the pinned Tibia object appearances. The generator preserves the declared phase duration ranges, synchronization metadata, default phase and loop metadata. For deterministic atlas output, variable duration ranges use their midpoint in the browser schedule; source min/max values remain in the generated record.

The browser animates environment objects only at close zoom (`>= 1.5`) and only for chunks intersecting the viewport. Painting is capped and suspended while the document is hidden. No GIF is generated per map occurrence; frame PNGs are deduplicated by appearance/pattern while occurrences use small chunked JSON records.

Promotion is deliberately conservative: the object must be the topmost visible item on its tile, every selected phase/layer must be exactly 32x32, and the appearance must have no displacement or height offset. A per-occurrence underlay is rendered with that exact top item omitted, so switching away from the static default phase does not leave a ghost frame. Larger, displaced or occluded cyclic appearances remain deterministic static pixels until a future dynamic stack renderer can preserve cross-tile occlusion exactly.

State changes such as open/closed doors, switches, on/off variants, quest state and other server-controlled transitions are not inferred from cyclic animation metadata. They stay at the canonical OTBM state unless a separate factual runtime/evidence layer explicitly models a state transition.

Generated files live under `data/environment-animations/`: deduplicated phase images, underlays, viewport chunk shards and `index.json` with policy and statistics.
