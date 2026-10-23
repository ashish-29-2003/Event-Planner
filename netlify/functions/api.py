"""
Netlify Functions ASGI Entrypoint for Samaroh (समारोह)
Wraps FastAPI application with Mangum for serverless execution.
"""

from mangum import Mangum

from src.main import app

# Mangum adapts ASGI FastAPI app for Netlify (AWS Lambda) serverless environment
handler = Mangum(app, lifespan="off")
