"""Main API router that aggregates all v1 routers."""
from fastapi import APIRouter

from .admin import admin_router
from .auth import auth_router
from .endpoints import user_router

# Create main API router
api_router = APIRouter()

# Include all routers
# Auth router already has prefix="/auth" in its definition
api_router.include_router(auth_router)
# User endpoints router - no prefix, endpoints are at root level
# Each endpoint has its own tag (FAQs, Cuisines, Dishes, etc.)
api_router.include_router(user_router)
# Admin router - add /admin prefix
api_router.include_router(admin_router, prefix="/admin")

__all__ = ["api_router"]

