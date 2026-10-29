"""
Security Headers & Content-Security-Policy (CSP) Matrix Tests for Samaroh (समारोह).
Verifies that all HTTP responses carry strict OWASP-recommended security headers
and that FastAPI and Netlify configuration remain synchronized as a single source of truth.
"""

from pathlib import Path

import tomllib
from fastapi.testclient import TestClient

from src.main import create_app

client = TestClient(create_app())


def test_api_health_carries_complete_security_headers():
    """Verify that every endpoint carries the complete security headers suite."""
    response = client.get("/api/health")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "max-age=31536000" in headers.get("Strict-Transport-Security", "")
    assert "camera=()" in headers.get("Permissions-Policy", "")
    assert headers.get("Cross-Origin-Opener-Policy") == "same-origin"

    csp = headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "script-src 'self'" in csp
    assert "https://cdn.jsdelivr.net" in csp
    assert "https://www.gstatic.com" in csp
    assert "connect-src 'self'" in csp


def test_static_index_carries_security_headers():
    """Verify that root / and HTML assets also carry the security headers."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert "Content-Security-Policy" in response.headers


def test_netlify_toml_synchronized_with_fastapi_headers():
    """Asserts that netlify.toml defines equivalent security headers for edge CDN routing."""
    netlify_path = Path("netlify.toml")
    assert netlify_path.exists()

    with open(netlify_path, "rb") as f:
        toml_data = tomllib.load(f)

    # Find headers block
    headers_blocks = toml_data.get("headers", [])
    assert len(headers_blocks) > 0

    values = headers_blocks[0].get("values", {})
    assert values.get("X-Frame-Options") == "DENY"
    assert values.get("X-Content-Type-Options") == "nosniff"
    assert values.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Strict-Transport-Security" in values
    assert "Permissions-Policy" in values
    assert "Cross-Origin-Opener-Policy" in values
    assert "Content-Security-Policy" in values
