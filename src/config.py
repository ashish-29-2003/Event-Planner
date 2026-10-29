"""
Configuration management for Samaroh (समारोह)
Loads environment variables securely with production fallbacks.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Find and load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    PROJECT_NAME: str = "Samaroh (समारोह) - GenAI Celebration & Event Planner"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    # Server network settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Google Gemini API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # Optional Google Maps Key
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # Firebase & Google Cloud Settings
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "samaroh-celebrations")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    ENABLE_AUTH_ENFORCEMENT: bool = os.getenv("ENABLE_AUTH_ENFORCEMENT", "True").lower() in (
        "true",
        "1",
        "yes",
    )
    ENABLE_APP_CHECK: bool = os.getenv("ENABLE_APP_CHECK", "False").lower() in (
        "true",
        "1",
        "yes",
    )

    # Security & Rate Limiting
    RATE_LIMIT_AI_REQUESTS: int = 20  # per 10 minutes
    RATE_LIMIT_WINDOW_SECONDS: int = 600


settings = Settings()
