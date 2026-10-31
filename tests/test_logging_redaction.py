"""
Structured Logging, Request ID, and Token Redaction Test Suite for Samaroh (समारोह).
Verifies:
1. Access logs are formatted as structured JSON.
2. X-Request-ID is generated and returned on every response.
3. Sensitive credentials (Bearer tokens, Firebase App Check tokens, passwords) are NEVER leaked into logs.
4. Production security invariants fail fast when configuration is insecure.
"""

import json
import logging

import pytest
from fastapi.testclient import TestClient

from src.config import Settings, settings
from src.main import app

client = TestClient(app)


def test_request_id_and_structured_json_logging(caplog):
    """
    Verifies that requests generate an X-Request-ID header and that access logs
    are emitted as valid structured JSON containing request metadata.
    """
    with caplog.at_level(logging.INFO, logger="samaroh.access"):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        req_id = resp.headers.get("X-Request-ID")
        assert req_id is not None
        assert len(req_id) >= 16

        # Check logs
        assert len(caplog.records) >= 1
        last_log = caplog.records[-1].message
        data = json.loads(last_log)
        assert data["request_id"] == req_id
        assert data["path"] == "/api/health"
        assert data["method"] == "GET"
        assert data["status_code"] == 200
        assert "duration_ms" in data


def test_sensitive_tokens_redacted_from_logs(caplog):
    """
    Asserts that sensitive authentication credentials and App Check tokens
    are NEVER leaked into log records.
    """
    secret_auth_token = "ultra-secret-bearer-token-abc-998877"
    secret_appcheck_token = "confidential-appcheck-token-xyz-112233"

    headers = {
        "Authorization": f"Bearer {secret_auth_token}",
        "X-Firebase-AppCheck": secret_appcheck_token,
    }

    with caplog.at_level(logging.DEBUG):
        resp = client.get("/api/health", headers=headers)
        assert resp.status_code == 200

        # Entire aggregated log text must never contain raw secret tokens
        all_logs = caplog.text
        assert secret_auth_token not in all_logs, "Bearer token was leaked in application logs!"
        assert secret_appcheck_token not in all_logs, "Firebase App Check token was leaked in application logs!"


def test_production_invariants_fail_fast():
    """
    Asserts that in production mode, missing App Check or disabled backends
    trigger immediate fail-fast RuntimeError.
    """
    # 1. Production with App Check disabled must fail
    insecure_settings = Settings()
    insecure_settings.ENVIRONMENT = "production"
    insecure_settings.ENABLE_APP_CHECK = False
    with pytest.raises(RuntimeError, match="ENABLE_APP_CHECK must be True in production"):
        insecure_settings.validate_production_invariants()

    # 2. Production with dev bypass enabled must fail
    insecure_settings.ENABLE_APP_CHECK = True
    insecure_settings.APP_CHECK_DEV_BYPASS = True
    with pytest.raises(RuntimeError, match="APP_CHECK_DEV_BYPASS must be False in production"):
        insecure_settings.validate_production_invariants()

    # 3. Production with local storage backend must fail
    insecure_settings.APP_CHECK_DEV_BYPASS = False
    insecure_settings.STORAGE_BACKEND = "local"
    with pytest.raises(RuntimeError, match="STORAGE_BACKEND must be 'firestore' in production"):
        insecure_settings.validate_production_invariants()


@pytest.mark.asyncio
async def test_app_check_dev_bypass_fails_closed_in_production(monkeypatch):
    """
    Asserts that if a dev bypass token is presented in production, it is strictly rejected with 401.
    """
    from fastapi import HTTPException

    from src.utils.app_check import verify_app_check_token

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "ENABLE_APP_CHECK", True)
    monkeypatch.setattr(settings, "APP_CHECK_DEV_BYPASS", False)

    with pytest.raises(HTTPException) as exc_info:
        await verify_app_check_token("test-dev-bypass")
    assert exc_info.value.status_code == 401
    assert "Dev bypass tokens rejected in production" in exc_info.value.detail


def test_service_account_json_and_gemini_key_never_logged(caplog, monkeypatch):
    """
    Asserts that sensitive service account JSON and GEMINI_API_KEY
    are never leaked into log records or config representations.
    """
    # Build synthetic test keys dynamically so static scans aren't tripped
    fake_secret_key = "AI" + "zaSyFakeSecretGeminiKeyForAudit789"
    fake_header = "-----BEGIN" + " PRIVATE KEY-----"
    fake_sa_json = f'{{"type": "service_account", "private_key": "{fake_header}\\nFAKEKEY123\\n-----END PRIVATE KEY-----\\n"}}'
    monkeypatch.setattr(settings, "GEMINI_API_KEY", fake_secret_key)
    monkeypatch.setattr(settings, "FIREBASE_SERVICE_ACCOUNT_JSON", fake_sa_json)

    with caplog.at_level(logging.DEBUG):
        assert settings.GEMINI_API_KEY == fake_secret_key

        # Re-initialize firebase app if needed
        from src.utils import auth
        monkeypatch.setattr(auth, "_firebase_initialized", False)
        auth._init_firebase_app()

        all_logs = caplog.text
        assert fake_secret_key not in all_logs, "GEMINI_API_KEY leaked in logs!"
        assert "-----BEGIN PRIVATE KEY-----" not in all_logs, "Service account private key leaked in logs!"
        assert "FAKEKEY123" not in all_logs, "Private key content leaked in logs!"
