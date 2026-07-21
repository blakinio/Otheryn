# OAM-029 Cyclopedia Character Adaptation

## Disposition

```text
cyclopedia-character ADAPT
```

## Immutable task-start inputs

- legacy/governance Canary: `ad267a87b3f565daf7e5901d80fbafb5a02b623c`
- Otheryn target: `1521906ffa8bd83ff2b35b0feadab4a44ea6df05`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `cyclopedia-character` depends only on completed `cyclopedia` and `player-persistence`. Its narrow server root is `src/creatures/players/components/player_cyclopedia.*`; shared Character-tab presentation does not transfer `titles` ownership.

## Accepted donor boundary

Task-start Otheryn and fresh upstream share `player_cyclopedia.cpp` blob `91a3235e53e5f7ca4da22649bff6bad34cf44e3a`. Merged legacy PR #188 contains exactly one Cyclopedia Character production hunk in `PlayerCyclopedia::loadRecentKills`.

The result query returns recent PvP kills only from the last 70 days, but its `count(*)` subquery historically counted all matching deaths. The resulting `entries` value can therefore advertise pages that contain no rows inside the 70-day presentation window. OAM-029 adds the same 70-day predicate to the count subquery so page count and page content use one window.

No Bestiary, Bosstiary, Charms, Titles, protocol, schema or maintained OTClient change is imported.

## Proof

The focused OAM-029 source-contract proof requires the recent-PvP query to contain the 70-day predicate twice: once in the count subquery and once in the outer result filter. Full target CI remains authoritative for compilation and regression safety.

## Explicit non-claims

OAM-029 does not claim full Cyclopedia Character parity, exact packet-byte compatibility, death-history correctness, KV/store-summary parity, database query performance, retained-history policy, maintained-client rendering, physical-client E2E closure, or full Real Tibia parity.
