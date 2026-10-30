"""
Asynchronous Load Testing Benchmark for Samaroh (R4-T07)
Runs high-concurrency requests against FastAPI endpoints to measure:
- p50, p90, p95, and p99 latency percentiles
- Error rate (failures / total)
- Throughput (requests/sec)
Outputs JSON metrics to docs/reports/load_test_results.json
"""
import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

import httpx

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import threading

import uvicorn

from src.main import app

PORT = 8999
HOST = "127.0.0.1"
BASE_URL = f"http://{HOST}:{PORT}"
NUM_REQUESTS = 200
CONCURRENCY = 20


def start_server():
    uvicorn.run(app, host=HOST, port=PORT, log_level="error")


async def worker(queue: asyncio.Queue, results: list, client: httpx.AsyncClient):
    headers = {"Authorization": "Bearer test-token-user-loadtest", "Content-Type": "application/json"}
    while not queue.empty():
        method, path, payload = await queue.get()
        t0 = time.perf_counter()
        status_code = None
        success = False
        try:
            if method == "GET":
                resp = await client.get(f"{BASE_URL}{path}", headers=headers, timeout=10.0)
            elif method == "POST":
                resp = await client.post(f"{BASE_URL}{path}", json=payload, headers=headers, timeout=10.0)
            status_code = resp.status_code
            success = 200 <= status_code < 400
        except Exception:
            status_code = 500
            success = False

        duration_ms = (time.perf_counter() - t0) * 1000.0
        results.append({
            "path": path,
            "status": status_code,
            "duration_ms": duration_ms,
            "success": success
        })
        queue.task_done()


async def run_benchmark():
    endpoints = [
        ("GET", "/api/health", None),
        ("GET", "/api/events", None),
        ("GET", "/api/events/demo-wedding-jaipur", None),
        ("GET", "/api/events/demo-wedding-jaipur/budget", None),
        ("GET", "/api/events/demo-wedding-jaipur/tasks", None),
        ("GET", "/api/events/demo-wedding-jaipur/guests", None),
        ("GET", "/api/places/search?query=haveli&city=Jaipur", None),
        ("GET", "/api/export/demo-wedding-jaipur/calendar", None),
    ]

    queue = asyncio.Queue()
    for i in range(NUM_REQUESTS):
        ep = endpoints[i % len(endpoints)]
        await queue.put(ep)

    results = []
    print(f"🚀 Starting load benchmark: {NUM_REQUESTS} requests, concurrency={CONCURRENCY}...")
    t_start = time.perf_counter()

    limits = httpx.Limits(max_keepalive_connections=20, max_connections=CONCURRENCY)
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [asyncio.create_task(worker(queue, results, client)) for _ in range(CONCURRENCY)]
        await queue.join()
        for t in tasks:
            t.cancel()

    total_time = time.perf_counter() - t_start
    durations = sorted([r["duration_ms"] for r in results])
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    error_rate = (fail_count / len(results)) * 100.0

    p50 = statistics.median(durations)
    p90 = durations[int(len(durations) * 0.90)]
    p95 = durations[int(len(durations) * 0.95)]
    p99 = durations[int(len(durations) * 0.99)]
    rps = len(results) / total_time

    summary = {
        "timestamp": time.time(),
        "total_requests": len(results),
        "concurrency": CONCURRENCY,
        "total_duration_sec": round(total_time, 2),
        "requests_per_second": round(rps, 1),
        "successful_requests": success_count,
        "failed_requests": fail_count,
        "error_rate_pct": round(error_rate, 2),
        "latency_ms": {
            "min": round(durations[0], 2),
            "p50": round(p50, 2),
            "p90": round(p90, 2),
            "p95": round(p95, 2),
            "p99": round(p99, 2),
            "max": round(durations[-1], 2),
            "mean": round(statistics.mean(durations), 2),
        }
    }

    print("\n" + "="*50)
    print("📊 LOAD TEST BENCHMARK RESULTS")
    print("="*50)
    print(f"  Requests Total:   {summary['total_requests']}")
    print(f"  Throughput:       {summary['requests_per_second']} req/s")
    print(f"  Success Rate:     {100 - summary['error_rate_pct']:.1f}% ({success_count}/{len(results)})")
    print(f"  p50 Latency:      {summary['latency_ms']['p50']} ms")
    print(f"  p90 Latency:      {summary['latency_ms']['p90']} ms")
    print(f"  p95 Latency:      {summary['latency_ms']['p95']} ms")
    print(f"  p99 Latency:      {summary['latency_ms']['p99']} ms")
    print("="*50 + "\n")

    out_file = ROOT_DIR / "docs" / "reports" / "load_test_results.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved results to {out_file}")


def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1.5)
    asyncio.run(run_benchmark())


if __name__ == "__main__":
    main()
