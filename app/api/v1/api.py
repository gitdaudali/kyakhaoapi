from fastapi import APIRouter

from app.api.v1.admin.api import router as admin_router
from app.api.v1.endpoints import auth, content, streaming, users, monetization

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(streaming.router, prefix="/streaming", tags=["streaming"])
api_router.include_router(monetization.router, prefix="/monetization", tags=["monetizaton"])


# Include admin router
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
