"""
Supply Chain & Secret Scan Audit Tests for Samaroh (समारोह).
Verifies that:
1. Container image configuration enforces least-privilege non-root execution.
2. .dockerignore eliminates secret leakage risks during image building.
3. No active service-account private keys or high-entropy API secrets are committed in git.
"""

import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def test_dockerfile_enforces_non_root_execution():
    """Verify that Dockerfile explicitly creates and switches to a non-root user."""
    dockerfile_path = ROOT_DIR / "Dockerfile"
    assert dockerfile_path.exists()
    content = dockerfile_path.read_text(encoding="utf-8")

    assert "FROM python:3.13-slim AS builder" in content
    assert "FROM python:3.13-slim AS runner" in content
    assert "useradd" in content
    assert "USER samaroh" in content
    # Assert it doesn't switch back to root
    lines = [line.strip() for line in content.splitlines()]
    user_lines = [line for line in lines if line.startswith("USER ")]
    assert user_lines[-1] != "USER root"
    assert user_lines[-1] == "USER samaroh"


def test_dockerignore_prevents_secret_copy():
    """Verify that sensitive patterns are excluded from Docker build context."""
    dockerignore_path = ROOT_DIR / ".dockerignore"
    assert dockerignore_path.exists()
    content = dockerignore_path.read_text(encoding="utf-8")

    assert ".env" in content
    assert ".git" in content
    assert ".venv" in content
    assert "*.service-account.json" in content or "*.json" in content


def test_no_secrets_in_tracked_code():
    """Scan tracked Python and JS files for accidentally hardcoded API keys or private keys."""
    # Pattern for Google AI Studio / Gemini API key
    gemini_key_pattern = re.compile(r"AIza[0-9A-Za-z_-]{35}")
    # Pattern for private keys
    private_key_pattern = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")

    scanned_extensions = {".py", ".js", ".html", ".json", ".md", ".toml"}
    scanned_count = 0

    for path in ROOT_DIR.rglob("*"):
        if not path.is_file():
            continue
        # Skip git, cache, virtualenvs, and test fixtures
        if any(part in path.parts for part in (".git", ".venv", "node_modules", ".pytest_cache")):
            continue
        if path.suffix not in scanned_extensions:
            continue
        if "injection_corpus.json" in path.name:
            continue  # contains synthetic attack payloads

        content = path.read_text(encoding="utf-8", errors="ignore")
        scanned_count += 1

        assert not gemini_key_pattern.search(content), f"Found potential Gemini API key in {path}"
        assert not private_key_pattern.search(content), f"Found potential private key in {path}"

    assert scanned_count > 15, f"Expected to scan at least 15 files, scanned {scanned_count}"
