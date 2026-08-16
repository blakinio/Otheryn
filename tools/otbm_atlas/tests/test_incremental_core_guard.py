from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.otbm_atlas.incremental_core_guard import strict_render_core_transition_reasons


_ROOTS = [
    "encode_tile",
    "decode_tiles",
    "spool_map",
    "reconcile_spool",
    "_dependency_ids_for_tile",
    "build_dependency_index",
    "collect_asset_state",
    "asset_impact",
    "detail_fingerprint",
    "render_contract_digest",
    "chunk_render_bounds",
    "render_selected_chunks",
]


def _source(version: int, helper_marker: int) -> str:
    lines = [
        f"RENDER_CORE_VERSION = {version}",
        "DEPENDENCY_INDEX_VERSION = 1",
        "SPOOL_VERSION = 1",
        "TILE_PIXELS = 32",
        "",
        "class ChunkKey:",
        "    pass",
        "",
        "def _helper():",
        f"    return {helper_marker}",
    ]
    for name in _ROOTS:
        lines.extend(["", f"def {name}():"])
        if name == "detail_fingerprint":
            lines.append("    return _helper()")
        else:
            lines.append("    return 0")
    return "\n".join(lines) + "\n"


def _write(root: Path, version: int, marker: int) -> None:
    path = root / "tools/otbm_atlas/incremental_core.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_source(version, marker), encoding="utf-8")


class IncrementalCoreGuardTests(unittest.TestCase):
    def test_reachable_helper_change_without_version_bump_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base, target = root / "base", root / "target"
            _write(base, 1, 1)
            _write(target, 1, 2)
            self.assertEqual(
                strict_render_core_transition_reasons(base, target),
                ["RENDER_CORE_SEMANTICS_CHANGED_WITHOUT_VERSION_BUMP"],
            )

    def test_reachable_helper_change_with_version_bump_requires_full_transition(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base, target = root / "base", root / "target"
            _write(base, 1, 1)
            _write(target, 2, 2)
            self.assertEqual(
                strict_render_core_transition_reasons(base, target),
                ["RENDER_CORE_VERSION_CHANGED"],
            )

    def test_unreachable_publication_helper_does_not_force_render_transition(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base, target = root / "base", root / "target"
            _write(base, 1, 1)
            _write(target, 1, 1)
            for candidate, marker in ((base, 1), (target, 2)):
                path = candidate / "tools/otbm_atlas/incremental_core.py"
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(f"\ndef publication_only():\n    return {marker}\n")
            self.assertEqual(strict_render_core_transition_reasons(base, target), [])

    def test_legacy_bootstrap_does_not_claim_false_global_invalidation(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base, target = root / "base", root / "target"
            base.mkdir()
            _write(target, 1, 1)
            self.assertEqual(strict_render_core_transition_reasons(base, target), [])


if __name__ == "__main__":
    unittest.main()
