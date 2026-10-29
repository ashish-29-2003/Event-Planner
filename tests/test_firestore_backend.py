"""
Unit & Integration Tests for Explicit STORAGE_BACKEND and Cloud Firestore Fail-Fast.
Verifies fail-fast on missing credentials in production, backend selection,
and Firestore collection hierarchy CRUD.
"""

from unittest.mock import MagicMock

import pytest

from src.config import settings
from src.models.event import CelebrationBrief, EventType
from src.services.gemini_service import gemini_service
from src.services.storage_service import (
    FirestoreStorageService,
    InMemoryStorageService,
    get_storage_service,
)


def test_production_fails_fast_without_firestore(monkeypatch):
    """Production environment MUST refuse to start if Cloud Firestore is unavailable."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "firestore")
    monkeypatch.setattr(settings, "FIREBASE_CREDENTIALS_PATH", "")

    # Mock _init_firebase_app and firestore.client to fail
    def mock_fail():
        raise ValueError("No GCP service account provided")

    monkeypatch.setattr("firebase_admin.firestore.client", mock_fail)

    with pytest.raises(RuntimeError) as exc_info:
        get_storage_service()

    assert "FATAL: Cloud Firestore persistence required" in str(exc_info.value)


def test_invalid_storage_backend_raises_value_error(monkeypatch):
    """Unsupported storage backend must be rejected."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "invalid_oracle_sql")

    with pytest.raises(ValueError) as exc_info:
        get_storage_service()

    assert "Invalid STORAGE_BACKEND" in str(exc_info.value)


def test_memory_storage_backend_selected(monkeypatch):
    """Selecting STORAGE_BACKEND=memory returns in-memory store with no persistence path."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "memory")

    store = get_storage_service()
    assert isinstance(store, InMemoryStorageService)
    assert store._persistence_path is None


def test_local_storage_backend_selected(monkeypatch):
    """Selecting STORAGE_BACKEND=local returns file-backed local store."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")

    store = get_storage_service()
    assert isinstance(store, InMemoryStorageService)
    assert store._persistence_path is not None


@pytest.mark.asyncio
async def test_firestore_crud_operations_with_client():
    """Verifies FirestoreStorageService CRUD operations using simulated Firestore client."""
    mock_client = MagicMock()
    mock_user_doc = MagicMock()
    mock_events_col = MagicMock()
    mock_event_doc = MagicMock()

    mock_client.collection.return_value.document.return_value = mock_user_doc
    mock_user_doc.collection.return_value = mock_events_col
    mock_events_col.document.return_value = mock_event_doc

    store = FirestoreStorageService(
        fallback_adapter=InMemoryStorageService(persistence_path=None),
        allow_fallback=True,
        firestore_client=mock_client,
    )

    brief = CelebrationBrief(
        title="Royal Marwari Sangeet",
        event_type=EventType.WEDDING,
        culture="Marwari",
        city="Udaipur",
        target_budget=2500000.0,
        guest_count=200,
    )
    plan, _ = await gemini_service.generate_master_plan(brief)
    event_id = store.create_event_from_plan(brief, plan, user_id="user-udaipur")

    assert event_id.startswith("event-")
    # Verify set was called on event document in Firestore
    mock_event_doc.set.assert_called()
    assert store.get_event("demo-wedding-jaipur") is not None
