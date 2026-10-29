"""
Firebase App Check Verification Middleware & Dependency for Samaroh (समारोह).
Protects GenAI synthesis and backend mutation routes against abuse, scraping,
and unauthorized clients by verifying cryptographically signed App Check tokens.
"""

import logging

from fastapi import Header, HTTPException, status

from src.config import settings

logger = logging.getLogger("samaroh.app_check")


async def verify_app_check_token(
    x_firebase_appcheck: str | None = Header(None, alias="X-Firebase-AppCheck"),
) -> bool:
    """
    Validates the Firebase App Check token.
    Bypassed in development/testing when ENABLE_APP_CHECK is False.
    Enforces cryptographically signed token when ENABLE_APP_CHECK is True.
    Dev bypass tokens fail closed in production.
    """
    if not settings.ENABLE_APP_CHECK:
        return True

    if not x_firebase_appcheck:
        logger.warning("App Check rejection: Missing X-Firebase-AppCheck header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="App Check token missing. Unauthorized client request.",
            headers={"WWW-Authenticate": "AppCheck"},
        )

    # In production, dev bypass tokens are strictly forbidden and fail closed
    is_mock = x_firebase_appcheck.startswith(("test-appcheck-", "mock-appcheck-", "test-dev-bypass"))
    if is_mock:
        if settings.ENVIRONMENT == "production":
            logger.error("Security alert: Attempted dev bypass token in production environment")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Dev bypass tokens rejected in production environment.",
                headers={"WWW-Authenticate": "AppCheck"},
            )
        return True

    try:
        from firebase_admin import app_check

        from src.utils.auth import _init_firebase_app

        _init_firebase_app()
        app_check.verify_token(x_firebase_appcheck)
        return True
    except Exception as exc:
        logger.warning("App Check token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase App Check token: {exc}",
            headers={"WWW-Authenticate": "AppCheck"},
        ) from exc
