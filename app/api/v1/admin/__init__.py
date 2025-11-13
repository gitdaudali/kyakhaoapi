"""Admin API module."""
from fastapi import APIRouter, Depends

from app.utils.auth import get_current_admin

from . import cuisines, dishes, moods, restaurants
from .endpoints import faq

admin_router = APIRouter(dependencies=[Depends(get_current_admin)])

admin_router.include_router(cuisines.router)
admin_router.include_router(dishes.router)
admin_router.include_router(moods.router)
admin_router.include_router(restaurants.router)
admin_router.include_router(
    faq.router, prefix="/faqs", tags=["Admin FAQ Management"]
)

