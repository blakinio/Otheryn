"""Exact decoded-sprite dependency fingerprints for Atlas incremental planning.

Sprite sheets are storage containers, not dependency boundaries.  This module
lets planners compare only sprite IDs that a chunk actually uses while still
using sheet SHA/ranges as the cheap first-stage change detector.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
import hashlib
from pathlib import Path
import struct
from typing import Any

from .assets import decode_sheet, extract_sprite, load_sprite_catalog, sheet_for_sprite

MISSING_SPRITE_DIGEST = "MISSING"


def _sprite_digest(value: tuple[int, int, bytes] | None) -> str:
    if value is None:
        return MISSING_SPRITE_DIGEST
    width, height, pixels = value
    digest = hashlib.sha256()
    digest.update(struct.pack(">II", int(width), int(height)))
    digest.update(pixels)
    return digest.hexdigest()


def sprite_digests(asset_dir: Path, sprite_ids: Iterable[int]) -> dict[str, str]:
    """Hash exact decoded pixels for requested sprite IDs, decoding each sheet once."""
    requested = sorted({int(value) for value in sprite_ids})
    sheets = load_sprite_catalog(asset_dir)
    grouped: dict[Path, tuple[Any, list[int]]] = {}
    result: dict[str, str] = {}
    for sprite_id in requested:
        sheet = sheet_for_sprite(sheets, sprite_id)
        if sheet is None:
            result[str(sprite_id)] = MISSING_SPRITE_DIGEST
            continue
        entry = grouped.get(sheet.path)
        if entry is None:
            grouped[sheet.path] = (sheet, [sprite_id])
        else:
            entry[1].append(sprite_id)
    for path in sorted(grouped, key=lambda value: value.as_posix()):
        sheet, ids = grouped[path]
        pixels = decode_sheet(sheet.path)[2]
        for sprite_id in ids:
            result[str(sprite_id)] = _sprite_digest(extract_sprite(sheet, pixels, sprite_id))
    return dict(sorted(result.items(), key=lambda item: int(item[0])))


def _sheet_records(state: Mapping[str, object] | None) -> list[dict[str, object]]:
    if not state:
        return []
    raw = state.get("sheets", [])
    return [dict(value) for value in raw if isinstance(value, Mapping)] if isinstance(raw, list) else []


def _sheet_for_id(records: list[dict[str, object]], sprite_id: int) -> dict[str, object] | None:
    for record in records:
        try:
            if int(record["firstSpriteId"]) <= sprite_id <= int(record["lastSpriteId"]):
                return record
        except (KeyError, TypeError, ValueError):
            continue
    return None


def _sheet_identity(record: Mapping[str, object] | None) -> tuple[object, ...] | None:
    if record is None:
        return None
    return (
        record.get("path"),
        record.get("sha256"),
        record.get("firstSpriteId"),
        record.get("lastSpriteId"),
        record.get("layout"),
        record.get("spriteSize"),
    )


def changed_sheet_paths(base_state: Mapping[str, object], target_state: Mapping[str, object]) -> list[str]:
    base = {str(value.get("path")): value for value in _sheet_records(base_state) if value.get("path") is not None}
    target = {str(value.get("path")): value for value in _sheet_records(target_state) if value.get("path") is not None}
    return sorted(path for path in set(base) | set(target) if base.get(path) != target.get(path))


def _candidate_sprite_ids(
    base_state: Mapping[str, object],
    target_state: Mapping[str, object],
    dependency_index: Mapping[str, object],
) -> list[int]:
    reverse = dependency_index.get("spriteToChunks", {})
    used = {int(value) for value in reverse} if isinstance(reverse, Mapping) else set()
    changed = set(changed_sheet_paths(base_state, target_state))
    if not changed or not used:
        return []
    base_records = _sheet_records(base_state)
    target_records = _sheet_records(target_state)
    result: list[int] = []
    for sprite_id in sorted(used):
        base_sheet = _sheet_for_id(base_records, sprite_id)
        target_sheet = _sheet_for_id(target_records, sprite_id)
        if (base_sheet and str(base_sheet.get("path")) in changed) or (target_sheet and str(target_sheet.get("path")) in changed):
            result.append(sprite_id)
    return result


def exact_changed_sprite_ids(
    base_asset_dir: Path,
    target_asset_dir: Path,
    base_state: Mapping[str, object],
    target_state: Mapping[str, object],
    dependency_index: Mapping[str, object],
) -> list[int]:
    candidates = _candidate_sprite_ids(base_state, target_state, dependency_index)
    if not candidates:
        return []
    before = sprite_digests(base_asset_dir, candidates)
    after = sprite_digests(target_asset_dir, candidates)
    return [sprite_id for sprite_id in candidates if before.get(str(sprite_id)) != after.get(str(sprite_id))]


def exact_asset_impact(
    base_asset_dir: Path,
    target_asset_dir: Path,
    base_state: Mapping[str, object],
    target_state: Mapping[str, object],
    dependency_index: Mapping[str, object],
    coarse_impact: Mapping[str, object],
) -> dict[str, object]:
    """Refine changed-sheet impact to exact used sprites while preserving global guards."""
    result = dict(coarse_impact)
    global_reasons = list(result.get("globalReasons", []))
    if global_reasons:
        return result
    reverse_appearances = dependency_index.get("appearanceToChunks", {})
    reverse_sprites = dependency_index.get("spriteToChunks", {})
    changed_appearances = [int(value) for value in result.get("changedAppearanceIds", [])]
    changed_sprites = exact_changed_sprite_ids(base_asset_dir, target_asset_dir, base_state, target_state, dependency_index)
    affected: set[str] = set()
    if isinstance(reverse_appearances, Mapping):
        for appearance_id in changed_appearances:
            affected.update(str(value) for value in reverse_appearances.get(str(appearance_id), []))
    if isinstance(reverse_sprites, Mapping):
        for sprite_id in changed_sprites:
            affected.update(str(value) for value in reverse_sprites.get(str(sprite_id), []))
    result["changedSpriteIds"] = changed_sprites
    result["affectedChunks"] = sorted(affected)
    return result


def prepare_production_sprite_digests(
    asset_dir: Path,
    current_asset_state: Mapping[str, object],
    dependency_index: Mapping[str, object],
    previous_state: Mapping[str, object] | None,
) -> dict[str, str]:
    """Reuse exact sprite digests across unchanged sheets and decode only changed/new sheets."""
    reverse = dependency_index.get("spriteToChunks", {})
    used = sorted(int(value) for value in reverse) if isinstance(reverse, Mapping) else []
    current_records = _sheet_records(current_asset_state)
    previous_records = _sheet_records({"sheets": previous_state.get("assetSheets", [])} if previous_state else None)
    previous_digests = previous_state.get("spriteDigests", {}) if previous_state and isinstance(previous_state.get("spriteDigests"), Mapping) else {}
    result: dict[str, str] = {}
    compute: list[int] = []
    for sprite_id in used:
        current_sheet = _sheet_for_id(current_records, sprite_id)
        previous_sheet = _sheet_for_id(previous_records, sprite_id)
        previous_digest = previous_digests.get(str(sprite_id))
        if isinstance(previous_digest, str) and _sheet_identity(current_sheet) == _sheet_identity(previous_sheet):
            result[str(sprite_id)] = previous_digest
        else:
            compute.append(sprite_id)
    result.update(sprite_digests(asset_dir, compute))
    return dict(sorted(result.items(), key=lambda item: int(item[0])))
