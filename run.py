"""
Single-Command Launcher for Utsav (उत्सव).
Usage: python run.py
Starts Uvicorn ASGI server and opens the local application in your browser.
"""
import sys
import webbrowser
import uvicorn
from src.config import settings

def main():
    print("=" * 65)
    print("॥ शुभ आरम्भ ॥")
    print("Launching Utsav (उत्सव) - GenAI Celebration & Event Planner")
    print(f"Server starting on http://{settings.HOST}:{settings.PORT}")
    print(f"API Docs available at http://{settings.HOST}:{settings.PORT}/api/docs")
    print("=" * 65)

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
        log_level="info"
    )

if __name__ == "__main__":
    main()
