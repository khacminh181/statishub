from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal, supabase

from app.api.company import router as company_router
from app.api.company import searchRouter as search_router
from app.api.admin import router as admnin_router
from fastapi.responses import HTMLResponse

from app.adminui.router import router as admin_ui_router


app = FastAPI(
    title="Statishub Company API",
    version="1.0.0"
)

app.include_router(admin_ui_router)

app.include_router(company_router)
app.include_router(search_router)
# app.include_router(admnin_router)

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



