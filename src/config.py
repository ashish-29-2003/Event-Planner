"""
Configuration management for Samaroh (समारोह)
Loads environment variables securely with production fallbacks and fail-fast validation.
"""

import os
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv

# Find and load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    PROJECT_NAME: str = "Samaroh (समारोह) - GenAI Celebration & Event Planner"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    # Server network settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS configuration (list of allowed origins)
    CORS_ORIGINS: ClassVar[list[str]] = [
        x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()
    ]

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
    APP_CHECK_DEV_BYPASS: bool = os.getenv("APP_CHECK_DEV_BYPASS", "False").lower() in (
        "true",
        "1",
        "yes",
    )

    # Persistence Backend: 'firestore', 'local', or 'memory'
    STORAGE_BACKEND: str = os.getenv(
        "STORAGE_BACKEND",
        "firestore" if os.getenv("ENVIRONMENT", "development").lower() == "production" else "local",
    ).lower()

    # Security & Rate Limiting
    RATE_LIMIT_AI_REQUESTS: int = int(os.getenv("RATE_LIMIT_AI_REQUESTS", "25"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "600"))

    def validate_production_invariants(self) -> None:
        """
        Fails fast if production configuration violates strict security invariants.
        """
        if self.ENVIRONMENT == "production":
            if not self.ENABLE_APP_CHECK:
                raise RuntimeError(
                    "Security Invariant Violation: ENABLE_APP_CHECK must be True in production."
                )
            if self.APP_CHECK_DEV_BYPASS:
                raise RuntimeError(
                    "Security Invariant Violation: APP_CHECK_DEV_BYPASS must be False in production."
                )
            if self.STORAGE_BACKEND != "firestore":
                raise RuntimeError(
                    f"Security Invariant Violation: STORAGE_BACKEND must be 'firestore' in production, got '{self.STORAGE_BACKEND}'."
                )


settings = Settings()
settings.validate_production_invariants()
