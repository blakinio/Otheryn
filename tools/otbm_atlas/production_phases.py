"""Persistent, byte-verified phase cache for the production Atlas builder."""
from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping
import hashlib
import json
from pathlib import Path
from typing import Any

from .incremental_core import canonical_json, sha256_bytes, sha256_file, write_bytes_atomic, write_json_atomic

PHASE_STATE_VERSION = 1


def payload_digest(value: object) -> str:
    return sha256_bytes(canonical_json(value))


def tree_digest(root: Path, patterns: Iterable[str] = ("**/*",)) -> str:
    """Digest selected file names and bytes independent of directory ordering."""
    files: dict[str, Path] = {}
    if root.exists():
        for pattern in patterns:
            for path in root.glob(pattern):
                if path.is_file():
                    files[path.relative_to(root).as_posix()] = path
    digest = hashlib.sha256()
    for relative in sorted(files):
        encoded = relative.encode("utf-8")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
        digest.update(bytes.fromhex(sha256_file(files[relative])))
    return digest.hexdigest()


def semantics_digest(paths: Iterable[Path]) -> str:
    """Whitespace/comment-insensitive Python semantic digest; byte digest otherwise."""
    digest = hashlib.sha256()
    for path in sorted({value.resolve() for value in paths}, key=lambda value: value.as_posix()):
        label = path.name.encode("utf-8")
        digest.update(len(label).to_bytes(4, "big"))
        digest.update(label)
        if path.suffix == ".py":
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
            digest.update(ast.dump(tree, include_attributes=False).encode("utf-8"))
        else:
            digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def write_json_if_changed(path: Path, value: object) -> bool:
    payload = json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    if path.is_file() and path.read_bytes() == payload:
        return False
    write_bytes_atomic(path, payload)
    return True


def copy_if_changed(source: Path, target: Path) -> bool:
    if target.is_file() and sha256_file(source) == sha256_file(target):
        return False
    write_bytes_atomic(target, source.read_bytes())
    return True


class ProductionPhaseCache:
    def __init__(self, output: Path) -> None:
        self.output = output
        self.path = output / ".incremental-state" / "phase-state.json"
        self.state: dict[str, Any] = {"schemaVersion": PHASE_STATE_VERSION, "phases": {}}
        if self.path.is_file():
            try:
                candidate = json.loads(self.path.read_text(encoding="utf-8"))
                if candidate.get("schemaVersion") == PHASE_STATE_VERSION and isinstance(candidate.get("phases"), dict):
                    self.state = candidate
            except (OSError, json.JSONDecodeError, AttributeError):
                pass

    def _files(self, patterns: Iterable[str]) -> dict[str, Path]:
        found: dict[str, Path] = {}
        for pattern in patterns:
            if any(token in pattern for token in "*?["):
                candidates = self.output.glob(pattern)
            else:
                candidates = (self.output / pattern,)
            for path in candidates:
                if path.is_file():
                    found[path.relative_to(self.output).as_posix()] = path
        return dict(sorted(found.items()))

    @staticmethod
    def _identity(path: Path) -> dict[str, object]:
        stat = path.stat()
        return {"size": stat.st_size, "mtimeNs": stat.st_mtime_ns, "sha256": sha256_file(path)}

    @staticmethod
    def _identity_valid(path: Path, identity: Mapping[str, object]) -> bool:
        if not path.is_file():
            return False
        stat = path.stat()
        if identity.get("size") == stat.st_size and identity.get("mtimeNs") == stat.st_mtime_ns:
            return True
        expected = identity.get("sha256")
        return isinstance(expected, str) and sha256_file(path) == expected

    def current(self, name: str, fingerprint: str, output_patterns: Iterable[str]) -> bool:
        phases = self.state.get("phases", {})
        record = phases.get(name) if isinstance(phases, dict) else None
        if not isinstance(record, dict) or record.get("fingerprint") != fingerprint:
            return False
        expected = record.get("outputs")
        if not isinstance(expected, dict):
            return False
        current = self._files(output_patterns)
        if set(current) != set(expected):
            return False
        return all(isinstance(expected[relative], dict) and self._identity_valid(path, expected[relative]) for relative, path in current.items())

    def result(self, name: str) -> dict[str, object] | None:
        phases = self.state.get("phases", {})
        record = phases.get(name) if isinstance(phases, dict) else None
        value = record.get("result") if isinstance(record, dict) else None
        return dict(value) if isinstance(value, dict) else None

    def commit(self, name: str, fingerprint: str, output_patterns: Iterable[str], result: Mapping[str, object] | None = None) -> None:
        files = self._files(output_patterns)
        record = {
            "fingerprint": fingerprint,
            "outputs": {relative: self._identity(path) for relative, path in files.items()},
            "result": {} if result is None else dict(result),
        }
        phases = self.state.setdefault("phases", {})
        assert isinstance(phases, dict)
        phases[name] = record
        write_json_atomic(self.path, self.state)
