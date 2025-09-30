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

        # Convert SQLAlchemy object to dictionary for proper serialization
        person_dict = {
            "id": person.id,
            "name": person.name,
            "slug": person.slug,
            "biography": person.biography,
            "birth_date": person.birth_date,
            "death_date": person.death_date,
            "birth_place": person.birth_place,
            "nationality": person.nationality,
            "gender": person.gender,
            "profile_image_url": person.profile_image_url,
            "cover_image_url": person.cover_image_url,
            "known_for_department": person.known_for_department,
            "is_verified": person.is_verified,
            "is_featured": person.is_featured,
            "created_at": person.created_at,
            "updated_at": person.updated_at,
            # Convert relationships to dictionaries
            "content_cast": [
                {
                    "content_id": cast.content_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in person.content_cast
            ],
            "content_crew": [
                {
                    "content_id": crew.content_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in person.content_crew
            ],
        }
        return PersonAdminResponse.model_validate(person_dict)
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

        # Convert SQLAlchemy objects to dictionaries for proper serialization
        serialized_people = []
        for person in people:
            person_dict = {
                "id": person.id,
                "name": person.name,
                "slug": person.slug,
                "biography": person.biography,
                "birth_date": person.birth_date,
                "death_date": person.death_date,
                "birth_place": person.birth_place,
                "nationality": person.nationality,
                "gender": person.gender,
                "profile_image_url": person.profile_image_url,
                "cover_image_url": person.cover_image_url,
                "known_for_department": person.known_for_department,
                "is_verified": person.is_verified,
                "is_featured": person.is_featured,
                "created_at": person.created_at,
                "updated_at": person.updated_at,
                # Convert relationships to dictionaries
                "content_cast": [
                    {
                        "content_id": cast.content_id,
                        "character_name": cast.character_name,
                        "job_title": cast.job_title,
                    }
                    for cast in person.content_cast
                ],
                "content_crew": [
                    {
                        "content_id": crew.content_id,
                        "job_title": crew.job_title,
                        "department": crew.department,
                    }
                    for crew in person.content_crew
                ],
            }
            serialized_people.append(person_dict)

        return PersonAdminListResponse(
            items=serialized_people,
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

        # Convert SQLAlchemy object to dictionary for proper serialization
        person_dict = {
            "id": person.id,
            "name": person.name,
            "slug": person.slug,
            "biography": person.biography,
            "birth_date": person.birth_date,
            "death_date": person.death_date,
            "birth_place": person.birth_place,
            "nationality": person.nationality,
            "gender": person.gender,
            "profile_image_url": person.profile_image_url,
            "cover_image_url": person.cover_image_url,
            "known_for_department": person.known_for_department,
            "is_verified": person.is_verified,
            "is_featured": person.is_featured,
            "created_at": person.created_at,
            "updated_at": person.updated_at,
            # Convert relationships to dictionaries
            "content_cast": [
                {
                    "content_id": cast.content_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in person.content_cast
            ],
            "content_crew": [
                {
                    "content_id": crew.content_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in person.content_crew
            ],
        }
        return PersonAdminResponse.model_validate(person_dict)
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

        # Convert SQLAlchemy object to dictionary for proper serialization
        person_dict = {
            "id": person.id,
            "name": person.name,
            "slug": person.slug,
            "biography": person.biography,
            "birth_date": person.birth_date,
            "death_date": person.death_date,
            "birth_place": person.birth_place,
            "nationality": person.nationality,
            "gender": person.gender,
            "profile_image_url": person.profile_image_url,
            "cover_image_url": person.cover_image_url,
            "known_for_department": person.known_for_department,
            "is_verified": person.is_verified,
            "is_featured": person.is_featured,
            "created_at": person.created_at,
            "updated_at": person.updated_at,
            # Convert relationships to dictionaries
            "content_cast": [
                {
                    "content_id": cast.content_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in person.content_cast
            ],
            "content_crew": [
                {
                    "content_id": crew.content_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in person.content_crew
            ],
        }
        return PersonAdminResponse.model_validate(person_dict)
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

        # Convert SQLAlchemy object to dictionary for proper serialization
        person_dict = {
            "id": person.id,
            "name": person.name,
            "slug": person.slug,
            "biography": person.biography,
            "birth_date": person.birth_date,
            "death_date": person.death_date,
            "birth_place": person.birth_place,
            "nationality": person.nationality,
            "gender": person.gender,
            "profile_image_url": person.profile_image_url,
            "cover_image_url": person.cover_image_url,
            "known_for_department": person.known_for_department,
            "is_verified": person.is_verified,
            "is_featured": person.is_featured,
            "created_at": person.created_at,
            "updated_at": person.updated_at,
            # Convert relationships to dictionaries
            "content_cast": [
                {
                    "content_id": cast.content_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in person.content_cast
            ],
            "content_crew": [
                {
                    "content_id": crew.content_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in person.content_crew
            ],
        }

        return {
            "message": message,
            "person": PersonAdminResponse.model_validate(person_dict),
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

        # Convert SQLAlchemy object to dictionary for proper serialization
        person_dict = {
            "id": person.id,
            "name": person.name,
            "slug": person.slug,
            "biography": person.biography,
            "birth_date": person.birth_date,
            "death_date": person.death_date,
            "birth_place": person.birth_place,
            "nationality": person.nationality,
            "gender": person.gender,
            "profile_image_url": person.profile_image_url,
            "cover_image_url": person.cover_image_url,
            "known_for_department": person.known_for_department,
            "is_verified": person.is_verified,
            "is_featured": person.is_featured,
            "created_at": person.created_at,
            "updated_at": person.updated_at,
            # Convert relationships to dictionaries
            "content_cast": [
                {
                    "content_id": cast.content_id,
                    "character_name": cast.character_name,
                    "job_title": cast.job_title,
                }
                for cast in person.content_cast
            ],
            "content_crew": [
                {
                    "content_id": crew.content_id,
                    "job_title": crew.job_title,
                    "department": crew.department,
                }
                for crew in person.content_crew
            ],
        }

        return {
            "message": message,
            "person": PersonAdminResponse.model_validate(person_dict),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling person verified status: {str(e)}",
        )
