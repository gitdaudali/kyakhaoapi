from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    UserProfileListResponse,
    UserProfileListData,
    ProfileSwitchRequest,
    ProfileSwitchResponse,
    ProfileDeleteResponse,
    ProfileStats
)
from app.utils.user_profile_utils import (
    create_user_profile,
    get_user_profiles,
    get_profile_by_id,
    update_user_profile,
    delete_user_profile,
    set_primary_profile,
    update_profile_last_used,
    get_profile_stats,
    get_primary_profile
)

router = APIRouter()


@router.get("/", response_model=UserProfileListResponse)
async def get_user_profiles_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all profiles for the current user"""
    try:
        profiles = await get_user_profiles(current_user.id, db)
        primary_profile = await get_primary_profile(current_user.id, db)
        
        profile_responses = [
            UserProfileResponse(
                id=profile.id,
                user_id=profile.user_id,
                name=profile.name,
                avatar_url=profile.avatar_url,
                profile_type=profile.profile_type,
                is_primary=profile.is_primary,
                age_rating_limit=profile.age_rating_limit,
                language_preference=profile.language_preference,
                subtitle_preference=profile.subtitle_preference,
                is_active=getattr(profile, 'is_active', True),  # Handle existing data
                created_at=profile.created_at,
                updated_at=profile.updated_at,
                last_used_at=profile.last_used_at
            )
            for profile in profiles
        ]
        
        return UserProfileListResponse(
            data=UserProfileListData(
                profiles=profile_responses,
                total=len(profile_responses),
                primary_profile_id=primary_profile.id if primary_profile else None
            )
        )
        
    except Exception as e:
        print(f"Error in get_user_profiles_list: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profiles: {str(e)}"
        )


@router.post("/", response_model=UserProfileResponse)
async def create_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new user profile"""
    try:
        # Check profile limit (max 5 profiles per user)
        existing_profiles = await get_user_profiles(current_user.id, db)
        if len(existing_profiles) >= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum of 5 profiles allowed per account"
            )
        
        profile = await create_user_profile(current_user.id, profile_data, db)
        
        return UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            avatar_url=profile.avatar_url,
            profile_type=profile.profile_type,
            is_primary=profile.is_primary,
            age_rating_limit=profile.age_rating_limit,
            language_preference=profile.language_preference,
            subtitle_preference=profile.subtitle_preference,
            is_active=getattr(profile, 'is_active', True),
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            last_used_at=profile.last_used_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_profile: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating profile: {str(e)}"
        )


@router.get("/{profile_id}", response_model=UserProfileResponse)
async def get_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get a specific profile by ID"""
    try:
        profile = await get_profile_by_id(profile_id, current_user.id, db)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            avatar_url=profile.avatar_url,
            profile_type=profile.profile_type,
            is_primary=profile.is_primary,
            age_rating_limit=profile.age_rating_limit,
            language_preference=profile.language_preference,
            subtitle_preference=profile.subtitle_preference,
            is_active=getattr(profile, 'is_active', True),
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            last_used_at=profile.last_used_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile: {str(e)}"
        )


@router.put("/{profile_id}", response_model=UserProfileResponse)
async def update_profile(
    profile_id: UUID,
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update a user profile"""
    try:
        profile = await update_user_profile(profile_id, current_user.id, profile_data, db)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            avatar_url=profile.avatar_url,
            profile_type=profile.profile_type,
            is_primary=profile.is_primary,
            age_rating_limit=profile.age_rating_limit,
            language_preference=profile.language_preference,
            subtitle_preference=profile.subtitle_preference,
            is_active=getattr(profile, 'is_active', True),
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            last_used_at=profile.last_used_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )


@router.delete("/{profile_id}", response_model=ProfileDeleteResponse)
async def delete_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete a user profile"""
    try:
        success = await delete_user_profile(profile_id, current_user.id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found or cannot be deleted"
            )
        
        return ProfileDeleteResponse(
            message="Profile deleted successfully",
            deleted_profile_id=profile_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile: {str(e)}"
        )


@router.post("/{profile_id}/set-primary", response_model=dict)
async def set_primary_profile_endpoint(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Set a profile as primary"""
    try:
        success = await set_primary_profile(profile_id, current_user.id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return {"message": "Primary profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting primary profile: {str(e)}"
        )


@router.get("/{profile_id}/stats", response_model=ProfileStats)
async def get_profile_statistics(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get statistics for a specific profile"""
    try:
        stats = await get_profile_stats(profile_id, current_user.id, db)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return ProfileStats(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile statistics: {str(e)}"
        )


@router.post("/switch", response_model=ProfileSwitchResponse)
async def switch_profile(
    switch_request: ProfileSwitchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Switch to a different profile (returns new token)"""
    try:
        profile = await get_profile_by_id(switch_request.profile_id, current_user.id, db)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Update last used timestamp
        await update_profile_last_used(switch_request.profile_id, current_user.id, db)
        
        # TODO: Generate new JWT token with profile context
        # For now, return the profile info
        profile_response = UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            avatar_url=profile.avatar_url,
            profile_type=profile.profile_type,
            is_primary=profile.is_primary,
            is_kids_profile=profile.is_kids_profile,
            age_rating_limit=profile.age_rating_limit,
            language_preference=profile.language_preference,
            subtitle_preference=profile.subtitle_preference,
            status=profile.status,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            last_used_at=profile.last_used_at
        )
        
        return ProfileSwitchResponse(
            message="Profile switched successfully",
            profile=profile_response,
            access_token="new_token_here"  # TODO: Generate actual token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error switching profile: {str(e)}"
        )
