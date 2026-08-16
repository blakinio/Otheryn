"""Local dependency fingerprints for resumable Atlas environment animations."""
from __future__ import annotations

import ast
from dataclasses import asdict
import hashlib
from pathlib import Path
import sys
from typing import Iterable, Mapping

from . import assets as assets_module
from . import environment_animation as environment_animation_module
from . import environment_spool as environment_spool_module
from . import render as render_module
from .environment_animation import ANIMATION_ZOOM, _items
from .environment_spool import decode_spool_tiles
from .incremental_core import canonical_json, sha256_bytes, sha256_file
from .render import AssetRenderer


class EnvironmentAssetFingerprinter:
    """Memoize exact appearance + decoded-sprite content dependencies."""

    def __init__(self, renderer: AssetRenderer) -> None:
        self.renderer = renderer
        self._appearance_cache: dict[int, str] = {}

    def appearance_digest(self, appearance_id: int) -> str:
        cached = self._appearance_cache.get(int(appearance_id))
        if cached is not None:
            return cached
        appearance = self.renderer.appearances.get(int(appearance_id))
        if appearance is None:
            digest = sha256_bytes(canonical_json({"appearanceId": int(appearance_id), "status": "MISSING"}))
            self._appearance_cache[int(appearance_id)] = digest
            return digest
        digest = hashlib.sha256(); digest.update(canonical_json(asdict(appearance)))
        sprite_ids = sorted({int(sprite_id) for frame in appearance.frames for sprite_id in frame.sprite_ids})
        for sprite_id in sprite_ids:
            digest.update(f"sprite:{sprite_id}\0".encode("ascii"))
            decoded = self.renderer.sprite(sprite_id)
            if decoded is None:
                digest.update(b"MISSING\0"); continue
            width, height, pixels = decoded
            digest.update(f"{width}x{height}\0".encode("ascii")); digest.update(hashlib.sha256(pixels).digest())
        value = digest.hexdigest(); self._appearance_cache[int(appearance_id)] = value; return value

    def chunk_fingerprint(self, contract_fingerprint: str, spool_path: Path, logical_bounds: list[int] | tuple[int, ...]) -> str:
        appearance_ids: set[int] = set()
        for tile in decode_spool_tiles(spool_path): appearance_ids.update(int(item.server_id) for item in _items(tile))
        return sha256_bytes(canonical_json({
            "contractFingerprint": contract_fingerprint,
            "spoolSha256": sha256_file(spool_path),
            "logicalBounds": [int(value) for value in logical_bounds],
            "appearanceDigests": {str(value): self.appearance_digest(value) for value in sorted(appearance_ids)},
        }))


def python_semantics_digest(paths: Iterable[Path]) -> str:
    """Deterministic AST digest, insensitive to whitespace/comments/line endings."""
    digest = hashlib.sha256()
    for path in sorted({value.resolve() for value in paths}, key=lambda value: value.as_posix()):
        label = path.name.encode("utf-8"); digest.update(len(label).to_bytes(4, "big")); digest.update(label)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
        digest.update(ast.dump(tree, include_attributes=False).encode("utf-8"))
    return digest.hexdigest()


def _automatic_semantics_digest() -> str:
    # Bind every direct code dependency that can change emitted environment bytes
    # or the local spool interpretation. Monolithic source/asset identities remain
    # deliberately excluded; exact per-chunk content is fingerprinted separately.
    paths = [
        Path(__file__),
        Path(environment_animation_module.__file__),
        Path(environment_spool_module.__file__),
        Path(render_module.__file__),
        Path(assets_module.__file__),
    ]
    resume = sys.modules.get(f"{__package__}.environment_animation_resume")
    resume_file = getattr(resume, "__file__", None) if resume is not None else None
    if resume_file: paths.append(Path(resume_file))
    return python_semantics_digest(paths)


def environment_contract_fingerprint(
    manifest: Mapping[str, object],
    *,
    export_version: int,
    overlap_radius: int,
    semantics_digest: str | None = None,
) -> str:
    """Hash only genuinely global environment-export semantics.

    Monolithic map/asset SHA values and complete chunk inventory are excluded.
    Code semantics are bound automatically so a compositor/exporter behavior
    change invalidates checkpoints even if a human forgets to bump a version.
    """
    return sha256_bytes(canonical_json({
        "exportVersion": int(export_version),
        "schemaVersion": manifest.get("schemaVersion"),
        "chunkSize": manifest.get("chunkSize"),
        "animationZoom": ANIMATION_ZOOM,
        "overlapSafetyRadiusTiles": int(overlap_radius),
        "semanticsDigest": semantics_digest or _automatic_semantics_digest(),
    }))
