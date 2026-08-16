"""Real-browser product acceptance probe for the deployed OTBM Atlas.

This complements ``deployed_browser_probe`` with the product-readiness journeys
for Tile inspector, keyboard, touch/mobile, responsive details and reduced
motion.  It intentionally runs against the same served URL the owner uses.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urljoin, urlparse


def _url(base: str, **query: object) -> str:
    return base.rstrip("/") + "/?" + urlencode(query)


def _request_json(context: Any, base: str, relative: str) -> dict[str, Any] | None:
    response = context.request.get(urljoin(base, relative), fail_on_status_code=False)
    try:
        if not response.ok:
            return None
        value = response.json()
        return value if isinstance(value, dict) else None
    finally:
        response.dispose()


def _find_inspector_record(context: Any, base: str, manifest: dict[str, Any], *, floor: int | None = None, multi: bool = False) -> tuple[dict[str, Any], dict[str, Any]] | None:
    chunks = manifest.get("chunks", [])
    for chunk in chunks:
        if floor is not None and int(chunk.get("z", -1)) != floor:
            continue
        relative = f"data/tile-inspector/z{chunk['z']}/{chunk['chunkX']}_{chunk['chunkY']}.json"
        shard = _request_json(context, base, relative)
        if not shard:
            continue
        for record in shard.get("records", []):
            if not isinstance(record, dict):
                continue
            if multi and len(record.get("items", [])) < 2:
                continue
            if record.get("ground") or record.get("items"):
                return chunk, record
    return None


def _expected_inspector_lines(record: dict[str, Any]) -> list[str]:
    lines = [f"X {record['x']}  Y {record['y']}  Z {record['z']}"]
    ground = record.get("ground")
    if ground:
        lines.append(f"Ground ID: {ground['serverId']}")
    else:
        lines.append("Ground ID: none")
    for index, item in enumerate(record.get("items", []), start=1):
        lines.append(f"Item {index}: {item['serverId']}")
    if not record.get("items"):
        lines.append("Items: none")
    return lines


def _assert_tooltip(page: Any, record: dict[str, Any]) -> str:
    tooltip = page.locator("#tileInspectorTooltip:not([hidden])")
    tooltip.wait_for(state="visible")
    text = tooltip.inner_text()
    for expected in _expected_inspector_lines(record):
        assert expected in text, (expected, text)
    ground = record.get("ground") or {}
    if "actionId" in ground:
        assert f"AID {ground['actionId']}" in text
    if "uniqueId" in ground:
        assert f"UID {ground['uniqueId']}" in text
    for item in record.get("items", []):
        if "actionId" in item:
            assert f"AID {item['actionId']}" in text
        if "uniqueId" in item:
            assert f"UID {item['uniqueId']}" in text
    return text


def _touch_event(session: Any, kind: str, points: list[tuple[float, float]]) -> None:
    session.send(
        "Input.dispatchTouchEvent",
        {
            "type": kind,
            "touchPoints": [
                {"x": x, "y": y, "radiusX": 2, "radiusY": 2, "force": 1, "id": index}
                for index, (x, y) in enumerate(points)
            ],
        },
    )


def run(base_url: str, output: Path, *, ignore_https_errors: bool = False) -> dict[str, Any]:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError("base URL must be an absolute http(s) URL without query/fragment")
    base_url = base_url.rstrip("/") + "/"
    output.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError("Playwright 1.54.0 with Chromium is required") from error

    results: dict[str, Any] = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        desktop = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=ignore_https_errors)
        manifest = _request_json(desktop, base_url, "manifest.json")
        assert manifest and manifest.get("schemaVersion") == 3
        target = _find_inspector_record(desktop, base_url, manifest, floor=7, multi=True) or _find_inspector_record(desktop, base_url, manifest, floor=7)
        assert target, "no factual tile-inspector record found on Z7"
        chunk, record = target
        page = desktop.new_page()
        console_errors: list[str] = []
        page_errors: list[str] = []
        inspector_requests: list[str] = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("request", lambda request: inspector_requests.append(request.url) if "/data/tile-inspector/" in request.url else None)
        center_url = _url(base_url, x=record["x"] + .5, y=record["y"] + .5, z=record["z"], zoom=1, render="detailed")
        page.goto(center_url, wait_until="networkidle")
        page.wait_for_function("document.querySelector('#status')?.textContent.includes('Drag to pan')")

        # OFF -> no factual inspector work or tooltip.
        before_requests = len(inspector_requests)
        page.mouse.move(720, 450)
        page.wait_for_timeout(150)
        results["tile_inspector_off"] = {
            "status": "PASS" if page.locator("#tileInspectorTooltip").is_hidden() and len(inspector_requests) == before_requests else "FAIL",
            "requests": len(inspector_requests) - before_requests,
        }

        # ON -> exact canonical IDs, with no URL or selection mutation.
        page.locator("#tileInspector").check()
        before_url = page.url
        page.mouse.move(720, 450)
        tooltip_text = _assert_tooltip(page, record)
        results["tile_inspector_exact"] = {
            "status": "PASS" if page.url == before_url and page.locator("#details").is_hidden() else "FAIL",
            "text": tooltip_text,
            "record": record,
        }

        # Same logical tile across zoom and render modes must preserve identity.
        identity_texts = []
        for mode in ("auto", "performance", "detailed"):
            page.goto(_url(base_url, x=record["x"] + .5, y=record["y"] + .5, z=record["z"], zoom=1.5, render=mode), wait_until="networkidle")
            page.locator("#tileInspector").check()
            page.mouse.move(720, 450)
            identity_texts.append(_assert_tooltip(page, record))
        results["tile_identity_stable"] = {"status": "PASS" if len(set(identity_texts)) == 1 else "FAIL", "renderModes": ["auto", "performance", "detailed"]}

        # Overview scale is explicit and must not load a factual tile shard on hover.
        page.goto(_url(base_url, x=record["x"] + .5, y=record["y"] + .5, z=record["z"], zoom=.4, render="performance"), wait_until="networkidle")
        page.locator("#tileInspector").check()
        inspector_requests.clear()
        page.mouse.move(720, 450)
        overview_tooltip = page.locator("#tileInspectorTooltip:not([hidden])")
        overview_tooltip.wait_for(state="visible")
        overview_text = overview_tooltip.inner_text()
        results["tile_overview_policy"] = {"status": "PASS" if "detail zoom" in overview_text and not inspector_requests else "FAIL", "requests": len(inspector_requests), "text": overview_text}

        # Floor isolation using a real different-floor factual record.
        other = next((candidate for z in range(16) if z != record["z"] if (candidate := _find_inspector_record(desktop, base_url, manifest, floor=z)) is not None), None)
        if other:
            _, other_record = other
            page.goto(_url(base_url, x=other_record["x"] + .5, y=other_record["y"] + .5, z=other_record["z"], zoom=1, render="detailed"), wait_until="networkidle")
            page.locator("#tileInspector").check(); page.mouse.move(720, 450)
            text = _assert_tooltip(page, other_record)
            results["tile_floor_isolation"] = {"status": "PASS", "z": other_record["z"], "text": text}
        else:
            results["tile_floor_isolation"] = {"status": "UNKNOWN", "reason": "no second-floor factual record found"}

        # Keyboard navigation/focus.
        page.goto(center_url, wait_until="networkidle")
        canvas = page.locator("#map"); canvas.focus()
        assert page.evaluate("document.activeElement?.id") == "map"
        keyboard_before = page.url
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(100)
        arrow_url = page.url
        page.keyboard.press("+")
        page.wait_for_timeout(100)
        zoom_url = page.url
        page.goto(center_url, wait_until="networkidle")
        page.locator("#tileInspector").check()
        canvas = page.locator("#map"); canvas.focus()
        page.keyboard.press("Enter")
        keyboard_tooltip = page.locator("#tileInspectorTooltip:not([hidden])")
        keyboard_tooltip.wait_for(state="visible")
        keyboard_inspector = all(expected in keyboard_tooltip.inner_text() for expected in _expected_inspector_lines(record))
        focus_outline = page.evaluate("getComputedStyle(document.querySelector('#map')).outlineStyle !== 'none'")
        results["keyboard_navigation"] = {"status": "PASS" if arrow_url != keyboard_before and zoom_url != arrow_url and keyboard_inspector and focus_outline else "FAIL", "before": keyboard_before, "afterArrow": arrow_url, "afterZoom": zoom_url, "inspector": keyboard_inspector, "visibleFocus": focus_outline}

        page.screenshot(path=str(output / "product-desktop.png"), full_page=True)
        results["desktop_console"] = {"status": "PASS" if not console_errors and not page_errors else "FAIL", "console": console_errors, "pageErrors": page_errors}
        desktop.close()

        # Mobile/touch journey: small viewport, touch pan, two-finger zoom and tap inspection.
        mobile = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2, ignore_https_errors=ignore_https_errors)
        mpage = mobile.new_page()
        mpage.goto(center_url, wait_until="networkidle")
        mpage.wait_for_function("document.querySelector('#status')?.textContent.includes('Drag to pan')")
        responsive = mpage.locator(".top").is_visible() and mpage.locator(".controls").is_visible() and mpage.locator("#tileInspector").is_visible()
        mobile_no_overflow = mpage.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        mobile_layer_controls = mpage.locator('[data-overlay="npcSpawns"]').is_visible()
        session = mobile.new_cdp_session(mpage)
        touch_before = mpage.url
        _touch_event(session, "touchStart", [(195, 420)])
        _touch_event(session, "touchMove", [(255, 470)])
        _touch_event(session, "touchEnd", [])
        mpage.wait_for_timeout(150)
        pan_url = mpage.url
        # Recenter for deterministic pinch/tap acceptance.
        mpage.goto(center_url, wait_until="networkidle")
        pinch_before = mpage.url
        _touch_event(session, "touchStart", [(150, 420), (240, 420)])
        _touch_event(session, "touchMove", [(115, 420), (275, 420)])
        _touch_event(session, "touchEnd", [])
        mpage.wait_for_timeout(200)
        pinch_url = mpage.url
        mpage.goto(center_url, wait_until="networkidle")
        mpage.locator("#tileInspector").check()
        tap_before_url = mpage.url
        mpage.touchscreen.tap(195, 422)
        touch_tooltip = mpage.locator("#tileInspectorTooltip:not([hidden])")
        touch_tooltip.wait_for(state="visible")
        touch_text = touch_tooltip.inner_text()
        touch_ids_ok = all(expected in touch_text for expected in _expected_inspector_lines(record))
        touch_non_mutating = mpage.url == tap_before_url and mpage.locator("#details").is_hidden()
        results["mobile_touch"] = {
            "status": "PASS" if responsive and mobile_no_overflow and mobile_layer_controls and pan_url != touch_before and pinch_url != pinch_before and touch_ids_ok and touch_non_mutating else "FAIL",
            "responsive": responsive,
            "noHorizontalOverflow": mobile_no_overflow,
            "layerControlsVisible": mobile_layer_controls,
            "panChanged": pan_url != touch_before,
            "pinchChanged": pinch_url != pinch_before,
            "tapInspector": touch_ids_ok,
            "tapNonMutating": touch_non_mutating,
        }

        # Responsive details surface through real search index.
        search = _request_json(mobile, base_url, "data/search-index.json") or {"records": []}
        search_record = next((item for item in search.get("records", []) if isinstance(item, dict) and item.get("label") and item.get("position")), None)
        if search_record:
            mpage.locator("#search").fill(str(search_record["label"]))
            button = mpage.locator("#searchResults button").first; button.wait_for(state="visible"); button.click()
            details = mpage.locator("#details:not([hidden])"); details.wait_for(state="visible")
            box = details.bounding_box()
            results["mobile_details"] = {"status": "PASS" if box and box["width"] <= 390 else "FAIL", "box": box}
        else:
            results["mobile_details"] = {"status": "UNKNOWN", "reason": "no search record"}
        mpage.screenshot(path=str(output / "product-mobile.png"), full_page=True)
        mobile.close()

        # Reduced-motion context must be explicit in the rendered document.
        reduce_context = browser.new_context(viewport={"width": 1280, "height": 720}, reduced_motion="reduce", ignore_https_errors=ignore_https_errors)
        rpage = reduce_context.new_page(); rpage.goto(center_url, wait_until="networkidle")
        rpage.wait_for_function("document.documentElement.dataset.reducedMotion === 'reduce'")
        results["reduced_motion"] = {"status": "PASS", "dataset": rpage.evaluate("document.documentElement.dataset.reducedMotion")}
        reduce_context.close()
        browser_version = browser.version
        browser.close()

    required = [
        "tile_inspector_off", "tile_inspector_exact", "tile_identity_stable", "tile_overview_policy",
        "keyboard_navigation", "desktop_console", "mobile_touch", "reduced_motion",
    ]
    blockers = {name: results[name] for name in required if results.get(name, {}).get("status") != "PASS"}
    report = {"status": "PASS" if not blockers else "FAIL", "browser": {"name": "Chromium", "version": browser_version}, "results": results, "blockers": blockers}
    (output / "product-acceptance.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--output", type=Path, default=Path("build/atlas-product-evidence"))
    parser.add_argument("--ignore-https-errors", action="store_true")
    args = parser.parse_args()
    report = run(args.url, args.output, ignore_https_errors=args.ignore_https_errors)
    print(json.dumps({"status": report["status"], "browser": report["browser"], "blockers": report["blockers"]}, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
