from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from sqlmodel import SQLModel

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.deps import validate_client_headers
from app.core.response_handler import (
    BaseAPIException,
    handle_exception,
    error_response
)


# Database tables are now managed by Alembic migrations
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("✅ FastAPI application started")
    yield
    # Shutdown
    print("✅ FastAPI application shutdown")


# Create FastAPI app with enhanced OpenAPI documentation
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    contact={
        "name": "Cup Streaming Team",
        "email": "support@cupstreaming.com",
        "url": "https://cupstreaming.com",
    },
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    servers=[{"url": f"{settings.BASE_URL}"}],
    tags_metadata=[
        {
            "name": "authentication",
            "description": (
                "User authentication operations. Register, login, and "
                "manage user sessions."
            ),
            "externalDocs": {
                "description": "JWT Authentication Guide",
                "url": "https://fastapi.tiangolo.com/tutorial/security/",
            },
        },
        {
            "name": "users",
            "description": (
                "User management operations. Create, read, update, and "
                "delete user accounts."
            ),
        },
        {
            "name": "Content",
            "description": ("Content Related Operations of Videos TV and serials."),
        },
    ],
    lifespan=lifespan,
)

# Add CORS middleware - Configure from settings
# Explicitly allow custom headers and ensure OPTIONS preflight works
# When allow_credentials=True, we must explicitly list headers (can't use "*")
cors_origins = settings.ALLOWED_ORIGINS
allow_creds = "*" not in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_creds,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Device-Id",
        "X-Device-Type",
        "X-App-Version",
        "Accept",
        "Origin",
        "X-Requested-With",
    ] if allow_creds else ["*"],  # Use wildcard only when credentials=False
    expose_headers=["*"],
    max_age=3600,  # Cache preflight for 1 hour
)

# Security
security = HTTPBearer()


app.include_router(api_router, prefix="/api/v1", dependencies=[Depends(validate_client_headers)])

# Global exception handlers
@app.exception_handler(BaseAPIException)
async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """Handle custom API exceptions."""
    return handle_exception(request, exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return handle_exception(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions with detailed error formatting."""
    field_errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        if field not in field_errors:
            field_errors[field] = []
        field_errors[field].append(error["msg"])
    
    return error_response(
        message="Request validation failed",
        status_code=422,
        data=field_errors
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return handle_exception(request, exc)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
    )

    # Add custom security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: Bearer <token>",
        },
        "ClientHeaders": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Device-Id",
            "description": "Client device identifier (required for all API requests)"
        },
        "DeviceTypeHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Device-Type",
            "description": "Client device type (ios, android, web, desktop) - required for all API requests"
        },
        "AppVersionHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-App-Version",
            "description": "Client app version (e.g., 1.0.0) - required for all API requests"
        }
    }

    # Add global security requirements
    openapi_schema["security"] = [
        {"ClientHeaders": []},
        {"DeviceTypeHeader": []},
        {"AppVersionHeader": []},
        {"BearerAuth": []}
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "endpoints": {
            "authentication": "/api/v1/auth",
            "users": "/api/v1/users",
            "videos": "/api/v1/content",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api-info")
async def api_info():
    """Get detailed API information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "framework": "FastAPI",
        "database": "PostgreSQL",
        "authentication": "JWT",
        "debug": settings.DEBUG,
        "features": [
            "User Authentication & Management",
            "Video Upload & Streaming",
            "Social Features (Likes, Views)",
            "Analytics & Metrics",
            "AWS S3 Integration",
        ]
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
