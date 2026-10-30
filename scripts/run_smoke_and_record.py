"""
Self-contained runner for Samaroh smoke tests.
Boots FastAPI on 127.0.0.1:8001, executes scripts/smoke_test.py, captures output, and tears down cleanly.
"""
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def run():
    port = 8001
    url = f"http://127.0.0.1:{port}"
    print(f"Starting Samaroh server on {url}...")
    
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to become responsive
    max_retries = 30
    ready = False
    for _ in range(max_retries):
        try:
            with urllib.request.urlopen(f"{url}/api/health", timeout=1.0) as res:
                if res.status == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(0.3)
            
    if not ready:
        print("ERROR: Server failed to start in time.")
        server_proc.terminate()
        return 1
        
    print("Server ready. Executing smoke test...")
    try:
        test_proc = subprocess.run(
            [sys.executable, "scripts/smoke_test.py", "--url", url],
            capture_output=True,
            text=True,
            check=False
        )
        output = test_proc.stdout + ("\n" + test_proc.stderr if test_proc.stderr else "")
        print(output)
        
        # Save report
        report_path = Path("docs/reports/smoke_test_local_report.txt")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding="utf-8")
        print(f"Saved report to {report_path}")
        return test_proc.returncode
    finally:
        print("Shutting down test server...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            server_proc.kill()

if __name__ == "__main__":
    sys.exit(run())
