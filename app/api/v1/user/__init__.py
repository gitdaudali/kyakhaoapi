from fastapi import APIRouter, Depends

from app.utils.auth import get_current_user

from . import ai, auth, cuisines, dishes, featured, moods, reservations, restaurants, search

user_router = APIRouter()

# Authentication routes must remain public so that new users can register/login
user_router.include_router(auth.router)

protected_dependencies = [Depends(get_current_user)]

user_router.include_router(ai.router, dependencies=protected_dependencies)
user_router.include_router(cuisines.router, dependencies=protected_dependencies)
user_router.include_router(dishes.router, dependencies=protected_dependencies)
user_router.include_router(featured.router, dependencies=protected_dependencies)
user_router.include_router(moods.router, dependencies=protected_dependencies)
user_router.include_router(reservations.router, dependencies=protected_dependencies)
user_router.include_router(restaurants.router, dependencies=protected_dependencies)
user_router.include_router(search.router, dependencies=protected_dependencies)

