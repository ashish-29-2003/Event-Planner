"""
Unit & Integration Tests for Google Maps Platform Places Proxy.
Verifies venue/vendor discovery, curated fallback behavior, and response schemas.
"""

import pytest
from httpx import ASGITransport, AsyncClient, Response

from src.main import app
from src.services.places_service import PlacesService


@pytest.mark.asyncio
async def test_places_search_curated_fallback():
    """When no Google Maps API key is configured, proxy returns verified curated candidates."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/places/search?query=palace+heritage&city=Jaipur&category=venue")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["source"] == "curated_catalog"
        assert data["count"] > 0
        assert any("Jaipur" in r["city"] for r in data["results"])
        assert any(r["rating"] is not None for r in data["results"])


@pytest.mark.asyncio
async def test_places_search_category_filter():
    """Verifies category filtering for catering."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/places/search?query=halwai&city=Jaipur&category=catering")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] > 0
        assert any("catering" in r["category"] for r in data["results"])


@pytest.mark.asyncio
async def test_places_search_with_mock_google_maps_api(monkeypatch):
    """When Google Maps API returns candidates, proxy parses and tags source as google_places."""
    service = PlacesService(api_key="mock-valid-google-maps-key")

    mock_response = {
        "status": "OK",
        "results": [
            {
                "place_id": "google-place-101",
                "name": "Rambagh Palace Heritage Lawns",
                "formatted_address": "Bhawani Singh Road, Jaipur, Rajasthan 302005",
                "rating": 4.9,
                "user_ratings_total": 5400,
                "geometry": {"location": {"lat": 26.8978, "lng": 75.8089}},
            }
        ],
    }

    async def mock_get(*args, **kwargs):
        return Response(200, json=mock_response)

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    results, source = await service.search_places("Rambagh", "Jaipur", "venue")
    assert source == "google_places"
    assert len(results) == 1
    assert results[0].place_id == "google-place-101"
    assert results[0].name == "Rambagh Palace Heritage Lawns"
    assert results[0].rating == 4.9
    assert results[0].lat == 26.8978
