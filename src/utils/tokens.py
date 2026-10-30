"""
High-entropy HMAC-signed URL and Export Tokens for Samaroh (समारोह).
Enables secure time-bound sharing of celebration summaries and calendar exports.
"""

import hashlib
import hmac
import time

from src.config import settings


def generate_share_token(event_id: str, ttl_seconds: int = 7 * 86400) -> str:
    """
    Generates a secure HMAC-SHA256 signed time-bound token for public celebration sharing.
    Format: <expires_at>.<hex_digest>
    """
    expires_at = int(time.time()) + ttl_seconds
    payload = f"{event_id}:{expires_at}"
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{expires_at}.{signature}"


def verify_share_token(event_id: str, token: str, current_time: float | None = None) -> bool:
    """
    Verifies that a share token was signed by SECRET_KEY for the given event_id
    and has not yet expired. Uses constant-time comparison to prevent timing attacks.
    """
    if not token or "." not in token:
        return False

    parts = token.split(".", 1)
    if len(parts) != 2:
        return False

    expires_at_str, signature = parts
    try:
        expires_at = int(expires_at_str)
    except ValueError:
        return False

    now = current_time if current_time is not None else time.time()
    if now > expires_at:
        return False

    payload = f"{event_id}:{expires_at}"
    expected_signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)
