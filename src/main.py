"""
FastAPI Application Entrypoint for Utsav (उत्सव).
GenAI Celebration & Event Planner.
"""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.api.ai_routes import router as ai_router
from src.api.event_routes import router as event_router
from src.api.export_routes import router as export_router

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

def create_app() -> FastAPI:
    app = FastAPI(
        title="Utsav (उत्सव) API",
        description="GenAI Celebration & Event Planner for Indian weddings, birthdays, and community festivals",
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
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
            "project": "Utsav (उत्सव)",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "gemini_configured": bool(settings.GEMINI_API_KEY)
        }

    # Serve static assets if public directory exists
    if PUBLIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(PUBLIC_DIR)), name="static")

        @app.get("/")
        async def serve_index():
            index_path = PUBLIC_DIR / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return JSONResponse({"message": "Utsav API operational. UI initializing..."})

    return app

app = create_app()
