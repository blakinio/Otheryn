"""Persistent local change-impact planning for the canonical Atlas entry point.

This module is deliberately separate from the PR base-vs-head planner.  The
production builder has one immutable target snapshot plus an existing output
publication, so its authority is the last successfully committed local render
state.  A changed monolithic map may still require one parse, but unchanged
spatial shards and detail images remain reusable.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
import json
from pathlib import Path
import shutil
from typing import Any

from .incremental_core import (
    RENDER_CORE_VERSION,
    ChunkKey,
    collect_asset_state,
    detail_fingerprint,
    reconcile_spool,
    render_contract_digest,
    sha256_file,
    spool_hashes,
    write_bytes_atomic,
    write_json_atomic,
)
from .incremental_state import prepare_dependency_index

PRODUCTION_STATE_VERSION = 1

SpoolBuilder = Callable[[Path, Path, int], Mapping[str, object]]


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def _same_source(existing: Mapping[str, object] | None, expected: Mapping[str, object]) -> bool:
    if not existing:
        return False
    keys = ("mapSha256", "assetsSha256", "chunkSize", "atlasVersion")
    return all(existing.get(key) == expected.get(key) for key in keys)


def _file_hashes(root: Path, suffix: str) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(candidate for candidate in root.rglob(f"*{suffix}") if candidate.is_file())
    }


def _reconcile_aux_tree(candidate: Path, stable: Path, suffix: str) -> dict[str, object]:
    old = _file_hashes(stable, suffix)
    new = _file_hashes(candidate, suffix)
    changed = sorted(path for path, digest in new.items() if old.get(path) != digest)
    reused = sorted(path for path, digest in new.items() if old.get(path) == digest)
    deleted = sorted(path for path in old if path not in new)
    for relative in changed:
        write_bytes_atomic(stable / relative, (candidate / relative).read_bytes())
    for relative in deleted:
        target = stable / relative
        if target.exists():
            target.unlink()
    if stable.exists():
        for directory in sorted((path for path in stable.rglob("*") if path.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass
    return {"changed": changed, "reused": reused, "deleted": deleted}


def _copy_if_changed(source: Path, target: Path) -> bool:
    if target.is_file() and sha256_file(source) == sha256_file(target):
        return False
    write_bytes_atomic(target, source.read_bytes())
    return True


def _replace_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)


def _spool_contract_matches(metadata: Mapping[str, object] | None, expected: Mapping[str, object], map_sha: str, chunk_size: int) -> bool:
    if metadata is None:
        return False
    if int(metadata.get("schemaVersion", -1)) != 1:
        return False
    if int(metadata.get("chunkSize", -1)) != chunk_size:
        return False
    if str(metadata.get("sourceSha256", "")) != map_sha:
        return False
    return all(metadata.get(key) == value for key, value in expected.items())


def _normalized_hashes(value: Mapping[str, object] | None) -> dict[str, str] | None:
    if value is None:
        return None
    normalized: dict[str, str] = {}
    for key, digest in value.items():
        if not isinstance(key, str) or not isinstance(digest, str):
            return None
        normalized[key] = digest
    return normalized


def _prepare_spool(
    map_path: Path,
    output: Path,
    state_root: Path,
    chunk_size: int,
    spool_contract: Mapping[str, object],
    spool_builder: SpoolBuilder,
    *,
    expected_spool_hashes: Mapping[str, object] | None = None,
    allow_unbound_legacy_reuse: bool = False,
) -> tuple[Path, dict[str, object]]:
    stable = output / ".spool"
    map_sha = sha256_file(map_path)
    metadata = _read_json(stable / "spool.json")
    auxiliary_ok = (stable / "facts.json").is_file() and (stable / "tile-facts").is_dir()
    contract_ok = _spool_contract_matches(metadata, spool_contract, map_sha, chunk_size) and auxiliary_ok
    expected_hashes = _normalized_hashes(expected_spool_hashes)
    integrity_mismatch = False
    if contract_ok:
        current_hashes = spool_hashes(stable)
        if expected_hashes is not None and current_hashes == expected_hashes:
            return stable, {
                "parsed": False,
                "integrity": "verified",
                "renderShards": {"changed": [], "reused": sorted(current_hashes), "deleted": []},
                "tileFacts": {"changed": [], "reused": [], "deleted": []},
                "factsChanged": False,
            }
        if expected_hashes is None and allow_unbound_legacy_reuse:
            return stable, {
                "parsed": False,
                "integrity": "legacy-adoption-bound-on-commit",
                "renderShards": {"changed": [], "reused": sorted(current_hashes), "deleted": []},
                "tileFacts": {"changed": [], "reused": [], "deleted": []},
                "factsChanged": False,
            }
        integrity_mismatch = expected_hashes is not None

    candidate = state_root / "spool-candidate"
    if candidate.exists():
        shutil.rmtree(candidate)
    spool_builder(map_path, candidate, chunk_size)
    candidate_metadata = _read_json(candidate / "spool.json")
    if candidate_metadata is None:
        raise RuntimeError("Atlas spool builder did not produce spool.json")
    normalized_metadata = dict(candidate_metadata)
    normalized_metadata["schemaVersion"] = 1
    normalized_metadata["sourceSha256"] = map_sha
    for key, value in spool_contract.items():
        normalized_metadata[key] = value
    write_json_atomic(candidate / "spool.json", normalized_metadata)

    stable_metadata = _read_json(stable / "spool.json")
    if stable.exists() and stable_metadata and int(stable_metadata.get("chunkSize", -1)) == chunk_size:
        render_reconciliation = reconcile_spool(candidate, stable)
        facts_changed = _copy_if_changed(candidate / "facts.json", stable / "facts.json")
        tile_fact_reconciliation = _reconcile_aux_tree(candidate / "tile-facts", stable / "tile-facts", ".jsonl")
    else:
        _replace_tree(candidate, stable)
        hashes = spool_hashes(stable)
        render_reconciliation = {"changed": sorted(hashes), "reused": [], "deleted": []}
        tile_hashes = _file_hashes(stable / "tile-facts", ".jsonl")
        tile_fact_reconciliation = {"changed": sorted(tile_hashes), "reused": [], "deleted": []}
        facts_changed = True

    if candidate.exists():
        shutil.rmtree(candidate)
    stale_index = state_root / "spool-index.json"
    if stale_index.exists():
        stale_index.unlink()
    return stable, {
        "parsed": True,
        "integrity": "repaired-from-canonical-source" if integrity_mismatch else "rebuilt-from-canonical-source",
        "renderShards": render_reconciliation,
        "tileFacts": tile_fact_reconciliation,
        "factsChanged": facts_changed,
    }


def _manifest_chunk_keys(manifest: Mapping[str, object] | None) -> set[str]:
    if not manifest:
        return set()
    chunks = manifest.get("chunks", [])
    if not isinstance(chunks, list):
        return set()
    result: set[str] = set()
    for chunk in chunks:
        if not isinstance(chunk, Mapping):
            continue
        try:
            result.add(ChunkKey(int(chunk["z"]), int(chunk["chunkX"]), int(chunk["chunkY"])).text)
        except (KeyError, TypeError, ValueError):
            continue
    return result


def _detail_files_exist(output: Path, chunk_text: str) -> bool:
    key = ChunkKey.parse(chunk_text)
    tile = output / "tiles" / f"z{key.z}" / f"{key.x}_{key.y}.png"
    return tile.is_file() and tile.with_suffix(".json").is_file()


def remove_deleted_chunk_outputs(output: Path, chunk_keys: list[str]) -> None:
    for text in chunk_keys:
        key = ChunkKey.parse(text)
        for directory in ("tiles", "overview", "overview-low"):
            path = output / directory / f"z{key.z}" / f"{key.x}_{key.y}.png"
            report = path.with_suffix(".json")
            if path.exists():
                path.unlink()
            if report.exists():
                report.unlink()


def prepare_production_render_plan(
    map_path: Path,
    asset_dir: Path,
    output: Path,
    repository_root: Path,
    chunk_size: int,
    expected_sources: Mapping[str, object],
    spool_contract: Mapping[str, object],
    spool_builder: SpoolBuilder,
    *,
    allow_full_build: bool = False,
) -> dict[str, object]:
    """Return local fingerprints and the exact set of detail chunks to render.

    A pre-incremental Atlas can be adopted without rewriting its image corpus
    when its published source identity exactly matches the current canonical
    source.  The first successful run records local fingerprints; subsequent
    runs compare those fingerprints instead of a whole-map/tree SHA.
    """
    state_root = output / ".incremental-state"
    state_root.mkdir(parents=True, exist_ok=True)
    state_path = state_root / "production-render-state.json"
    invalid_state = False
    try:
        previous = _read_json(state_path)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        previous = None
        invalid_state = True

    manifest = _read_json(output / "manifest.json")
    asset_state = collect_asset_state(asset_dir)
    render_digest = render_contract_digest(repository_root)
    full_reasons: set[str] = set()
    if invalid_state:
        full_reasons.add("PRODUCTION_STATE_INVALID")
    if previous is not None:
        if int(previous.get("stateVersion", -1)) != PRODUCTION_STATE_VERSION:
            full_reasons.add("PRODUCTION_STATE_VERSION_CHANGED")
        if int(previous.get("chunkSize", -1)) != chunk_size:
            full_reasons.add("CHUNK_SIZE_CHANGED")
        if int(previous.get("renderCoreVersion", -1)) != RENDER_CORE_VERSION:
            full_reasons.add("RENDER_CORE_VERSION_CHANGED")
        if str(previous.get("renderContractDigest", "")) != render_digest:
            full_reasons.add("RENDER_CONTRACT_CHANGED")
        if previous.get("gutterProfile") != asset_state.get("gutterProfile"):
            full_reasons.add("GLOBAL_GUTTER_PROFILE_CHANGED")
    elif manifest is not None and int(manifest.get("chunkSize", chunk_size)) != chunk_size:
        full_reasons.add("CHUNK_SIZE_CHANGED")

    if full_reasons and not allow_full_build:
        reasons = ", ".join(sorted(full_reasons))
        raise RuntimeError(f"full Atlas detail rebuild is required but not authorized: {reasons}; rerun explicitly with --allow-full-build")

    manifest_sources = manifest.get("sources") if manifest and isinstance(manifest.get("sources"), Mapping) else None
    legacy_adoption = previous is None and _same_source(manifest_sources, expected_sources)
    previous_spool_hashes = previous.get("spoolChunkHashes") if previous and isinstance(previous.get("spoolChunkHashes"), Mapping) else None
    stable_spool, spool_report = _prepare_spool(
        map_path,
        output,
        state_root,
        chunk_size,
        spool_contract,
        spool_builder,
        expected_spool_hashes=previous_spool_hashes,
        allow_unbound_legacy_reuse=legacy_adoption,
    )
    current_spool_hashes = spool_hashes(stable_spool)
    dependency_index, dependency_report = prepare_dependency_index(stable_spool, asset_dir, state_root)
    records = dependency_index.get("chunks", {})
    if not isinstance(records, Mapping):
        raise ValueError("production dependency index has no chunks mapping")
    fingerprints = {
        str(text): detail_fingerprint(record, asset_state, render_digest)
        for text, record in records.items()
        if isinstance(text, str) and isinstance(record, Mapping)
    }

    previous_fingerprints = previous.get("chunkFingerprints", {}) if previous and isinstance(previous.get("chunkFingerprints"), Mapping) else {}
    old_keys = set(str(key) for key in previous_fingerprints) if previous is not None else _manifest_chunk_keys(manifest)
    current_keys = set(fingerprints)
    deleted = sorted(old_keys - current_keys, key=lambda text: (ChunkKey.parse(text).z, ChunkKey.parse(text).y, ChunkKey.parse(text).x))

    dirty: list[str] = []
    reused: list[str] = []
    for text in sorted(current_keys, key=lambda value: (ChunkKey.parse(value).z, ChunkKey.parse(value).y, ChunkKey.parse(value).x)):
        exists = _detail_files_exist(output, text)
        if full_reasons and allow_full_build:
            dirty.append(text)
        elif previous is not None and previous_fingerprints.get(text) == fingerprints[text] and exists:
            reused.append(text)
        elif legacy_adoption and exists:
            reused.append(text)
        else:
            dirty.append(text)

    next_state = {
        "stateVersion": PRODUCTION_STATE_VERSION,
        "chunkSize": chunk_size,
        "renderCoreVersion": RENDER_CORE_VERSION,
        "renderContractDigest": render_digest,
        "gutterProfile": asset_state.get("gutterProfile"),
        "assetStateDigest": asset_state.get("stateDigest"),
        "mapSha256": sha256_file(map_path),
        "spoolChunkHashes": dict(sorted(current_spool_hashes.items())),
        "chunkFingerprints": dict(sorted(fingerprints.items())),
        "adoptedLegacyPublication": legacy_adoption,
    }
    return {
        "schemaVersion": PRODUCTION_STATE_VERSION,
        "spoolDir": str(stable_spool),
        "dirtyDetailChunks": dirty,
        "reusedDetailChunks": reused,
        "deletedDetailChunks": deleted,
        "chunkFingerprints": fingerprints,
        "fullBuildRequired": bool(full_reasons),
        "fullBuildReasons": sorted(full_reasons),
        "legacyPublicationAdopted": legacy_adoption,
        "spool": spool_report,
        "dependencies": dependency_report,
        "nextState": next_state,
    }


def commit_production_render_state(output: Path, plan: Mapping[str, object]) -> None:
    state = plan.get("nextState")
    if not isinstance(state, Mapping):
        raise ValueError("production render plan has no nextState")
    write_json_atomic(output / ".incremental-state" / "production-render-state.json", dict(state))
