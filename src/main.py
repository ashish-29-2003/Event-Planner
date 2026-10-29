"""
FastAPI Application Entrypoint for Samaroh (समारोह).
GenAI Celebration & Event Planner.
"""

import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is on sys.path if run directly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.ai_routes import router as ai_router
from src.api.event_routes import router as event_router
from src.api.export_routes import router as export_router
from src.config import settings

PUBLIC_DIR = ROOT_DIR / "public"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Samaroh (समारोह) API",
        description="GenAI Celebration & Event Planner for Indian weddings, birthdays, and community festivals",
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security Headers Middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Mount API routers
    app.include_router(ai_router)
    app.include_router(event_router)
    app.include_router(export_router)

    # Health check endpoint
    @app.get("/api/health")
    async def health_check():
        return {
            "status": "healthy",
            "project": "Samaroh (समारोह)",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "gemini_configured": bool(settings.GEMINI_API_KEY),
        }

    # Serve static assets if public directory exists
    if PUBLIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(PUBLIC_DIR)), name="static")

        @app.get("/")
        async def serve_index():
            index_path = PUBLIC_DIR / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return JSONResponse({"message": "Samaroh API operational. UI initializing..."})

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
