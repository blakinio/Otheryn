# OAM-052 Deployment Operations disposition

## Final disposition

```text
deployment-operations → DO_NOT_MIGRATE
```

The canonical Canary package is a reviewed-content deployment and validation stack. It assembles a trusted full datapack plus a symlink-free reviewed overlay, launches a compiled Canary binary for preflight, atomically publishes a release directory, switches `active` and `previous`, runs a second smoke test, attempts rollback when possible and records a SHA-256 manifest.

That responsibility remains in the Canary laboratory. Otheryn does not receive a copy of `tools/deploy/**`, the Canary-specific smoke adapter, content-deployment workflows or the release-root symlink layout.

## Target ownership boundary

Otheryn production operations are governed by the separate Production Resilience programme:

- PRS-001 owns bounded disposable backup and PITR proof;
- PRS-007 may later own replica and manual-failover configuration after fencing prerequisites;
- PRS-008 may later own the production Compose stack and hardening;
- OAM packages must not opportunistically add production deployment behavior.

Current Otheryn has no target-owned reviewed-content promotion interface, no `tools/deploy` implementation root, no matching workflow, no runtime/startup consumer and no proven long-running supervisor contract for Canary's datapack release model. PRS-001 recovery-set publication is adjacent atomic filesystem tooling, but it protects encrypted database recovery artifacts and is not a datapack deployment mechanism.

## Boundary classification

| Boundary | Result |
|---|---|
| ownership/lifecycle | Canary owns the existing reviewed-content deployment stack; Otheryn has no target owner for it. |
| build/toolchain | No Otheryn build entry or dependency consumes the Canary Python tools. |
| configuration | Target production configuration remains PRS-owned and unresolved beyond completed PRS-001 proof. |
| service/API | No target release API, promotion handoff or supervisor interface exists. |
| scheduling/concurrency | No production scheduler or deployment serialization contract is present. |
| persistence | Canary release manifests and symlink state are not Otheryn gameplay/database persistence. |
| protocol/session | Not applicable. |
| identifiers/assets | Reviewed datapack files are package inputs; no target asset migration is authorized. |
| world/map | The existing stack validates content but does not authorize map mutation or blind import. |
| runtime | No target-local deployment runtime is added or executed. |
| tests | Exact-head repository checks validate this disposition; no production behavior is claimed. |
| physical-client E2E | Not applicable to the docs-only disposition. |
| operations | Future Otheryn deployment must be designed under bounded PRS ownership from target requirements. |
| security/privacy | No endpoint, secret, key, production release root or host is accessed or configured. |

## Why REUSE and ADAPT are rejected now

`REUSE` is rejected because generic atomic rename, checksum and rollback mechanics do not establish target ownership or compatibility. The current implementation assumes Canary repository layout, a compiled Canary binary, Canary datapack inputs, temporary smoke databases and a specific filesystem release-root contract.

`ADAPT` is rejected for this package because no current Otheryn consumer or accepted target interface requires adaptation. Adding one now would pre-empt the separately governed production-resilience roadmap and mix content-laboratory tooling with production-server deployment ownership.

A future bounded target package may design a distinct reviewed-content promotion or full-release mechanism after it defines the release artifact, supervisor, configuration, secrets, failure injection, rollout, rollback and operator contracts. That would be new target-owned engineering, not migration approval for the current Canary package.

## Target effect

This disposition adds no Otheryn runtime, deployment script, workflow, Compose file, scheduler, service, schema, map/datapack content, endpoint, credential, production configuration or host action.

Canary's deployment tooling remains available as laboratory and content-validation infrastructure. Any future use against an exact Otheryn revision requires a separately authorized invocation contract and proof; this package does not claim such compatibility.

## Delivery evidence

Target feature PR #136 changed exactly this report and its active task record. Final head `b0e6a965399008a9834f8449c95981d78885ed10` passed exact-head Required run `30214361783`, had no comments, reviews or review threads, was behind target `main` by zero and squash-merged with expected-head protection as `2afcaef4a3d023a7ec987e4380e80905534fdd2b`.

No runtime or deployment path was added by the target delivery.

## Nonclaims

This result does not claim that Otheryn production deployment is complete, that PRS-008 is implemented, that backup/PITR proves application rollout safety, that Canary's toolchain is permanently sufficient, that rollback targets always exist, that a real supervisor will consume symlinked datapacks, or that production readiness, operator correctness, availability, RPO or RTO has been established.
