from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database import supabase

from app.api.company import router as company_router
from app.api.company import searchRouter as search_router
from app.api.admin import router as admin_router
from app.api.health import router as health_router

from app.adminui.router import router as admin_ui_router
from app.core.exceptions import StatishubException
from app.core.middleware import RequestIDMiddleware, LoggingMiddleware, setup_cors
from app.core.logging import setup_logging, get_logger
from app.core.config import settings

# Setup logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Statishub Company API",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1
    },
    version="1.0.0",
    debug=settings.debug
)

# Add middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
setup_cors(app)


# Global exception handler
@app.exception_handler(StatishubException)
async def statishub_exception_handler(request: Request, exc: StatishubException):
    """Handle custom application exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Application error: {exc.message}",
        extra={"request_id": request_id, "status_code": exc.status_code}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "request_id": request_id
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(
        f"Unexpected error: {str(exc)}",
        extra={"request_id": request_id}
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id
        }
    )


@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    logger.info(f"Starting Statishub API in {settings.environment} mode")
    logger.info(f"Debug mode: {settings.debug}")


app.include_router(health_router)
app.include_router(admin_ui_router)
app.include_router(company_router)
app.include_router(search_router)
# app.include_router(admin_router)

# @app.get("/docs", include_in_schema=False)
# def custom_swagger_ui():
#     return HTMLResponse("""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
#         <title>Statishub Company API - Swagger UI</title>
#     </head>
#     <body>
#     <div id="swagger-ui"></div>
#     <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
#     <script>
#     const ui = SwaggerUIBundle({
#         url: '/openapi.json',
#         dom_id: '#swagger-ui',
#         deepLinking: true,
#         presets: [
#             SwaggerUIBundle.presets.apis,
#             SwaggerUIBundle.SwaggerUIStandalonePreset
#         ],
#         requestInterceptor: (req) => {
#             req.headers['ngrok-skip-browser-warning'] = 'true';
#             return req;
#         }
#     })
#     </script>
#     </body>
#     </html>
#     """)



