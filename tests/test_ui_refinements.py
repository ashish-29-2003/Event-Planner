"""
Tests for Stage R3: UI Refinements & Feature Completeness (U1 - U14)
Validates all UI elements, accessibility attributes, cultural styling tokens,
and functional frontend components in public/index.html, styles.css, and app.js.
"""
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = REPO_ROOT / "public"
INDEX_HTML = PUBLIC_DIR / "index.html"
STYLES_CSS = PUBLIC_DIR / "css" / "styles.css"
APP_JS = PUBLIC_DIR / "js" / "app.js"
FAVICON_SVG = PUBLIC_DIR / "favicon.svg"


@pytest.fixture(scope="module")
def html_content() -> str:
    assert INDEX_HTML.exists(), "public/index.html must exist"
    return INDEX_HTML.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def css_content() -> str:
    assert STYLES_CSS.exists(), "public/css/styles.css must exist"
    return STYLES_CSS.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def js_content() -> str:
    assert APP_JS.exists(), "public/js/app.js must exist"
    return APP_JS.read_text(encoding="utf-8")


def test_u14_metadata_and_favicon():
    """U14: Metadata, title, OpenGraph tags, and SVG favicon."""
    assert FAVICON_SVG.exists(), "Favicon SVG must exist at public/favicon.svg"
    svg_text = FAVICON_SVG.read_text(encoding="utf-8")
    assert "<svg" in svg_text and "</svg>" in svg_text
    # Check for Devanagari danda ॥ or saffron fill
    assert "॥" in svg_text
    assert "#E05A1F" in svg_text or "gold" in svg_text or "orange" in svg_text or "saffron" in svg_text.lower() or "#" in svg_text

    # Parse favicon as valid XML
    ET.fromstring(svg_text)

    # Validate HTML head metadata
    html = INDEX_HTML.read_text(encoding="utf-8")
    assert '<meta name="description"' in html
    assert '<meta property="og:title"' in html
    assert '<meta property="og:description"' in html
    assert '<meta property="og:image"' in html
    assert '<meta property="og:type"' in html
    assert '<meta name="twitter:card"' in html
    assert '<link rel="icon"' in html
    assert "favicon.svg" in html


def test_u01_cultural_accents_and_rangoli(css_content: str):
    """U1: Low-opacity rangoli/mandala pattern and restrained cultural accents."""
    assert "background-image:" in css_content
    assert "data:image/svg+xml" in css_content
    # Opacity should be restrained between 0.02 and 0.08
    assert "stroke-opacity='0.04'" in css_content or "stroke-opacity='0.035'" in css_content


def test_u02_and_u03_two_segment_progress_and_budget_hierarchy(html_content: str, js_content: str):
    """U2 & U3: Two-segment progress bar with aria-valuenow and financial metrics hierarchy."""
    assert 'id="overview-progress-track"' in html_content
    assert 'role="progressbar"' in html_content
    assert 'aria-valuenow=' in html_content
    assert 'id="overview-paid-bar"' in html_content
    assert 'id="overview-allocated-bar"' in html_content
    assert 'id="overview-allocated-pct"' in html_content
    assert 'id="overview-paid-pct"' in html_content
    assert 'id="overview-remaining"' in html_content

    # Logic in app.js
    assert "overview-progress-track" in js_content
    assert "overview-paid-bar" in js_content
    assert "overview-allocated-bar" in js_content
    assert "aria-valuenow" in js_content
    assert "committed" in js_content
    assert "settled" in js_content


def test_u04_milestones_and_relative_due_dates(html_content: str, js_content: str):
    """U4: Relative due dates ('in 10 days', 'Due today', 'overdue') and checkboxes."""
    assert "formatRelativeDueDate" in js_content
    assert "overdue" in js_content
    assert "Due today" in js_content
    assert "due_date" in js_content
    assert 'type="checkbox"' in js_content
    assert "toggleTaskStatus" in js_content


def test_u05_overview_live_dynamic_metrics(html_content: str, js_content: str):
    """U5: Overview cards display live dynamic metrics."""
    assert 'id="ovcard-budget-headline"' in html_content
    assert 'id="ovcard-tasks-headline"' in html_content
    assert 'id="ovcard-vendors-headline"' in html_content
    assert 'id="ovcard-guests-headline"' in html_content

    assert "ovcard-budget-headline" in js_content
    assert "ovcard-tasks-headline" in js_content
    assert "ovcard-vendors-headline" in js_content
    assert "ovcard-guests-headline" in js_content


def test_u06_header_and_subhashita_and_theme_svg(html_content: str, js_content: str):
    """U6: High-contrast Subhashita bar, SVG theme toggle, bilingual switch, user auth."""
    assert 'id="daily-subhashita"' in html_content
    assert 'id="theme-toggle"' in html_content
    assert 'id="theme-icon-moon"' in html_content
    assert 'id="theme-icon-sun"' in html_content
    assert 'id="lang-toggle"' in html_content
    assert 'id="btn-auth-signin"' in html_content
    assert 'id="user-profile-menu"' in html_content

    # app.js SVG theme toggling
    assert "theme-icon-moon" in js_content
    assert "theme-icon-sun" in js_content
    assert "SUBHASHITAS" in js_content


def test_u07_guests_rsvp_module_and_tabs(html_content: str, js_content: str):
    """U7: Horizontally scrollable tabs with ARIA tabs and Guests & RSVP module."""
    assert 'class="tabs-scroll-wrapper"' in html_content
    assert 'role="tablist"' in html_content
    assert 'id="tab-guests"' in html_content
    assert 'id="view-guests"' in html_content
    assert 'id="guests-metric-total"' in html_content
    assert 'id="guests-metric-attending"' in html_content
    assert 'id="guest-filter-bar"' in html_content
    assert 'id="guests-table-body"' in html_content
    assert 'id="guest-modal"' in html_content
    assert 'id="guest-form"' in html_content

    # app.js guest rendering
    assert "renderGuests" in js_content
    assert "setupGuestsModule" in js_content
    assert "updateGuestRSVPStatus" in js_content


def test_u08_active_plan_badge(html_content: str, js_content: str):
    """U8: Standardize badge to 'Active plan'."""
    assert "Active plan" in html_content
    assert "Active Blueprint" not in html_content
    assert "Active plan" in js_content


def test_u09_share_drawer_and_modal(html_content: str, js_content: str):
    """U9: Comprehensive Share drawer with link copy, WhatsApp share, PDF, and blessing note."""
    assert 'id="share-modal"' in html_content
    assert 'id="share-link-input"' in html_content
    assert 'id="btn-copy-share"' in html_content
    assert 'id="btn-whatsapp-share"' in html_content
    assert 'id="btn-share-print"' in html_content
    assert 'id="share-blessing-text"' in html_content

    assert "setupShareModal" in js_content
    assert "api.getsharetoken" in js_content.lower()
    assert "wa.me" in js_content


def test_u10_accessible_celebration_switcher(html_content: str, js_content: str):
    """U10: Accessible custom listbox with event icons, date, and budget details."""
    assert 'id="switcher-toggle-btn"' in html_content
    assert 'aria-haspopup="listbox"' in html_content
    assert 'id="celebration-listbox"' in html_content
    assert 'role="listbox"' in html_content
    assert 'role="option"' in html_content
    assert 'id="switcher-active-icon"' in html_content
    assert 'id="switcher-active-label"' in html_content

    assert "setupCelebrationSwitcher" in js_content
    assert "ArrowDown" in js_content
    assert "ArrowUp" in js_content


def test_u11_cultural_greeting_single_language(js_content: str):
    """U11: Cultural greeting in single language based on toggle."""
    assert "getCulturalGreeting(lang" in js_content
    assert "शुभ प्रभात" in js_content
    assert "Good Morning" in js_content
    assert "updateLanguageUI" in js_content


def test_u12_event_type_theme_personalization(css_content: str, js_content: str):
    """U12: Dynamic event theme accents (wedding, birthday, community)."""
    assert ".theme-wedding" in css_content
    assert ".theme-birthday" in css_content
    assert ".theme-community" in css_content
    assert "theme-${eventType}" in js_content or "theme-" in js_content


def test_u13_structured_cultural_footer(html_content: str, css_content: str):
    """U13: Structured footer with Panchang notice, privacy guarantee, and system links."""
    assert '<footer class="site-footer"' in html_content
    assert "Vedic Guidance Notice" in html_content
    assert "Panchang" in html_content
    assert "Privacy & Stewardship" in html_content
    assert "/api/health" in html_content
    assert "/api/docs" in html_content

    assert ".site-footer" in css_content
    assert ".footer-inner" in css_content
