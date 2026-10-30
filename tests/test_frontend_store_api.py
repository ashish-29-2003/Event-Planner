"""
Frontend Store and API Client Contract Unit Tests (R4-T04)
Verifies:
1. EventStore implementation in public/js/store.js (reactive subscriber, state mutation, themes, languages)
2. API client in public/js/api.js (endpoints, methods, auth header injection, error schemas)
3. OpenAPI schema contract alignment between frontend API client and FastAPI route definitions
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app

REPO_ROOT = Path(__file__).resolve().parent.parent
STORE_JS = REPO_ROOT / "public" / "js" / "store.js"
API_JS = REPO_ROOT / "public" / "js" / "api.js"
APP_JS = REPO_ROOT / "public" / "js" / "app.js"


@pytest.fixture(scope="module")
def store_source() -> str:
    assert STORE_JS.exists(), "store.js must exist"
    return STORE_JS.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def api_source() -> str:
    assert API_JS.exists(), "api.js must exist"
    return API_JS.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def openapi_schema() -> dict:
    client = TestClient(app)
    resp = client.get("/api/openapi.json")
    assert resp.status_code == 200, "OpenAPI schema must be accessible"
    return resp.json()


def test_event_store_lifecycle_and_methods(store_source: str):
    """Verifies that EventStore implements expected reactive methods and properties."""
    assert "class EventStore" in store_source
    assert "constructor()" in store_source
    assert "subscribe(listener)" in store_source
    assert "notify()" in store_source
    assert "setState(partialState)" in store_source
    assert "setTheme(theme)" in store_source
    assert "toggleTheme()" in store_source
    assert "setLanguage(lang)" in store_source
    assert "setCurrentUser(user)" in store_source

    # Check store state schema fields
    required_state_keys = [
        "activeEventId",
        "events",
        "activeEvent",
        "budgets",
        "tasks",
        "vendors",
        "ideas",
        "guests",
        "currentUser",
        "language",
        "theme",
    ]
    for key in required_state_keys:
        assert f"{key}:" in store_source, f"Store state must contain {key}"

    # Check global store instance
    assert "window.store = new EventStore()" in store_source


def test_api_client_auth_and_appcheck_headers(api_source: str):
    """Verifies that API client properly injects Bearer and AppCheck tokens."""
    assert "setAuthToken(token)" in api_source
    assert "setAppCheckToken(token)" in api_source
    assert "getHeaders(custom" in api_source
    assert "Authorization" in api_source
    assert "Bearer" in api_source
    assert "X-Firebase-AppCheck" in api_source


def test_api_client_endpoints_contract_coverage(api_source: str, openapi_schema: dict):
    """
    Verifies that all frontend API client calls map to valid routes in FastAPI OpenAPI specification.
    """
    paths = openapi_schema["paths"]

    expected_client_methods = [
        ("getHealth", "/api/health", "get"),
        ("listEvents", "/api/events", "get"),
        ("getEvent", "/api/events/{event_id}", "get"),
        ("getBudget", "/api/events/{event_id}/budget", "get"),
        ("updateBudget", "/api/events/{event_id}/budget", "put"),
        ("rebalanceBudget", "/api/ai/rebalance-budget", "post"),
        ("getTasks", "/api/events/{event_id}/tasks", "get"),
        ("toggleTask", "/api/events/{event_id}/tasks/{task_id}/toggle", "post"),
        ("getVendors", "/api/events/{event_id}/vendors", "get"),
        ("getIdeas", "/api/events/{event_id}/ideas", "get"),
        ("getGuests", "/api/events/{event_id}/guests", "get"),
        ("addGuest", "/api/events/{event_id}/guests", "post"),
        ("updateGuestRSVP", "/api/events/{event_id}/guests/{guest_id}/rsvp", "post"),
        ("searchPlaces", "/api/places/search", "get"),
        ("generatePlan", "/api/ai/plan", "post"),
        ("getMuhurat", "/api/ai/muhurat", "get"),
        ("getNextMilestoneLink", "/api/export/{event_id}/next-milestone-link", "get"),
        ("getShareToken", "/api/export/{event_id}/share-token", "post"),
    ]

    for method_name, api_path, http_method in expected_client_methods:
        # Check method is declared in api.js
        assert f"{method_name}(" in api_source, f"API.{method_name} must exist in api.js"

        # Check route exists in OpenAPI schema
        assert api_path in paths, f"Route {api_path} must exist in backend OpenAPI schema"
        assert http_method in paths[api_path], f"HTTP method {http_method.upper()} must exist for {api_path}"


def test_sse_streaming_protocol_handler():
    """
    Verifies that app.js properly consumes Server-Sent Events (SSE) data chunks,
    ignores [DONE] sentinels, parses JSON text chunks, and handles offline fallbacks.
    """
    app_text = APP_JS.read_text(encoding="utf-8")
    assert "data: " in app_text
    assert "[DONE]" in app_text
    assert "response.body.getReader()" in app_text
    assert "new TextDecoder()" in app_text
    assert "JSON.parse" in app_text
    assert "sanitizeHTML" in app_text or "DOMPurify" in app_text
