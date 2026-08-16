"""Public deployed-browser probe with exhaustive bounded environment-animation discovery."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import _deployed_browser_probe_core as core


def _environment_result(base_url: str, output: Path, *, ignore_https_errors: bool) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError("Playwright is required; install playwright==1.54.0 and Chromium") from error

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=ignore_https_errors,
        )
        try:
            manifest_status, manifest = core._api_json(context, base_url, "manifest.json")
            index_status, index = core._api_json(context, base_url, "data/environment-animations/index.json")
            if manifest_status != 200 or not manifest:
                return {"status": "FAIL", "reason": "manifest unavailable during full environment-animation discovery", "httpStatus": manifest_status}
            if index_status != 200 or not index:
                return {"status": "PARTIAL", "reason": "final environment-animation index is absent", "httpStatus": index_status}

            statistics = index.get("statistics", {}) if isinstance(index.get("statistics"), dict) else {}
            expected_chunks = int(statistics.get("chunks", 0) or 0)
            expected_instances = int(statistics.get("instances", 0) or 0)
            if expected_chunks == 0 and expected_instances == 0:
                return {
                    "status": "PASS",
                    "reason": "final environment-animation index reports no available animation instances",
                    "indexStatistics": statistics,
                    "scannedChunks": 0,
                }

            chunks = manifest.get("chunks", []) if isinstance(manifest.get("chunks"), list) else []
            candidates = sorted(
                (chunk for chunk in chunks if isinstance(chunk, dict)),
                key=lambda chunk: (
                    abs(int(chunk.get("z", 0)) - core.DEFAULT_Z),
                    int(chunk.get("z", 0)),
                    int(chunk.get("chunkY", 0)),
                    int(chunk.get("chunkX", 0)),
                ),
            )
            record = None
            scanned = 0
            found_shards = 0
            for chunk in candidates:
                scanned += 1
                relative = f"data/environment-animations/chunks/z{chunk['z']}/{chunk['chunkX']}_{chunk['chunkY']}.json"
                shard_status, shard = core._api_json(context, base_url, relative)
                if shard_status != 200 or not shard:
                    continue
                found_shards += 1
                records = shard.get("records", [])
                if isinstance(records, list) and records:
                    record = records[0]
                    break

            if record is None:
                status = "FAIL" if expected_chunks > 0 or expected_instances > 0 else "PASS"
                return {
                    "status": status,
                    "reason": "no environment-animation record found after bounded full-manifest discovery",
                    "scannedChunks": scanned,
                    "foundShards": found_shards,
                    "indexStatistics": statistics,
                }

            page = context.new_page()
            position = record["position"]
            page.goto(
                core._url(
                    base_url,
                    x=position["x"],
                    y=position["y"],
                    z=position["z"],
                    zoom=2,
                    render="detailed",
                ),
                wait_until="networkidle",
            )
            page.wait_for_timeout(1200)
            frames = record.get("frames", [])
            frame_status = core._api_status(context, base_url, str(frames[0])) if frames else 0
            canvas_pixels = core._canvas_has_pixels(page, "#environmentAnimations")
            page.screenshot(path=str(output / "03-environment-animation-full.png"), full_page=True)
            return {
                "status": "PASS" if frame_status == 200 and canvas_pixels else "FAIL",
                "serverId": record.get("serverId"),
                "frameHttpStatus": frame_status,
                "canvasPixels": canvas_pixels,
                "scannedChunks": scanned,
                "foundShards": found_shards,
                "indexStatistics": statistics,
            }
        finally:
            context.close()
            browser.close()


def _finalize_report(report: dict[str, Any], *, allow_partial_animations: bool) -> dict[str, Any]:
    required = {
        "initial_load", "warm_load", "atlas_identity", "pan", "zoom", "floor_switch", "coordinate_jump", "search",
        "details_surface", "factual_overlays", "render_mode_switching", "overview_detail_transition",
        "creature_rendering", "creature_animation", "environment_animation", "deep_link_reload", "back_forward",
        "missing_resource_404", "no_runaway_request_loop", "console_errors", "failed_network_requests", "navigation_performance",
    }
    partial_allowed = {"environment_animation"} if allow_partial_animations else set()
    results = report.get("results", {})
    blockers = {
        name: results[name]
        for name in required
        if name in results and results[name].get("status") != "PASS" and name not in partial_allowed
    }
    report["blockers"] = blockers
    report["status"] = (
        "PASS"
        if not blockers
        else "PARTIAL"
        if all(item.get("status") in {"PARTIAL", "UNKNOWN"} for item in blockers.values())
        else "FAIL"
    )
    return report


def run_probe(
    base_url: str,
    output: Path,
    *,
    allow_partial_animations: bool = False,
    ignore_https_errors: bool = False,
) -> dict[str, Any]:
    # The core journey deliberately tolerates an inconclusive environment search;
    # this public wrapper then resolves that one result over the complete, fixed
    # 3494-chunk manifest before computing the final acceptance status.
    report = core.run_probe(
        base_url,
        output,
        allow_partial_animations=True,
        ignore_https_errors=ignore_https_errors,
    )
    environment = report.get("results", {}).get("environment_animation", {})
    if environment.get("status") != "PASS":
        report.setdefault("results", {})["environment_animation"] = _environment_result(
            base_url.rstrip("/") + "/",
            output,
            ignore_https_errors=ignore_https_errors,
        )
    report = _finalize_report(report, allow_partial_animations=allow_partial_animations)
    (output / "browser-e2e.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--output", type=Path, default=Path("build/atlas-browser-evidence"))
    parser.add_argument(
        "--allow-partial-animations",
        action="store_true",
        help="diagnostic core preview only; this may tolerate missing environment animation but cannot close ATLAS-PR-003",
    )
    parser.add_argument(
        "--ignore-https-errors",
        action="store_true",
        help="private DSM testing only when the owner knowingly uses a self-signed certificate",
    )
    args = parser.parse_args()
    report = run_probe(
        args.url,
        args.output,
        allow_partial_animations=args.allow_partial_animations,
        ignore_https_errors=args.ignore_https_errors,
    )
    print(json.dumps({"status": report["status"], "browser": report["browser"], "blockers": report["blockers"]}, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
