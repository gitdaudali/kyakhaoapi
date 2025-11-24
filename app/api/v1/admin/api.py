"""Admin main router - aggregates all admin endpoints."""
from fastapi import APIRouter

from app.api.v1.admin.endpoints import faq

admin_router = APIRouter()

# Include all admin endpoint routers
admin_router.include_router(
    faq.router, prefix="/faqs", tags=["Admin FAQ Management"]
)

