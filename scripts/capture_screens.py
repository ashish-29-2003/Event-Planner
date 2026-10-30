"""
Playwright automated screen capture utility for Samaroh.
Captures light and dark mode screenshots across all 8 modules into docs/reports/ui-before/ (or ui-after/).
Usage: python scripts/capture_screens.py [output_dir]
"""

import asyncio
import sys
import threading
import time
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from playwright.async_api import async_playwright

from src.main import app

PORT = 8765
HOST = "127.0.0.1"


def run_server():
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


async def capture_all(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📸 Starting screen capture into {output_dir}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        url = f"http://{HOST}:{PORT}"
        print(f"Connecting to {url}...")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_selector("#overview-title", timeout=10000)
        await asyncio.sleep(1.0)  # Allow store hydration

        tabs = [
            ("overview", "Overview"),
            ("budget", "Budget"),
            ("timeline", "Timeline"),
            ("vendors", "Vendors"),
            ("ideas", "Ideas"),
            ("muhurat", "Muhurat"),
            ("chat", "Chat"),
            ("export", "Export"),
        ]

        for tab_id, _tab_label in tabs:
            # Click tab
            tab_btn = page.locator(f".nav-tab[data-view='{tab_id}']")
            if await tab_btn.count() > 0:
                await tab_btn.click()
                await asyncio.sleep(0.5)

            # Capture Light Theme
            await page.evaluate("document.documentElement.setAttribute('data-theme', 'light')")
            await asyncio.sleep(0.3)
            light_path = output_dir / f"{tab_id}-light.png"
            await page.screenshot(path=str(light_path), full_page=True)
            print(f"  ✓ Saved {light_path.name}")

            # Capture Dark Theme
            await page.evaluate("document.documentElement.setAttribute('data-theme', 'dark')")
            await asyncio.sleep(0.3)
            dark_path = output_dir / f"{tab_id}-dark.png"
            await page.screenshot(path=str(dark_path), full_page=True)
            print(f"  ✓ Saved {dark_path.name}")

        await browser.close()
        print("🎉 Screen capture complete!")


def main():
    target_folder = "ui-before"
    if len(sys.argv) > 1:
        target_folder = sys.argv[1]

    output_dir = ROOT_DIR / "docs" / "reports" / target_folder

    # Start background server
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1.5)

    asyncio.run(capture_all(output_dir))


if __name__ == "__main__":
    main()
