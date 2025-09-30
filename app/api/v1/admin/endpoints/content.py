from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_content_admin():
    """Get content admin endpoint"""
    return {"message": "Content admin endpoint - Coming soon"}
