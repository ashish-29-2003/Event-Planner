"""
Google Maps Places HTTP Boundary Contract Test Suite for Samaroh (समारोह).
Uses respx to mock the Google Places API at the network boundary and verifies:
1. 200 OK with realistic candidate payload parses geometry, rating, and address correctly.
2. 400 Bad Request degrades gracefully to curated regional catalog.
3. 403 Invalid API key degrades gracefully to curated regional catalog.
4. 429 Over Quota / ResourceExhausted degrades gracefully to curated regional catalog.
5. Network / ConnectTimeout degrades gracefully to curated regional catalog.
6. GOOGLE_MAPS_API_KEY is NEVER exposed in the client response payload or candidate objects.
"""

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.services.places_service import PlacesService

client = TestClient(app)
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
SECRET_TEST_KEY = "AIzaSySecretContractTestKey_9876543210"


@pytest.mark.asyncio
@respx.mock
async def test_places_contract_200_realistic_response(monkeypatch):
    """
    Contract test: Google Places 200 OK returns structured PlaceCandidates
    with coordinates, ratings, and formatted addresses.
    """
    monkeypatch.setattr(settings, "GOOGLE_MAPS_API_KEY", SECRET_TEST_KEY)
    service = PlacesService(api_key=SECRET_TEST_KEY)

    mock_google_payload = {
        "status": "OK",
        "results": [
            {
                "place_id": "ChIJ_z1bOau_bTkR0qL9rJm1x1A",
                "name": "Rambagh Palace Heritage Resort",
                "formatted_address": "Bhawani Singh Road, Jaipur, Rajasthan 302005",
                "rating": 4.9,
                "user_ratings_total": 5420,
                "geometry": {
                    "location": {
                        "lat": 26.8979,
                        "lng": 75.8081,
                    }
                },
            }
        ],
    }

    respx.get(GOOGLE_PLACES_URL).respond(status_code=200, json=mock_google_payload)

    candidates, source = await service.search_places("Rambagh", "Jaipur", "venue")

    assert source == "google_places"
    assert len(candidates) == 1
    c = candidates[0]
    assert c.name == "Rambagh Palace Heritage Resort"
    assert c.rating == 4.9
    assert c.lat == 26.8979
    assert c.lng == 75.8081
    assert c.place_id == "ChIJ_z1bOau_bTkR0qL9rJm1x1A"

    # Verify secret API key is NOT in serialized PlaceCandidate
    dumped = c.model_dump()
    assert SECRET_TEST_KEY not in str(dumped)


@pytest.mark.asyncio
@respx.mock
async def test_places_contract_400_bad_request(monkeypatch):
    """Contract test: 400 Bad Request from Google Maps falls back cleanly to catalog."""
    monkeypatch.setattr(settings, "GOOGLE_MAPS_API_KEY", SECRET_TEST_KEY)
    service = PlacesService(api_key=SECRET_TEST_KEY)

    respx.get(GOOGLE_PLACES_URL).respond(
        status_code=400,
        json={"status": "INVALID_REQUEST", "error_message": "Invalid query parameters"},
    )

    candidates, source = await service.search_places("Corrupted??&&", "Jaipur", "venue")
    assert source == "curated_catalog"
    assert len(candidates) > 0
    assert SECRET_TEST_KEY not in str([c.model_dump() for c in candidates])


@pytest.mark.asyncio
@respx.mock
async def test_places_contract_403_invalid_key(monkeypatch):
    """Contract test: 403 Forbidden (bad API key) falls back cleanly to catalog."""
    monkeypatch.setattr(settings, "GOOGLE_MAPS_API_KEY", SECRET_TEST_KEY)
    service = PlacesService(api_key=SECRET_TEST_KEY)

    respx.get(GOOGLE_PLACES_URL).respond(
        status_code=403,
        json={"status": "REQUEST_DENIED", "error_message": "The provided API key is invalid"},
    )

    candidates, source = await service.search_places("Palace", "Jaipur", "venue")
    assert source == "curated_catalog"
    assert len(candidates) > 0


@pytest.mark.asyncio
@respx.mock
async def test_places_contract_429_quota_exhaustion(monkeypatch):
    """Contract test: 429 Over Quota falls back cleanly to catalog."""
    monkeypatch.setattr(settings, "GOOGLE_MAPS_API_KEY", SECRET_TEST_KEY)
    service = PlacesService(api_key=SECRET_TEST_KEY)

    respx.get(GOOGLE_PLACES_URL).respond(
        status_code=429,
        json={"status": "OVER_QUERY_LIMIT", "error_message": "You have exceeded your daily request quota for this API"},
    )

    candidates, source = await service.search_places("Palace", "Jaipur", "venue")
    assert source == "curated_catalog"
    assert len(candidates) > 0


@pytest.mark.asyncio
@respx.mock
async def test_places_contract_network_timeout(monkeypatch):
    """Contract test: Upstream timeout falls back cleanly without crashing."""
    monkeypatch.setattr(settings, "GOOGLE_MAPS_API_KEY", SECRET_TEST_KEY)
    service = PlacesService(api_key=SECRET_TEST_KEY)

    respx.get(GOOGLE_PLACES_URL).mock(side_effect=httpx.ConnectTimeout("Network unreachable"))

    candidates, source = await service.search_places("Palace", "Jaipur", "venue")
    assert source == "curated_catalog"
    assert len(candidates) > 0


def test_api_places_route_never_leaks_api_key_to_client(monkeypatch):
    """
    HTTP route integration assertion:
    Verifies that calling the public proxy endpoint /api/places/search
    never reveals the GOOGLE_MAPS_API_KEY in HTTP response headers or body.
    """
    monkeypatch.setattr(settings, "GOOGLE_MAPS_API_KEY", SECRET_TEST_KEY)

    resp = client.get("/api/places/search?query=palace&city=Jaipur&category=venue")
    assert resp.status_code == 200

    raw_response = resp.text
    assert SECRET_TEST_KEY not in raw_response, "Google Cloud API Key leaked in response body!"

    for header_name, header_val in resp.headers.items():
        assert SECRET_TEST_KEY not in header_name
        assert SECRET_TEST_KEY not in header_val
