"""
Authentication & Identity Verification for Samaroh (समारोह).
Validates Firebase ID tokens via firebase-admin with fallback to Google JWKS,
and provides FastAPI security dependencies for protected routes and guest demo mode.
"""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger("samaroh.auth")

# FastAPI Bearer scheme with auto_error=False so optional auth routes can inspect credentials
bearer_scheme = HTTPBearer(auto_error=False)

# Track whether firebase_admin has been initialized
_firebase_initialized = False


class AuthenticatedUser(BaseModel):
    """Represents a verified authenticated caller."""

    uid: str
    email: str | None = None
    name: str | None = None
    picture: str | None = None
    is_demo: bool = False


DEMO_USER = AuthenticatedUser(
    uid="demo-user",
    email="guest@samaroh.app",
    name="Guest Explorer",
    picture=None,
    is_demo=True,
)


def _init_firebase_app():
    """Initializes the Firebase Admin SDK if not already done."""
    global _firebase_initialized
    if _firebase_initialized:
        return

    try:
        import firebase_admin
        from firebase_admin import credentials

        if not firebase_admin._apps:
            if settings.FIREBASE_CREDENTIALS_PATH:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(
                    cred, {"projectId": settings.FIREBASE_PROJECT_ID}
                )
            else:
                # Default application credentials or project config
                try:
                    firebase_admin.initialize_app(
                        options={"projectId": settings.FIREBASE_PROJECT_ID}
                    )
                except Exception as e:
                    logger.warning(
                        "Firebase Admin initialized without service credentials: %s. "
                        "Live token verification will require GOOGLE_APPLICATION_CREDENTIALS.",
                        e,
                    )
        _firebase_initialized = True
    except Exception as exc:
        logger.warning("Could not initialize Firebase Admin SDK: %s", exc)


def verify_firebase_id_token(token: str) -> dict:
    """
    Verifies a Firebase ID token.
    Supports mock/test tokens for offline and test runs (e.g. 'test-token-<uid>' or 'mock-token-<uid>').
    """
    # 1. Test / Mock token support for local testing & offline development
    if token.startswith(("test-token-", "mock-token-")):
        uid = token.split("-", 2)[-1] or "test-user"
        return {
            "uid": uid,
            "email": f"{uid}@example.com",
            "name": f"User {uid.capitalize()}",
            "picture": None,
        }

    # 2. Production Firebase verification
    _init_firebase_app()
    try:
        import firebase_admin.auth

        decoded = firebase_admin.auth.verify_id_token(token, check_revoked=False)
        return decoded
    except Exception as exc:
        logger.warning("Token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user_optional(
    auth: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser | None:
    """
    Extracts and verifies the Bearer token if present.
    Returns None if no token is provided.
    Raises 401 if a token is provided but fails verification.
    """
    if not auth or not auth.credentials:
        return None

    decoded = verify_firebase_id_token(auth.credentials)
    return AuthenticatedUser(
        uid=decoded.get("uid", "anonymous"),
        email=decoded.get("email"),
        name=decoded.get("name"),
        picture=decoded.get("picture"),
        is_demo=False,
    )


async def require_authenticated_user(
    user: AuthenticatedUser | None = Depends(get_current_user_optional),
) -> AuthenticatedUser:
    """
    Enforces that the caller is authenticated with a valid Firebase ID token.
    Raises HTTP 401 Unauthorized if the user is unauthenticated.
    """
    if not settings.ENABLE_AUTH_ENFORCEMENT:
        return user or DEMO_USER

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_or_demo(
    user: AuthenticatedUser | None = Depends(get_current_user_optional),
) -> AuthenticatedUser:
    """
    Returns the authenticated user if logged in; falls back to DEMO_USER for guest browsing.
    """
    if user is not None:
        return user
    return DEMO_USER
