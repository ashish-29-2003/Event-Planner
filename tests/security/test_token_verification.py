"""
Strict Token Verification Tests for Samaroh (समारोह).
Validates Firebase ID token claims: audience, issuer, subject, expiration,
issued-at, and clock skew tolerance, as well as rejection of mock tokens in production.
"""

import time

import pytest
from fastapi import HTTPException

from src.config import settings
from src.utils.auth import (
    validate_firebase_token_claims,
    verify_firebase_id_token,
)


def test_valid_token_claims_pass():
    """Verify that a token with correct audience, issuer, sub, and unexpired exp passes."""
    now = time.time()
    claims = {
        "sub": "user-riya-123",
        "aud": settings.FIREBASE_PROJECT_ID,
        "iss": f"https://securetoken.google.com/{settings.FIREBASE_PROJECT_ID}",
        "exp": now + 3600,
        "iat": now - 60,
        "email": "riya@example.com",
    }
    validated = validate_firebase_token_claims(claims, current_time=now)
    assert validated["uid"] == "user-riya-123"
    assert validated["email"] == "riya@example.com"


def test_mismatched_audience_rejected():
    """Verify that tokens from another Firebase project (audience mismatch) are rejected."""
    now = time.time()
    claims = {
        "sub": "attacker-uid",
        "aud": "malicious-firebase-project",
        "iss": f"https://securetoken.google.com/{settings.FIREBASE_PROJECT_ID}",
        "exp": now + 3600,
    }
    with pytest.raises(HTTPException) as exc_info:
        validate_firebase_token_claims(claims, current_time=now)
    assert exc_info.value.status_code == 401
    assert "audience" in exc_info.value.detail


def test_mismatched_issuer_rejected():
    """Verify that tokens signed by untrusted issuers are rejected."""
    now = time.time()
    claims = {
        "sub": "attacker-uid",
        "aud": settings.FIREBASE_PROJECT_ID,
        "iss": "https://accounts.google.com",  # Not securetoken.google.com/<project_id>
        "exp": now + 3600,
    }
    with pytest.raises(HTTPException) as exc_info:
        validate_firebase_token_claims(claims, current_time=now)
    assert exc_info.value.status_code == 401
    assert "issuer" in exc_info.value.detail


def test_missing_or_empty_subject_rejected():
    """Verify that tokens without subject / UID are rejected."""
    now = time.time()
    claims = {
        "sub": "",
        "aud": settings.FIREBASE_PROJECT_ID,
        "iss": f"https://securetoken.google.com/{settings.FIREBASE_PROJECT_ID}",
        "exp": now + 3600,
    }
    with pytest.raises(HTTPException) as exc_info:
        validate_firebase_token_claims(claims, current_time=now)
    assert exc_info.value.status_code == 401
    assert "subject" in exc_info.value.detail


def test_expired_token_rejected_beyond_clock_skew():
    """Verify that expired tokens exceeding the clock skew tolerance are rejected."""
    now = time.time()
    # Expired 30 seconds ago, clock skew is 10 seconds
    claims = {
        "sub": "expired-user",
        "aud": settings.FIREBASE_PROJECT_ID,
        "iss": f"https://securetoken.google.com/{settings.FIREBASE_PROJECT_ID}",
        "exp": now - 30,
    }
    with pytest.raises(HTTPException) as exc_info:
        validate_firebase_token_claims(claims, clock_skew_seconds=10, current_time=now)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail


def test_clock_skew_tolerance_accepts_slight_drift():
    """Verify that small clock drift (e.g. within 10s skew) is tolerated."""
    now = time.time()
    # Expired 5 seconds ago, skew tolerance is 10 seconds -> passes
    claims = {
        "sub": "skew-user",
        "aud": settings.FIREBASE_PROJECT_ID,
        "iss": f"https://securetoken.google.com/{settings.FIREBASE_PROJECT_ID}",
        "exp": now - 5,
    }
    validated = validate_firebase_token_claims(claims, clock_skew_seconds=10, current_time=now)
    assert validated["uid"] == "skew-user"


def test_mock_tokens_rejected_in_production(monkeypatch):
    """Verify that test/mock tokens are rejected when ENVIRONMENT is production."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    with pytest.raises(HTTPException) as exc_info:
        verify_firebase_id_token("test-token-alice")
    assert exc_info.value.status_code == 401
    assert "rejected in production" in exc_info.value.detail
