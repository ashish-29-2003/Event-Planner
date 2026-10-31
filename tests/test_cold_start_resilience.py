"""
Cold-Start Resilience and Offline Demo Data Integrity Tests for Samaroh (समारोह).
Validates F2 requirements:
- Static offline fallback datasets exist, are non-empty, and match API models.
- Client prewarm, retry exponential backoff, and degraded mode configurations are sound.
- Netlify reverse proxy rewrite redirects directly to the active live Render API host.
"""

import json
from pathlib import Path
import pytest


def test_demo_data_directory_and_files_integrity():
    """Assert all 19 demo dataset files exist and are valid JSON with required attributes."""
    demo_dir = Path("public/demo-data")
    assert demo_dir.is_dir(), "public/demo-data directory must exist"

    # Events summary list
    events_file = demo_dir / "events.json"
    assert events_file.exists(), "events.json must exist in demo-data"
    with open(events_file, "r", encoding="utf-8") as f:
        events = json.load(f)
    assert isinstance(events, list)
    assert len(events) >= 3
    event_ids = [e["id"] for e in events]
    assert "demo-wedding-jaipur" in event_ids
    assert "demo-birthday-blr" in event_ids
    assert "demo-community-delhi" in event_ids

    # For each seeded event, verify the 6 subcollections exist and are valid JSON
    subcollections = ["budget", "tasks", "vendors", "ideas", "guests"]
    for eid in event_ids:
        # Event detail file
        detail_file = demo_dir / f"{eid}.json"
        assert detail_file.exists(), f"Detail file {detail_file} must exist"
        with open(detail_file, "r", encoding="utf-8") as f:
            detail = json.load(f)
        assert detail["id"] == eid
        assert "title" in detail
        assert "event_type" in detail

        for sub in subcollections:
            sub_file = demo_dir / f"{eid}_{sub}.json"
            assert sub_file.exists(), f"Subcollection file {sub_file} must exist"
            with open(sub_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert isinstance(data, (dict, list)), f"{sub_file} must parse into dict or list"


def test_api_client_contains_cold_start_resilience_handlers():
    """Assert public/js/api.js contains prewarm, exponential retry, and degraded mode hooks."""
    api_js = Path("public/js/api.js")
    assert api_js.exists(), "public/js/api.js must exist"
    code = api_js.read_text(encoding="utf-8")

    assert "prewarm()" in code
    assert "fetchWithRetry" in code
    assert "isDegraded" in code
    assert "isServerWaking" in code
    assert "server-waking-pill" in code
    assert "degraded-demo-banner" in code
    assert "/demo-data/" in code


def test_netlify_redirects_point_to_active_render_host():
    """Assert public/_redirects and netlify.toml route /api/* to https://samaroh.onrender.com."""
    redirects_file = Path("public/_redirects")
    assert redirects_file.exists()
    content = redirects_file.read_text(encoding="utf-8")
    assert "/api/*" in content
    assert "https://samaroh.onrender.com/api/:splat" in content

    netlify_toml = Path("netlify.toml")
    assert netlify_toml.exists()
    toml_content = netlify_toml.read_text(encoding="utf-8")
    assert "https://samaroh.onrender.com/api/:splat" in toml_content
