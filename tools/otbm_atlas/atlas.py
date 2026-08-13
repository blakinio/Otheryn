"""Versioned public entry point for the resumable OTBM atlas builder."""

from __future__ import annotations

from . import _atlas_core as _core

# Render semantics changed in atlas v3 (container visibility and subtype patterns).
# Set the core module's global before exporting its functions so cache fingerprints
# and manifest schemaVersion are computed with the public version.
_core.ATLAS_VERSION = 3

from ._atlas_core import *  # noqa: F401,F403,E402

ATLAS_VERSION = _core.ATLAS_VERSION


if __name__ == "__main__":
	raise SystemExit(_core.main())
