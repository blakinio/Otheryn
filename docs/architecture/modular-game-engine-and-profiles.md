# Modular Game Engine and Historical Profiles

Status: **active architecture contract; implementation is not authorized by this document alone**

Tracking issue: `blakinio/Otheryn#120`

Task-start target:

```text
blakinio/Otheryn@4eedf835621e2a64d093dd5096b4b28e632e50f3
```

## 1. Purpose

This document defines the target architecture for evolving Otheryn into a modular game engine while preserving one efficient game-channel process.

The target is a **modular monolith per game channel**:

```text
one Otheryn channel process
  + explicit core-engine modules
  + explicit gameplay-feature modules
  + datapack-owned content packages
```

It is not a microservice-per-feature design. Wheel, Prey, Charms, Market, Quests or Houses do not receive separate containers merely because they are modules.

The architecture must also support future historical and custom game profiles, including a possible Tibia 7.6 profile, without maintaining separate long-lived engine forks.

## 2. Evidence boundary

This document records a target design, not proof that the current source tree already implements it.

Current relevant repository facts:

- Otheryn already uses a typed C++ `ConfigManager` that loads configuration from Lua;
- the Lua runtime is a shared engine subsystem with explicit lifecycle handling;
- protocol compatibility is already represented through reviewed protocol-profile concepts;
- production resilience, persistence fencing and multichannel safety remain governed by their own architecture and future packages;
- current gameplay systems still contain legacy cross-domain coupling and must be inventoried before module boundaries are claimed.

Therefore future agents must distinguish:

- `PROVEN`: exact current source or deterministic test evidence;
- `DERIVED`: a conclusion following from proven contracts;
- `TARGET`: the design in this document;
- `UNKNOWN`: behavior not yet established.

A target module name does not prove that a corresponding isolated implementation exists.

## 3. Architectural decision

Otheryn should use:

```text
modular monolith per channel
+
typed C++ module registry and lifecycle
+
declarative Lua game profiles
+
profile-selected protocol/rules/content
```

One channel process keeps latency-sensitive world, creature, player, item, combat and Lua interaction local. Explicit module boundaries reduce coupling and make later multichannel ownership, testing and historical profiles possible.

## 4. Three levels of composition

### 4.1 Core-engine modules

Core-engine modules provide foundational capabilities needed by most or all profiles:

```text
engine-runtime
scheduler/dispatcher
network transport
protocol
sessions
world
players
items
creatures
combat
persistence
Lua runtime
observability
```

Most core modules are required and cannot be disabled by an ordinary profile flag.

### 4.2 Gameplay-feature modules

Gameplay-feature modules own substantial systems with their own state, rules, operations, persistence or protocol surface:

```text
Wheel of Destiny
Prey
Charms
Bestiary
Bosstiary
Exaltation Forge
Imbuements
Market
Trade
Bank and guild bank
Guilds
Houses
Achievements
Instances
Boss encounters
Raids
Quest mechanism
NPC mechanism
Spawn mechanism
```

A gameplay feature may be optional for one profile and required for another.

### 4.3 Content packages

Content packages provide concrete game data and scripts through an existing mechanism:

```text
one quest line
one NPC or NPC family
one monster definition
one spell or rune
one raid definition
one boss encounter configuration
one map region
one item set
```

A single quest, spell, NPC or monster is normally content, not a new C++ module.

The rule is:

```text
module = reusable mechanism and ownership boundary
content package = concrete game content using that mechanism
```

## 5. Required module contract

A module is not merely a directory. Every accepted module must declare:

```text
identity
public API
owned state
legal dependencies
startup/shutdown lifecycle
threading and mutation ownership
persistence contract
failure behavior
configuration schema
protocol capabilities
reload policy
tests and observability
```

A future module descriptor may have a shape similar to:

```cpp
struct ModuleDescriptor {
    ModuleId id;
    ModuleRequirement requirement;
    std::span<const ModuleId> dependencies;
    ReloadCapability reloadCapability;
    PersistenceClass persistenceClass;
};
```

The exact API is future implementation work.

## 6. Composition root

Modules must be created and wired in one explicit composition root, such as `Application` or the server lifecycle root.

The composition root owns:

- loading the typed game profile;
- validating the module dependency graph;
- constructing modules and adapters;
- starting modules in dependency order;
- publishing readiness only after required modules succeed;
- stopping modules in reverse dependency order;
- failing startup when the profile is invalid.

It must not become a replacement location for gameplay rules.

Conceptual shape:

```cpp
class Application {
public:
    bool start(const GameProfile& profile);
    void stop();

private:
    ModuleRegistry moduleRegistry;
    ModuleGraph moduleGraph;
};
```

## 7. Dependency direction

The intended dependency direction is:

```text
protocol/Lua/infrastructure adapters
        ↓
application use cases
        ↓
domain rules and public module APIs
        ↓
foundational abstractions
```

Gameplay modules must not depend directly on concrete global infrastructure when a bounded API is required.

Examples of dependencies to eliminate gradually:

```text
feature → global Game
feature → global Database
feature → ProtocolGame internals
feature → raw Redis client
feature → arbitrary Lua state mutation
```

Adapters may depend on a module public API. The module domain must not depend on a concrete protocol adapter.

Example:

```text
ProtocolGame
  → AllocateWheelCommand
  → WheelService
  → WheelResult
  → protocol response
```

## 8. Public APIs and mutation boundaries

Module APIs should expose commands, queries, snapshots and explicit results rather than unrestricted mutable engine objects.

Prefer:

```cpp
MarketResult createOffer(const CreateOfferCommand& command);
PlayerSnapshot getPlayerSnapshot(PlayerId playerId) const;
InventoryResult moveItem(const MoveItemCommand& command);
```

Avoid making these the default cross-module API:

```cpp
Game*
Database*
ProtocolGame*
LuaState*
std::shared_ptr<Player>
std::shared_ptr<Item>
```

Passing a shared pointer is not itself forbidden, but it must not silently grant unrestricted cross-module mutation ownership.

## 9. Communication between modules

Use three primary forms.

### 9.1 Synchronous public API

Use when the caller needs an immediate result and the operation belongs to one controlled mutation boundary.

### 9.2 Commands

Commands request state changes and should carry all required authority and consistency fields, for example:

```cpp
struct WithdrawBankCommand {
    PlayerId playerId;
    Money amount;
    OperationId operationId;
    StateRevision expectedRevision;
};
```

### 9.3 Events

Events notify other modules after an accepted state transition:

```cpp
struct MonsterKilled {
    PlayerId playerId;
    MonsterRaceId raceId;
};
```

Bestiary, Charms, Achievements, Prey and Tasks may react to the same event. The event must not obscure who owns the original mutation.

Events requiring durable delivery must follow the persistence/outbox contract. An in-memory event bus alone does not prove durable completion.

## 10. Threading model

Modularity does not authorize arbitrary multithreaded mutation.

The safe target remains:

```text
network/input threads
  → validated commands
  → authoritative world mutation lane
  → immutable snapshots or compute jobs
  → worker pool
  → generation-validated result
  → authoritative mutation lane
```

Good candidates for parallel computation include:

- packet decoding and shape validation;
- pathfinding over immutable snapshots;
- selected AI calculations;
- compression;
- telemetry;
- backup and reporting work outside the world mutation lane.

State that must retain explicit ownership includes:

- movement application;
- damage and death;
- inventory and container transfer;
- trade finalization;
- market value mutation;
- house ownership;
- player revision updates;
- session handoff;
- Lua operations that mutate the world.

Every asynchronous result must carry enough generation/revision context to reject stale application.

## 11. Persistence and failure contracts

Each module must answer:

```text
What state does it own?
Which state is durable?
When is success acknowledged?
Can the operation be retried?
What happens after process crash?
How is a stale writer rejected?
How is partial failure reconciled?
```

Example: Market

```text
owner: Economy/Market module
durable state: MariaDB
success: only after required transaction commit
retry: only with proven idempotency identity
crash: reload SQL state and reconcile durable outbox
stale write: authoritative revision/fencing predicate
partial failure: reconciliation workflow
```

Example: Creature AI

```text
owner: channel world/creature module
durable state: normally none for current AI decision
success: current world generation only
retry: recompute
crash: reload or respawn from authoritative world/content state
stale result: snapshot generation rejection
```

Existing fail-closed database, migration and save-result contracts must not regress during modularization.

## 12. C++ and Lua configuration boundary

The configuration model is deliberately hybrid.

### 12.1 C++ owns the architecture

C++ must define and validate:

- which modules legally exist;
- stable module identifiers;
- required and optional classification;
- legal dependencies;
- lifecycle ordering;
- threading and ownership rules;
- persistence and transaction boundaries;
- protocol capability requirements;
- typed configuration schemas and safe ranges;
- startup failure behavior;
- which fields are startup-only or reloadable.

Lua must not be able to redefine dependencies, remove safety requirements or create arbitrary engine modules.

### 12.2 Lua declares a profile

Lua may select from capabilities provided by C++:

- profile identity;
- enabled optional modules;
- selected ruleset implementations;
- datapack, map and item registry identifiers;
- bounded balance/configuration values;
- content package selection.

Example target shape:

```lua
return {
    id = "tibia-7.6",
    protocolProfile = "760",

    modules = {
        wheel = false,
        prey = false,
        charms = false,
        bestiary = false,
        forge = false,
        market = false,

        quests = true,
        houses = true,
        guilds = true,
        trade = true,
        raids = true
    },

    rules = {
        combat = "classic-760",
        death = "classic-760",
        pvp = "classic-760",
        progression = "classic-760",
        items = "classic-760"
    },

    content = {
        datapack = "data-tibia-76",
        map = "tibia-76.otbm",
        items = "items-760"
    }
}
```

All identifiers in the table must resolve to C++-registered modules, rulesets or content contracts.

### 12.3 Snapshot, not continuous Lua lookup

Startup should follow:

```text
minimal C++ config bootstrap
  → execute profile Lua
  → copy values into typed immutable GameProfile
  → validate full profile and module graph
  → construct modules
  → start server
```

Runtime code must not repeatedly query Lua to decide whether a module exists.

Do not spread patterns such as:

```cpp
if (luaGetBoolean("wheelEnabled")) {
    // gameplay path
}
```

The profile becomes a typed snapshot. Failed parsing or validation blocks startup.

## 13. Module requirement classes

A future registry should distinguish at least:

```cpp
enum class ModuleRequirement {
    CoreRequired,
    ProfileRequired,
    Optional
};
```

### Core required

Examples:

```text
engine runtime
world
players
items
persistence
network transport
selected protocol implementation
```

A normal Lua profile cannot disable them.

### Profile required

A profile can require a feature or mechanism as part of its accepted contract.

### Optional

Examples may include:

```text
Wheel
Prey
Charms
Bestiary
Forge
Market
analytics
```

Optional does not mean dependency-free or safe to toggle while the server is running.

## 14. Startup validation

The server must fail closed before opening login/game readiness when:

- an unknown module or ruleset is referenced;
- a required dependency is disabled;
- the selected protocol lacks a required capability;
- a content pack requires a missing mechanism;
- two selected modules have an illegal conflict;
- module dependencies form a cycle;
- configuration values fail type or range validation;
- a required module fails initialization.

Example diagnostic:

```text
Profile validation failed:
module "market" is enabled,
but protocol profile "760" has no market capability.
```

The server must not start partially and defer structural errors until a player uses the feature.

## 15. Capabilities instead of scattered version checks

Client version numbers are input to profile resolution, not the long-term business-rule mechanism.

Avoid spreading:

```cpp
if (clientVersion <= 760) {
    // old rule
}
```

across unrelated engine code.

Prefer typed capabilities and selected rule implementations:

```cpp
struct ProtocolCapabilities {
    bool supportsMarket;
    bool supportsPrey;
    bool supportsWheel;
    bool supportsForge;
    bool supportsStore;
};
```

and:

```text
CombatRules760
CombatRulesCurrent
DeathRules760
DeathRulesCurrent
```

A capability says what the protocol/client can represent. A ruleset defines how the game behaves. They are related but not interchangeable.

## 16. Historical profiles such as Tibia 7.6

Disabling modern modules is necessary but not sufficient for a historical profile.

A credible Tibia 7.6 profile requires a compatible set:

```text
protocol 7.6
rulesets approximating or reproducing 7.6 mechanics
7.6-compatible item registry and assets
compatible map and datapack
spells, runes, monsters, NPCs and quests from the intended scope
profile-specific tests
physical client evidence
```

The target composition is:

```text
shared hardened Otheryn engine
  + GameProfile 7.6
  + ProtocolProfile 760
  + Ruleset family 760
  + Datapack 760
  + Assets/item registry 760
```

Do not claim historical parity from flags such as:

```text
wheel = false
prey = false
forge = false
```

alone.

A customized server using protocol 7.6 plus new mechanics should use a custom profile identity, for example `otheryn-classic`, rather than claiming exact Tibia 7.6 parity.

## 17. Shared engine versus profile-specific implementations

Keep shared where semantics are genuinely common:

```text
scheduler
transport foundations
database core
Lua runtime
logging and metrics
backup/recovery
basic world representation
item ownership/container primitives
```

Use profile-selected implementations where behavior differs materially:

```text
Protocol760 / ProtocolCurrent
CombatRules760 / CombatRulesCurrent
DeathRules760 / DeathRulesCurrent
PvpRules760 / PvpRulesCurrent
Items760 / ItemsCurrent
```

Do not force unrelated eras through one class containing many version branches merely to maximize code reuse.

## 18. Reload policy

The module graph is startup-only.

Changes requiring restart include:

```text
module enabled/disabled state
module dependencies
selected protocol implementation
selected ruleset implementation
persistent-state ownership
```

A module may explicitly allow controlled reload of:

```text
configuration values
scripts
content definitions
```

only when it proves safe snapshot replacement and active-state behavior.

Persistent player/module state must never be erased merely because configuration or scripts reload.

## 19. Build and packaging

The initial target is one linked executable per channel.

Modules may later become static CMake libraries to enforce dependencies at build time:

```cmake
add_library(otheryn_wheel STATIC ...)
add_library(otheryn_market STATIC ...)
```

Dynamic `.so`/`.dll` plugin ABI is not an initial goal. It would add ownership, allocator, exception, versioning and deployment complexity before module boundaries are proven.

## 20. Multichannel relationship

Each channel should own its latency-sensitive local state:

```text
world instance
active creatures
active local players
combat execution
Lua runtime
network sessions
```

Shared durable domains may include:

```text
accounts
character persistence
market
global bank/guild state
guilds
houses
global scheduled jobs
session ownership
```

Module boundaries do not replace authoritative multichannel fencing. Shared writes still require durable revision/session-epoch contracts from the production resilience architecture.

Redis may support leases, cache and pub/sub, but it must not become the sole authority for durable writer ownership.

## 21. Recommended migration sequence

Do not rewrite the source tree or move every file first.

### MGE-001 — current ownership and dependency inventory

Produce evidence-backed maps for:

- global/singleton access;
- source-level dependencies;
- state ownership;
- mutation thread/lane;
- persistence paths;
- protocol and Lua entry points;
- module candidates and cycles.

No runtime refactor is required in this first package.

### MGE-002 — typed GameProfile and validation contract

Define typed profile data, startup-only loading, identifiers, capability validation and deterministic diagnostics without yet modularizing every feature.

### MGE-003 — ModuleRegistry and composition root

Introduce registry/lifecycle foundations with existing behavior preserved.

### MGE-004 — first vertical gameplay module

Extract one bounded real feature through public API, adapters, persistence and tests. A critical economy operation is a strong candidate because it exercises transactions, idempotency and failure behavior.

### MGE-005 — protocol and Lua adapters

Move selected entry points to the same application service instead of maintaining independent mutation paths.

### MGE-006 — historical-profile proof

Add one narrowly scoped non-current profile cell only after protocol, rules, content and client evidence are available.

### MGE-007 — static-library/build boundary enforcement

Split modules into build targets only after logical dependencies are proven.

### MGE-008 — broader module extraction

Continue feature by feature. Do not create a generic framework without at least one real module proving each abstraction.

## 22. First vertical module selection

A first module should:

- have a clear owner;
- expose a small public API;
- have deterministic tests;
- cross protocol/Lua/application/domain/persistence boundaries;
- be valuable enough to prove the architecture;
- remain bounded enough for one reviewable package.

Recommended candidates:

1. one critical economy operation;
2. Market create/cancel/accept operation family, if split into smaller slices;
3. one already isolated gameplay feature such as Wheel configuration/allocation, without combining parity or balance changes.

Avoid using the initial package for a complete `Game`, `Player`, `Combat` or source-tree rewrite.

## 23. Validation strategy

Every modularization package should apply:

```text
current source inventory
→ accepted ownership and API contract
→ dependency/cycle check
→ focused unit tests
→ adapter equivalence tests
→ persistence/failure injection when applicable
→ controlled runtime/client evidence
→ exact-head repository gates
```

Profile tests should validate at least:

- exact enabled module set;
- required dependencies;
- selected protocol and rulesets;
- compatible content identifiers;
- rejection of unsupported modern commands/opcodes;
- modern Lua API absence or rejection when the module is unavailable;
- save/logout/relogin behavior;
- physical client login and gameplay for the claimed profile cell.

## 24. Explicit non-goals

This architecture does not authorize:

- one Docker container or network service per gameplay feature;
- dynamic C++ plugin ABI;
- immediate source-tree relocation;
- complete `Game` or `Player` rewrite;
- automatic hot toggling of modules;
- Lua-defined dependencies, lifecycle or transaction rules;
- generic event sourcing for all gameplay;
- Redis as durable source of truth;
- historical-parity claims without evidence;
- combining modularization with unrelated balance, map, protocol or gameplay changes.

## 25. Future-agent starting contract

Before implementing modularity, a future agent must read:

```text
AGENTS.md
docs/agents/CONTEXT_HANDOFF.md
docs/architecture/modular-game-engine-and-profiles.md
docs/architecture/production-resilience-and-recovery.md
```

Then inspect the exact current source for the selected bounded package. Do not infer implementation state from this target document.

The next authorized package is **MGE-001: current ownership and dependency inventory**. It must create a separate issue, branch, active task checkpoint and evidence report before any broad runtime refactor.