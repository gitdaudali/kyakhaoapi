from fastapi import APIRouter, Depends

from app.utils.auth import get_current_user

from . import allergies, auth, contact, cuisines, dishes, faq, favorites, featured, moods, notifications, personalization, promotions, reservations, restaurants, reviews, search, user_allergies, user_profile

user_router = APIRouter()

# Export auth_router for use in api.py
auth_router = auth.router

# ============================================================================
# PUBLIC ROUTES (No authentication required)
# ============================================================================
# FAQ routes are public so users can view published FAQs
user_router.include_router(faq.router, prefix="/faqs")
# Contact form is public so anyone can submit messages
user_router.include_router(contact.router, prefix="/contact")
# Promotions are public so users can view and apply promo codes
user_router.include_router(promotions.router, prefix="/promotions")
# Allergies - public endpoint to get list of allergies
user_router.include_router(allergies.router)

# ============================================================================
# PROTECTED ROUTES (Authentication required)
# ============================================================================
protected_dependencies = [Depends(get_current_user)]

user_router.include_router(cuisines.router, dependencies=protected_dependencies)
user_router.include_router(dishes.router, dependencies=protected_dependencies)
user_router.include_router(favorites.router, dependencies=protected_dependencies)
user_router.include_router(featured.router, dependencies=protected_dependencies)
user_router.include_router(moods.router, dependencies=protected_dependencies)
user_router.include_router(notifications.router, dependencies=protected_dependencies)
user_router.include_router(reservations.router, dependencies=protected_dependencies)
user_router.include_router(restaurants.router, dependencies=protected_dependencies)
user_router.include_router(reviews.router, dependencies=protected_dependencies)
user_router.include_router(search.router, dependencies=protected_dependencies)
user_router.include_router(user_allergies.router, dependencies=protected_dependencies)
user_router.include_router(personalization.router, dependencies=protected_dependencies)
user_router.include_router(user_profile.router, dependencies=protected_dependencies)

