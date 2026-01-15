"""
Interface para visualização de Swagger / OpenAPI
Somente UI (sem token, sem consumo da API)

Autor: Gustavo F. Lima
Licença: MIT
Created: 2026
"""

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse

# ==================================================
# CONFIGURAÇÃO
# ==================================================

OPENAPI_URL = "https://petstore.swagger.io/v2/swagger.json"
# Substitua depois pela sua:
# http://localhost:8080/v3/api-docs
# https://api.sistema.com/openapi.json

APP_TITLE = "Swagger Viewer"

# ==================================================
# APP
# ==================================================

app = FastAPI(
    title=APP_TITLE,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/", include_in_schema=False)
def swagger_ui() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=OPENAPI_URL,
        title=APP_TITLE,
    )


@app.get("/redoc", include_in_schema=False)
def redoc_ui() -> HTMLResponse:
    return get_redoc_html(
        openapi_url=OPENAPI_URL,
        title=f"{APP_TITLE} - ReDoc",
    )
