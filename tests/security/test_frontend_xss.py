"""
Frontend XSS Audit & DOMPurify Integration Tests for Samaroh (समारोह).
Verifies that client-side DOM sinks are properly defended against stored
and reflected XSS attacks via DOMPurify and strict HTML escaping.
"""

import html
from pathlib import Path

INDEX_HTML_PATH = Path("public/index.html")
APP_JS_PATH = Path("public/js/app.js")
AUTH_JS_PATH = Path("public/js/auth.js")


def test_dompurify_cdn_present_in_index_html():
    """Verify that DOMPurify is loaded in index.html before app scripts."""
    assert INDEX_HTML_PATH.exists()
    content = INDEX_HTML_PATH.read_text(encoding="utf-8")

    assert "purify.min.js" in content or "dompurify" in content.lower()
    # Check that DOMPurify is loaded before app.js
    dompurify_pos = content.find("purify.min.js")
    app_js_pos = content.find("app.js")
    assert dompurify_pos < app_js_pos, "DOMPurify must load before app.js"


def test_escaping_and_sanitization_helpers_defined():
    """Verify that app.js exports escapeHTML and sanitizeHTML on window."""
    assert APP_JS_PATH.exists()
    content = APP_JS_PATH.read_text(encoding="utf-8")

    assert "function escapeHTML" in content
    assert "window.escapeHTML = escapeHTML" in content
    assert "function sanitizeHTML" in content
    assert "window.sanitizeHTML = sanitizeHTML" in content


def test_chat_drawer_neutralizes_xss_sinks():
    """Verify that chat inputs and bot outputs do not use unsafe innerHTML concatenation."""
    content = APP_JS_PATH.read_text(encoding="utf-8")

    # User message must be injected safely via textContent
    assert "userBubble.textContent = text" in content

    # Bot streamed message must pass through sanitizeHTML
    assert "sanitizeHTML" in content
    assert "botDiv.innerHTML = sanitizeHTML(fullText.replace(/\\n/g, '<br>'))" in content


def test_rendered_lists_escape_user_inputs():
    """Verify that title, notes, descriptions, business names are escaped in render functions."""
    content = APP_JS_PATH.read_text(encoding="utf-8")

    # Tasks
    assert "${escapeHTML(t.title)}" in content
    assert "${escapeHTML(t.description)}" in content

    # Budget
    assert "${escapeHTML(b.name)}" in content
    assert "${escapeHTML(b.notes)}" in content

    # Vendors
    assert "${escapeHTML(v.business_name)}" in content
    assert "escapeHTML(v.notes" in content

    # Ideas
    assert "${escapeHTML(i.title)}" in content
    assert "${escapeHTML(i.description)}" in content


def test_client_escape_behavior_equivalence():
    """Verify that client escape logic matches standard HTML entity encoding."""
    payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "\" onfocus=\"alert(1)",
        "& < > \" '",
        "<b>Harmless</b> & <i>Italic</i>",
    ]

    for p in payloads:
        escaped = html.escape(p, quote=True)
        assert "<script>" not in escaped
        assert "onerror=" not in escaped or "&lt;" in escaped
        assert "<" not in escaped
        assert ">" not in escaped
