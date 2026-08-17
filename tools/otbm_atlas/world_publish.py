"""Build global Atlas publication data and assemble verified world shards.

Render work belongs to GitHub-hosted shard runners. This module builds only the
source-driven global product data on hosted compute, then verifies/assembles the
received shard corpora on the Synology deployment coordinator.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from typing import Any, Iterable, Mapping

EXPECTED_SHARDS = 32
EXPECTED_CHUNKS = 3494
EXPECTED_CHUNK_SIZE = 128
EXPECTED_ATLAS_VERSION = 3
EXPECTED_MAP_SHA256 = "3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034"
EXPECTED_FLOORS = {
    0: 87, 1: 120, 2: 150, 3: 183, 4: 213, 5: 240, 6: 251, 7: 346,
    8: 285, 9: 286, 10: 265, 11: 238, 12: 234, 13: 201, 14: 210, 15: 185,
}
PRODUCER_RE = re.compile(r"^[0-9a-f]{40}$")
GENERATION_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,95}$")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _chunk_key(chunk: Mapping[str, object]) -> str:
    return f"z{int(chunk['z'])}/{int(chunk['chunkX'])}_{int(chunk['chunkY'])}"


def _chunk_sort_key(text: str) -> tuple[int, int, int]:
    floor, stem = text.split("/", 1)
    x_text, y_text = stem.split("_", 1)
    return int(floor[1:]), int(y_text), int(x_text)


def _coverage_digest(values: Iterable[str]) -> str:
    ordered = sorted(set(values), key=_chunk_sort_key)
    return hashlib.sha256(("\n".join(ordered) + "\n").encode("utf-8")).hexdigest()


def _canonical(value: object) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def _validate_producer(value: str) -> str:
    if not PRODUCER_RE.fullmatch(value):
        raise ValueError("producer SHA must be lowercase 40-hex")
    return value


def _validate_generation(value: str) -> str:
    if not GENERATION_RE.fullmatch(value):
        raise ValueError("invalid deployment generation")
    return value


def merge_shard_manifests(directory: Path, producer_sha: str) -> dict[str, Any]:
    producer_sha = _validate_producer(producer_sha)
    paths = sorted(directory.glob("shard-manifest-*.json"))
    if len(paths) != EXPECTED_SHARDS:
        raise ValueError(f"expected {EXPECTED_SHARDS} shard manifests, found {len(paths)}")
    manifests = [_load_json(path) for path in paths]
    by_index: dict[int, dict[str, Any]] = {}
    all_chunks: list[dict[str, Any]] = []
    chunk_keys: list[str] = []
    source_identity: str | None = None
    provenance_identity: str | None = None
    world_plan_digest: str | None = None
    expected_coverage: str | None = None

    for manifest in manifests:
        if int(manifest.get("schemaVersion", -1)) != EXPECTED_ATLAS_VERSION:
            raise ValueError("shard Atlas schemaVersion mismatch")
        if int(manifest.get("chunkSize", -1)) != EXPECTED_CHUNK_SIZE:
            raise ValueError("shard chunkSize mismatch")
        certification = manifest.get("certification")
        if not isinstance(certification, dict) or certification.get("scope") != "world-chunk-shard":
            raise ValueError("shard manifest is not world-chunk-shard certified")
        index = int(certification.get("shardIndex", -1))
        if index in by_index or not 0 <= index < EXPECTED_SHARDS:
            raise ValueError(f"invalid/duplicate shard index: {index}")
        if int(certification.get("shardCount", -1)) != EXPECTED_SHARDS:
            raise ValueError("shardCount mismatch")
        by_index[index] = manifest
        sources = manifest.get("sources")
        provenance = manifest.get("provenance")
        if not isinstance(sources, dict) or not isinstance(provenance, dict):
            raise ValueError("shard source/provenance metadata missing")
        if sources.get("mapSha256") != EXPECTED_MAP_SHA256:
            raise ValueError("shard map SHA-256 is not the certified canonical world")
        if int(sources.get("chunkSize", -1)) != EXPECTED_CHUNK_SIZE or int(sources.get("atlasVersion", -1)) != EXPECTED_ATLAS_VERSION:
            raise ValueError("shard source Atlas identity mismatch")
        source_text = _canonical(sources)
        provenance_text = _canonical(provenance)
        source_identity = source_text if source_identity is None else source_identity
        provenance_identity = provenance_text if provenance_identity is None else provenance_identity
        if source_text != source_identity or provenance_text != provenance_identity:
            raise ValueError("shard source/provenance identity differs")
        plan = str(certification.get("worldPlanDigest", ""))
        coverage = str(certification.get("coverageDigest", ""))
        world_plan_digest = plan if world_plan_digest is None else world_plan_digest
        expected_coverage = coverage if expected_coverage is None else expected_coverage
        if plan != world_plan_digest or coverage != expected_coverage:
            raise ValueError("shard plan/coverage digest differs")
        chunks = manifest.get("chunks")
        if not isinstance(chunks, list) or not chunks:
            raise ValueError(f"shard {index} contains no chunks")
        for raw in chunks:
            if not isinstance(raw, dict):
                raise ValueError("invalid chunk metadata")
            chunk = dict(raw)
            all_chunks.append(chunk)
            chunk_keys.append(_chunk_key(chunk))

    if sorted(by_index) != list(range(EXPECTED_SHARDS)):
        raise ValueError("shard manifest indices are incomplete")
    if len(chunk_keys) != EXPECTED_CHUNKS or len(set(chunk_keys)) != EXPECTED_CHUNKS:
        raise ValueError("shard manifests do not cover 3494 unique chunks exactly once")
    floors = Counter(int(text.split("/", 1)[0][1:]) for text in chunk_keys)
    if dict(sorted(floors.items())) != EXPECTED_FLOORS:
        raise ValueError(f"floor coverage differs: {dict(sorted(floors.items()))}")
    actual_coverage = _coverage_digest(chunk_keys)
    if actual_coverage != expected_coverage:
        raise ValueError("computed full-world coverage digest differs from shard certification")

    first = by_index[0]
    chunks_sorted = sorted(all_chunks, key=lambda chunk: _chunk_sort_key(_chunk_key(chunk)))
    return {
        "schemaVersion": int(first.get("schemaVersion", -1)),
        "chunkSize": int(first.get("chunkSize", -1)),
        "tilePixels": int(first.get("tilePixels", -1)),
        "overviewFactor": int(first.get("overviewFactor", -1)),
        "lowOverviewFactor": int(first.get("lowOverviewFactor", -1)),
        "overviewVersion": int(first.get("overviewVersion", -1)),
        "chunks": chunks_sorted,
        "sources": dict(first["sources"]),
        "provenance": dict(first["provenance"]),
        "certification": {
            "scope": "full-world-assembled-publication",
            "producerSha": producer_sha,
            "renderShards": EXPECTED_SHARDS,
            "worldPlanDigest": world_plan_digest,
            "coverageDigest": actual_coverage,
            "chunks": EXPECTED_CHUNKS,
            "floors": list(range(16)),
        },
    }


def build_global_bundle(manifest_dir: Path, map_path: Path, asset_dir: Path, output: Path, repository_root: Path, producer_sha: str) -> dict[str, Any]:
    """Build viewer/factual/search/tile-inspector data without rendering world detail."""
    manifest = merge_shard_manifests(manifest_dir, producer_sha)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    _write_json(output / "manifest.json", manifest)

    # Lazy imports keep Synology assembly/promotion usable in a minimal stdlib
    # container without the vendored source corpus.
    from .atlas import canonical_source_paths, spool_map
    from .production_data import build_incremental_production_data

    canonical = canonical_source_paths(repository_root)
    if map_path.resolve() != canonical["map"].resolve():
        raise ValueError("global publication data requires the canonical map")
    if asset_dir.resolve() != canonical["appearanceAssetRoot"].resolve():
        raise ValueError("global publication data requires canonical appearance assets")
    chunk_size = int(manifest["chunkSize"])
    spool = output / ".spool"
    spool_map(map_path, spool, chunk_size)
    expected_spool_chunks = {_chunk_key(chunk) for chunk in manifest["chunks"]}
    actual_spool_chunks = {f"{path.parent.name}/{path.stem}" for path in spool.glob("z*/*.bin")}
    if actual_spool_chunks != expected_spool_chunks:
        raise RuntimeError("global spool coverage differs from certified render coverage")

    render_plan = {
        "dirtyDetailChunks": [],
        "reusedDetailChunks": sorted(expected_spool_chunks, key=_chunk_sort_key),
        "deletedDetailChunks": [],
        "fullBuildRequired": False,
        "fullBuildReasons": [],
        "legacyPublicationAdopted": False,
        "spool": {},
    }
    deferred_environment = {
        "instances": 0,
        "uniqueAnimations": 0,
        "chunks": 0,
        "staticFallbacks": 0,
        "completedChunks": 0,
        "reusedChunks": 0,
        "outputFiles": 0,
        "outputBytes": 0,
        "status": "DEFERRED_TO_VERIFIED_SHARD_ASSEMBLY",
    }
    build_incremental_production_data(
        map_path=map_path,
        asset_dir=asset_dir,
        output=output,
        repository_root=repository_root,
        canonical=canonical,
        chunk_size=chunk_size,
        chunks=list(manifest["chunks"]),
        render_plan=render_plan,
        provenance=dict(manifest["provenance"]),
        assets_sha=str(manifest["sources"]["assetsSha256"]),
        environment_statistics_override=deferred_environment,
    )
    deployment_source = {
        "schemaVersion": 1,
        "producerSha": producer_sha,
        "worldPlanDigest": manifest["certification"]["worldPlanDigest"],
        "coverageDigest": manifest["certification"]["coverageDigest"],
        "chunks": EXPECTED_CHUNKS,
        "sources": manifest["sources"],
    }
    _write_json(output / "data" / "deployment-source.json", deployment_source)
    shutil.rmtree(output / ".spool", ignore_errors=True)
    shutil.rmtree(output / ".incremental-state", ignore_errors=True)
    for forbidden in ("tiles", "overview", "overview-low", "data/environment-animations"):
        if (output / forbidden).exists():
            raise RuntimeError(f"global bundle unexpectedly contains render-owned path: {forbidden}")
    return {"manifest": manifest, "deploymentSource": deployment_source}


def _copy_file_verified(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file():
        if _sha256(source) != _sha256(target):
            raise RuntimeError(f"non-identical publication file collision: {target}")
        return
    if target.exists():
        raise RuntimeError(f"publication path collision: {target}")
    try:
        # Received bundles and assembled/current live below the same Synology
        # Atlas root. Hardlinks avoid a second ~11 GiB assembly copy while
        # preserving independent directory lifecycles. Fall back safely if the
        # backing filesystem refuses hardlinks.
        os.link(source, target)
    except OSError:
        shutil.copy2(source, target)


def _copy_tree(source: Path, target: Path, *, exclude_names: set[str] | None = None) -> None:
    exclude_names = exclude_names or set()
    if not source.exists():
        return
    for path in sorted(source.rglob("*"), key=lambda value: value.relative_to(source).as_posix()):
        relative = path.relative_to(source)
        if any(part in exclude_names for part in relative.parts):
            continue
        destination = target / relative
        if path.is_symlink():
            raise RuntimeError(f"symlink in received publication bundle: {path}")
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            _copy_file_verified(path, destination)


def _aggregate_environment(assembled: Path, shard_roots: list[Path], expected_chunks: list[str]) -> dict[str, int]:
    indexes = [_load_json(root / "data/environment-animations/index.json") for root in shard_roots]
    first = indexes[0]
    contract_fields = ("schemaVersion", "animationZoom", "overlapSafetyRadiusTiles", "policy")
    for index in indexes[1:]:
        for field in contract_fields:
            if _canonical(index.get(field)) != _canonical(first.get(field)):
                raise RuntimeError(f"environment shard {field} differs across render shards")
        left = first.get("exporter", {})
        right = index.get("exporter", {})
        if not isinstance(left, dict) or not isinstance(right, dict) or left.get("sourceFingerprint") != right.get("sourceFingerprint"):
            raise RuntimeError("environment source fingerprint differs across render shards")

    root = assembled / "data/environment-animations"
    checkpoints_root = root / "checkpoints"
    instances = fallbacks = chunks_with_records = 0
    animation_keys: set[str] = set()
    for text in expected_chunks:
        floor, stem = text.split("/", 1)
        checkpoint_path = checkpoints_root / floor / f"{stem}.json"
        if not checkpoint_path.is_file():
            raise RuntimeError(f"assembled environment checkpoint missing: {text}")
        checkpoint = _load_json(checkpoint_path)
        count = int(checkpoint.get("instances", -1))
        fallback = int(checkpoint.get("staticFallbacks", -1))
        if count < 0 or fallback < 0:
            raise RuntimeError(f"invalid assembled environment checkpoint counters: {text}")
        instances += count
        fallbacks += fallback
        chunks_with_records += int(count > 0)
        keys = checkpoint.get("animationKeys", [])
        if not isinstance(keys, list):
            raise RuntimeError(f"invalid animationKeys in checkpoint: {text}")
        animation_keys.update(map(str, keys))

    data_files = [
        path for path in root.rglob("*")
        if path.is_file() and path.name not in {"index.json", "export-state.json"}
    ]
    output_bytes = sum(path.stat().st_size for path in data_files)
    stats = {
        "instances": instances,
        "uniqueAnimations": len(animation_keys),
        "chunks": chunks_with_records,
        "staticFallbacks": fallbacks,
        "completedChunks": len(expected_chunks),
        "reusedChunks": sum(int(index.get("statistics", {}).get("reusedChunks", 0)) for index in indexes if isinstance(index.get("statistics"), dict)),
        "outputFiles": len(data_files),
        "outputBytes": output_bytes,
    }
    exporter = dict(first.get("exporter", {})) if isinstance(first.get("exporter"), dict) else {}
    exporter.update({
        "workerProcesses": sum(int(index.get("exporter", {}).get("workerProcesses", 0)) for index in indexes if isinstance(index.get("exporter"), dict)),
        "scheduling": "32 independently verified hosted render shards; deterministic Synology assembly",
        "assembly": "verified-shard-union-v1",
    })
    final_index = {
        "schemaVersion": first.get("schemaVersion"),
        "animationZoom": first.get("animationZoom"),
        "overlapSafetyRadiusTiles": first.get("overlapSafetyRadiusTiles"),
        "statistics": stats,
        "exporter": exporter,
        "policy": first.get("policy"),
    }
    _write_json(root / "index.json", final_index)
    _write_json(root / "export-state.json", {
        "schemaVersion": 1,
        "exportVersion": exporter.get("version"),
        "sourceFingerprint": exporter.get("sourceFingerprint"),
        "status": "complete",
        "statistics": stats,
    })
    return stats


def _validate_receipts(generation_root: Path, producer_sha: str) -> None:
    receipts = generation_root / "receipts"
    expected = {"global", *(f"shard-{index:02d}" for index in range(EXPECTED_SHARDS))}
    found = {path.stem for path in receipts.glob("*.json")}
    if found != expected:
        raise RuntimeError(f"received bundle receipt set differs: expected={sorted(expected)} found={sorted(found)}")
    for bundle_id in sorted(expected):
        receipt = _load_json(receipts / f"{bundle_id}.json")
        if receipt.get("status") != "COMPLETE" or receipt.get("producerSha") != producer_sha or receipt.get("bundleId") != bundle_id:
            raise RuntimeError(f"invalid receiver receipt: {bundle_id}")
        if bundle_id == "global":
            if receipt.get("kind") != "global" or receipt.get("shardIndex") is not None:
                raise RuntimeError("invalid global receiver receipt")
        else:
            index = int(bundle_id.split("-", 1)[1])
            if receipt.get("kind") != "shard" or int(receipt.get("shardIndex", -1)) != index:
                raise RuntimeError(f"invalid shard receiver receipt: {bundle_id}")


def assemble_generation(generation_root: Path, output: Path, producer_sha: str) -> dict[str, Any]:
    producer_sha = _validate_producer(producer_sha)
    _validate_receipts(generation_root, producer_sha)
    bundles = generation_root / "bundles"
    global_root = bundles / "global"
    global_manifest = _load_json(global_root / "manifest.json")
    source = _load_json(global_root / "data/deployment-source.json")
    if source.get("producerSha") != producer_sha:
        raise RuntimeError("global bundle producer identity mismatch")
    expected_chunks = sorted((_chunk_key(chunk) for chunk in global_manifest.get("chunks", []) if isinstance(chunk, dict)), key=_chunk_sort_key)
    if len(expected_chunks) != EXPECTED_CHUNKS or len(set(expected_chunks)) != EXPECTED_CHUNKS:
        raise RuntimeError("global manifest does not describe the certified 3494 chunks")

    from .verify_world_shard import verify_world_shard

    shard_roots: list[Path] = []
    physical_chunks: list[str] = []
    for index in range(EXPECTED_SHARDS):
        root = bundles / f"shard-{index:02d}"
        report = verify_world_shard(root)
        if not report.get("ok"):
            raise RuntimeError(f"received shard {index} failed independent verification: {report.get('errors')}")
        certification = report.get("certification", {})
        if not isinstance(certification, dict) or int(certification.get("shardIndex", -1)) != index:
            raise RuntimeError(f"received shard {index} certification identity mismatch")
        physical_chunks.extend(map(str, report.get("chunkKeys", [])))
        shard_roots.append(root)
    if sorted(physical_chunks, key=_chunk_sort_key) != expected_chunks or len(set(physical_chunks)) != EXPECTED_CHUNKS:
        raise RuntimeError("received physical shard coverage differs from global manifest")

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    _copy_tree(global_root, output)
    for root in shard_roots:
        for name in ("tiles", "overview", "overview-low"):
            _copy_tree(root / name, output / name)
        _copy_tree(
            root / "data/environment-animations",
            output / "data/environment-animations",
            exclude_names={"index.json", "export-state.json"},
        )
    environment = _aggregate_environment(output, shard_roots, expected_chunks)
    statistics_path = output / "data/statistics.json"
    statistics = _load_json(statistics_path)
    statistics["environmentAnimations"] = environment
    _write_json(statistics_path, statistics)
    _write_json(output / "data/deployment-assembly.json", {
        "schemaVersion": 1,
        "producerSha": producer_sha,
        "renderShards": EXPECTED_SHARDS,
        "chunks": EXPECTED_CHUNKS,
        "coverageDigest": source.get("coverageDigest"),
        "worldPlanDigest": source.get("worldPlanDigest"),
        "status": "ASSEMBLED_FROM_VERIFIED_SHARDS",
    })
    return {"chunks": EXPECTED_CHUNKS, "producerSha": producer_sha, "environmentAnimations": environment}


def current_state(atlas_root: Path) -> dict[str, Any]:
    current = atlas_root / "current"
    exists = current.is_dir()
    if exists:
        manifest = current / "manifest.json"
        if not manifest.is_file():
            raise RuntimeError("existing Atlas current has no manifest.json; refusing automated deployment")
        manifest_sha = _sha256(manifest)
    else:
        manifest_sha = None
    return {"schemaVersion": 1, "exists": exists, "manifestSha256": manifest_sha}


def capture_current(atlas_root: Path, output: Path) -> dict[str, Any]:
    state = current_state(atlas_root)
    _write_json(output, state)
    return state


def promote(assembled: Path, atlas_root: Path, expected_state_path: Path, generation: str, receipt_path: Path) -> dict[str, Any]:
    generation = _validate_generation(generation)
    expected = _load_json(expected_state_path)
    actual = current_state(atlas_root)
    if actual != expected:
        raise RuntimeError(f"Atlas current changed during deployment: expected={expected} actual={actual}")
    if not assembled.is_dir() or not (assembled / "manifest.json").is_file():
        raise RuntimeError("assembled publication is missing manifest.json")
    current = atlas_root / "current"
    previous = atlas_root / f"previous-{generation}"
    if previous.exists():
        raise RuntimeError(f"previous generation path already exists: {previous}")
    previous_created = False
    if current.exists():
        os.replace(current, previous)
        previous_created = True
    try:
        os.replace(assembled, current)
    except Exception:
        if previous_created and previous.exists() and not current.exists():
            os.replace(previous, current)
        raise
    receipt = {
        "schemaVersion": 1,
        "generation": generation,
        "status": "PROMOTED_PENDING_RUNTIME",
        "previous": previous.name if previous_created else None,
        "promotedManifestSha256": _sha256(current / "manifest.json"),
        "producerSha": _load_json(current / "data/deployment-source.json").get("producerSha"),
    }
    _write_json(receipt_path, receipt)
    return receipt


def activate(atlas_root: Path, receipt_path: Path) -> dict[str, Any]:
    receipt = _load_json(receipt_path)
    current = atlas_root / "current"
    if not current.is_dir() or _sha256(current / "manifest.json") != receipt.get("promotedManifestSha256"):
        raise RuntimeError("current Atlas differs from promoted deployment receipt")
    receipt["status"] = "ACTIVE"
    _write_json(receipt_path, receipt)
    return receipt


def rollback(atlas_root: Path, receipt_path: Path) -> dict[str, Any]:
    receipt = _load_json(receipt_path)
    generation = _validate_generation(str(receipt.get("generation", "")))
    current = atlas_root / "current"
    failed = atlas_root / f"failed-{generation}"
    if failed.exists():
        raise RuntimeError(f"failed-generation path already exists: {failed}")
    if not current.is_dir() or _sha256(current / "manifest.json") != receipt.get("promotedManifestSha256"):
        raise RuntimeError("current Atlas differs from promoted deployment; refusing rollback mutation")
    os.replace(current, failed)
    previous_name = receipt.get("previous")
    if previous_name:
        previous = atlas_root / str(previous_name)
        if not previous.is_dir():
            raise RuntimeError("previous Atlas is missing after failed runtime deployment")
        os.replace(previous, current)
    receipt["status"] = "ROLLED_BACK_RUNTIME_FAILURE"
    receipt["failed"] = failed.name
    _write_json(receipt_path, receipt)
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    global_cmd = commands.add_parser("global", help="build source-driven global publication bundle without detail rendering")
    global_cmd.add_argument("manifests", type=Path)
    global_cmd.add_argument("map", type=Path)
    global_cmd.add_argument("assets", type=Path)
    global_cmd.add_argument("output", type=Path)
    global_cmd.add_argument("--repository", type=Path, default=Path("."))
    global_cmd.add_argument("--producer-sha", required=True)

    assemble = commands.add_parser("assemble", help="verify transferred shards and assemble a complete publication")
    assemble.add_argument("generation", type=Path)
    assemble.add_argument("output", type=Path)
    assemble.add_argument("--producer-sha", required=True)

    capture = commands.add_parser("capture-current")
    capture.add_argument("atlas_root", type=Path)
    capture.add_argument("--output", type=Path, required=True)

    promote_cmd = commands.add_parser("promote")
    promote_cmd.add_argument("assembled", type=Path)
    promote_cmd.add_argument("atlas_root", type=Path)
    promote_cmd.add_argument("--expected-state", type=Path, required=True)
    promote_cmd.add_argument("--generation", required=True)
    promote_cmd.add_argument("--receipt", type=Path, required=True)

    activate_cmd = commands.add_parser("activate")
    activate_cmd.add_argument("atlas_root", type=Path)
    activate_cmd.add_argument("--receipt", type=Path, required=True)

    rollback_cmd = commands.add_parser("rollback")
    rollback_cmd.add_argument("atlas_root", type=Path)
    rollback_cmd.add_argument("--receipt", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "global":
        result = build_global_bundle(args.manifests, args.map, args.assets, args.output, args.repository, args.producer_sha)
    elif args.command == "assemble":
        result = assemble_generation(args.generation, args.output, args.producer_sha)
    elif args.command == "capture-current":
        result = capture_current(args.atlas_root, args.output)
    elif args.command == "promote":
        result = promote(args.assembled, args.atlas_root, args.expected_state, args.generation, args.receipt)
    elif args.command == "activate":
        result = activate(args.atlas_root, args.receipt)
    else:
        result = rollback(args.atlas_root, args.receipt)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
