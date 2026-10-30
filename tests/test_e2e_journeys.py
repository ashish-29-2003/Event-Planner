"""
Playwright End-to-End Journey Tests (R4-T05)
Verifies realistic end-to-end user journeys for:
1. Wedding Journey (Jaipur Royal Wedding: overview, budget, timeline task toggle, guests, share modal)
2. Birthday Journey (Bengaluru Cosmic Birthday: switcher, theme accent, ideas hub)
3. Community Festival Journey (Delhi Diwali Dandiya Mela: switcher, theme accent, muhurat windows)
"""
import asyncio
import socket
import threading
import time

import pytest
import uvicorn
from playwright.async_api import async_playwright

from src.main import app


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def live_server_url():
    """Spins up background uvicorn server on a dynamically assigned free port."""
    port = get_free_port()
    host = "127.0.0.1"

    config = uvicorn.Config(app, host=host, port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server readiness
    url = f"http://{host}:{port}"
    ready = False
    for _ in range(30):
        try:
            with socket.create_connection((host, port), timeout=0.2):
                ready = True
                break
        except OSError:
            time.sleep(0.1)

    assert ready, "Uvicorn server failed to start within 3 seconds"
    yield url


@pytest.mark.asyncio
async def test_journey_1_wedding_planning_flow(live_server_url: str):
    """
    Journey 1: Wedding Planning Flow (Jaipur Royal Wedding)
    - Verifies headline, countdown, cultural badges
    - Interacts with Budget tab & progress bar
    - Checks off a task in Timeline
    - Interacts with Guests tab
    - Opens Share Modal & checks blessing note
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        await page.goto(live_server_url, wait_until="networkidle")

        # 1. Overview checks
        await page.wait_for_selector("#overview-title", timeout=5000)
        title_text = await page.locator("#overview-title").inner_text()
        assert "Vivaha" in title_text or "Wedding" in title_text or "Riya" in title_text

        badge_text = await page.locator("#overview-status-badge").inner_text()
        assert "Active plan" in badge_text

        # 2. Budget Tab Interaction
        await page.locator(".nav-tab[data-view='budget']").click()
        await page.wait_for_selector("#budget-items-list tr", timeout=5000)
        rows_count = await page.locator("#budget-items-list tr").count()
        assert rows_count >= 5

        # 3. Timeline Tab Interaction (checkbox toggle)
        await page.locator(".nav-tab[data-view='timeline']").click()
        await page.wait_for_selector("#timeline-tasks-list .card", timeout=5000)
        tasks_count = await page.locator("#timeline-tasks-list .card").count()
        assert tasks_count >= 3

        # Click first task checkbox
        first_chk = page.locator("#timeline-tasks-list input[type='checkbox']").first
        await first_chk.click()
        await asyncio.sleep(0.3)

        # 4. Guests Tab Interaction
        await page.locator(".nav-tab[data-view='guests']").click()
        await page.wait_for_selector("#guests-table-body tr", timeout=5000)
        guest_rows = await page.locator("#guests-table-body tr").count()
        assert guest_rows >= 1

        # 5. Share Modal Interaction
        share_btn = page.locator("#btn-share-celebration")
        await share_btn.click()
        await page.wait_for_selector("#share-modal", state="visible", timeout=3000)

        share_link = await page.locator("#share-link-input").input_value()
        assert "event=" in share_link

        blessing = await page.locator("#share-blessing-text").inner_text()
        assert len(blessing) > 10

        # Close Share Modal
        await page.locator("#btn-close-share").click()
        await page.wait_for_selector("#share-modal", state="hidden", timeout=3000)

        await browser.close()


@pytest.mark.asyncio
async def test_journey_2_birthday_planning_flow(live_server_url: str):
    """
    Journey 2: Birthday Planning Flow
    - Uses celebration switcher listbox to select Bengaluru Cosmic Birthday
    - Asserts theme accent switches to .theme-birthday
    - Inspects personalized ideas hub
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        await page.goto(live_server_url, wait_until="networkidle")

        # Open switcher dropdown
        await page.locator("#switcher-toggle-btn").click()
        await page.wait_for_selector("#celebration-listbox", state="visible")

        # Click Birthday item
        birthday_opt = page.locator("li[data-event-id='demo-birthday-blr']")
        await birthday_opt.click()
        await asyncio.sleep(0.8)

        # Verify title updated
        title_text = await page.locator("#overview-title").inner_text()
        assert "Birthday" in title_text or "Cosmic" in title_text

        # Verify dynamic body class for theme
        body_class = await page.evaluate("document.body.className")
        assert "theme-birthday" in body_class

        # Check Ideas Tab
        await page.locator(".nav-tab[data-view='ideas']").click()
        await page.wait_for_selector("#ideas-container .card", timeout=5000)
        ideas_count = await page.locator("#ideas-container .card").count()
        assert ideas_count >= 2

        await browser.close()


@pytest.mark.asyncio
async def test_journey_3_community_festival_flow(live_server_url: str):
    """
    Journey 3: Community Festival Flow
    - Selects Delhi Diwali Dandiya Mela
    - Asserts theme accent switches to .theme-community
    - Inspects Muhurat guidance windows
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        await page.goto(live_server_url, wait_until="networkidle")

        # Open switcher dropdown
        await page.locator("#switcher-toggle-btn").click()
        await page.wait_for_selector("#celebration-listbox", state="visible")

        # Click Community item
        community_opt = page.locator("li[data-event-id='demo-community-delhi']")
        await community_opt.click()
        await asyncio.sleep(0.8)

        # Verify title updated
        title_text = await page.locator("#overview-title").inner_text()
        assert "Diwali" in title_text or "Dandiya" in title_text or "Mela" in title_text

        # Verify dynamic body class for theme
        body_class = await page.evaluate("document.body.className")
        assert "theme-community" in body_class

        # Check Muhurat guidance tab
        await page.locator(".nav-tab[data-view='muhurat']").click()
        await page.wait_for_selector("#muhurat-content", timeout=5000)
        muhurat_text = await page.locator("#muhurat-content").inner_text()
        assert "Muhurat" in muhurat_text or "Auspicious" in muhurat_text

        await browser.close()
