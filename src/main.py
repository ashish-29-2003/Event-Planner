"""
FastAPI Application Entrypoint for Samaroh (समारोह).
GenAI Celebration & Event Planner.
"""

import json
import logging
import sys
import time
import uuid
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

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.ai_routes import router as ai_router
from src.api.event_routes import router as event_router
from src.api.export_routes import router as export_router
from src.api.places_routes import router as places_router
from src.config import SECURITY_HEADERS, settings

PUBLIC_DIR = ROOT_DIR / "public"

access_logger = logging.getLogger("samaroh.access")
access_logger.setLevel(logging.INFO)

STATUS_TO_CODE: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHENTICATED",
    403: "PERMISSION_DENIED",
    404: "NOT_FOUND",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
}


def create_app() -> FastAPI:
    app = FastAPI(
        title="Samaroh (समारोह) API",
        description="GenAI Celebration & Event Planner for Indian weddings, birthdays, and community festivals",
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # CORS configuration using centralized settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Body Size Limit Middleware (Max 1MB)
    max_body_bytes = 1024 * 1024

    @app.middleware("http")
    async def request_body_size_limit_middleware(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > max_body_bytes:
                    req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": {
                                "code": "PAYLOAD_TOO_LARGE",
                                "message": "Request payload exceeds maximum allowed size of 1 MB.",
                                "request_id": req_id,
                            },
                            "detail": "Request payload exceeds maximum allowed size of 1 MB.",
                        },
                        headers={"X-Request-ID": req_id, **SECURITY_HEADERS},
                    )
            except ValueError:
                pass
        return await call_next(request)

    # Standardized Exception Handlers
    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        code = STATUS_TO_CODE.get(exc.status_code, "ERROR")
        message = str(exc.detail) if isinstance(exc.detail, str) else "Request error."
        content = {
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
                "details": exc.detail,
            },
            "detail": exc.detail,
        }
        headers = dict(SECURITY_HEADERS)
        headers["X-Request-ID"] = request_id
        if exc.headers:
            headers.update(exc.headers)
        return JSONResponse(status_code=exc.status_code, content=content, headers=headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        content = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed.",
                "request_id": request_id,
                "details": exc.errors(),
            },
            "detail": exc.errors(),
        }
        headers = dict(SECURITY_HEADERS)
        headers["X-Request-ID"] = request_id
        return JSONResponse(status_code=422, content=content, headers=headers)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        content = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal server error occurred.",
                "request_id": request_id,
            },
            "detail": "An internal server error occurred.",
        }
        headers = dict(SECURITY_HEADERS)
        headers["X-Request-ID"] = request_id
        return JSONResponse(status_code=500, content=content, headers=headers)

    # Security Headers Middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        for header_name, header_value in SECURITY_HEADERS.items():
            response.headers[header_name] = header_value
        return response

    # Structured JSON Logging & Request ID Middleware
    @app.middleware("http")
    async def structured_json_logging_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        # Extract UID safely without recording raw token or credentials
        auth_header = request.headers.get("authorization")
        user_id = None
        if auth_header and "Bearer test-token-" in auth_header:
            user_id = auth_header.split("Bearer test-token-")[-1]

        log_entry = {
            "timestamp": time.time(),
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "client_ip": request.client.host if request.client else "unknown",
        }
        access_logger.info(json.dumps(log_entry))
        return response

    # Mount API routers
    app.include_router(ai_router)
    app.include_router(event_router)
    app.include_router(export_router)
    app.include_router(places_router)

    # Health check endpoint
    @app.get("/api/health")
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "project": "Samaroh (समारोह)",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "gemini_configured": bool(settings.GEMINI_API_KEY),
            "google_maps_configured": bool(settings.GOOGLE_MAPS_API_KEY),
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
