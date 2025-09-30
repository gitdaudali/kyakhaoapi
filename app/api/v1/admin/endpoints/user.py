from fastapi import APIRouter

from app.core.admin_deps import AdminUser

router = APIRouter()


@router.get("/")
async def get_users_admin(current_user: AdminUser):
    """Get users admin endpoint"""
    return {"message": "Users admin endpoint - Coming soon"}
