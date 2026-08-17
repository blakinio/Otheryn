"""Fail-closed publication gate for OTBM Atlas deployment modes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.otbm_atlas.deploy_preflight import deployment_preflight

EXPECTED_ATLAS_VERSION = 3
EXPECTED_CHUNK_SIZE = 128
EXPECTED_CHUNKS = 3494
EXPECTED_MAP_SHA256 = "3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034"
INTERNET_MODES = {"internet-authenticated", "internet-public"}
MODES = {"private-local", *INTERNET_MODES}


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def evaluate_publication(
    preflight: dict[str, Any],
    *,
    mode: str,
    approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if mode not in MODES:
        raise ValueError(f"unsupported publication mode: {mode}")

    reasons: list[str] = []
    identity = preflight.get("identity") if isinstance(preflight.get("identity"), dict) else {}
    verification = preflight.get("verification") if isinstance(preflight.get("verification"), dict) else {}

    readiness_checks = (
        (preflight.get("status") == "FULL_RUNTIME_READY", "deployment preflight status must be FULL_RUNTIME_READY"),
        (preflight.get("corePreviewReady") is True, "deployment preflight corePreviewReady must be true"),
        (preflight.get("fullRuntimeReady") is True, "deployment preflight fullRuntimeReady must be true"),
        (identity.get("schemaVersion") == EXPECTED_ATLAS_VERSION, f"Atlas schemaVersion must be {EXPECTED_ATLAS_VERSION}"),
        (identity.get("chunkSize") == EXPECTED_CHUNK_SIZE, f"Atlas chunkSize must be {EXPECTED_CHUNK_SIZE}"),
        (identity.get("chunks") == EXPECTED_CHUNKS, f"Atlas chunk count must be {EXPECTED_CHUNKS}"),
        (identity.get("mapSha256") == EXPECTED_MAP_SHA256, "Atlas map SHA-256 is not the certified canonical world"),
        (preflight.get("viewer", {}).get("status") == "CURRENT" if isinstance(preflight.get("viewer"), dict) else False, "viewer runtime must be CURRENT"),
        (preflight.get("spatial", {}).get("status") == "READY" if isinstance(preflight.get("spatial"), dict) else False, "spatial data must be READY"),
        (preflight.get("tileInspector", {}).get("status") == "READY" if isinstance(preflight.get("tileInspector"), dict) else False, "tile inspector must be READY"),
        (preflight.get("creatures", {}).get("status") == "READY" if isinstance(preflight.get("creatures"), dict) else False, "creature assets must be READY"),
        (preflight.get("environmentAnimations", {}).get("status") == "READY" if isinstance(preflight.get("environmentAnimations"), dict) else False, "environment animations must be READY"),
        (verification.get("ok") is True, "independent Atlas verification must be successful"),
    )
    reasons.extend(message for ok, message in readiness_checks if not ok)

    approval_state: dict[str, Any] = {
        "required": mode in INTERNET_MODES,
        "present": approval is not None,
        "valid": mode == "private-local",
        "scope": None,
    }

    if mode in INTERNET_MODES:
        if approval is None:
            reasons.append("ATLAS-PR-009 Internet-facing redistribution approval is required")
        else:
            approval_state["scope"] = approval.get("scope")
            approval_checks = (
                (approval.get("schemaVersion") == 1, "approval schemaVersion must be 1"),
                (approval.get("approved") is True, "approval must explicitly set approved=true"),
                (approval.get("requirement") == "ATLAS-PR-009", "approval requirement must be ATLAS-PR-009"),
                (approval.get("scope") == mode, f"approval scope must exactly match {mode}"),
                (approval.get("atlasVersion") == EXPECTED_ATLAS_VERSION, f"approval atlasVersion must be {EXPECTED_ATLAS_VERSION}"),
                (approval.get("mapSha256") == EXPECTED_MAP_SHA256, "approval mapSha256 must match the certified canonical world"),
                (_nonempty_string(approval.get("approvedBy")), "approval approvedBy must be non-empty"),
                (_nonempty_string(approval.get("approvedAt")), "approval approvedAt must be non-empty"),
                (_nonempty_string(approval.get("decision")), "approval decision must be non-empty"),
            )
            approval_errors = [message for ok, message in approval_checks if not ok]
            reasons.extend(approval_errors)
            approval_state["valid"] = not approval_errors

    ready = not reasons
    return {
        "status": "READY" if ready else "BLOCKED",
        "mode": mode,
        "internetFacing": mode in INTERNET_MODES,
        "publicationReady": ready,
        "approval": approval_state,
        "identity": {
            "atlasVersion": identity.get("schemaVersion"),
            "chunkSize": identity.get("chunkSize"),
            "chunks": identity.get("chunks"),
            "mapSha256": identity.get("mapSha256"),
        },
        "preflightStatus": preflight.get("status"),
        "reasons": reasons,
    }


def evaluate_atlas(
    atlas_root: Path,
    *,
    mode: str,
    approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a fresh full deployment preflight against the real corpus, then gate publication."""
    preflight = deployment_preflight(
        atlas_root,
        verify_chunks=True,
        require_environment_animations=True,
    )
    return evaluate_publication(preflight, mode=mode, approval=approval)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("atlas", type=Path, help="generated Atlas directory; the gate always performs a fresh full deployment preflight")
    parser.add_argument("--mode", choices=sorted(MODES), required=True)
    parser.add_argument("--approval", type=Path, help="ATLAS-PR-009 approval JSON; mandatory for Internet-facing modes")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        approval = _read_json(args.approval) if args.approval else None
        report = evaluate_atlas(args.atlas, mode=args.mode, approval=approval)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        report = {
            "status": "BLOCKED",
            "mode": args.mode,
            "internetFacing": args.mode in INTERNET_MODES,
            "publicationReady": False,
            "approval": {"required": args.mode in INTERNET_MODES, "present": bool(args.approval), "valid": False, "scope": None},
            "identity": {},
            "preflightStatus": "ERROR",
            "reasons": [str(error)],
        }

    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if report["publicationReady"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
