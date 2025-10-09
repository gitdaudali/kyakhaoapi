from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
import random
from functools import wraps
import asyncio

# Local Imports
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine
from app.utils.retry_helper import retry_on_exception


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    print("✅ FastAPI application started")
    yield
    print("✅ FastAPI application shutdown")


# 🔹 Initialize Rate Limiter with global default
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)

# 🔹 Initialize FastAPI App
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
    lifespan=lifespan,
)

# 🔹 Register Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 🔹 Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Security
security = HTTPBearer()

# Include API routers
app.include_router(api_router, prefix="/api/v1")


# 🔹 Custom OpenAPI Documentation
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

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token as: Bearer <token>",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# 🔹 Function to wrap all endpoints with retry globally
def apply_global_retry(app: FastAPI, max_attempts=3, wait_initial=1):
    for route in app.routes:
        # Only wrap functions with endpoint handlers (ignore static files, etc.)
        if hasattr(route, "endpoint"):
            original_endpoint = route.endpoint
            wrapped_endpoint = retry_on_exception(max_attempts=max_attempts, wait_initial=wait_initial)(original_endpoint)
            route.endpoint = wrapped_endpoint


# Apply retry globally after all routes are added
apply_global_retry(app)


# ✅ Public routes
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "videos": "/api/v1/content",
        },
    }


@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api-info")
async def api_info(request: Request):
    """API metadata"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
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
        ],
    }


# 🔹 Demo endpoint to test unstable behavior
@app.get("/unstable")
async def unstable_endpoint():
    if random.random() < 0.7:  # 70% failure rate
        raise Exception("Random failure! Retry should trigger.")
    return {"status": "success"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
