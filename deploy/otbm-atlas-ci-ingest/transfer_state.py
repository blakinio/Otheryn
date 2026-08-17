"""Durable TRANSFERRED_VERIFIED state for Atlas Synology shard handoff.

The hosted renderer owns BUILD/VERIFY/UPLOAD. This helper runs only against the
Synology generation root and turns a COMPLETE receiver receipt into a durable
TRANSFERRED_VERIFIED marker after independently rebuilding the deterministic
archive and re-verifying the physical shard corpus.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any

EXPECTED_SHARDS = 32
PRODUCER_RE = re.compile(r"^[0-9a-f]{40}$")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _producer(value: str) -> str:
    if not PRODUCER_RE.fullmatch(value):
        raise ValueError("producer SHA must be lowercase 40-hex")
    return value


def _bundle_id(index: int) -> str:
    if not 0 <= index < EXPECTED_SHARDS:
        raise ValueError(f"shard index out of range: {index}")
    return f"shard-{index:02d}"


def _marker_root(generation: Path) -> Path:
    return generation / "control" / "transferred-verified"


def _marker_path(generation: Path, index: int) -> Path:
    return _marker_root(generation) / f"shard-{index:02d}.json"


def _load_uploader(path: Path):
    spec = importlib.util.spec_from_file_location("atlas_transfer_state_uploader", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load uploader: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _remove_marker(generation: Path, index: int) -> None:
    marker = _marker_path(generation, index)
    marker.unlink(missing_ok=True)
    evidence = _marker_root(generation) / "evidence"
    (evidence / f"full-world-shard-{index:02d}.json").unlink(missing_ok=True)
    (evidence / f"shard-manifest-{index:02d}.json").unlink(missing_ok=True)


def _evidence(bundle: Path, producer_sha: str, index: int, verification: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = _load_json(bundle / "manifest.json")
    environment = _load_json(bundle / "data" / "environment-animations" / "index.json")
    certification = manifest.get("certification")
    if not isinstance(certification, dict):
        raise RuntimeError(f"shard {index} certification missing")
    if certification.get("scope") != "world-chunk-shard":
        raise RuntimeError(f"shard {index} certification scope mismatch")
    if int(certification.get("shardIndex", -1)) != index or int(certification.get("shardCount", -1)) != EXPECTED_SHARDS:
        raise RuntimeError(f"shard {index} certification identity mismatch")
    if verification.get("ok") is not True or verification.get("missingSprites") != {}:
        raise RuntimeError(f"shard {index} physical verification failed: {verification.get('errors')}")
    chunk_keys = list(map(str, verification.get("chunkKeys", [])))
    if int(verification.get("chunks", -1)) != len(chunk_keys) or not chunk_keys:
        raise RuntimeError(f"shard {index} chunk inventory mismatch")
    completed = int(environment.get("statistics", {}).get("completedChunks", -1))
    if completed != len(chunk_keys):
        raise RuntimeError(f"shard {index} environment completion mismatch")
    evidence = {
        "schemaVersion": 2,
        "producerSha": producer_sha,
        "shardIndex": index,
        "shardCount": EXPECTED_SHARDS,
        "chunks": len(chunk_keys),
        "chunkKeys": chunk_keys,
        "floorCounts": verification.get("floors", {}),
        "sources": manifest.get("sources", {}),
        "workers": certification.get("workers"),
        "worldPlanDigest": certification.get("worldPlanDigest"),
        "coverageDigest": certification.get("coverageDigest"),
        "assignmentDigest": certification.get("assignmentDigest"),
        "verification": "PASS",
        "missingSprites": {},
        "environmentCompletedChunks": completed,
    }
    return evidence, manifest


def verify_shard(generation: Path, producer_sha: str, index: int, uploader_path: Path) -> dict[str, Any]:
    producer_sha = _producer(producer_sha)
    bundle_id = _bundle_id(index)
    bundle = generation / "bundles" / bundle_id
    receipt_path = generation / "receipts" / f"{bundle_id}.json"
    try:
        if not bundle.is_dir() or not receipt_path.is_file():
            raise FileNotFoundError(f"missing physical bundle/receipt for {bundle_id}")
        receipt = _load_json(receipt_path)
        if receipt.get("status") != "COMPLETE" or receipt.get("producerSha") != producer_sha:
            raise RuntimeError(f"invalid COMPLETE receipt for {bundle_id}")
        if receipt.get("bundleId") != bundle_id or receipt.get("kind") != "shard" or int(receipt.get("shardIndex", -1)) != index:
            raise RuntimeError(f"receiver identity mismatch for {bundle_id}")

        from tools.otbm_atlas.verify_world_shard import verify_world_shard

        verification = verify_world_shard(bundle)
        evidence, manifest = _evidence(bundle, producer_sha, index, verification)
        uploader = _load_uploader(uploader_path)
        with tempfile.TemporaryDirectory(prefix=f"atlas-transfer-verify-{index:02d}-") as temporary:
            archive = Path(temporary) / "rebuilt.tar"
            info = uploader.build_archive(bundle, archive)
        if int(receipt.get("archiveBytes", -1)) != int(info["bytes"]):
            raise RuntimeError(f"archive byte identity mismatch for {bundle_id}")
        if receipt.get("archiveSha256") != info["sha256"]:
            raise RuntimeError(f"archive SHA-256 identity mismatch for {bundle_id}")

        marker = {
            "schemaVersion": 1,
            "status": "TRANSFERRED_VERIFIED",
            "producerSha": producer_sha,
            "bundleId": bundle_id,
            "shardIndex": index,
            "archiveBytes": int(info["bytes"]),
            "archiveSha256": info["sha256"],
            "chunks": int(verification["chunks"]),
        }
        _write_json(_marker_path(generation, index), marker)
        evidence_root = _marker_root(generation) / "evidence"
        _write_json(evidence_root / f"full-world-shard-{index:02d}.json", evidence)
        _write_json(evidence_root / f"shard-manifest-{index:02d}.json", manifest)
        return marker
    except Exception:
        _remove_marker(generation, index)
        raise


def verify_existing(generation: Path, producer_sha: str, uploader_path: Path, require_all: bool = False) -> dict[str, Any]:
    producer_sha = _producer(producer_sha)
    verified: list[int] = []
    missing: list[int] = []
    for index in range(EXPECTED_SHARDS):
        receipt = generation / "receipts" / f"shard-{index:02d}.json"
        bundle = generation / "bundles" / f"shard-{index:02d}"
        if not receipt.is_file() or not bundle.is_dir():
            _remove_marker(generation, index)
            missing.append(index)
            continue
        verify_shard(generation, producer_sha, index, uploader_path)
        verified.append(index)
    summary = {
        "schemaVersion": 1,
        "status": "TRANSFERRED_VERIFIED" if len(verified) == EXPECTED_SHARDS else "PARTIAL_TRANSFERRED_VERIFIED",
        "producerSha": producer_sha,
        "verifiedShards": verified,
        "missingShards": missing,
    }
    _write_json(_marker_root(generation) / "summary.json", summary)
    if require_all and missing:
        raise RuntimeError(f"missing TRANSFERRED_VERIFIED shards: {missing}")
    return summary


def export_resume(generation: Path, producer_sha: str, output: Path) -> dict[str, Any]:
    producer_sha = _producer(producer_sha)
    output.mkdir(parents=True, exist_ok=True)
    verified: list[int] = []
    marker_root = _marker_root(generation)
    evidence_root = marker_root / "evidence"
    for index in range(EXPECTED_SHARDS):
        marker_path = _marker_path(generation, index)
        if not marker_path.is_file():
            continue
        try:
            marker = _load_json(marker_path)
            if marker.get("status") != "TRANSFERRED_VERIFIED" or marker.get("producerSha") != producer_sha or int(marker.get("shardIndex", -1)) != index:
                continue
            if not (generation / "receipts" / f"shard-{index:02d}.json").is_file():
                continue
            if not (generation / "bundles" / f"shard-{index:02d}").is_dir():
                continue
            evidence = evidence_root / f"full-world-shard-{index:02d}.json"
            manifest = evidence_root / f"shard-manifest-{index:02d}.json"
            if not evidence.is_file() or not manifest.is_file():
                continue
            shutil.copy2(evidence, output / evidence.name)
            shutil.copy2(manifest, output / manifest.name)
            verified.append(index)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            continue
    summary = {
        "schemaVersion": 1,
        "producerSha": producer_sha,
        "transferredVerifiedShards": verified,
        "transferredCsv": ",".join(map(str, verified)),
    }
    _write_json(output / "resume-summary.json", summary)
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    verify = commands.add_parser("verify-existing", help="physically reverify received shards and persist durable transfer markers")
    verify.add_argument("generation", type=Path)
    verify.add_argument("--producer-sha", required=True)
    verify.add_argument("--uploader", type=Path, required=True)
    verify.add_argument("--require-all", action="store_true")
    verify.add_argument("--output", type=Path)

    resume = commands.add_parser("export-resume", help="export evidence for shards already TRANSFERRED_VERIFIED")
    resume.add_argument("generation", type=Path)
    resume.add_argument("--producer-sha", required=True)
    resume.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "verify-existing":
        summary = verify_existing(args.generation, args.producer_sha, args.uploader, args.require_all)
        if args.output:
            _write_json(args.output, summary)
        print(json.dumps(summary, sort_keys=True))
        return 0
    if args.command == "export-resume":
        summary = export_resume(args.generation, args.producer_sha, args.output)
        print(json.dumps(summary, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
