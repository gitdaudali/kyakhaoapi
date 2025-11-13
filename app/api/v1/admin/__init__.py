from fastapi import APIRouter, Depends

from app.utils.auth import get_current_admin

from . import cuisines, dishes, moods, restaurants

admin_router = APIRouter(dependencies=[Depends(get_current_admin)])

admin_router.include_router(cuisines.router)
admin_router.include_router(dishes.router)
admin_router.include_router(moods.router)
admin_router.include_router(restaurants.router)

