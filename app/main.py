"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.adminui.router import router as admin_ui_router
from app.api.company import router as company_router
from app.api.company import searchRouter as search_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.exceptions import StatishubException
from app.core.logging import get_logger, setup_logging
from app.core.middleware import LoggingMiddleware, RequestIDMiddleware, setup_cors
from app.core.security_headers import SecurityHeadersMiddleware

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Statishub Company API",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    version="1.0.0",
    debug=settings.debug,
)

# Middleware order matters: first added = last executed
# Security headers should be applied to all responses
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
setup_cors(app)


@app.exception_handler(StatishubException)
async def statishub_exception_handler(request: Request, exc: StatishubException) -> JSONResponse:
    """Handle custom application exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Application error: {exc.message}",
        extra={"request_id": request_id, "status_code": exc.status_code},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "request_id": request_id},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(f"Unexpected error: {str(exc)}", extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "request_id": request_id},
    )


@app.on_event("startup")
async def startup_event() -> None:
    """Run startup tasks."""
    logger.info(f"Starting Statishub API in {settings.environment} mode")
    logger.info(f"Debug mode: {settings.debug}")


app.include_router(health_router)
app.include_router(admin_ui_router)
app.include_router(company_router)
app.include_router(search_router)
