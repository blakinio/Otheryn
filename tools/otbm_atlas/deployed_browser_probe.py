"""Exercise a deployed OTBM Atlas through the real browser URL and record evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
from typing import Any
from urllib.parse import urlencode, urljoin, urlparse

DEFAULT_X = 32360
DEFAULT_Y = 32230
DEFAULT_Z = 7


def _url(base: str, **query: object) -> str:
    return base.rstrip("/") + "/?" + urlencode(query)


def _resource_metrics(page: Any) -> dict[str, Any]:
    entries = page.evaluate(
        """() => performance.getEntriesByType('resource').map(r => ({
          name:r.name, initiatorType:r.initiatorType, duration:r.duration,
          transferSize:r.transferSize, encodedBodySize:r.encodedBodySize,
          decodedBodySize:r.decodedBodySize
        }))"""
    )
    chunks = [entry for entry in entries if "/tiles/" in entry["name"] or "/overview" in entry["name"]]
    names = [entry["name"] for entry in entries]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    return {
        "requests": len(entries),
        "transferBytes": sum(int(entry.get("transferSize") or 0) for entry in entries),
        "encodedBodyBytes": sum(int(entry.get("encodedBodySize") or 0) for entry in entries),
        "decodedBodyBytes": sum(int(entry.get("decodedBodySize") or 0) for entry in entries),
        "zeroTransferEntries": sum(1 for entry in entries if int(entry.get("transferSize") or 0) == 0),
        "meanResourceDurationMs": round(sum(float(entry.get("duration") or 0) for entry in entries) / len(entries), 3) if entries else 0,
        "maxResourceDurationMs": round(max((float(entry.get("duration") or 0) for entry in entries), default=0), 3),
        "chunkRequests": len(chunks),
        "meanChunkDurationMs": round(sum(float(entry.get("duration") or 0) for entry in chunks) / len(chunks), 3) if chunks else 0,
        "maxChunkDurationMs": round(max((float(entry.get("duration") or 0) for entry in chunks), default=0), 3),
        "duplicateResourceNames": duplicates,
    }


def _memory(page: Any) -> dict[str, Any] | str:
    return page.evaluate(
        """() => performance.memory ? {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize,
          jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
        } : 'UNKNOWN'"""
    )


def _canvas_has_pixels(page: Any, selector: str) -> bool:
    return bool(page.evaluate(
        """selector => {
          const canvas=document.querySelector(selector); if(!canvas||!canvas.width||!canvas.height)return false;
          const data=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
          for(let i=3;i<data.length;i+=4)if(data[i])return true;
          return false;
        }""", selector
    ))


def _fetch_json(page: Any, relative: str) -> dict[str, Any] | None:
    return page.evaluate(
        """async relative => {
          const response=await fetch(relative,{cache:'no-store'});
          if(!response.ok)return null;
          try{return await response.json()}catch{return null}
        }""", relative
    )


def _record(results: dict[str, Any], name: str, status: str, **evidence: object) -> None:
    results[name] = {"status": status, **evidence}


def run_probe(base_url: str, output: Path, *, allow_partial_animations: bool = False, ignore_https_errors: bool = False) -> dict[str, Any]:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("preview URL must be an absolute http(s) URL")
    base_url = base_url.rstrip("/") + "/"
    output.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError("Playwright is required; install playwright==1.54.0 and Chromium") from error

    results: dict[str, Any] = {}
    console_errors: list[str] = []
    console_warnings: list[str] = []
    page_errors: list[str] = []
    bad_responses: list[str] = []
    response_count = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=ignore_https_errors)
        page = context.new_page()

        def on_console(message: Any) -> None:
            if message.type == "error":
                console_errors.append(message.text)
            elif message.type == "warning":
                console_warnings.append(message.text)

        def on_response(response: Any) -> None:
            nonlocal response_count
            response_count += 1
            if response.status >= 400:
                bad_responses.append(f"{response.status}:{response.url}")

        page.on("console", on_console)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("response", on_response)

        cold_url = _url(base_url, x=DEFAULT_X, y=DEFAULT_Y, z=DEFAULT_Z, zoom=1, render="detailed")
        cold_start = time.perf_counter()
        page.goto(cold_url, wait_until="networkidle")
        page.wait_for_function("document.querySelector('#status')?.textContent.includes('Drag to pan')")
        cold_interactable_ms = round((time.perf_counter() - cold_start) * 1000, 3)
        cold_metrics = _resource_metrics(page)
        cold_metrics["interactableMs"] = cold_interactable_ms
        cold_metrics["memory"] = _memory(page)
        page.screenshot(path=str(output / "01-cold-load.png"), full_page=True)
        _record(results, "initial_load", "PASS", url=page.url, metrics=cold_metrics)

        manifest = _fetch_json(page, "manifest.json")
        if not manifest or manifest.get("schemaVersion") != 3 or len(manifest.get("chunks", [])) != 3494:
            _record(results, "atlas_identity", "FAIL", manifestSchema=None if not manifest else manifest.get("schemaVersion"), chunks=None if not manifest else len(manifest.get("chunks", [])))
            chunks: list[dict[str, Any]] = []
        else:
            chunks = list(manifest["chunks"])
            floors = sorted({int(chunk["z"]) for chunk in chunks})
            sources = manifest.get("sources", {})
            identity_ok = floors == list(range(16)) and sources.get("mapSha256") == "3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034"
            _record(results, "atlas_identity", "PASS" if identity_ok else "FAIL", schemaVersion=manifest.get("schemaVersion"), chunks=len(chunks), floors=floors, sources=sources)

        page.evaluate("performance.clearResourceTimings()")
        warm_start = time.perf_counter()
        page.reload(wait_until="networkidle")
        page.wait_for_function("document.querySelector('#status')?.textContent.includes('Drag to pan')")
        warm_metrics = _resource_metrics(page)
        warm_metrics["interactableMs"] = round((time.perf_counter() - warm_start) * 1000, 3)
        warm_metrics["memory"] = _memory(page)
        _record(results, "warm_load", "PASS", metrics=warm_metrics)

        page.goto(cold_url, wait_until="networkidle")
        page.wait_for_function("document.querySelector('#map')")
        before_url = page.url
        page.mouse.move(720, 450)
        page.mouse.down()
        page.mouse.move(820, 520, steps=8)
        page.mouse.up()
        _record(results, "pan", "PASS" if page.url != before_url else "FAIL", before=before_url, after=page.url)

        before_zoom = page.url
        page.locator("#zoomIn").click()
        page.wait_for_timeout(100)
        page.locator("#zoomOut").click()
        _record(results, "zoom", "PASS" if "zoom=" in page.url and page.url != before_zoom else "FAIL", url=page.url)

        current_floor = page.locator("#floor").input_value()
        floor_options = page.locator("#floor option").evaluate_all("nodes => nodes.map(n => n.value)")
        alternate_floor = next((value for value in floor_options if value != current_floor), None)
        if alternate_floor is None:
            _record(results, "floor_switch", "FAIL", reason="no alternate populated floor")
        else:
            page.locator("#floor").select_option(alternate_floor)
            floor_ok = f"z={alternate_floor}" in page.url.lower()
            page.locator("#floor").select_option(current_floor)
            _record(results, "floor_switch", "PASS" if floor_ok else "FAIL", alternateFloor=alternate_floor)

        target_chunk = next((chunk for chunk in chunks if int(chunk.get("z", -1)) == DEFAULT_Z), None)
        if target_chunk:
            bounds = target_chunk["logicalBounds"]
            target_x = (int(bounds[0]) + int(bounds[1])) // 2
            target_y = (int(bounds[2]) + int(bounds[3])) // 2
            page.locator("#x").fill(str(target_x))
            page.locator("#y").fill(str(target_y))
            page.locator("#z").fill(str(DEFAULT_Z))
            page.locator("#jump").click()
            jump_ok = f"x={target_x}" in page.url and f"y={target_y}" in page.url and f"z={DEFAULT_Z}" in page.url
            _record(results, "coordinate_jump", "PASS" if jump_ok else "FAIL", target=[target_x, target_y, DEFAULT_Z], url=page.url)
        else:
            _record(results, "coordinate_jump", "FAIL", reason="no Z7 chunk")

        search_index = _fetch_json(page, "data/search-index.json") or {"records": []}
        search_record = next((record for record in search_index.get("records", []) if isinstance(record, dict) and record.get("label") and record.get("position")), None)
        if search_record:
            page.locator("#search").fill(str(search_record["label"]))
            button = page.locator("#searchResults button").first
            button.wait_for(state="visible")
            button.click()
            page.locator("#details:not([hidden])").wait_for(state="visible")
            _record(results, "search", "PASS", label=search_record["label"], kind=search_record.get("kind"))
            _record(results, "details_surface", "PASS", text=page.locator("#details").inner_text()[:1000])
        else:
            _record(results, "search", "FAIL", reason="search index has no navigable record")
            _record(results, "details_surface", "FAIL", reason="search could not open details")

        overlay_boxes = page.locator("[data-overlay]")
        if overlay_boxes.count():
            box = overlay_boxes.first
            kind = box.get_attribute("data-overlay")
            if not box.is_checked():
                box.check()
            _record(results, "factual_overlays", "PASS" if kind in page.url else "FAIL", overlay=kind, url=page.url)
        else:
            _record(results, "factual_overlays", "FAIL", reason="no factual overlay controls")

        render_states: dict[str, bool] = {}
        for mode in ("performance", "detailed", "auto"):
            page.locator("#renderMode").select_option(mode)
            page.wait_for_timeout(100)
            render_states[mode] = page.locator("#renderMode").input_value() == mode and f"render={mode}" in page.url
        _record(results, "render_mode_switching", "PASS" if all(render_states.values()) else "FAIL", modes=render_states)

        page.locator("#showDiagnostics").check()
        page.goto(_url(base_url, x=DEFAULT_X, y=DEFAULT_Y, z=DEFAULT_Z, zoom=.12, render="auto"), wait_until="networkidle")
        page.locator("#showDiagnostics").check()
        low = page.locator("#diagnostics").inner_text()
        page.goto(_url(base_url, x=DEFAULT_X, y=DEFAULT_Y, z=DEFAULT_Z, zoom=1.2, render="auto"), wait_until="networkidle")
        page.locator("#showDiagnostics").check()
        detailed = page.locator("#diagnostics").inner_text()
        transition_ok = "Base layer: overview-low" in low and "Base layer: detailed" in detailed
        _record(results, "overview_detail_transition", "PASS" if transition_ok else "FAIL", lowDiagnostics=low, detailedDiagnostics=detailed)

        spawns = _fetch_json(page, "data/spawns.json") or {}
        creature_records = []
        for kind in ("npcSpawns", "monsterSpawns", "supplementalNpcSpawns", "supplementalMonsterSpawns"):
            for record in spawns.get(kind, []) if isinstance(spawns.get(kind, []), list) else []:
                if isinstance(record, dict) and record.get("position"):
                    creature_records.append((kind, record))
        static = next(((kind, record) for kind, record in creature_records if record.get("sprite")), None)
        animated = next(((kind, record) for kind, record in creature_records if record.get("spriteAnimation")), None)
        if static:
            kind, record = static
            position = record["position"]
            page.goto(_url(base_url, x=position["x"], y=position["y"], z=position["z"], zoom=1, render="detailed", layers=kind), wait_until="networkidle")
            page.wait_for_timeout(500)
            sprite_response = page.evaluate("path => fetch(path,{cache:'no-store'}).then(r => r.status)", record["sprite"])
            _record(results, "creature_rendering", "PASS" if sprite_response == 200 else "FAIL", kind=kind, sprite=record["sprite"], httpStatus=sprite_response)
            page.screenshot(path=str(output / "02-creature.png"), full_page=True)
        else:
            _record(results, "creature_rendering", "UNKNOWN", reason="no creature record with sprite reference found")

        if animated:
            kind, record = animated
            position = record["position"]
            page.goto(_url(base_url, x=position["x"], y=position["y"], z=position["z"], zoom=1, render="detailed", layers=kind), wait_until="networkidle")
            page.wait_for_timeout(1200)
            descriptor_status = page.evaluate("path => fetch(path,{cache:'no-store'}).then(r => r.status)", record["spriteAnimation"])
            animation_pixels = _canvas_has_pixels(page, "#creatureAnimations")
            _record(results, "creature_animation", "PASS" if descriptor_status == 200 and animation_pixels else "FAIL", descriptor=record["spriteAnimation"], httpStatus=descriptor_status, canvasPixels=animation_pixels)
        else:
            _record(results, "creature_animation", "UNKNOWN", reason="no creature animation descriptor reference found")

        environment_index = _fetch_json(page, "data/environment-animations/index.json")
        if not environment_index:
            _record(results, "environment_animation", "PARTIAL", reason="final environment-animation index is absent")
        else:
            record = None
            candidate_chunks = sorted(chunks, key=lambda chunk: abs(int(chunk.get("z", 0)) - DEFAULT_Z))[:128]
            for chunk in candidate_chunks:
                relative = f"data/environment-animations/chunks/z{chunk['z']}/{chunk['chunkX']}_{chunk['chunkY']}.json"
                shard = _fetch_json(page, relative)
                records = [] if not shard else shard.get("records", [])
                if records:
                    record = records[0]
                    break
            if not record:
                _record(results, "environment_animation", "PARTIAL", reason="environment index exists but no animation shard was found in bounded scan", indexStatistics=environment_index.get("statistics", {}))
            else:
                position = record["position"]
                page.goto(_url(base_url, x=position["x"], y=position["y"], z=position["z"], zoom=2, render="detailed"), wait_until="networkidle")
                page.wait_for_timeout(1200)
                frame_status = page.evaluate("path => fetch(path,{cache:'no-store'}).then(r => r.status)", record["frames"][0])
                animation_pixels = _canvas_has_pixels(page, "#environmentAnimations")
                _record(results, "environment_animation", "PASS" if frame_status == 200 and animation_pixels else "FAIL", serverId=record.get("serverId"), httpStatus=frame_status, canvasPixels=animation_pixels)
                page.screenshot(path=str(output / "03-environment-animation.png"), full_page=True)

        deep = _url(base_url, x=DEFAULT_X + 3, y=DEFAULT_Y + 4, z=DEFAULT_Z, zoom=.75, render="performance")
        page.goto(deep, wait_until="networkidle")
        page.reload(wait_until="networkidle")
        reload_ok = f"x={DEFAULT_X + 3}" in page.url and f"y={DEFAULT_Y + 4}" in page.url and "render=performance" in page.url
        _record(results, "deep_link_reload", "PASS" if reload_ok else "FAIL", url=page.url)

        first = _url(base_url, x=DEFAULT_X, y=DEFAULT_Y, z=DEFAULT_Z, zoom=.5, render="auto")
        second = _url(base_url, x=DEFAULT_X + 20, y=DEFAULT_Y + 20, z=DEFAULT_Z, zoom=.5, render="auto")
        page.goto(first, wait_until="networkidle")
        page.goto(second, wait_until="networkidle")
        page.go_back(wait_until="networkidle")
        back_ok = f"x={DEFAULT_X}" in page.url and f"y={DEFAULT_Y}" in page.url
        page.go_forward(wait_until="networkidle")
        forward_ok = f"x={DEFAULT_X + 20}" in page.url and f"y={DEFAULT_Y + 20}" in page.url
        _record(results, "back_forward", "PASS" if back_ok and forward_ok else "FAIL", back=back_ok, forward=forward_ok)

        missing_path = f"__atlas_missing_probe_{int(time.time())}.json"
        missing_status = page.evaluate("path => fetch(path,{cache:'no-store'}).then(r => r.status)", missing_path)
        _record(results, "missing_resource_404", "PASS" if missing_status == 404 else "FAIL", statusCode=missing_status)

        page.goto(_url(base_url, x=DEFAULT_X, y=DEFAULT_Y, z=DEFAULT_Z, zoom=.18, render="performance"), wait_until="networkidle")
        before_idle = response_count
        page.wait_for_timeout(3000)
        idle_requests = response_count - before_idle
        _record(results, "no_runaway_request_loop", "PASS" if idle_requests <= 2 else "FAIL", requestsDuring3Seconds=idle_requests)

        page.evaluate("performance.clearResourceTimings()")
        nav_start = time.perf_counter()
        jumps: list[list[int]] = []
        for chunk in [chunk for chunk in chunks if int(chunk.get("z", -1)) == DEFAULT_Z][:4]:
            bounds = chunk["logicalBounds"]
            x = (int(bounds[0]) + int(bounds[1])) // 2
            y = (int(bounds[2]) + int(bounds[3])) // 2
            page.goto(_url(base_url, x=x, y=y, z=DEFAULT_Z, zoom=1, render="detailed"), wait_until="networkidle")
            jumps.append([x, y, DEFAULT_Z])
        navigation = _resource_metrics(page)
        navigation["elapsedMs"] = round((time.perf_counter() - nav_start) * 1000, 3)
        navigation["memory"] = _memory(page)
        navigation["jumps"] = jumps
        _record(results, "navigation_performance", "PASS" if jumps else "UNKNOWN", metrics=navigation)

        page.screenshot(path=str(output / "04-final.png"), full_page=True)
        browser_version = browser.version
        context.close()
        browser.close()

    expected_404_marker = "__atlas_missing_probe_"
    unexpected_bad = [entry for entry in bad_responses if expected_404_marker not in entry]
    _record(results, "console_errors", "PASS" if not console_errors and not page_errors else "FAIL", consoleErrors=console_errors, pageErrors=page_errors, warnings=console_warnings)
    _record(results, "failed_network_requests", "PASS" if not unexpected_bad else "FAIL", responses=unexpected_bad)

    required = {
        "initial_load", "atlas_identity", "pan", "zoom", "floor_switch", "coordinate_jump", "search",
        "details_surface", "factual_overlays", "render_mode_switching", "overview_detail_transition", "creature_rendering",
        "creature_animation", "environment_animation", "deep_link_reload", "back_forward", "missing_resource_404",
        "no_runaway_request_loop", "console_errors", "failed_network_requests", "navigation_performance",
    }
    partial_allowed = {"creature_rendering", "creature_animation", "environment_animation"} if allow_partial_animations else set()
    blockers = {
        name: results[name]
        for name in required
        if name in results and results[name]["status"] != "PASS" and name not in partial_allowed
    }
    report = {
        "status": "PASS" if not blockers else "PARTIAL" if all(item["status"] in {"PARTIAL", "UNKNOWN"} for item in blockers.values()) else "FAIL",
        "previewUrl": base_url,
        "browser": {"name": "Chromium", "version": browser_version},
        "results": results,
        "cold": results.get("initial_load", {}).get("metrics", "UNKNOWN"),
        "warm": results.get("warm_load", {}).get("metrics", "UNKNOWN"),
        "navigation": results.get("navigation_performance", {}).get("metrics", "UNKNOWN"),
        "blockers": blockers,
    }
    (output / "browser-e2e.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--output", type=Path, default=Path("build/atlas-browser-evidence"))
    parser.add_argument("--allow-partial-animations", action="store_true", help="diagnostic preview only; never use this to close ATLAS-PR-003")
    parser.add_argument("--ignore-https-errors", action="store_true", help="private DSM testing only when the owner knowingly uses a self-signed certificate")
    args = parser.parse_args()
    report = run_probe(args.url, args.output, allow_partial_animations=args.allow_partial_animations, ignore_https_errors=args.ignore_https_errors)
    print(json.dumps({"status": report["status"], "browser": report["browser"], "blockers": report["blockers"]}, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
