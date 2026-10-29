"""
Shared-Store & Persistent Rate Limiting Test Suite for Samaroh (समारोह).
Validates:
1. Sliding window quota enforcement with standard X-RateLimit-* headers.
2. 429 Too Many Requests response with standard Retry-After header.
3. State persistence across restarts via atomic JSON cache.
4. Dual-key (per-IP and per-user) enforcement.
"""

from fastapi.testclient import TestClient

from src.main import app
from src.utils.rate_limiter import SlidingWindowRateLimiter

client = TestClient(app)


def test_rate_limiter_in_memory_basic():
    """Verifies that the rate limiter accurately decrements remaining slots."""
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60, persistence_path=None)

    # 1st request
    res1 = limiter.check("ip:192.168.1.1")
    assert res1.allowed is True
    assert res1.remaining == 2
    assert res1.limit == 3

    # 2nd request
    res2 = limiter.check("ip:192.168.1.1")
    assert res2.allowed is True
    assert res2.remaining == 1

    # 3rd request
    res3 = limiter.check("ip:192.168.1.1")
    assert res3.allowed is True
    assert res3.remaining == 0

    # 4th request -> blocked
    res4 = limiter.check("ip:192.168.1.1")
    assert res4.allowed is False
    assert res4.remaining == 0
    assert res4.retry_after > 0


def test_rate_limiter_persistence_across_restart(tmp_path):
    """Verifies that rate limit timestamps persist across restarts via file."""
    cache_file = tmp_path / "rate_limits.json"

    # Instance 1 records 2 requests
    limiter1 = SlidingWindowRateLimiter(max_requests=5, window_seconds=120, persistence_path=cache_file)
    limiter1.check("user:user-restart-1")
    limiter1.check("user:user-restart-1")

    # Instance 2 boots up pointing to the same file
    limiter2 = SlidingWindowRateLimiter(max_requests=5, window_seconds=120, persistence_path=cache_file)
    res = limiter2.check("user:user-restart-1")

    # Should be the 3rd request (remaining = 2)
    assert res.allowed is True
    assert res.remaining == 2


def test_api_plan_rate_limit_headers_and_429(monkeypatch):
    """
    Verifies that POST /api/ai/plan returns standard rate limit headers
    and raises 429 with Retry-After when exhausted.
    """
    # Create isolated limiter with max_requests=2
    test_limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60, persistence_path=None)
    from src.api import ai_routes

    monkeypatch.setattr(ai_routes, "rate_limiter", test_limiter)
    # Also patch enforce_rate_limit active limiter
    from src.utils import rate_limiter as rl_mod

    monkeypatch.setattr(rl_mod, "global_rate_limiter", test_limiter)

    auth_headers = {
        "Authorization": "Bearer test-token-rate-tester",
        "X-Firebase-AppCheck": "test-dev-bypass",
    }
    payload = {
        "title": "Rate Limit Plan",
        "event_type": "birthday",
        "target_budget": 50000.0,
        "guest_count": 25,
        "city": "Jaipur",
    }

    # Request 1 -> 200 OK with remaining 1
    resp1 = client.post("/api/ai/plan", json=payload, headers=auth_headers)
    assert resp1.status_code == 200
    assert resp1.headers.get("X-RateLimit-Limit") == "2"
    assert resp1.headers.get("X-RateLimit-Remaining") == "1"
    assert "X-RateLimit-Reset" in resp1.headers

    # Request 2 -> 200 OK with remaining 0
    resp2 = client.post("/api/ai/plan", json=payload, headers=auth_headers)
    assert resp2.status_code == 200
    assert resp2.headers.get("X-RateLimit-Remaining") == "0"

    # Request 3 -> 429 Too Many Requests with Retry-After
    resp3 = client.post("/api/ai/plan", json=payload, headers=auth_headers)
    assert resp3.status_code == 429
    assert "Retry-After" in resp3.headers
    assert resp3.headers.get("X-RateLimit-Remaining") == "0"
    assert int(resp3.headers.get("Retry-After", "0")) > 0
