from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import AdminUser
from app.core.deps import get_db
from app.core.messages import (
    PERSON_CREATED,
    PERSON_DELETED,
    PERSON_FEATURED,
    PERSON_NOT_FOUND,
    PERSON_UNFEATURED,
    PERSON_UNVERIFIED,
    PERSON_UPDATED,
    PERSON_VERIFIED,
)
from app.schemas.admin import (
    PersonAdminCreate,
    PersonAdminListResponse,
    PersonAdminQueryParams,
    PersonAdminResponse,
    PersonAdminUpdate,
)
from app.utils.admin_utils import (
    create_person,
    delete_person,
    get_people_admin_list,
    get_person_admin_by_id,
    toggle_person_featured,
    toggle_person_verified,
    update_person,
)
from app.utils.content_utils import calculate_pagination_info

router = APIRouter()


@router.post("/", response_model=PersonAdminResponse)
async def create_person_admin(
    current_user: AdminUser,
    person_data: PersonAdminCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new person (Admin only).
    """
    try:
        person = await create_person(db, person_data.dict())
        return PersonAdminResponse.model_validate(person)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating person: {str(e)}",
        )


@router.get("/", response_model=PersonAdminListResponse)
async def get_people_admin(
    current_user: AdminUser,
    query_params: PersonAdminQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get people list with pagination and filtering (Admin only).
    """
    try:
        people, total = await get_people_admin_list(db, query_params)
        pagination_info = calculate_pagination_info(
            query_params.page, query_params.size, total
        )

        return PersonAdminListResponse(
            items=[PersonAdminResponse.model_validate(person) for person in people],
            total=pagination_info["total"],
            page=pagination_info["page"],
            size=pagination_info["size"],
            pages=pagination_info["pages"],
            has_next=pagination_info["has_next"],
            has_prev=pagination_info["has_prev"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving people list: {str(e)}",
        )


@router.get("/{person_id}", response_model=PersonAdminResponse)
async def get_person_admin(
    person_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get person by ID for admin.
    """
    try:
        person = await get_person_admin_by_id(db, person_id)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=PERSON_NOT_FOUND,
            )

        return PersonAdminResponse.model_validate(person)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving person: {str(e)}",
        )


@router.put("/{person_id}", response_model=PersonAdminResponse)
async def update_person_admin(
    person_id: UUID,
    current_user: AdminUser,
    person_data: PersonAdminUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update person (Admin only).
    """
    try:
        # Filter out None values
        update_data = {k: v for k, v in person_data.dict().items() if v is not None}

        person = await update_person(db, person_id, update_data)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=PERSON_NOT_FOUND,
            )

        return PersonAdminResponse.model_validate(person)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating person: {str(e)}",
        )


@router.delete("/{person_id}")
async def delete_person_admin(
    person_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete person (Admin only).
    """
    try:
        success = await delete_person(db, person_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=PERSON_NOT_FOUND,
            )

        return {"message": PERSON_DELETED}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting person: {str(e)}",
        )


@router.patch("/{person_id}/featured")
async def toggle_person_featured_admin(
    person_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Toggle person featured status (Admin only).
    """
    try:
        person = await toggle_person_featured(db, person_id)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=PERSON_NOT_FOUND,
            )

        message = PERSON_FEATURED if person.is_featured else PERSON_UNFEATURED

        return {
            "message": message,
            "person": PersonAdminResponse.model_validate(person),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling person featured status: {str(e)}",
        )


@router.patch("/{person_id}/verified")
async def toggle_person_verified_admin(
    person_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Toggle person verified status (Admin only).
    """
    try:
        person = await toggle_person_verified(db, person_id)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=PERSON_NOT_FOUND,
            )

        message = PERSON_VERIFIED if person.is_verified else PERSON_UNVERIFIED

        return {
            "message": message,
            "person": PersonAdminResponse.model_validate(person),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling person verified status: {str(e)}",
        )
