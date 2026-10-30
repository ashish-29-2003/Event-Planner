"""
Gentle probe against live URL to measure real-world network edge latency.
"""
import statistics
import time
import urllib.request


def probe():
    url = "https://utsav-ai.netlify.app/"
    print(f"Sending 10 gentle probe requests to {url}...")
    latencies = []
    
    for i in range(10):
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Samaroh-Probe/1.0"})
            with urllib.request.urlopen(req, timeout=10.0) as res:
                code = res.status
                res.read()
        except Exception:
            code = 500
        dur_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(dur_ms)
        print(f"Request {i+1}: {code} ({dur_ms:.1f}ms)")
        time.sleep(0.2)
        
    p50 = statistics.median(latencies)
    mean = statistics.mean(latencies)
    print(f"Summary: p50={p50:.1f}ms, mean={mean:.1f}ms, min={min(latencies):.1f}ms, max={max(latencies):.1f}ms")

if __name__ == "__main__":
    probe()
