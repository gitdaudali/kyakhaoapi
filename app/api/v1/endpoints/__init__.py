from fastapi import APIRouter, Depends

from app.utils.auth import get_current_user

from . import ai, auth, cart, cuisines, dishes, faq, featured, menu, moods, orders, reservations, restaurants, search

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

user_router.include_router(ai.router, dependencies=protected_dependencies)
user_router.include_router(cart.router, dependencies=protected_dependencies)
user_router.include_router(cuisines.router, dependencies=protected_dependencies)
user_router.include_router(dishes.router, dependencies=protected_dependencies)
user_router.include_router(featured.router, dependencies=protected_dependencies)
user_router.include_router(menu.router, dependencies=protected_dependencies)
user_router.include_router(moods.router, dependencies=protected_dependencies)
user_router.include_router(orders.router, dependencies=protected_dependencies)
user_router.include_router(reservations.router, dependencies=protected_dependencies)
user_router.include_router(restaurants.router, dependencies=protected_dependencies)
user_router.include_router(search.router, dependencies=protected_dependencies)

