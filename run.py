"""
Single-Command Launcher for Samaroh (समारोह).
Usage: python run.py
Starts Uvicorn ASGI server and opens the local application in your browser.
"""

import os
import sys
import webbrowser
from pathlib import Path

# Ensure UTF-8 output on Windows consoles to prevent charmap/UnicodeEncodeError
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn  # noqa: E402
from src.config import settings  # noqa: E402


def safe_print(message: str) -> None:
    """Print message safely across Windows terminals with non-UTF8 codepages."""
    try:
        print(message)
    except UnicodeEncodeError:
        try:
            print(message.encode("ascii", errors="replace").decode("ascii"))
        except Exception:
            pass


def main():
    safe_print("=" * 65)
    safe_print("॥ शुभ आरम्भ ॥")
    safe_print("Launching Samaroh (समारोह) - GenAI Celebration & Event Planner")
    safe_print(f"Server starting on http://{settings.HOST}:{settings.PORT}")
    safe_print(f"API Docs available at http://{settings.HOST}:{settings.PORT}/api/docs")
    safe_print("=" * 65)

    # Open browser automatically if running interactively
    if settings.DEBUG:
        try:
            webbrowser.open(f"http://{settings.HOST}:{settings.PORT}")
        except Exception:
            pass

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )


if __name__ == "__main__":
    main()
