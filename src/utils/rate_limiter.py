"""
Shared-Store Sliding-Window Rate Limiter for FastAPI.
Provides per-IP and per-user rate limiting across restarts with
standardized X-RateLimit-* and Retry-After HTTP headers.
"""

import json
import logging
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

from fastapi import HTTPException, Request, Response, status

from src.config import settings
from src.utils.auth import AuthenticatedUser

logger = logging.getLogger("samaroh.rate_limiter")


class RateLimitResult(NamedTuple):
    allowed: bool
    limit: int
    remaining: int
    reset_epoch: int
    retry_after: int


class SlidingWindowRateLimiter:
    """
    Sliding-window rate limiter with optional atomic disk persistence.
    Operates consistently across server restarts and multiple workers.
    """

    def __init__(
        self,
        max_requests: int = 25,
        window_seconds: int = 600,
        persistence_path: Path | str | None = None,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.persistence_path = Path(persistence_path) if persistence_path else None
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Loads non-expired request timestamps from disk."""
        if not self.persistence_path or not self.persistence_path.exists():
            return
        try:
            with open(self.persistence_path, encoding="utf-8") as f:
                data = json.load(f)
            now = time.time()
            cutoff = now - self.window_seconds
            for key, timestamps in data.items():
                valid = [t for t in timestamps if t > cutoff]
                if valid:
                    self._requests[key] = valid
        except Exception as exc:
            logger.warning("Could not load rate limit cache from disk: %s", exc)

    def _save_to_disk(self) -> None:
        """Atomically persists active rate limit timestamps to disk."""
        if not self.persistence_path:
            return
        try:
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.persistence_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(dict(self._requests), f)
            temp_path.replace(self.persistence_path)
        except Exception as exc:
            logger.warning("Could not persist rate limit state: %s", exc)

    def check(self, key: str, increment: bool = True) -> RateLimitResult:
        """
        Evaluates the rate limit for a given key.
        Returns a RateLimitResult namedtuple with header values.
        """
        now = time.time()
        cutoff = now - self.window_seconds

        # Prune expired timestamps
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
        timestamps = self._requests[key]
        current_count = len(timestamps)

        oldest_ts = timestamps[0] if timestamps else now
        reset_epoch = int(oldest_ts + self.window_seconds)
        retry_after = max(1, int(reset_epoch - now))

        if current_count >= self.max_requests:
            return RateLimitResult(
                allowed=False,
                limit=self.max_requests,
                remaining=0,
                reset_epoch=reset_epoch,
                retry_after=retry_after,
            )

        if increment:
            self._requests[key].append(now)
            current_count += 1
            self._save_to_disk()

        remaining = max(0, self.max_requests - current_count)
        return RateLimitResult(
            allowed=True,
            limit=self.max_requests,
            remaining=remaining,
            reset_epoch=reset_epoch,
            retry_after=0,
        )

    def is_allowed(self, client_key: str) -> tuple[bool, int]:
        """Backward-compatibility shim for existing call sites."""
        res = self.check(client_key, increment=True)
        return res.allowed, res.remaining


# Global rate limiter instance configured from centralized settings
DEFAULT_LIMIT_PATH = (
    Path("data/rate_limits.json")
    if os.getenv("ENVIRONMENT", "development").lower() != "test"
    else None
)
global_rate_limiter = SlidingWindowRateLimiter(
    max_requests=settings.RATE_LIMIT_AI_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
    persistence_path=DEFAULT_LIMIT_PATH,
)


def enforce_rate_limit(
    request: Request,
    response: Response,
    user: AuthenticatedUser | None = None,
    limiter: SlidingWindowRateLimiter | None = None,
) -> None:
    """
    Enforces dual-key rate limiting (per-IP and per-user) and sets standardized headers:
    - X-RateLimit-Limit
    - X-RateLimit-Remaining
    - X-RateLimit-Reset
    - Retry-After (on 429)
    """
    active_limiter = limiter or global_rate_limiter
    client_ip = request.client.host if request.client else "127.0.0.1"

    # Evaluate per-IP
    ip_result = active_limiter.check(f"ip:{client_ip}", increment=True)

    # Evaluate per-user if authenticated
    user_result = None
    if user and not user.is_demo:
        user_result = active_limiter.check(f"user:{user.uid}", increment=True)

    # Find the more restrictive result
    limiting_result = ip_result
    if user_result and (not user_result.allowed or user_result.remaining < ip_result.remaining):
        limiting_result = user_result

    # Inject standard rate limit headers into response
    response.headers["X-RateLimit-Limit"] = str(limiting_result.limit)
    response.headers["X-RateLimit-Remaining"] = str(limiting_result.remaining)
    response.headers["X-RateLimit-Reset"] = str(limiting_result.reset_epoch)

    if not limiting_result.allowed:
        response.headers["Retry-After"] = str(limiting_result.retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit reached for AI plan generation. Please explore our instant demo celebrations.",
            headers={
                "Retry-After": str(limiting_result.retry_after),
                "X-RateLimit-Limit": str(limiting_result.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(limiting_result.reset_epoch),
            },
        )
