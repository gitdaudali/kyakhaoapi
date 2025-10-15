from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_user
from app.core.messages import (
    PROFILE_UPDATE_SUCCESS,
    AVATAR_UPLOAD_SUCCESS,
    AVATAR_REMOVED_SUCCESS,
    INVALID_FILE_TYPE,
    FILE_TOO_LARGE
)
from app.core.response_handler import (
    success_response,
    error_response,
    InvalidFileFormatException,
    FileTooLargeException,
    InternalServerException
)
from app.models.user import User
from app.schemas.user import (
    ProfileResponse,
    SearchHistoryCreate,
    SearchHistoryDeleteResponse,
    SearchHistoryListResponse,
    SearchHistoryResponse,
)
from app.schemas.user import User as UserSchema
from app.schemas.user import UserUpdate
from app.utils.s3_utils import delete_file_from_s3, upload_file_to_s3
from app.utils.user_utils import (
    add_search_to_history,
    clear_all_search_history,
    delete_search_from_history,
    get_recent_searches,
    get_user_search_history,
)

router = APIRouter()


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile_with_avatar(
    first_name: str = Form(None),
    last_name: str = Form(None),
    avatar: UploadFile = File(None),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """
    Update user profile with optional avatar upload in a single request.
    """
    try:
        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name

        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)

        if avatar:
            avatar_url = await upload_file_to_s3(
                file=avatar,
                folder="avatars",
                allowed_extensions=settings.AVATAR_ALLOWED_FILE_TYPES,
                max_size_mb=5,
            )

            if current_user.avatar_url:
                delete_file_from_s3(current_user.avatar_url)

            current_user.avatar_url = avatar_url

        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)

        profile_data = ProfileResponse(
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            email=current_user.email,
            avatar_url=current_user.avatar_url,
            is_email_verified=current_user.profile_status != "pending_verification",
            profile_complete=bool(current_user.first_name and current_user.last_name),
        )
        
        return success_response(
            message=PROFILE_UPDATE_SUCCESS,
            data=profile_data.dict()
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise InternalServerException(
            detail=f"Error updating profile: {str(e)}"
        )


@router.post("/search-history", response_model=SearchHistoryResponse)
async def add_search_history(
    search_data: SearchHistoryCreate,
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> SearchHistoryResponse:
    """
    Add a search query to user's search history.
    If the same search already exists, it will update the count and move it to the top.
    """
    try:
        search_entry = await add_search_to_history(
            db, current_user.id, search_data.search_query
        )
        return success_response(
            message="Search added to history successfully",
            data=SearchHistoryResponse.from_orm(search_entry).dict()
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise InternalServerException(
            detail=f"Error adding search to history: {str(e)}"
        )


@router.get("/search-history", response_model=SearchHistoryListResponse)
async def get_search_history(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Page size"),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> SearchHistoryListResponse:
    """
    Get user's search history with pagination.
    Returns searches ordered by last_searched_at (most recent first).
    """
    try:
        search_entries, total = await get_user_search_history(
            db, current_user.id, page, size
        )

        # Calculate pagination info
        pages = (total + size - 1) // size
        has_next = page < pages
        has_prev = page > 1

        response_data = SearchHistoryListResponse(
            items=[SearchHistoryResponse.from_orm(entry) for entry in search_entries],
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev,
        )
        
        return success_response(
            message="Search history retrieved successfully",
            data=response_data.dict()
        )

    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving search history: {str(e)}"
        )


@router.get("/search-history/recent", response_model=list[SearchHistoryResponse])
async def get_recent_search_history(
    limit: int = Query(
        5, ge=1, le=20, description="Number of recent searches to return"
    ),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> list[SearchHistoryResponse]:
    """
    Get user's recent search history for autocomplete/suggestions.
    Returns the most recent searches ordered by last_searched_at.
    """
    try:
        recent_searches = await get_recent_searches(db, current_user.id, limit)
        return success_response(
            message="Recent searches retrieved successfully",
            data=[SearchHistoryResponse.from_orm(entry).dict() for entry in recent_searches]
        )

    except Exception as e:
        raise InternalServerException(
            detail=f"Error retrieving recent searches: {str(e)}"
        )


@router.delete(
    "/search-history/{search_history_id}", response_model=SearchHistoryDeleteResponse
)
async def delete_search_history(
    search_history_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> SearchHistoryDeleteResponse:
    """
    Delete a specific search history entry.
    """
    try:
        deleted = await delete_search_from_history(
            db, current_user.id, search_history_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Search history entry not found",
            )

        return success_response(
            message="Search history entry deleted successfully",
            data={"deleted_count": 1}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerException(
            detail=f"Error deleting search history: {str(e)}"
        )


@router.delete("/search-history", response_model=SearchHistoryDeleteResponse)
async def clear_search_history(
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: AsyncSession = Depends(get_db),
) -> SearchHistoryDeleteResponse:
    """
    Clear all search history for the current user.
    """
    try:
        deleted_count = await clear_all_search_history(db, current_user.id)

        return success_response(
            message=f"All search history cleared successfully. {deleted_count} entries deleted.",
            data={"deleted_count": deleted_count}
        )

    except Exception as e:
        raise InternalServerException(
            detail=f"Error clearing search history: {str(e)}"
        )
