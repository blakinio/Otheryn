"""Resumable, locally invalidated environment-animation exporter.

The browser contract remains schema 2. Export work is checkpointed per canonical
chunk and, on multi-core hosts, heavy chunks are processed by persistent worker
processes. Pixel-composition behaviour remains sourced from environment_animation.
"""
from __future__ import annotations

from collections import OrderedDict
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import tempfile
import threading
import time
from typing import Any

from .assets import encode_png
from .render import AssetRenderer, _blend
from .environment_animation import (
    ANIMATION_ZOOM,
    _candidate_details,
    _durations,
    _has_alpha,
    _hooks,
    _items,
    _opaque_composite,
    _overlap_conflicts,
    _overlap_radius,
    _phase_rgba,
    _rect,
)
from .environment_incremental import EnvironmentAssetFingerprinter, environment_contract_fingerprint
from .environment_spool import decode_spool_tiles

# v3 changes checkpoint identity from monolithic manifest.sources/chunk-list hashing
# to a global semantic contract plus local spool/appearance/sprite content.
EXPORT_VERSION = 3
_DEFAULT_WORKER_CAP = 4
_PHASE_CACHE_LIMIT = 512
_FILE_DIGEST_CACHE_LIMIT = 8192
_HEARTBEAT_SECONDS = 60.0

_WORKER_RENDERER: AssetRenderer | None = None
_WORKER_FINGERPRINTER: EnvironmentAssetFingerprinter | None = None
_WORKER_OUTPUT: Path | None = None
_WORKER_SOURCE_FINGERPRINT: str | None = None
_WORKER_RADIUS: int | None = None
_WORKER_PHASE_CACHE: OrderedDict[str, tuple[bytes, ...]] = OrderedDict()
_WORKER_FRAME_CACHE: OrderedDict[str, tuple[bytes, ...]] = OrderedDict()
_FILE_DIGEST_CACHE: OrderedDict[str, str] = OrderedDict()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _remember_file_digest(path: Path, digest: str) -> None:
    key = path.as_posix()
    _FILE_DIGEST_CACHE.pop(key, None)
    _FILE_DIGEST_CACHE[key] = digest
    while len(_FILE_DIGEST_CACHE) > _FILE_DIGEST_CACHE_LIMIT:
        _FILE_DIGEST_CACHE.popitem(last=False)


def _atomic_bytes(path: Path, payload: bytes) -> None:
    """Atomically publish bytes with a process-unique temporary name.

    Multiple environment workers can legitimately materialize the same
    content-addressed asset. A fixed ``.tmp`` name is therefore not safe.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _atomic_json(path: Path, value: Any) -> None:
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _atomic_bytes(path, payload)
    _remember_file_digest(path, hashlib.sha256(payload).hexdigest())


def _atomic_compact_json(path: Path, value: Any) -> None:
    payload = (json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")
    _atomic_bytes(path, payload)
    _remember_file_digest(path, hashlib.sha256(payload).hexdigest())


def _payload_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _ensure_bytes(path: Path, payload: bytes) -> str:
    expected = _payload_sha256(payload)
    key = path.as_posix()
    cached = _FILE_DIGEST_CACHE.get(key)
    if cached == expected and path.is_file():
        _FILE_DIGEST_CACHE.move_to_end(key)
        return expected
    if not path.is_file() or _sha256(path) != expected:
        _atomic_bytes(path, payload)
    _remember_file_digest(path, expected)
    return expected


def _content_png(output: Path, kind: str, width: int, height: int, pixels: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(struct.pack(">II", width, height))
    digest.update(pixels)
    hexdigest = digest.hexdigest()
    relative = f"data/environment-animations/{kind}/{hexdigest[:2]}/{hexdigest}.png"
    path = output / relative
    _ensure_bytes(path, encode_png(width, height, pixels))
    return relative


def _record_assets(record: dict[str, Any]) -> set[str]:
    result = {value for value in record.get("frames", []) if isinstance(value, str)}
    for key in ("underlay", "overdraw"):
        value = record.get(key)
        if isinstance(value, str):
            result.add(value)
    return result


def _valid_checkpoint(output: Path, checkpoint: dict[str, Any], fingerprint: str) -> bool:
    if checkpoint.get("exportVersion") != EXPORT_VERSION or checkpoint.get("fingerprint") != fingerprint:
        return False
    records = int(checkpoint.get("instances", -1))
    if records < 0:
        return False
    shard = checkpoint.get("shard")
    if records:
        if not isinstance(shard, str) or not (output / shard).is_file():
            return False
        shard_checksum = checkpoint.get("shardChecksum")
        if not isinstance(shard_checksum, str) or _sha256(output / shard) != shard_checksum:
            return False
        try:
            payload = json.loads((output / shard).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        values = payload.get("records", []) if isinstance(payload, dict) else []
        if not isinstance(values, list) or len(values) != records:
            return False
        expected_assets = sorted({path for record in values if isinstance(record, dict) for path in _record_assets(record)})
        if expected_assets != checkpoint.get("assets", []):
            return False
    elif shard is not None or checkpoint.get("shardChecksum") is not None:
        return False
    assets = checkpoint.get("assets", [])
    checksums = checkpoint.get("assetChecksums")
    if not isinstance(assets, list) or not isinstance(checksums, dict) or set(checksums) != set(assets):
        return False
    for relative in assets:
        path = output / relative
        expected = checksums.get(relative)
        if not path.is_file() or not isinstance(expected, str) or _sha256(path) != expected:
            return False
    return True


def _prepare_root(root: Path, source_fingerprint: str) -> None:
    state_path = root / "export-state.json"
    compatible = False
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            compatible = state.get("exportVersion") == EXPORT_VERSION and state.get("sourceFingerprint") == source_fingerprint
        except (OSError, json.JSONDecodeError):
            compatible = False
    if root.exists() and not compatible:
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    _atomic_json(
        state_path,
        {
            "schemaVersion": 1,
            "exportVersion": EXPORT_VERSION,
            "sourceFingerprint": source_fingerprint,
            "status": "active",
        },
    )


def _prune_unreachable_files(root: Path, live_paths: set[Path]) -> None:
    if not root.exists():
        return
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        if path not in live_paths:
            path.unlink()
    for directory in sorted((candidate for candidate in root.rglob("*") if candidate.is_dir()), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass


def _effective_worker_count(requested: int | None, work_items: int) -> int:
    if work_items <= 1:
        return 1
    cpu_count = max(1, os.cpu_count() or 1)
    if requested is None:
        configured = os.environ.get("OTBM_ATLAS_ENV_WORKERS")
        requested = int(configured) if configured else min(cpu_count, _DEFAULT_WORKER_CAP)
    if requested <= 0:
        raise ValueError("environment animation worker count must be positive")
    return max(1, min(int(requested), cpu_count, work_items))


def _chunk_text(chunk: dict[str, Any]) -> str:
    return f"z{int(chunk['z'])}/{int(chunk['chunkX'])}_{int(chunk['chunkY'])}"


def _chunk_weight(output: Path, spool: Path, chunk: dict[str, Any]) -> tuple[int, int, int]:
    """Use prior measured work when available; otherwise use local spool bytes.

    Sorting descending starts known stragglers first while ProcessPoolExecutor's
    shared queue naturally gives idle workers the next chunk.
    """
    z, chunk_x, chunk_y = int(chunk["z"]), int(chunk["chunkX"]), int(chunk["chunkY"])
    spool_path = spool / f"z{z}" / f"{chunk_x}_{chunk_y}.bin"
    spool_bytes = spool_path.stat().st_size if spool_path.is_file() else 0
    checkpoint_path = output / "data/environment-animations/checkpoints" / f"z{z}" / f"{chunk_x}_{chunk_y}.json"
    if checkpoint_path.is_file():
        try:
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            measured = max(0, int(checkpoint.get("instances", 0))) + max(0, int(checkpoint.get("staticFallbacks", 0)))
            return 1, measured, spool_bytes
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    return 0, 0, spool_bytes


def _worker_init(asset_dir: str, output: str, source_fingerprint: str, radius: int) -> None:
    global _WORKER_RENDERER, _WORKER_FINGERPRINTER, _WORKER_OUTPUT, _WORKER_SOURCE_FINGERPRINT, _WORKER_RADIUS
    global _WORKER_PHASE_CACHE, _WORKER_FRAME_CACHE, _FILE_DIGEST_CACHE
    _WORKER_RENDERER = AssetRenderer(Path(asset_dir))
    _WORKER_FINGERPRINTER = EnvironmentAssetFingerprinter(_WORKER_RENDERER)
    _WORKER_OUTPUT = Path(output)
    _WORKER_SOURCE_FINGERPRINT = source_fingerprint
    _WORKER_RADIUS = int(radius)
    _WORKER_PHASE_CACHE = OrderedDict()
    _WORKER_FRAME_CACHE = OrderedDict()
    _FILE_DIGEST_CACHE = OrderedDict()


def _lru_store(cache: OrderedDict[str, tuple[bytes, ...]], key: str, value: tuple[bytes, ...]) -> tuple[bytes, ...]:
    cache.pop(key, None)
    cache[key] = value
    while len(cache) > _PHASE_CACHE_LIMIT:
        cache.popitem(last=False)
    return value


def _phase_pixels_cached(key: str, details: Any) -> tuple[bytes, ...]:
    if _WORKER_RENDERER is None:
        raise RuntimeError("environment worker renderer is not initialized")
    cached = _WORKER_PHASE_CACHE.get(key)
    if cached is not None:
        _WORKER_PHASE_CACHE.move_to_end(key)
        return cached
    phases: list[bytes] = []
    for phase in range(details.frame.animation_phases):
        phase_width, phase_height, pixels = _phase_rgba(_WORKER_RENDERER, details.frame, details.px, details.py, details.pz, phase)
        if (phase_width, phase_height) != (details.width, details.height):
            raise ValueError("animation phase geometry changed after candidate validation")
        phases.append(pixels)
    return _lru_store(_WORKER_PHASE_CACHE, key, tuple(phases))


def _frame_pngs_cached(key: str, details: Any, phase_pixels: tuple[bytes, ...]) -> tuple[bytes, ...]:
    cached = _WORKER_FRAME_CACHE.get(key)
    if cached is not None:
        _WORKER_FRAME_CACHE.move_to_end(key)
        return cached
    encoded = tuple(encode_png(details.width, details.height, pixels) for pixels in phase_pixels)
    return _lru_store(_WORKER_FRAME_CACHE, key, encoded)


def _paint_cached(
    canvas: bytearray,
    patch_left: int,
    patch_top: int,
    width: int,
    height: int,
    tile: Any,
    stack_index: int,
    item: Any,
    south: bool,
    east: bool,
    tile_order: int,
    paint_cache: dict[tuple[int, int], tuple[Any, ...]],
) -> None:
    if _WORKER_RENDERER is None:
        raise RuntimeError("environment worker renderer is not initialized")
    cache_key = (tile_order, stack_index)
    rendered = paint_cache.get(cache_key)
    if rendered is None:
        rendered = tuple(_WORKER_RENDERER.item_sprites(item, tile.position.x, tile.position.y, tile.position.z, south, east))
        paint_cache[cache_key] = rendered
    for appearance, _sprite_id, (sprite_width, sprite_height, pixels) in rendered:
        shift_x, shift_y = appearance.shift or (0, 0)
        height_offset = appearance.height or 0
        draw_x = tile.position.x * 32 - patch_left - (sprite_width - 32) - shift_x - height_offset
        draw_y = tile.position.y * 32 - patch_top - (sprite_height - 32) - shift_y - height_offset
        _blend(canvas, width, height, pixels, sprite_width, sprite_height, draw_x, draw_y)


def _compose_context_cached(
    by_pos: dict[tuple[int, int], Any],
    order_by_pos: dict[tuple[int, int], int],
    items_by_pos: dict[tuple[int, int], list[Any]],
    hooks_by_pos: dict[tuple[int, int], tuple[bool, bool]],
    target_tile: Any,
    target_stack_index: int,
    details: Any,
    radius: int,
    nearby_cache: dict[tuple[int, int], tuple[tuple[int, Any], ...]],
    paint_cache: dict[tuple[int, int], tuple[Any, ...]],
) -> tuple[bytes, bytes]:
    patch_left, patch_top, _patch_right, _patch_bottom = _rect(details, target_tile.position.x, target_tile.position.y)
    width, height = details.width, details.height
    underlay = bytearray(width * height * 4)
    overdraw = bytearray(width * height * 4)
    target_position = (target_tile.position.x, target_tile.position.y)
    target_key = (order_by_pos[target_position], target_stack_index)
    nearby = nearby_cache.get(target_position)
    if nearby is None:
        values: list[tuple[int, Any]] = []
        for nx in range(target_tile.position.x - radius, target_tile.position.x + radius + 1):
            for ny in range(target_tile.position.y - radius, target_tile.position.y + radius + 1):
                tile = by_pos.get((nx, ny))
                if tile is not None:
                    values.append((order_by_pos[(nx, ny)], tile))
        nearby = tuple(sorted(values, key=lambda pair: pair[0]))
        nearby_cache[target_position] = nearby
    for tile_order, tile in nearby:
        position = (tile.position.x, tile.position.y)
        items = items_by_pos[position]
        south, east = hooks_by_pos[position]
        for stack_index, item in enumerate(items):
            key = (tile_order, stack_index)
            if key == target_key:
                continue
            canvas = underlay if key < target_key else overdraw
            _paint_cached(canvas, patch_left, patch_top, width, height, tile, stack_index, item, south, east, tile_order, paint_cache)
    return bytes(underlay), bytes(overdraw)


def _heartbeat(chunk: str, started: float, stopped: threading.Event) -> None:
    while not stopped.wait(_HEARTBEAT_SECONDS):
        print(
            f"ENV_ANIM_HEARTBEAT pid={os.getpid()} chunk={chunk} elapsed={time.monotonic() - started:.1f}s",
            flush=True,
        )


def _process_chunk(job: tuple[int, int, dict[str, Any]]) -> dict[str, Any]:
    if _WORKER_RENDERER is None or _WORKER_FINGERPRINTER is None or _WORKER_OUTPUT is None or _WORKER_SOURCE_FINGERPRINT is None or _WORKER_RADIUS is None:
        raise RuntimeError("environment worker is not initialized")
    ordinal, total, chunk = job
    output = _WORKER_OUTPUT
    radius = _WORKER_RADIUS
    z, chunk_x, chunk_y = int(chunk["z"]), int(chunk["chunkX"]), int(chunk["chunkY"])
    text = f"z{z}/{chunk_x}_{chunk_y}"
    spool_path = output / ".spool" / f"z{z}" / f"{chunk_x}_{chunk_y}.bin"
    checkpoint_path = output / "data/environment-animations/checkpoints" / f"z{z}" / f"{chunk_x}_{chunk_y}.json"
    started = time.monotonic()
    stopped = threading.Event()
    heartbeat = threading.Thread(target=_heartbeat, args=(text, started, stopped), daemon=True)
    print(f"ENV_ANIM_CHUNK_START pid={os.getpid()} chunk={text} ordinal={ordinal}/{total}", flush=True)
    heartbeat.start()
    try:
        fingerprint = _WORKER_FINGERPRINTER.chunk_fingerprint(_WORKER_SOURCE_FINGERPRINT, spool_path, chunk["logicalBounds"])
        checkpoint: dict[str, Any] | None = None
        if checkpoint_path.is_file():
            try:
                candidate = json.loads(checkpoint_path.read_text(encoding="utf-8"))
                if isinstance(candidate, dict) and _valid_checkpoint(output, candidate, fingerprint):
                    checkpoint = candidate
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                checkpoint = None
        if checkpoint is not None:
            elapsed = time.monotonic() - started
            return {
                "ordinal": ordinal,
                "chunk": text,
                "status": "reused",
                "instances": int(checkpoint["instances"]),
                "staticFallbacks": int(checkpoint["staticFallbacks"]),
                "animationKeys": [str(key) for key in checkpoint.get("animationKeys", [])],
                "assets": [str(path) for path in checkpoint.get("assets", [])],
                "shard": checkpoint.get("shard"),
                "checkpoint": checkpoint_path.as_posix(),
                "elapsedSeconds": elapsed,
            }

        tiles = list(decode_spool_tiles(spool_path))
        by_pos = {(tile.position.x, tile.position.y): tile for tile in tiles}
        order_by_pos = {(tile.position.x, tile.position.y): index for index, tile in enumerate(tiles)}
        items_by_pos: dict[tuple[int, int], list[Any]] = {}
        hooks_by_pos: dict[tuple[int, int], tuple[bool, bool]] = {}
        x1, x2, y1, y2, _ = map(int, chunk["logicalBounds"])
        candidates = []
        chunk_fallbacks = 0
        for tile in tiles:
            position = (tile.position.x, tile.position.y)
            items = _items(tile)
            items_by_pos[position] = items
            if not items:
                hooks_by_pos[position] = (False, False)
                continue
            south, east = _hooks(items, _WORKER_RENDERER)
            hooks_by_pos[position] = (south, east)
            for stack_index, item in enumerate(items):
                appearance = _WORKER_RENDERER.appearances.get(item.server_id)
                if not appearance or not appearance.frames or appearance.frames[0].animation_phases <= 1:
                    continue
                details = _candidate_details(_WORKER_RENDERER, item, tile.position.x, tile.position.y, tile.position.z, south, east)
                if details is None:
                    chunk_fallbacks += 1
                    continue
                candidates.append((tile, stack_index, item, details, _rect(details, tile.position.x, tile.position.y), south, east))

        conflicts = _overlap_conflicts([candidate[4] for candidate in candidates])
        records: list[dict[str, Any]] = []
        chunk_keys: set[str] = set()
        chunk_assets: set[str] = set()
        nearby_cache: dict[tuple[int, int], tuple[tuple[int, Any], ...]] = {}
        paint_cache: dict[tuple[int, int], tuple[Any, ...]] = {}
        for index, (tile, stack_index, item, details, _visual_rect, south, east) in enumerate(candidates):
            x, y = tile.position.x, tile.position.y
            if index in conflicts:
                chunk_fallbacks += 1
                continue
            if x - x1 < radius or x2 - x < radius or y - y1 < radius or y2 - y < radius:
                chunk_fallbacks += 1
                continue
            subtype = -1 if item.subtype is None else int(item.subtype)
            key = f"{item.server_id}-{subtype}-{details.px}-{details.py}-{details.pz}-{int(south)}-{int(east)}"
            underlay_pixels, overdraw_pixels = _compose_context_cached(
                by_pos,
                order_by_pos,
                items_by_pos,
                hooks_by_pos,
                tile,
                stack_index,
                details,
                radius,
                nearby_cache,
                paint_cache,
            )
            phase_pixels = _phase_pixels_cached(key, details)
            if not _opaque_composite(underlay_pixels, overdraw_pixels, list(phase_pixels), details.width, details.height):
                chunk_fallbacks += 1
                continue

            frames = [f"data/environment-animations/frames/{key}/{phase}.png" for phase in range(details.frame.animation_phases)]
            encoded_frames = _frame_pngs_cached(key, details, phase_pixels)
            for relative, payload in zip(frames, encoded_frames, strict=True):
                _ensure_bytes(output / relative, payload)
                chunk_assets.add(relative)
            chunk_keys.add(key)

            underlay = _content_png(output, "underlays", details.width, details.height, underlay_pixels)
            chunk_assets.add(underlay)
            overdraw: str | None = None
            if _has_alpha(overdraw_pixels):
                overdraw = _content_png(output, "overdraws", details.width, details.height, overdraw_pixels)
                chunk_assets.add(overdraw)

            ranges = _durations(details.frame)
            loop = -1 if details.frame.loop_type > 1 else details.frame.loop_type
            record: dict[str, Any] = {
                "position": {"x": x, "y": y, "z": tile.position.z},
                "serverId": item.server_id,
                "animationKey": key,
                "frames": frames,
                "underlay": underlay,
                "spriteSize": [details.width, details.height],
                "drawOffsetPixels": [details.offset_x, details.offset_y],
                "stackIndex": stack_index,
                "stackSize": len(items_by_pos[(tile.position.x, tile.position.y)]),
                "phaseDurationsMs": [max(1, (low + high) // 2) for low, high in ranges],
                "durationRangesMs": [[low, high] for low, high in ranges],
                "defaultStartPhase": details.frame.default_start_phase,
                "synchronized": details.frame.synchronized,
                "randomStartPhase": details.frame.random_start_phase,
                "loopType": loop,
                "loopCount": details.frame.loop_count,
                "policy": "cyclic-appearance-composited",
            }
            if overdraw is not None:
                record["overdraw"] = overdraw
            if item.subtype is not None:
                record["subtype"] = item.subtype
            records.append(record)

        shard_relative: str | None = None
        canonical_shard_relative = f"data/environment-animations/chunks/z{z}/{chunk_x}_{chunk_y}.json"
        canonical_shard_path = output / canonical_shard_relative
        if records:
            shard_relative = canonical_shard_relative
            _atomic_compact_json(canonical_shard_path, {"schemaVersion": 2, "records": records})
        elif canonical_shard_path.exists():
            canonical_shard_path.unlink()

        sorted_assets = sorted(chunk_assets)
        checkpoint = {
            "schemaVersion": 1,
            "exportVersion": EXPORT_VERSION,
            "fingerprint": fingerprint,
            "instances": len(records),
            "staticFallbacks": chunk_fallbacks,
            "animationKeys": sorted(chunk_keys),
            "assets": sorted_assets,
            "assetChecksums": {relative: _sha256(output / relative) for relative in sorted_assets},
            "shard": shard_relative,
            "shardChecksum": _sha256(canonical_shard_path) if records else None,
        }
        _atomic_json(checkpoint_path, checkpoint)
        elapsed = time.monotonic() - started
        return {
            "ordinal": ordinal,
            "chunk": text,
            "status": "built",
            "instances": len(records),
            "staticFallbacks": chunk_fallbacks,
            "animationKeys": sorted(chunk_keys),
            "assets": sorted_assets,
            "shard": shard_relative,
            "checkpoint": checkpoint_path.as_posix(),
            "elapsedSeconds": elapsed,
        }
    finally:
        stopped.set()
        heartbeat.join(timeout=1.0)


def _accumulate_result(
    result: dict[str, Any],
    output: Path,
    animation_keys: set[str],
    live_assets: set[str],
    live_checkpoints: set[Path],
    live_shards: set[Path],
) -> tuple[int, int, int, int]:
    instances = int(result.get("instances", 0))
    fallbacks = int(result.get("staticFallbacks", 0))
    reused = 1 if result.get("status") == "reused" else 0
    chunks_with_records = 1 if instances else 0
    animation_keys.update(str(key) for key in result.get("animationKeys", []))
    live_assets.update(str(path) for path in result.get("assets", []))
    checkpoint = result.get("checkpoint")
    if isinstance(checkpoint, str):
        live_checkpoints.add(Path(checkpoint))
    shard = result.get("shard")
    if isinstance(shard, str):
        live_shards.add(output / shard)
    return instances, fallbacks, reused, chunks_with_records


def enrich_environment_animations_resumable(asset_dir: Path, output: Path, workers: int | None = None) -> dict[str, int]:
    manifest_path = output / "manifest.json"
    spool = output / ".spool"
    zero = {
        "instances": 0,
        "uniqueAnimations": 0,
        "chunks": 0,
        "staticFallbacks": 0,
        "completedChunks": 0,
        "reusedChunks": 0,
        "outputFiles": 0,
        "outputBytes": 0,
    }
    if not manifest_path.exists() or not (spool / "spool.json").exists():
        return zero

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_chunks = list(manifest.get("chunks", []))
    bootstrap_renderer = AssetRenderer(asset_dir)
    radius = _overlap_radius(bootstrap_renderer)
    source_fingerprint = environment_contract_fingerprint(
        manifest,
        export_version=EXPORT_VERSION,
        overlap_radius=radius,
    )
    root = output / "data" / "environment-animations"
    _prepare_root(root, source_fingerprint)

    animation_keys: set[str] = set()
    live_assets: set[str] = set()
    live_checkpoints: set[Path] = set()
    live_shards: set[Path] = set()
    instances = chunks_with_records = fallbacks = reused = 0
    total = len(manifest_chunks)
    jobs: list[tuple[int, int, dict[str, Any]]] = []
    no_spool = 0
    for ordinal, raw_chunk in enumerate(manifest_chunks, start=1):
        chunk = dict(raw_chunk)
        z, chunk_x, chunk_y = int(chunk["z"]), int(chunk["chunkX"]), int(chunk["chunkY"])
        spool_path = spool / f"z{z}" / f"{chunk_x}_{chunk_y}.bin"
        if not spool_path.is_file():
            no_spool += 1
            print(f"ENV_ANIM_PROGRESS completed={no_spool}/{total} reused=0 chunk=z{z}/{chunk_x}_{chunk_y} status=no-spool", flush=True)
            continue
        jobs.append((ordinal, total, chunk))

    jobs.sort(key=lambda value: _chunk_weight(output, spool, value[2]), reverse=True)
    effective_workers = _effective_worker_count(workers, len(jobs)) if jobs else 1
    print(
        f"ENV_ANIM_EXECUTOR workers={effective_workers} requested={workers if workers is not None else 'auto'} chunks={len(jobs)} noSpool={no_spool}",
        flush=True,
    )

    completed = no_spool
    if jobs and effective_workers == 1:
        _worker_init(str(asset_dir), str(output), source_fingerprint, radius)
        for job in jobs:
            result = _process_chunk(job)
            delta_instances, delta_fallbacks, delta_reused, delta_chunks = _accumulate_result(
                result, output, animation_keys, live_assets, live_checkpoints, live_shards
            )
            instances += delta_instances
            fallbacks += delta_fallbacks
            reused += delta_reused
            chunks_with_records += delta_chunks
            completed += 1
            print(
                f"ENV_ANIM_PROGRESS completed={completed}/{total} reused={reused} chunk={result['chunk']} status={result['status']} instances={delta_instances} fallbacks={delta_fallbacks} elapsed={float(result['elapsedSeconds']):.1f}s",
                flush=True,
            )
    elif jobs:
        with ProcessPoolExecutor(
            max_workers=effective_workers,
            initializer=_worker_init,
            initargs=(str(asset_dir), str(output), source_fingerprint, radius),
        ) as executor:
            futures = {executor.submit(_process_chunk, job): job for job in jobs}
            for future in as_completed(futures):
                result = future.result()
                delta_instances, delta_fallbacks, delta_reused, delta_chunks = _accumulate_result(
                    result, output, animation_keys, live_assets, live_checkpoints, live_shards
                )
                instances += delta_instances
                fallbacks += delta_fallbacks
                reused += delta_reused
                chunks_with_records += delta_chunks
                completed += 1
                print(
                    f"ENV_ANIM_PROGRESS completed={completed}/{total} reused={reused} chunk={result['chunk']} status={result['status']} instances={delta_instances} fallbacks={delta_fallbacks} elapsed={float(result['elapsedSeconds']):.1f}s",
                    flush=True,
                )

    # Global cleanup/finalization is coordinator-only. Workers may concurrently
    # materialize identical content-addressed assets, but never prune them.
    _prune_unreachable_files(root / "checkpoints", live_checkpoints)
    _prune_unreachable_files(root / "chunks", live_shards)
    for kind in ("frames", "underlays", "overdraws"):
        payload_root = root / kind
        if not payload_root.exists():
            continue
        for path in sorted(candidate for candidate in payload_root.rglob("*") if candidate.is_file()):
            relative = path.relative_to(output).as_posix()
            if relative not in live_assets:
                path.unlink()
        for directory in sorted((candidate for candidate in payload_root.rglob("*") if candidate.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass

    data_files = [path for path in root.rglob("*") if path.is_file() and path.name not in {"export-state.json", "index.json"}]
    output_bytes = sum(path.stat().st_size for path in data_files)
    stats = {
        "instances": instances,
        "uniqueAnimations": len(animation_keys),
        "chunks": chunks_with_records,
        "staticFallbacks": fallbacks,
        "completedChunks": total,
        "reusedChunks": reused,
        "outputFiles": len(data_files),
        "outputBytes": output_bytes,
    }
    index = {
        "schemaVersion": 2,
        "animationZoom": ANIMATION_ZOOM,
        "overlapSafetyRadiusTiles": radius,
        "statistics": stats,
        "exporter": {
            "version": EXPORT_VERSION,
            "sourceFingerprint": source_fingerprint,
            "workerProcesses": effective_workers,
            "scheduling": "historical-work/spool-weighted longest-first shared process queue",
            "resumePolicy": "reuse checkpointed chunks only when global environment contract, local spool, logical bounds, used appearance semantics, exact referenced sprite pixels and referenced output bytes remain valid",
            "occurrenceAssetPolicy": "content-addressed deduplication for underlays and overdraws",
            "invalidationPolicy": "unrelated map/source/sprite changes do not invalidate checkpoints outside their dependent chunks; only global environment-contract or overlap-radius transitions reset the tree",
        },
        "policy": {
            "cyclicAppearance": "browser animated from pinned object appearance phases without GIF/WebP animation assets",
            "geometry": "32x32, 32x64, 64x32 and 64x64 sprite sheets with canonical shift/height offsets",
            "stacking": "safe ground and non-topmost entries use canonical per-instance composition",
            "statefulAppearance": "not inferred; server-driven variants remain canonical static state",
            "eligibility": "decodable cyclic object whose replacement patch is opaque and does not overlap another animated instance or a chunk edge safety zone",
            "fallback": "unsupported, conflicting, edge-risk or non-replaceable animations remain deterministic static pixels",
        },
    }
    _atomic_json(root / "index.json", index)
    _atomic_json(
        root / "export-state.json",
        {
            "schemaVersion": 1,
            "exportVersion": EXPORT_VERSION,
            "sourceFingerprint": source_fingerprint,
            "status": "complete",
            "statistics": stats,
        },
    )
    print(
        f"ENV_ANIM_DONE completed={total}/{total} reused={reused} workers={effective_workers} instances={instances} files={len(data_files)} bytes={output_bytes}",
        flush=True,
    )
    return stats
