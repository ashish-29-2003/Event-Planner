"""
In-memory Sliding-Window Rate Limiter for FastAPI endpoints.
Protects Google Gemini API quota and deters abusive request loops.
"""

import time
from collections import defaultdict


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int = 20, window_seconds: int = 600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_key: str) -> tuple[bool, int]:
        """
        Returns (is_allowed, remaining_requests).
        """
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean expired timestamps
        self.requests[client_key] = [t for t in self.requests[client_key] if t > cutoff]

        current_count = len(self.requests[client_key])
        if current_count >= self.max_requests:
            return False, 0

        self.requests[client_key].append(now)
        return True, self.max_requests - (current_count + 1)
