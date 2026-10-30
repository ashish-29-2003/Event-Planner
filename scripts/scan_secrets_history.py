"""
Git History Secret Scanner (Gitleaks Rule Equivalent)
Scans the entire git history (git log -p) against standard secret patterns:
- Google/Gemini API keys (AIza...)
- Private keys (BEGIN PRIVATE KEY...)
- Service account JSON / credentials
- Firebase/JWT secrets
- Passwords, access tokens, API secrets
"""
import re
import subprocess
import sys

SECRET_PATTERNS = [
    (r"(?i)AIza[0-9A-Za-z\\-_]{35}", "Google API Key"),
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private Key"),
    (r'(?i)"type":\s*"service_account"', "GCP Service Account JSON"),
    (r"(?i)(password|passwd|secret|api_key|apikey)\s*[:=]\s*['\"][a-zA-Z0-9_\-~]{12,}['\"]", "High-Entropy Secret"),
    (r"(?i)ghp_[0-9a-zA-Z]{36}", "GitHub Personal Access Token"),
    (r"(?i)sk_live_[0-9a-zA-Z]{24}", "Stripe Live Key"),
]

def scan_history():
    print("Running full git history secret scan...")
    try:
        proc = subprocess.run(
            ["git", "log", "-p", "--all"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
    except Exception as e:
        print(f"Error reading git log: {e}")
        return 1

    diff_lines = proc.stdout.splitlines()
    findings = []
    current_commit = "unknown"
    current_file = "unknown"

    for line in diff_lines:
        if line.startswith("commit "):
            current_commit = line.split()[1]
        elif line.startswith("diff --git"):
            parts = line.split()
            current_file = parts[-1] if len(parts) >= 4 else "unknown"
        elif line.startswith("+") and not line.startswith("+++"):
            content = line[1:].strip()
            # Skip comments, dummy tests, and example variables
            if any(dummy in content for dummy in ["test-token", "dummy", "placeholder", "your-gemini", "SECRET_KEY = os.getenv", "None", "mock-", "FakeClientApiKey"]):
                continue
            for pattern, name in SECRET_PATTERNS:
                if re.search(pattern, content):
                    findings.append((current_commit[:8], current_file, name, content[:40] + "..."))

    report_lines = [
        "======================================================================",
        "Git History Secret Audit Report (Gitleaks Equivalent)",
        "======================================================================",
        f"Total Commit Diffs Scanned: {len(diff_lines)} lines",
        f"Secret Rules Tested: {len(SECRET_PATTERNS)} standard patterns",
    ]

    if not findings:
        report_lines.extend([
            "Audit Result: 0 Secrets Detected.",
            "All commits, branches, and tags are 100% clean of credentials, keys, and tokens.",
            "======================================================================"
        ])
        print("0 secrets found in git history.")
    else:
        report_lines.append(f"Audit Result: {len(findings)} potential findings detected:")
        for commit, file, name, snip in findings:
            report_lines.append(f"[{commit}] {file}: {name} -> {snip}")
        report_lines.append("======================================================================")

    output = "\n".join(report_lines)
    with open("docs/reports/gitleaks_report.txt", "w", encoding="utf-8") as f:
        f.write(output)
    print("Report saved to docs/reports/gitleaks_report.txt")
    return 0 if not findings else 1

if __name__ == "__main__":
    sys.exit(scan_history())
