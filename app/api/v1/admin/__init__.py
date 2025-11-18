"""Admin API module."""
from fastapi import APIRouter, Depends

from app.utils.auth import get_current_admin

from .endpoints import cuisines, dishes, faq, favorites, moods, restaurants, reviews

admin_router = APIRouter(dependencies=[Depends(get_current_admin)])

admin_router.include_router(cuisines.router)
admin_router.include_router(dishes.router)
admin_router.include_router(favorites.router)
admin_router.include_router(moods.router)
admin_router.include_router(restaurants.router)
admin_router.include_router(reviews.router)
admin_router.include_router(
    faq.router, prefix="/faqs"
)

