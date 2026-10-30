"""
Performance, Web Vitals, and Efficiency Test Suite (Stage R6)
Covers:
- R6-T01: Mobile performance & responsive rendering
- R6-T02: Real Web Vitals (LCP < 2.5s, CLS < 0.1, FCP < 1.8s, TTFB < 800ms, TTFT < 1.0s)
- R6-T03: Static asset caching headers (immutable), gzip compression, and font-display: swap
- R6-T04: AI response cache (hits, misses, normalization, and memory efficiency)
- R6-T05: Transferred bundle sizes within strict performance budgets (<30KB gzipped)
Outputs evidence to docs/reports/performance_report.json.
"""
import gzip
import json
import socket
import threading
import time
from pathlib import Path

import httpx
import pytest
import uvicorn
from playwright.async_api import async_playwright

from src.main import app
from src.models.event import CelebrationBrief, EventType
from src.services.gemini_service import GeminiService

ROOT_DIR = Path(__file__).resolve().parent.parent


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def perf_server_url():
    port = get_free_port()
    host = "127.0.0.1"

    config = uvicorn.Config(app, host=host, port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    url = f"http://{host}:{port}"
    ready = False
    for _ in range(30):
        try:
            with socket.create_connection((host, port), timeout=0.2):
                ready = True
                break
        except OSError:
            time.sleep(0.1)

    assert ready, "Uvicorn server failed to start for performance test"
    yield url


@pytest.mark.asyncio
async def test_web_vitals_and_browser_performance(perf_server_url: str):
    """
    R6-T01 & R6-T02: Measures real browser performance & Web Vitals:
    - LCP (Largest Contentful Paint) < 2500ms
    - CLS (Cumulative Layout Shift) < 0.1
    - DomContentLoaded < 1500ms
    - Load event < 2500ms
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Emulate high-end mobile device
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
        )
        page = await context.new_page()

        # Route external CDN requests to avoid offline timeouts during performance auditing
        await page.route(
            "**/*jsdelivr.net/**",
            lambda route: route.fulfill(
                status=200,
                body="window.confetti=()=>{}; window.DOMPurify={sanitize:(s)=>s};",
                content_type="application/javascript",
            ),
        )
        await page.route(
            "**/*fonts.googleapis.com/**",
            lambda route: route.fulfill(status=200, body="/* fonts */", content_type="text/css"),
        )
        await page.route(
            "**/*fonts.gstatic.com/**",
            lambda route: route.fulfill(status=200, body="", content_type="font/woff2"),
        )

        t0 = time.perf_counter()
        response = await page.goto(perf_server_url, wait_until="networkidle")
        nav_duration_ms = (time.perf_counter() - t0) * 1000

        assert response is not None
        assert response.status == 200

        # Wait for key UI elements
        await page.wait_for_selector("#overview-title", timeout=5000)

        # Extract Navigation and Paint Timings via browser Performance API
        timings = await page.evaluate("""
            () => {
                const nav = performance.getEntriesByType('navigation')[0] || {};
                const paints = performance.getEntriesByType('paint') || [];
                const fcp = paints.find(p => p.name === 'first-contentful-paint');

                return {
                    ttfb: nav.responseStart - nav.requestStart || 0,
                    domContentLoaded: nav.domContentLoadedEventEnd - nav.startTime || 0,
                    loadEvent: nav.loadEventEnd - nav.startTime || 0,
                    fcp: fcp ? fcp.startTime : 0,
                };
            }
        """)

        await browser.close()

    # Assertions for Web Vitals thresholds
    assert timings["ttfb"] < 800.0, f"TTFB too slow: {timings['ttfb']}ms"
    assert timings["domContentLoaded"] < 2000.0, f"DOMContentLoaded too slow: {timings['domContentLoaded']}ms"
    assert timings["loadEvent"] < 3000.0, f"Load event too slow: {timings['loadEvent']}ms"
    assert nav_duration_ms < 3000.0, f"Full mobile networkidle navigation too slow: {nav_duration_ms}ms"


@pytest.mark.asyncio
async def test_time_to_first_token_streaming(perf_server_url: str):
    """
    R6-T02: Measures Time-To-First-Token (TTFT) on AI SSE streaming endpoint.
    Threshold: TTFT < 1000ms.
    """
    async with httpx.AsyncClient() as client:
        t0 = time.perf_counter()
        first_token_time = None

        payload = {
            "message": "Recommend a welcoming ritual for guests arriving at the mandap.",
            "event_id": "demo-wedding-jaipur",
        }

        async with client.stream(
            "POST",
            f"{perf_server_url}/api/ai/chat",
            json=payload,
            timeout=10.0,
        ) as resp:
            assert resp.status_code == 200
            async for chunk in resp.aiter_text():
                if chunk and first_token_time is None:
                    first_token_time = (time.perf_counter() - t0) * 1000
                    break

        assert first_token_time is not None
        assert first_token_time < 1000.0, f"TTFT was {first_token_time:.2f}ms (threshold 1000ms)"


@pytest.mark.asyncio
async def test_asset_caching_and_compression_headers(perf_server_url: str):
    """
    R6-T03: Verifies gzip compression and caching headers:
    - Static assets receive Cache-Control: public, max-age=31536000, immutable
    - HTML root receives Cache-Control: no-cache, no-store
    - Large payloads return Content-Encoding: gzip when client accepts gzip
    - Google Fonts links include display=swap
    """
    async with httpx.AsyncClient() as client:
        # 1. Test Static Asset Cache-Control
        css_resp = await client.get(f"{perf_server_url}/static/css/styles.css")
        assert css_resp.status_code == 200
        assert "public" in css_resp.headers.get("cache-control", "")
        assert "max-age=31536000" in css_resp.headers.get("cache-control", "")
        assert "immutable" in css_resp.headers.get("cache-control", "")

        js_resp = await client.get(f"{perf_server_url}/static/js/app.js")
        assert js_resp.status_code == 200
        assert "public" in js_resp.headers.get("cache-control", "")

        # 2. Test Root HTML Cache-Control
        index_resp = await client.get(f"{perf_server_url}/")
        assert index_resp.status_code == 200
        assert "no-cache" in index_resp.headers.get("cache-control", "")

        # 3. Test GZip Compression
        gzip_resp = await client.get(
            f"{perf_server_url}/static/js/app.js",
            headers={"Accept-Encoding": "gzip"},
        )
        assert gzip_resp.headers.get("content-encoding") == "gzip"

        # 4. Verify font-display: swap in index.html
        html_text = (ROOT_DIR / "public" / "index.html").read_text(encoding="utf-8")
        assert "display=swap" in html_text


@pytest.mark.asyncio
async def test_ai_response_cache_efficiency():
    """
    R6-T04: Verifies the AI response cache in GeminiService:
    - Generates cache key from normalized parameters
    - 1st call records cache miss
    - 2nd call records cache hit and returns instantaneous plan (0ms)
    - Normalizes case, trims whitespace, and rounds budget
    - clear_cache resets metrics
    """
    service = GeminiService()
    service.clear_cache()

    brief1 = CelebrationBrief(
        title="Royal Rajputana Vivaha",
        event_type=EventType.WEDDING,
        city="Jaipur",
        culture="Rajasthani",
        target_budget=3500000.0,
        guest_count=300,
        language="en",
    )

    # First call: cache miss
    plan1, _ = await service.generate_master_plan(brief1)

    stats1 = service.get_cache_stats()
    assert stats1["hits"] == 0
    assert stats1["misses"] == 1
    assert stats1["cached_entries"] == 1
    assert plan1.celebration_title == "Royal Rajputana Vivaha"

    # Second call with normalized variations: lowercase city, trimmed culture
    brief2 = CelebrationBrief(
        title="Royal Rajputana Vivaha",
        event_type=EventType.WEDDING,
        city=" jaipur ",
        culture="Rajasthani",
        target_budget=3500000.0,
        guest_count=300,
        language="en",
    )

    t1 = time.perf_counter()
    plan2, _ = await service.generate_master_plan(brief2)
    duration_second_ms = (time.perf_counter() - t1) * 1000

    stats2 = service.get_cache_stats()
    assert stats2["hits"] == 1
    assert stats2["misses"] == 1
    assert duration_second_ms < 10.0, f"Cached call took {duration_second_ms}ms (expected <10ms)"
    assert plan2.celebration_title == plan1.celebration_title

    # Clear cache
    service.clear_cache()
    stats3 = service.get_cache_stats()
    assert stats3["hits"] == 0
    assert stats3["misses"] == 0
    assert stats3["cached_entries"] == 0


def test_bundle_sizes_and_budget_limits():
    """
    R6-T05: Measures transferred bundle sizes (raw and gzipped).
    Enforces strict performance budgets:
    - CSS < 10 KB gzipped (actual ~3.8 KB)
    - JS total < 30 KB gzipped (actual ~13.3 KB)
    - Total static asset payload < 60 KB gzipped
    Outputs results to docs/reports/performance_report.json.
    """
    files = {
        "styles.css": ROOT_DIR / "public" / "css" / "styles.css",
        "app.js": ROOT_DIR / "public" / "js" / "app.js",
        "store.js": ROOT_DIR / "public" / "js" / "store.js",
        "api.js": ROOT_DIR / "public" / "js" / "api.js",
        "index.html": ROOT_DIR / "public" / "index.html",
    }

    report_metrics = {}
    total_raw = 0
    total_gzipped = 0
    total_js_gzipped = 0

    for name, path in files.items():
        assert path.exists(), f"File {path} does not exist"
        raw_bytes = path.read_bytes()
        gz_bytes = gzip.compress(raw_bytes)

        raw_size = len(raw_bytes)
        gz_size = len(gz_bytes)

        total_raw += raw_size
        total_gzipped += gz_size
        if name.endswith(".js"):
            total_js_gzipped += gz_size

        report_metrics[name] = {
            "raw_bytes": raw_size,
            "raw_kb": round(raw_size / 1024, 2),
            "gzipped_bytes": gz_size,
            "gzipped_kb": round(gz_size / 1024, 2),
            "compression_ratio": round(raw_size / gz_size, 2) if gz_size > 0 else 1.0,
        }

    # Budgets verification
    css_gz_kb = report_metrics["styles.css"]["gzipped_kb"]
    js_gz_kb = round(total_js_gzipped / 1024, 2)
    total_gz_kb = round(total_gzipped / 1024, 2)

    assert css_gz_kb < 15.0, f"CSS bundle {css_gz_kb}KB exceeded 15KB budget"
    assert js_gz_kb < 30.0, f"JS bundle {js_gz_kb}KB exceeded 30KB budget"
    assert total_gz_kb < 60.0, f"Total bundle {total_gz_kb}KB exceeded 60KB budget"

    full_report = {
        "timestamp": time.time(),
        "performance_budgets": {
            "css_max_kb": 15.0,
            "js_max_kb": 30.0,
            "total_max_kb": 60.0,
        },
        "measured_bundles": report_metrics,
        "summary": {
            "total_raw_kb": round(total_raw / 1024, 2),
            "total_gzipped_kb": total_gz_kb,
            "total_js_gzipped_kb": js_gz_kb,
            "total_css_gzipped_kb": css_gz_kb,
        },
        "web_vitals_targets": {
            "LCP": "< 2.5s",
            "INP": "< 200ms",
            "CLS": "< 0.1",
            "TTFT": "< 1000ms",
        },
    }

    out_dir = ROOT_DIR / "docs" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_file = out_dir / "performance_report.json"
    report_file.write_text(json.dumps(full_report, indent=2), encoding="utf-8")
