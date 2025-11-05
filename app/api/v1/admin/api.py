from fastapi import APIRouter

from app.api.v1.admin.endpoints import (
    analytics,
    announcement,
    content,
    genre,
    monetization,
    moviesource,
    people,
    popup,
    streaming,
    task,
    upload,
    user,
    policy,
    faq,
)

# Create main admin router
router = APIRouter()

# Include all admin sub-routers
router.include_router(
    streaming.router,
    prefix="/streaming-channels",
    tags=["Admin - Streaming Channels"],
)

router.include_router(
    genre.router,
    prefix="/genres",
    tags=["Admin - Genres"],
)

router.include_router(
    content.router,
    prefix="/content",
    tags=["Admin - Content"],
)

router.include_router(
    people.router,
    prefix="/people",
    tags=["Admin - People"],
)

router.include_router(
    user.router,
    prefix="/users",
    tags=["Admin - Users"],
)

router.include_router(
    upload.router,
    prefix="/upload",
    tags=["Admin - File Upload"],
)

router.include_router(
    monetization.router,
    prefix="/monetization",
    tags=["Admin - Monetization"],
)

router.include_router(
    policy.router,
    prefix="/policies",
    tags=["Admin - Policies"],
)

router.include_router(
    faq.router,
    prefix="/faq",
    tags=["Admin - FAQ"],
)

router.include_router(
    announcement.router,
    prefix="/announcements",
    tags=["Admin - Announcements"],
)

router.include_router(
    task.router,
    prefix="/tasks",
    tags=["Admin - Tasks"],
)

router.include_router(
    popup.router,
    prefix="/popups",
    tags=["Admin - Popups"],
)

router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Admin - Analytics"],
)

router.include_router(
    moviesource.router,
    prefix="/movie-sources",
    tags=["Admin - Movie Sources"],
)