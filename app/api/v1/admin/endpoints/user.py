from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_users_admin():
    """Get users admin endpoint"""
    return {"message": "Users admin endpoint - Coming soon"}
