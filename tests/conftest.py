"""
Pytest configuration and shared test fixtures for Samaroh (समारोह).
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
def reset_storage_for_tests():
    """Ensure test isolation by clearing dynamically created celebrations."""
    from src.services.storage_service import storage_service

    def _clean(target):
        if hasattr(target, "_events"):
            target._events = {k: v for k, v in target._events.items() if k.startswith("demo-")}
        if hasattr(target, "_budgets"):
            target._budgets = {k: v for k, v in target._budgets.items() if k.startswith("demo-")}
        if hasattr(target, "_tasks"):
            target._tasks = {k: v for k, v in target._tasks.items() if k.startswith("demo-")}
        if hasattr(target, "_vendors"):
            target._vendors = {k: v for k, v in target._vendors.items() if k.startswith("demo-")}
        if hasattr(target, "_ideas"):
            target._ideas = {k: v for k, v in target._ideas.items() if k.startswith("demo-")}
        if hasattr(target, "_guests"):
            target._guests = {k: v for k, v in target._guests.items() if k.startswith("demo-")}

    _clean(storage_service)
    if hasattr(storage_service, "_fallback"):
        _clean(storage_service._fallback)
