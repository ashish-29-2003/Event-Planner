import urllib.request
import urllib.error
import json
import sys

base_url = "https://samaroh.onrender.com"
plans = ["demo-wedding-jaipur", "demo-birthday-blr", "demo-community-delhi"]

def probe(path, method="GET", data=None, token=None):
    url = base_url + path
    headers = {"User-Agent": "Probe/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req_data = None
    if data:
        headers["Content-Type"] = "application/json"
        req_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
                if isinstance(parsed, list):
                    summary = f"List count: {len(parsed)}"
                elif isinstance(parsed, dict):
                    if "title" in parsed:
                        summary = f"Title: {parsed['title'][:25]}"
                    elif "updated_items" in parsed:
                        summary = f"Updated items: {len(parsed['updated_items'])}"
                    elif "windows" in parsed:
                        summary = f"Windows: {len(parsed['windows'])}"
                    elif "status" in parsed:
                        summary = f"Status: {parsed['status']}"
                    else:
                        summary = f"Dict keys: {list(parsed.keys())[:4]}"
                else:
                    summary = str(body)[:35]
            except Exception:
                summary = body[:35]
            return resp.status, summary
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(err_body)
            summary = err_json.get("detail") or str(err_json)
        except Exception:
            summary = err_body[:40]
        return e.code, f"Error: {summary}"
    except Exception as e:
        return 0, f"Exception: {str(e)}"

print("| Plan ID | Endpoint | Mode (a) No Auth | Mode (b) Bearer test-token-x |")
print("|---|---|---|---|")

# 1. Health
s_a, b_a = probe("/api/health")
s_b, b_b = probe("/api/health", token="test-token-x")
print(f"| all | `/api/health` | HTTP {s_a}: {b_a} | HTTP {s_b}: {b_b} |")

# 2. Muhurat
s_a, b_a = probe("/api/ai/muhurat?culture=Marwari+Hindu&event_type=wedding")
s_b, b_b = probe("/api/ai/muhurat?culture=Marwari+Hindu&event_type=wedding", token="test-token-x")
print(f"| all | `/api/ai/muhurat` | HTTP {s_a}: {b_a} | HTTP {s_b}: {b_b} |")

# 3. Rebalance
reb_data = {
    "target_budget": 4000000,
    "changed_category": "Venue & Accommodation",
    "new_amount": 1500000,
    "current_items": []
}
s_a, b_a = probe("/api/ai/rebalance-budget", method="POST", data=reb_data)
s_b, b_b = probe("/api/ai/rebalance-budget", method="POST", data=reb_data, token="test-token-x")
print(f"| all | `/api/ai/rebalance-budget` | HTTP {s_a}: {b_a} | HTTP {s_b}: {b_b} |")

# 4. Next milestone export link
for pid in plans:
    s_a, b_a = probe(f"/api/export/{pid}/next-milestone-link")
    s_b, b_b = probe(f"/api/export/{pid}/next-milestone-link", token="test-token-x")
    print(f"| {pid} | `/api/export/{pid}/next-milestone-link` | HTTP {s_a}: {b_a} | HTTP {s_b}: {b_b} |")

# Sub-resources for each demo plan
endpoints = ["", "/budget", "/tasks", "/vendors", "/ideas", "/guests"]
for pid in plans:
    for ep in endpoints:
        p = f"/api/events/{pid}{ep}"
        s_a, b_a = probe(p)
        s_b, b_b = probe(p, token="test-token-x")
        print(f"| {pid} | `{p}` | HTTP {s_a}: {b_a} | HTTP {s_b}: {b_b} |")
