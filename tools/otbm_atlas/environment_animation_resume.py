"""Resumable full-world environment-animation exporter.

This module preserves the schema-2 browser contract from ``environment_animation``
while adding content-addressed occurrence assets, per-chunk checkpoints and
observable deterministic progress.  The legacy renderer helpers remain the
single source of pixel-composition behaviour.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import struct
from typing import Any

from .assets import encode_png
from .render import AssetRenderer
from .environment_animation import (
    ANIMATION_ZOOM,
    _candidate_details,
    _compose_context,
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
from .environment_spool import decode_spool_tiles

EXPORT_VERSION = 1


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def _source_fingerprint(manifest: dict[str, Any]) -> str:
    stable = {
        "exportVersion": EXPORT_VERSION,
        "schemaVersion": manifest.get("schemaVersion"),
        "chunkSize": manifest.get("chunkSize"),
        "sources": manifest.get("sources"),
        "chunks": [
            {
                "z": chunk.get("z"),
                "chunkX": chunk.get("chunkX"),
                "chunkY": chunk.get("chunkY"),
                "logicalBounds": chunk.get("logicalBounds"),
            }
            for chunk in manifest.get("chunks", [])
        ],
    }
    return hashlib.sha256(json.dumps(stable, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def _chunk_fingerprint(source_fingerprint: str, spool_path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(source_fingerprint.encode("ascii"))
    digest.update(b"\0")
    with spool_path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _content_png(output: Path, kind: str, width: int, height: int, pixels: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(struct.pack(">II", width, height))
    digest.update(pixels)
    hexdigest = digest.hexdigest()
    relative = f"data/environment-animations/{kind}/{hexdigest[:2]}/{hexdigest}.png"
    path = output / relative
    if not path.exists():
        _atomic_bytes(path, encode_png(width, height, pixels))
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
    elif shard is not None:
        return False
    return all((output / relative).is_file() for relative in checkpoint.get("assets", []))


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


def enrich_environment_animations_resumable(asset_dir: Path, output: Path) -> dict[str, int]:
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
    source_fingerprint = _source_fingerprint(manifest)
    root = output / "data" / "environment-animations"
    _prepare_root(root, source_fingerprint)

    renderer = AssetRenderer(asset_dir)
    radius = _overlap_radius(renderer)
    animation_keys: set[str] = set()
    instances = chunks_with_records = fallbacks = reused = 0
    total = len(manifest_chunks)

    for ordinal, chunk in enumerate(manifest_chunks, start=1):
        z, chunk_x, chunk_y = int(chunk["z"]), int(chunk["chunkX"]), int(chunk["chunkY"])
        spool_path = spool / f"z{z}" / f"{chunk_x}_{chunk_y}.bin"
        checkpoint_path = root / "checkpoints" / f"z{z}" / f"{chunk_x}_{chunk_y}.json"
        if not spool_path.is_file():
            print(f"ENV_ANIM_PROGRESS completed={ordinal}/{total} reused={reused} chunk=z{z}/{chunk_x}_{chunk_y} status=no-spool", flush=True)
            continue
        fingerprint = _chunk_fingerprint(source_fingerprint, spool_path)
        checkpoint: dict[str, Any] | None = None
        if checkpoint_path.is_file():
            try:
                candidate = json.loads(checkpoint_path.read_text(encoding="utf-8"))
                if isinstance(candidate, dict) and _valid_checkpoint(output, candidate, fingerprint):
                    checkpoint = candidate
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                checkpoint = None
        if checkpoint is not None:
            reused += 1
            instances += int(checkpoint["instances"])
            fallbacks += int(checkpoint["staticFallbacks"])
            chunks_with_records += 1 if int(checkpoint["instances"]) else 0
            animation_keys.update(str(key) for key in checkpoint.get("animationKeys", []))
            print(f"ENV_ANIM_PROGRESS completed={ordinal}/{total} reused={reused} chunk=z{z}/{chunk_x}_{chunk_y} status=reused", flush=True)
            continue

        tiles = list(decode_spool_tiles(spool_path))
        by_pos = {(tile.position.x, tile.position.y): tile for tile in tiles}
        order_by_pos = {(tile.position.x, tile.position.y): index for index, tile in enumerate(tiles)}
        x1, x2, y1, y2, _ = map(int, chunk["logicalBounds"])
        candidates = []
        chunk_fallbacks = 0
        for tile in tiles:
            items = _items(tile)
            if not items:
                continue
            south, east = _hooks(items, renderer)
            for stack_index, item in enumerate(items):
                appearance = renderer.appearances.get(item.server_id)
                if not appearance or not appearance.frames or appearance.frames[0].animation_phases <= 1:
                    continue
                details = _candidate_details(renderer, item, tile.position.x, tile.position.y, tile.position.z, south, east)
                if details is None:
                    chunk_fallbacks += 1
                    continue
                candidates.append((tile, stack_index, item, details, _rect(details, tile.position.x, tile.position.y), south, east))

        conflicts = _overlap_conflicts([candidate[4] for candidate in candidates])
        records: list[dict[str, Any]] = []
        chunk_keys: set[str] = set()
        chunk_assets: set[str] = set()
        for index, (tile, stack_index, item, details, _visual_rect, south, east) in enumerate(candidates):
            x, y = tile.position.x, tile.position.y
            if index in conflicts:
                chunk_fallbacks += 1
                continue
            if x - x1 < radius or x2 - x < radius or y - y1 < radius or y2 - y < radius:
                chunk_fallbacks += 1
                continue
            underlay_pixels, overdraw_pixels = _compose_context(renderer, by_pos, order_by_pos, tile, stack_index, details, radius)
            phase_pixels: list[bytes] = []
            for phase in range(details.frame.animation_phases):
                phase_width, phase_height, pixels = _phase_rgba(renderer, details.frame, details.px, details.py, details.pz, phase)
                if (phase_width, phase_height) != (details.width, details.height):
                    raise ValueError("animation phase geometry changed after candidate validation")
                phase_pixels.append(pixels)
            if not _opaque_composite(underlay_pixels, overdraw_pixels, phase_pixels, details.width, details.height):
                chunk_fallbacks += 1
                continue

            subtype = -1 if item.subtype is None else int(item.subtype)
            key = f"{item.server_id}-{subtype}-{details.px}-{details.py}-{details.pz}-{int(south)}-{int(east)}"
            frames = [f"data/environment-animations/frames/{key}/{phase}.png" for phase in range(details.frame.animation_phases)]
            for phase, relative in enumerate(frames):
                path = output / relative
                if not path.exists():
                    _atomic_bytes(path, encode_png(details.width, details.height, phase_pixels[phase]))
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
                "stackSize": len(_items(tile)),
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
        if records:
            shard_relative = f"data/environment-animations/chunks/z{z}/{chunk_x}_{chunk_y}.json"
            shard_path = output / shard_relative
            shard_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = shard_path.with_suffix(shard_path.suffix + ".tmp")
            temporary.write_text(json.dumps({"schemaVersion": 2, "records": records}, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
            temporary.replace(shard_path)

        checkpoint = {
            "schemaVersion": 1,
            "exportVersion": EXPORT_VERSION,
            "fingerprint": fingerprint,
            "instances": len(records),
            "staticFallbacks": chunk_fallbacks,
            "animationKeys": sorted(chunk_keys),
            "assets": sorted(chunk_assets),
            "shard": shard_relative,
        }
        _atomic_json(checkpoint_path, checkpoint)
        instances += len(records)
        fallbacks += chunk_fallbacks
        chunks_with_records += 1 if records else 0
        animation_keys.update(chunk_keys)
        print(f"ENV_ANIM_PROGRESS completed={ordinal}/{total} reused={reused} chunk=z{z}/{chunk_x}_{chunk_y} instances={len(records)} fallbacks={chunk_fallbacks}", flush=True)

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
            "resumePolicy": "reuse checkpointed chunks only when spool fingerprint and all referenced assets remain valid",
            "occurrenceAssetPolicy": "content-addressed deduplication for underlays and overdraws",
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
    print(f"ENV_ANIM_DONE completed={total}/{total} reused={reused} instances={instances} files={len(data_files)} bytes={output_bytes}", flush=True)
    return stats
