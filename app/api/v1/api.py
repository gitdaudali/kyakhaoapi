from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    auth,
    cuisines,
    dishes,
    featured,
    moods,
    reservations,
    restaurants,
    search,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(cuisines.router)
api_router.include_router(moods.router)
api_router.include_router(restaurants.router)
api_router.include_router(dishes.router)
api_router.include_router(reservations.router)
api_router.include_router(ai.router)
api_router.include_router(search.router)
api_router.include_router(featured.router)
