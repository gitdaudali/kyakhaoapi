from fastapi import APIRouter, Depends

from app.utils.auth import get_current_user

from . import auth, cuisines, dishes, faq, favorites, featured, moods, reservations, restaurants, reviews, search

user_router = APIRouter()

# Export auth_router for use in api.py
auth_router = auth.router

# ============================================================================
# PUBLIC ROUTES (No authentication required)
# ============================================================================
# FAQ routes are public so users can view published FAQs
user_router.include_router(faq.router, prefix="/faqs")

# ============================================================================
# PROTECTED ROUTES (Authentication required)
# ============================================================================
protected_dependencies = [Depends(get_current_user)]

user_router.include_router(cuisines.router, dependencies=protected_dependencies)
user_router.include_router(dishes.router, dependencies=protected_dependencies)
user_router.include_router(favorites.router, dependencies=protected_dependencies)
user_router.include_router(featured.router, dependencies=protected_dependencies)
user_router.include_router(moods.router, dependencies=protected_dependencies)
user_router.include_router(reservations.router, dependencies=protected_dependencies)
user_router.include_router(restaurants.router, dependencies=protected_dependencies)
user_router.include_router(reviews.router, dependencies=protected_dependencies)
user_router.include_router(search.router, dependencies=protected_dependencies)

