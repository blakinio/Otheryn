"""Resume an interrupted local Atlas after the complete detail phase.

This path is intentionally fail-closed: existing detail PNG/report pairs are
adopted only when their checksums and production fingerprints match the current
canonical map, supplied asset corpus and render contract.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from . import atlas as core
from .incremental_core import RENDER_CORE_VERSION, collect_asset_state, render_contract_digest, spool_hashes
from .incremental_state import prepare_dependency_index
from .local_parallel_build import build_overviews
from .overview import LOW_OVERVIEW_FACTOR, OVERVIEW_FACTOR, OVERVIEW_VERSION
from .production_incremental import PRODUCTION_STATE_VERSION, _production_detail_fingerprint
from .sprite_dependency import prepare_production_sprite_digests


def _chunk_parts(text: str) -> tuple[int, int, int]:
    floor, name = text.split("/", 1)
    if not floor.startswith("z"):
        raise ValueError(f"invalid chunk key {text!r}")
    chunk_x_text, chunk_y_text = name.split("_", 1)
    return int(floor[1:]), int(chunk_x_text), int(chunk_y_text)


def _chunk_sort_key(text: str) -> tuple[int, int, int]:
    z, chunk_x, chunk_y = _chunk_parts(text)
    return z, chunk_y, chunk_x


def _load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def _verified_resume_plan(
    map_path: Path,
    asset_dir: Path,
    output: Path,
    repository_root: Path,
    chunk_size: int,
) -> tuple[dict[str, object], dict[str, str]]:
    """Reconstruct production fingerprints from the already-complete spool."""
    spool_dir = output / ".spool"
    spool_metadata_path = spool_dir / "spool.json"
    if not spool_metadata_path.is_file():
        raise RuntimeError(f"partial Atlas has no spool metadata: {spool_metadata_path}")
    metadata = _load_json(spool_metadata_path)
    map_sha = core._sha256(map_path)
    if int(metadata.get("schemaVersion", -1)) != 1:
        raise RuntimeError("partial Atlas spool schema is unsupported")
    if int(metadata.get("chunkSize", -1)) != chunk_size:
        raise RuntimeError("partial Atlas spool chunk size does not match requested chunk size")
    if str(metadata.get("sourceSha256", "")) != map_sha:
        raise RuntimeError("partial Atlas spool belongs to a different world.otbm")
    if not (spool_dir / "facts.json").is_file() or not (spool_dir / "tile-facts").is_dir():
        raise RuntimeError("partial Atlas spool is missing facts or tile-facts sidecars")

    current_spool_hashes = spool_hashes(spool_dir)
    if not current_spool_hashes:
        raise RuntimeError("partial Atlas spool contains no detail chunks")

    state_root = output / ".incremental-state"
    state_root.mkdir(parents=True, exist_ok=True)
    dependency_index, dependency_report = prepare_dependency_index(spool_dir, asset_dir, state_root)
    records = dependency_index.get("chunks", {})
    if not isinstance(records, Mapping):
        raise RuntimeError("partial Atlas dependency index has no chunks mapping")

    asset_state = collect_asset_state(asset_dir)
    exact_sprites = prepare_production_sprite_digests(asset_dir, asset_state, dependency_index, None)
    asset_state = dict(asset_state)
    asset_state["spriteDigests"] = exact_sprites
    render_digest = render_contract_digest(repository_root)
    fingerprints = {
        str(text): _production_detail_fingerprint(record, asset_state, render_digest)
        for text, record in records.items()
        if isinstance(text, str) and isinstance(record, Mapping)
    }
    if set(fingerprints) != set(current_spool_hashes):
        raise RuntimeError("partial Atlas spool and dependency index disagree on chunk inventory")

    next_state = {
        "stateVersion": PRODUCTION_STATE_VERSION,
        "chunkSize": chunk_size,
        "renderCoreVersion": RENDER_CORE_VERSION,
        "renderContractDigest": render_digest,
        "gutterProfile": asset_state.get("gutterProfile"),
        "assetStateDigest": asset_state.get("stateDigest"),
        "assetSheets": asset_state.get("sheets", []),
        "spriteDigests": exact_sprites,
        "mapSha256": map_sha,
        "spoolChunkHashes": dict(sorted(current_spool_hashes.items())),
        "chunkFingerprints": dict(sorted(fingerprints.items())),
        "adoptedLegacyPublication": False,
    }
    render_plan: dict[str, object] = {
        "schemaVersion": PRODUCTION_STATE_VERSION,
        "spoolDir": str(spool_dir),
        "dirtyDetailChunks": [],
        "reusedDetailChunks": sorted(fingerprints, key=_chunk_sort_key),
        "deletedDetailChunks": [],
        "chunkFingerprints": fingerprints,
        "fullBuildRequired": False,
        "fullBuildReasons": [],
        "legacyPublicationAdopted": False,
        "spool": {
            "parsed": False,
            "integrity": "resume-verified-from-existing-spool",
            "renderShards": {"changed": [], "reused": sorted(current_spool_hashes), "deleted": []},
            # None is intentionally selected by production_data when changed is
            # empty, causing a complete deterministic tile-inspector materialization.
            "tileFacts": {"changed": [], "reused": [], "deleted": []},
            "factsChanged": False,
        },
        "dependencies": dependency_report,
        "previousOverviewFiles": None,
        "nextState": next_state,
    }
    return render_plan, fingerprints


def load_verified_detail_chunks(
    output: Path,
    fingerprints: Mapping[str, str],
    chunk_size: int,
) -> list[dict[str, object]]:
    """Adopt existing detail outputs only after byte and fingerprint proof."""
    chunks: list[dict[str, object]] = []
    failures: list[str] = []
    for text in sorted(fingerprints, key=_chunk_sort_key):
        z, chunk_x, chunk_y = _chunk_parts(text)
        tile_path = output / "tiles" / f"z{z}" / f"{chunk_x}_{chunk_y}.png"
        report_path = tile_path.with_suffix(".json")
        report = core._read_report(report_path)
        if not tile_path.is_file() or report is None:
            failures.append(f"{text}: missing PNG/report")
            continue
        expected_fingerprint = fingerprints[text]
        if report.get("fingerprint") != expected_fingerprint:
            failures.append(f"{text}: fingerprint mismatch")
            continue
        expected_checksum = report.get("checksum")
        if not isinstance(expected_checksum, str) or core._sha256(tile_path) != expected_checksum:
            failures.append(f"{text}: PNG checksum mismatch")
            continue
        required = ("imageWidth", "imageHeight", "tiles", "groundItems", "childItems", "renderOperations")
        if any(key not in report for key in required):
            failures.append(f"{text}: incomplete detail report")
            continue
        logical_bounds = (
            chunk_x * chunk_size,
            chunk_x * chunk_size + chunk_size - 1,
            chunk_y * chunk_size,
            chunk_y * chunk_size + chunk_size - 1,
            z,
        )
        chunks.append({
            "z": z,
            "chunkX": chunk_x,
            "chunkY": chunk_y,
            "logicalBounds": list(logical_bounds),
            "path": tile_path.relative_to(output).as_posix(),
            **report,
            "fingerprint": expected_fingerprint,
        })

    actual_pngs = list((output / "tiles").glob("z*/*.png"))
    if len(actual_pngs) != len(fingerprints):
        failures.append(f"detail PNG inventory mismatch: files={len(actual_pngs)} expected={len(fingerprints)}")
    if failures:
        sample = "; ".join(failures[:8])
        raise RuntimeError(f"refusing partial Atlas adoption ({len(failures)} failures): {sample}")
    return chunks


def resume_partial_build(
    map_path: Path,
    asset_dir: Path,
    output: Path,
    *,
    repository_root: Path = Path("."),
    chunk_size: int = 128,
    workers: int = 1,
) -> dict[str, object]:
    if workers <= 0:
        raise ValueError("workers must be positive")
    canonical = core.canonical_source_paths(repository_root)
    core._require_canonical_source(map_path, canonical["map"], "map")
    core._require_canonical_source(asset_dir, canonical["appearanceAssetRoot"], "appearance assets")

    map_sha = core._sha256(map_path)
    assets_sha = core._tree_sha256(asset_dir)
    expected = {
        "mapSha256": map_sha,
        "assetsSha256": assets_sha,
        "chunkSize": chunk_size,
        "atlasVersion": core.ATLAS_VERSION,
        "tileFactsVersion": core.TILE_FACTS_VERSION,
    }
    render_plan, fingerprints = _verified_resume_plan(map_path, asset_dir, output, repository_root, chunk_size)
    print(f"Resume detail validation: {len(fingerprints)} chunks", flush=True)
    chunks = load_verified_detail_chunks(output, fingerprints, chunk_size)
    print(f"Resume detail validation: PASS ({len(chunks)} chunks, checksums+fingerprints)", flush=True)

    build_overviews(chunks, output, None, workers)

    provenance = {
        "map": core.CANONICAL_WORLD_ROOT.joinpath("world.otbm").as_posix(),
        "worldRoot": core.CANONICAL_WORLD_ROOT.as_posix(),
        "npcDefinitionRoot": core.CANONICAL_NPC_ROOT.as_posix(),
        "monsterDefinitionRoot": core.CANONICAL_MONSTER_ROOT.as_posix(),
        "appearanceAssetRoot": core.CANONICAL_ASSET_ROOT.as_posix(),
    }
    manifest = {
        "schemaVersion": core.ATLAS_VERSION,
        "chunkSize": chunk_size,
        "tilePixels": 32,
        "overviewFactor": OVERVIEW_FACTOR,
        "lowOverviewFactor": LOW_OVERVIEW_FACTOR,
        "overviewVersion": OVERVIEW_VERSION,
        "chunks": chunks,
        "sources": expected,
        "provenance": provenance,
    }
    core._write_text_atomic(output / "manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    core.commit_production_render_state(output, render_plan)
    spool_dir = Path(str(render_plan["spoolDir"]))
    core._write_text_atomic(spool_dir / "source.json", json.dumps(expected, sort_keys=True) + "\n")
    core.build_incremental_production_data(
        map_path=map_path,
        asset_dir=asset_dir,
        output=output,
        repository_root=repository_root,
        canonical=canonical,
        chunk_size=chunk_size,
        chunks=chunks,
        render_plan=render_plan,
        provenance=provenance,
        assets_sha=assets_sha,
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", type=Path)
    parser.add_argument("assets", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--repository", type=Path, default=Path("."))
    parser.add_argument("--chunk-size", type=int, default=128)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    repository_root = args.repository.resolve()
    assets = args.assets.resolve()
    try:
        core.CANONICAL_ASSET_ROOT = assets.relative_to(repository_root)
    except ValueError:
        core.CANONICAL_ASSET_ROOT = assets
    manifest = resume_partial_build(
        args.map.resolve(),
        assets,
        args.output.resolve(),
        repository_root=repository_root,
        chunk_size=args.chunk_size,
        workers=args.workers,
    )
    print(f"Resume complete: {len(manifest.get('chunks', []))} chunks", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
