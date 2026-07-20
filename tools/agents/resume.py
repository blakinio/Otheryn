#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, re
from pathlib import Path
import checkpoint


def task_id(path: Path) -> str:
    match = re.search(r"(?m)^task_id:\s*[\"']?([^\"'\n]+)", path.read_text(encoding="utf-8"))
    return match.group(1).strip() if match else path.stem


def bundle(path: Path) -> dict[str, object]:
    data = checkpoint.parse(path)
    if data is None:
        return {"task_id": task_id(path), "checkpoint": str(path), "warning": "CHECKPOINT_MISSING", "next_action": "Reconstruct and write a valid Context checkpoint from current Git, PR, CI and task evidence before substantive implementation."}
    errors = checkpoint.validate(data, path)
    if errors: raise ValueError("; ".join(errors))
    return {"task_id": task_id(path), "checkpoint": str(path), **{k: data.get(k) for k in ("head", "branch", "pr", "status", "proven", "derived", "unknown", "conflicts", "first_failure", "changed_paths", "validation", "blockers", "next_action")}}


def render(data: dict[str, object]) -> str:
    lines = [f"Continue task {data['task_id']} from repository state.", "Do not rely on previous chat history.", f"CHECKPOINT: {data['checkpoint']}"]
    if data.get("warning"):
        return "\n".join(lines + [f"WARNING: {data['warning']}", f"NEXT_ACTION: {data['next_action']}", "Verify live repository state before substantive implementation."])
    lines += [f"HEAD: {data.get('head', 'UNKNOWN')}", f"BRANCH: {data.get('branch', 'UNKNOWN')}", f"PR: {data.get('pr', 'none')}", f"STATUS: {data.get('status', 'UNKNOWN')}"]
    for label, key in (("PROVEN", "proven"), ("DERIVED", "derived"), ("UNKNOWN", "unknown"), ("CONFLICTS", "conflicts"), ("CHANGED_PATHS", "changed_paths"), ("BLOCKERS", "blockers")):
        lines.append(label + ":")
        lines += [f"- {item}" for item in data.get(key, [])]
    failure = data.get("first_failure", {})
    if isinstance(failure, dict): lines += [f"FIRST_FAILURE_MARKER: {failure.get('marker', 'none')}", f"FIRST_FAILURE_EVIDENCE: {failure.get('evidence', 'none')}"]
    lines.append("VALIDATION:")
    for item in data.get("validation", []):
        if isinstance(item, dict): lines.append(f"- {item.get('command', '')}: {item.get('result', '')}; evidence={item.get('evidence', '')}")
    lines += [f"NEXT_ACTION: {data.get('next_action', 'UNKNOWN')}", "", "OPERATING_RULES:", "- Treat Git, checkpoint and live PR/CI as source of truth.", "- Verify only live state that can invalidate NEXT_ACTION.", "- Do not repeat the full preflight when checkpoint and live state agree.", "- Do not rediscover PROVEN facts unless live evidence changed.", "- Preserve UNKNOWN and CONFLICT; never guess.", "- Do not paste full logs, diffs or old chat history.", "- Execute NEXT_ACTION autonomously when safe.", "- Update the checkpoint and leave exactly one next_action before handing off."]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate a compact continuation prompt from a task checkpoint")
    ap.add_argument("--task", type=Path, required=True); ap.add_argument("--json", action="store_true"); args = ap.parse_args()
    data = bundle(args.task.resolve()); print(json.dumps(data, indent=2) if args.json else render(data)); return 0


if __name__ == "__main__": raise SystemExit(main())
