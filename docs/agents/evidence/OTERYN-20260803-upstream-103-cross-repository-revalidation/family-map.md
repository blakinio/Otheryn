# Canonical duplicate and related-item families

Rows remain independent. Families share evidence but do not delete or merge canonical keys.

| Family | Canonical rows | Relationship | Audit treatment |
|---|---|---|---|
| Paralyzed spell casting | `opentibiabr/canary:issue:3986`, `opentibiabr/canary:pull_request:4058` | Issue and correcting PR for one alleged regression | one shared code comparison; two row conclusions |
| Expert/Open PvP | `opentibiabr/canary:pull_request:4033`, `zimbadev/crystalserver:issue:810`, `zimbadev/crystalserver:pull_request:813`, `zimbadev/crystalserver:pull_request:445` | three implementations/proposals for overlapping PvP modes, fields, marks and protocol behavior | compare architecture, protocol profiles and product scope; preserve supersession relationships |
| Multiworld | `opentibiabr/canary:pull_request:2826`, `zimbadev/crystalserver:pull_request:451` | Crystal donor port explicitly derived from Canary | one lineage family; independent target architecture conclusion per row |
| Dynamic map reload | `zimbadev/crystalserver:pull_request:785`, `zimbadev/crystalserver:issue:852` | proposed cache-clear correction and reproduction allegation | compare exact Otheryn map lifecycle and require bounded reproduction for crash claim |
| Summer Update 2026 | `zimbadev/crystalserver:issue:794`, `zimbadev/crystalserver:pull_request:805` | placeholder issue and under-construction content PR | product/content scope decision; no bulk migration |

## Additional thematic families

- build and dependency infrastructure: upstream Canary `#4052`, `#4055`;
- MyAAC/deployment: upstream Canary `#4048`;
- maintained-client/protocol contracts: upstream Canary `#4056`, `#4038`, `#4033`; CrystalServer `#812`, `#810`, `#826`;
- broad generated/bulk content: upstream Canary `#4029`, Issues `#618`, `#615`; CrystalServer `#805`;
- persistence architecture: CrystalServer `#545`, multiworld family;
- custom gameplay/product proposals: CrystalServer `#627`, `#742`;
- high-risk loss/crash/corruption corrections: CrystalServer `#851`, `#850`, `#849`, `#848`, `#122`, `#785/#852`.
