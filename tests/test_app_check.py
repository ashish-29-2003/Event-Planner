"""
Unit & Integration Tests for Firebase App Check Verification.
Verifies token enforcement on mutating endpoints, mock bypass, and 401 rejections.
"""

from unittest.mock import patch

import pytest
from fastapi import HTTPException

from src.config import settings
from src.utils.app_check import verify_app_check_token


@pytest.mark.asyncio
async def test_app_check_bypassed_when_disabled(monkeypatch):
    """When ENABLE_APP_CHECK is False, requests proceed without App Check headers."""
    monkeypatch.setattr(settings, "ENABLE_APP_CHECK", False)
    result = await verify_app_check_token(None)
    assert result is True


@pytest.mark.asyncio
async def test_app_check_rejected_when_missing_header(monkeypatch):
    """When ENABLE_APP_CHECK is True, missing header must raise 401."""
    monkeypatch.setattr(settings, "ENABLE_APP_CHECK", True)
    with pytest.raises(HTTPException) as exc_info:
        await verify_app_check_token(None)
    assert exc_info.value.status_code == 401
    assert "App Check token missing" in exc_info.value.detail


@pytest.mark.asyncio
async def test_app_check_test_token_accepted(monkeypatch):
    """When ENABLE_APP_CHECK is True, test and mock tokens pass validation."""
    monkeypatch.setattr(settings, "ENABLE_APP_CHECK", True)
    assert await verify_app_check_token("test-appcheck-valid-token") is True
    assert await verify_app_check_token("mock-appcheck-device-attestation") is True


@pytest.mark.asyncio
async def test_app_check_invalid_token_rejected(monkeypatch):
    """When ENABLE_APP_CHECK is True, invalid tokens are rejected with 401."""
    monkeypatch.setattr(settings, "ENABLE_APP_CHECK", True)
    with patch(
        "firebase_admin.app_check.verify_token",
        side_effect=ValueError("Invalid App Check token signature"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await verify_app_check_token("invalid-unverified-payload-xyz")
        assert exc_info.value.status_code == 401
