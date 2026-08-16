"""Persistent, non-render state for Atlas change-impact builds.

The cache contains only spatial spool bytes and dependency metadata derived from
repository inputs. It never stores rendered Tibia/CipSoft imagery. State is
self-validating by exact source and per-chunk digests and may be discarded at
any time without changing correctness; a miss only costs another deterministic
parse/index pass.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
from typing import Mapping

from .incremental_core import (
    build_dependency_index,
    canonical_json,
    reconcile_spool,
    sha256_bytes,
    sha256_file,
    spool_hashes,
    spool_map,
    write_json_atomic,
)

STATE_CACHE_VERSION = 2
SPOOL_INDEX_VERSION = 1


def _read_json(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def _spool_matches(metadata: Mapping[str, object] | None, source_sha: str, chunk_size: int) -> bool:
    return bool(
        metadata
        and int(metadata.get("schemaVersion", -1)) == 1
        and int(metadata.get("chunkSize", -1)) == chunk_size
        and str(metadata.get("sourceSha256", "")) == source_sha
    )


def _chunk_digest(chunks: Mapping[str, str]) -> str:
    return sha256_bytes(canonical_json(dict(sorted(chunks.items()))))


def _write_spool_index(state_root: Path, stable: Path) -> dict[str, object]:
    metadata = _read_json(stable / "spool.json")
    if metadata is None:
        raise FileNotFoundError(stable / "spool.json")
    chunks = spool_hashes(stable)
    index: dict[str, object] = {
        "schemaVersion": SPOOL_INDEX_VERSION,
        "sourceSha256": str(metadata["sourceSha256"]),
        "chunkSize": int(metadata["chunkSize"]),
        "chunks": dict(sorted(chunks.items())),
        "chunksDigest": _chunk_digest(chunks),
    }
    write_json_atomic(state_root / "spool-index.json", index)
    return index


def _validated_cached_hashes(state_root: Path, stable: Path, source_sha: str, chunk_size: int) -> dict[str, str] | None:
    metadata = _read_json(stable / "spool.json")
    index = _read_json(state_root / "spool-index.json")
    if not _spool_matches(metadata, source_sha, chunk_size) or not index:
        return None
    if int(index.get("schemaVersion", -1)) != SPOOL_INDEX_VERSION:
        return None
    if str(index.get("sourceSha256", "")) != source_sha or int(index.get("chunkSize", -1)) != chunk_size:
        return None
    declared = index.get("chunks")
    if not isinstance(declared, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in declared.items()):
        return None
    declared_hashes = {str(key): str(value) for key, value in declared.items()}
    if str(index.get("chunksDigest", "")) != _chunk_digest(declared_hashes):
        return None
    actual = spool_hashes(stable)
    if actual != declared_hashes:
        return None
    return actual


def _replace_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)


def prepare_persistent_spool(
    base_map: Path,
    target_map: Path,
    work: Path,
    state_root: Path,
    chunk_size: int,
) -> tuple[dict[str, str], dict[str, str], Path, dict[str, object]]:
    """Prepare target spatial spool while reusing only byte-validated state.

    If the cached spool already matches the target map and every chunk digest is
    intact, no OTBM parse occurs. If it matches the base map, the base chunk
    hashes are reused and only the target map is parsed once; changed candidate
    chunks are reconciled into the stable spool. Any unrelated, legacy or
    corrupted cache is treated as a miss.
    """
    state_root.mkdir(parents=True, exist_ok=True)
    stable = state_root / "spool"
    stable_meta = _read_json(stable / "spool.json")
    base_sha = sha256_file(base_map)
    target_sha = sha256_file(target_map)
    target_cached_hashes = _validated_cached_hashes(state_root, stable, target_sha, chunk_size)
    base_cached_hashes = target_cached_hashes if base_sha == target_sha else _validated_cached_hashes(state_root, stable, base_sha, chunk_size)

    if target_cached_hashes is not None:
        target_hashes = target_cached_hashes
        if base_sha == target_sha:
            base_hashes = dict(target_hashes)
            base_source = "target-cache"
        else:
            base_spool = work / "base-spool"
            spool_map(base_map, base_spool, chunk_size)
            base_hashes = spool_hashes(base_spool)
            base_source = "parsed"
        report = {
            "schemaVersion": STATE_CACHE_VERSION,
            "cacheHit": True,
            "cacheIntegrity": "VERIFIED",
            "targetSpoolSource": "persistent-cache",
            "baseSpoolSource": base_source,
            "reconciliation": {"changed": [], "reused": sorted(target_hashes), "deleted": []},
        }
        return base_hashes, target_hashes, stable, report

    if base_cached_hashes is not None:
        base_hashes: dict[str, str] | None = base_cached_hashes
        base_source = "persistent-cache"
    else:
        base_hashes = None
        base_source = "parsed"

    candidate = work / "target-spool-candidate"
    spool_map(target_map, candidate, chunk_size)
    target_hashes = spool_hashes(candidate)
    if base_sha == target_sha:
        base_hashes = dict(target_hashes)
        base_source = "target-parse"
    elif base_hashes is None:
        base_spool = work / "base-spool"
        spool_map(base_map, base_spool, chunk_size)
        base_hashes = spool_hashes(base_spool)

    assert base_hashes is not None
    if stable.exists() and stable_meta and int(stable_meta.get("chunkSize", -1)) == chunk_size:
        reconciliation = reconcile_spool(candidate, stable)
    else:
        _replace_tree(candidate, stable)
        reconciliation = {"changed": sorted(target_hashes), "reused": [], "deleted": []}
    actual = spool_hashes(stable)
    if actual != target_hashes:
        raise RuntimeError("persistent spool promotion did not reproduce target chunk hashes")
    spool_index = _write_spool_index(state_root, stable)
    if spool_index["chunksDigest"] != _chunk_digest(target_hashes):
        raise RuntimeError("persistent spool index does not bind the promoted target bytes")
    report = {
        "schemaVersion": STATE_CACHE_VERSION,
        "cacheHit": base_cached_hashes is not None,
        "cacheIntegrity": "REBUILT" if base_cached_hashes is None else "VERIFIED_BASE",
        "targetSpoolSource": "parsed-and-promoted",
        "baseSpoolSource": base_source,
        "reconciliation": reconciliation,
    }
    return base_hashes, target_hashes, stable, report


def _appearance_catalog(asset_dir: Path) -> Path:
    matches = sorted(asset_dir.glob("appearances-*.dat"))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one appearances-*.dat under {asset_dir}, found {len(matches)}")
    return matches[0]


def _dependency_cache_identity(spool_dir: Path, asset_dir: Path, state_root: Path) -> dict[str, object]:
    spool_meta = _read_json(spool_dir / "spool.json")
    spool_index = _read_json(state_root / "spool-index.json")
    if spool_meta is None:
        raise FileNotFoundError(spool_dir / "spool.json")
    if spool_index is None:
        # Non-persistent callers may provide a valid spool but no durable index;
        # create the byte-binding manifest before dependency caching.
        spool_index = _write_spool_index(state_root, spool_dir)
    expected_hashes = _validated_cached_hashes(
        state_root,
        spool_dir,
        str(spool_meta["sourceSha256"]),
        int(spool_meta["chunkSize"]),
    )
    if expected_hashes is None:
        raise ValueError("dependency index cache requires a byte-validated spatial spool")
    return {
        "cacheVersion": STATE_CACHE_VERSION,
        "spoolSourceSha256": str(spool_meta["sourceSha256"]),
        "spoolChunksDigest": str(spool_index["chunksDigest"]),
        "chunkSize": int(spool_meta["chunkSize"]),
        "appearanceCatalogSha256": sha256_file(_appearance_catalog(asset_dir)),
    }


def prepare_dependency_index(spool_dir: Path, asset_dir: Path, state_root: Path) -> tuple[dict[str, object], dict[str, object]]:
    """Reuse a dependency index only for exact, byte-validated spatial inputs."""
    state_root.mkdir(parents=True, exist_ok=True)
    cache_path = state_root / "dependency-index.json"
    identity = _dependency_cache_identity(spool_dir, asset_dir, state_root)
    cached = _read_json(cache_path)
    if cached and cached.get("cacheIdentity") == identity and isinstance(cached.get("chunks"), dict):
        return cached, {"dependencyIndexCacheHit": True, "identity": identity}

    index = build_dependency_index(spool_dir, asset_dir)
    index["cacheIdentity"] = identity
    write_json_atomic(cache_path, index)
    return index, {"dependencyIndexCacheHit": False, "identity": identity}


def write_operational_state(work: Path, target_spool: Path, spatial_report: Mapping[str, object], dependency_report: Mapping[str, object]) -> None:
    """Record runner-local paths outside the canonical impact-plan digest."""
    write_json_atomic(
        work / "operational-state.json",
        {
            "schemaVersion": STATE_CACHE_VERSION,
            "targetSpool": str(target_spool.resolve()),
            "spatial": dict(spatial_report),
            "dependencies": dict(dependency_report),
        },
    )


def read_target_spool(work: Path) -> Path:
    state = _read_json(work / "operational-state.json")
    if state is None:
        return work / "target-spool"
    value = state.get("targetSpool")
    if not isinstance(value, str) or not value:
        raise ValueError("operational-state targetSpool is missing")
    path = Path(value)
    if not (path / "spool.json").is_file():
        raise FileNotFoundError(path / "spool.json")
    return path
