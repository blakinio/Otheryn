"""Atomic filesystem release promotion and rollback for static Atlas deployments.

The Synology deployment keeps immutable versioned release directories.  The
``current`` and ``previous`` links are changed with ``os.replace`` so a browser
container is never pointed at a half-copied release.  Container recreation is a
separate explicit operator step after a successful pointer change.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def _link_target(path: Path) -> str | None:
    if not path.is_symlink():
        return None
    return os.readlink(path)


def _atomic_link(path: Path, target: str) -> None:
    temporary = path.with_name(f".{path.name}.next")
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    temporary.symlink_to(target)
    os.replace(temporary, path)


def promote(root: Path, release_id: str) -> dict[str, str | None]:
    root = root.resolve()
    release = root / "releases" / release_id
    if not release.is_dir():
        raise FileNotFoundError(f"release does not exist: {release}")
    if not (release / "manifest.json").is_file() or not (release / "index.html").is_file():
        raise ValueError("release must contain manifest.json and index.html")
    current = root / "current"
    previous = root / "previous"
    new_target = f"releases/{release_id}"
    old_target = _link_target(current)
    if current.exists() and not current.is_symlink():
        raise ValueError("current must be a symlink before atomic promotion")
    if old_target == new_target:
        return {"current": new_target, "previous": _link_target(previous), "changed": "false"}
    if old_target is not None:
        _atomic_link(previous, old_target)
    _atomic_link(current, new_target)
    return {"current": new_target, "previous": old_target, "changed": "true"}


def rollback(root: Path) -> dict[str, str | None]:
    root = root.resolve()
    current = root / "current"
    previous = root / "previous"
    current_target = _link_target(current)
    previous_target = _link_target(previous)
    if current_target is None or previous_target is None:
        raise ValueError("rollback requires current and previous release symlinks")
    previous_release = root / previous_target
    if not previous_release.is_dir() or not (previous_release / "manifest.json").is_file():
        raise ValueError(f"previous release is unavailable: {previous_target}")
    _atomic_link(current, previous_target)
    _atomic_link(previous, current_target)
    return {"current": previous_target, "previous": current_target, "changed": "true"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--promote", metavar="RELEASE_ID")
    group.add_argument("--rollback", action="store_true")
    args = parser.parse_args()
    result = rollback(args.root) if args.rollback else promote(args.root, args.promote)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
