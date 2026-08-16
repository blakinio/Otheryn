"""Semantic version guard for render-sensitive incremental-core behavior.

The guard derives a local call-graph closure from the render/invalidation roots,
so helper functions cannot silently change cache/render semantics merely because
they were omitted from a hand-maintained flat whitelist.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Iterable

_ROOT_FUNCTIONS = {
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
}
_ROOT_CLASSES = {"ChunkKey"}
_ROOT_CONSTANTS = {
    "RENDER_CORE_VERSION",
    "DEPENDENCY_INDEX_VERSION",
    "SPOOL_VERSION",
    "TILE_PIXELS",
}


def _called_local_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            names.add(child.func.id)
    return names


def _semantic_contract(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {"present": False, "version": None, "semanticDigest": None, "members": []}
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    assignments: dict[str, ast.Assign | ast.AnnAssign] = {}
    version: int | None = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = node
                    if target.id == "RENDER_CORE_VERSION":
                        if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, int):
                            raise ValueError("RENDER_CORE_VERSION must be an integer literal")
                        version = int(node.value.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assignments[node.target.id] = node
    missing_functions = sorted(_ROOT_FUNCTIONS - set(functions))
    missing_classes = sorted(_ROOT_CLASSES - set(classes))
    missing_constants = sorted(_ROOT_CONSTANTS - set(assignments))
    if missing_functions or missing_classes or missing_constants or version is None:
        raise ValueError(
            "incremental render-core contract incomplete: "
            f"functions={missing_functions}, classes={missing_classes}, constants={missing_constants}, version={version}"
        )

    reachable = set(_ROOT_FUNCTIONS)
    pending = list(_ROOT_FUNCTIONS)
    while pending:
        current = pending.pop()
        for called in _called_local_names(functions[current]):
            if called in functions and called not in reachable:
                reachable.add(called)
                pending.append(called)

    selected: list[ast.AST] = []
    members: list[str] = []
    for name in sorted(_ROOT_CONSTANTS):
        selected.append(assignments[name])
        members.append(f"const:{name}")
    for name in sorted(_ROOT_CLASSES):
        selected.append(classes[name])
        members.append(f"class:{name}")
    for name in sorted(reachable):
        selected.append(functions[name])
        members.append(f"func:{name}")
    module = ast.Module(body=selected, type_ignores=[])
    digest = hashlib.sha256(ast.dump(module, include_attributes=False).encode("utf-8")).hexdigest()
    return {"present": True, "version": version, "semanticDigest": digest, "members": members}


def strict_render_core_transition_reasons(base_root: Path, target_root: Path) -> list[str]:
    """Fail closed when render/invalidation semantics change without versioning."""
    relative = Path("tools/otbm_atlas/incremental_core.py")
    base = _semantic_contract(base_root / relative)
    target = _semantic_contract(target_root / relative)
    if not base["present"] and target["present"]:
        return []  # one-time bootstrap is proven against the legacy renderer by E2E
    if base["present"] and not target["present"]:
        return ["RENDER_CORE_REMOVED"]
    if not base["present"] and not target["present"]:
        return []
    if base["semanticDigest"] == target["semanticDigest"]:
        return []
    if base["version"] == target["version"]:
        return ["RENDER_CORE_SEMANTICS_CHANGED_WITHOUT_VERSION_BUMP"]
    return ["RENDER_CORE_VERSION_CHANGED"]
