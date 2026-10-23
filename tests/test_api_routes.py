"""
Integration tests for FastAPI route handlers.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_list_events():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/events")
        assert res.status_code == 200
        events = res.json()
        assert len(events) >= 3  # Jaipur wedding, BLR birthday, Delhi mela
        event_ids = [e["id"] for e in events]
        assert "demo-wedding-jaipur" in event_ids


@pytest.mark.asyncio
async def test_get_event_budget():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/events/demo-wedding-jaipur/budget")
        assert res.status_code == 200
        items = res.json()
        assert len(items) > 0
        assert items[0]["estimated_cost"] > 0


@pytest.mark.asyncio
async def test_get_event_tasks():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/events/demo-wedding-jaipur/tasks")
        assert res.status_code == 200
        tasks = res.json()
        assert len(tasks) > 0


@pytest.mark.asyncio
async def test_muhurat_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/ai/muhurat?culture=Marwari&event_type=wedding")
        assert res.status_code == 200
        data = res.json()
        assert "windows" in data
        assert "disclaimer" in data
        assert "Notice: Muhurat windows" in data["disclaimer"]


@pytest.mark.asyncio
async def test_calendar_export_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/export/demo-wedding-jaipur/calendar")
        assert res.status_code == 200
        assert res.headers["content-type"] == "text/calendar; charset=utf-8"
        assert "BEGIN:VCALENDAR" in res.text
        assert "END:VCALENDAR" in res.text
