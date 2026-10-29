"""
Netlify Functions ASGI Entrypoint for Samaroh (समारोह)
Wraps FastAPI application with Mangum for serverless execution.
"""

import sys
from pathlib import Path

# Add project root to sys.path so "src" is discoverable in serverless environment
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mangum import Mangum

from src.main import app

# Mangum adapts ASGI FastAPI app for Netlify (AWS Lambda) serverless environment
handler = Mangum(app, lifespan="off")
