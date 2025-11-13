from fastapi import APIRouter

from app.api.v1.admin.api import admin_router
from app.api.v1.endpoints import auth, faq

api_router = APIRouter()

# User endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(faq.router, prefix="/faqs", tags=["FAQs"])

# Admin endpoints
api_router.include_router(admin_router, prefix="/admin")
