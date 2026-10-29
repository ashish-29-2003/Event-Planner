"""
Smoke Test Verification Script for Samaroh (समारोह).
Validates health, authentication guards, security headers, places proxy, and event persistence
against any target deployment URL (local dev, Netlify Functions, or Cloud Run).

Usage:
    python scripts/smoke_test.py --url https://utsav-ai.netlify.app
    python scripts/smoke_test.py --url http://127.0.0.1:8000
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_check(name: str, check_fn) -> tuple[bool, str]:
    """Runs a check function and returns (passed, detail_message)."""
    try:
        passed, msg = check_fn()
        return passed, msg
    except Exception as exc:
        return False, f"Exception: {exc}"


def http_request(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    data: dict | None = None,
    timeout: float = 15.0,
) -> tuple[int, dict, dict]:
    """
    Executes an HTTP request using urllib.
    Returns (status_code, response_headers_dict, response_json_dict_or_raw).
    """
    req_headers = {"User-Agent": "Samaroh-SmokeTest/1.0"}
    if headers:
        req_headers.update(headers)

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.status
            resp_headers = dict(response.headers)
            raw = response.read().decode("utf-8")
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = {"raw": raw[:200]}
            return status, resp_headers, parsed
    except urllib.error.HTTPError as http_err:
        status = http_err.code
        resp_headers = dict(http_err.headers)
        raw = http_err.read().decode("utf-8")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"raw": raw[:200]}
        return status, resp_headers, parsed


def main():
    parser = argparse.ArgumentParser(description="Samaroh Live Deployment Smoke Tester")
    parser.add_argument(
        "--url",
        default=os.getenv("TARGET_URL", "http://127.0.0.1:8000"),
        help="Target base URL to probe (default: http://127.0.0.1:8000)",
    )
    args = parser.parse_args()
    base_url = args.url.rstrip("/")

    print("\n==================================================")
    print("SAMAROH (समारोह) LIVE SMOKE TEST")
    print(f"Target: {base_url}")
    print("==================================================\n")

    results = []

    # Check 1: Health check endpoint
    def check_health():
        status, _, body = http_request(f"{base_url}/api/health")
        if status == 200 and body.get("status") == "healthy":
            return True, f"Status 200, environment={body.get('environment')}"
        return False, f"Expected 200 healthy, got {status}: {body}"

    results.append(("1. Health Check (/api/health)", *run_check("health", check_health)))

    # Check 2: Demo celebration read
    def check_demo_read():
        status, _, body = http_request(f"{base_url}/api/events/demo-wedding-jaipur")
        if status == 200 and body.get("id") == "demo-wedding-jaipur":
            return True, f"Found '{body.get('title')}' in {body.get('city')}"
        return False, f"Expected 200 with demo event, got {status}: {body}"

    results.append(("2. Demo Celebration Read", *run_check("demo_read", check_demo_read)))

    # Check 3: Mutating route rejects unauthenticated request with 401
    def check_unauthenticated_reject():
        status, _, body = http_request(
            f"{base_url}/api/ai/plan",
            method="POST",
            data={"event_type": "wedding", "title": "Test Plan"},
        )
        if status == 401:
            return True, "Protected route returned 401 Unauthorized"
        return False, f"Expected 401 Unauthorized, got {status}: {body}"

    results.append(("3. Auth Guard (POST /api/ai/plan)", *run_check("auth_guard", check_unauthenticated_reject)))

    # Check 4: Security headers on root/index
    def check_security_headers():
        _status, headers, _ = http_request(f"{base_url}/")
        missing = []
        lower_headers = {k.lower(): v for k, v in headers.items()}
        if lower_headers.get("x-content-type-options") != "nosniff":
            missing.append("X-Content-Type-Options: nosniff")
        if lower_headers.get("x-frame-options") != "DENY":
            missing.append("X-Frame-Options: DENY")
        if not lower_headers.get("referrer-policy"):
            missing.append("Referrer-Policy")

        if not missing:
            return True, "All security headers present (nosniff, DENY, referrer-policy)"
        return False, f"Missing security headers: {', '.join(missing)}"

    results.append(("4. Security Headers (/)", *run_check("sec_headers", check_security_headers)))

    # Check 5: Places proxy endpoint
    def check_places():
        status, _, body = http_request(f"{base_url}/api/places/search?query=palace&city=Jaipur&category=venue")
        if status == 200 and body.get("success") is True and len(body.get("results", [])) > 0:
            return True, f"Returned {body.get('count')} candidates (source: {body.get('source')})"
        return False, f"Expected 200 with candidates, got {status}: {body}"

    results.append(("5. Places Discovery Proxy", *run_check("places", check_places)))

    # Check 6: Authenticated plan synthesis with mock/test token
    def check_authenticated_plan():
        headers = {
            "Authorization": "Bearer test-token-smoke-runner",
            "X-Firebase-AppCheck": "test-dev-bypass",
        }
        status, _, body = http_request(
            f"{base_url}/api/ai/plan",
            method="POST",
            headers=headers,
            data={
                "event_type": "birthday",
                "title": "Smoke Test Celebration",
                "city": "Bengaluru",
                "guest_count": 50,
                "target_budget": 200000.0,
                "culture": "Contemporary Indian",
            },
        )
        if status == 200 and body.get("success") is True:
            return True, f"Plan synthesized, event_id={body.get('event_id')} (fallback={body.get('is_fallback')})"
        return False, f"Expected 200 plan synthesis, got {status}: {body}"

    results.append(("6. Authenticated Plan Synthesis", *run_check("plan_synth", check_authenticated_plan)))

    # Summary report
    print(f"{'Check':<40} | {'Status':<8} | Detail")
    print("-" * 80)
    all_passed = True
    for name, passed, detail in results:
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"{name:<40} | {status_str:<8} | {detail}")

    print("\n" + "=" * 80)
    if all_passed:
        print("ALL SMOKE CHECKS PASSED SUCCESSFULLY (Exit Code 0)")
        sys.exit(0)
    else:
        print("ONE OR MORE SMOKE CHECKS FAILED (Exit Code 1)")
        sys.exit(1)


if __name__ == "__main__":
    main()
