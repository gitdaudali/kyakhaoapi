from datetime import datetime
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
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
        from sqlalchemy import select, and_
        
        # Get all profiles directly
        query = select(UserProfile).where(
            and_(
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        result = await db.execute(query)
        profiles = result.scalars().all()
        
        # Find primary profile
        primary_profile = next((p for p in profiles if p.is_primary), None)
        
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
        from sqlalchemy import select, and_
        query = select(UserProfile).where(
            and_(
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        result = await db.execute(query)
        existing_profiles = result.scalars().all()
        
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


@router.get("/active", response_model=UserProfileResponse)
async def get_active_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get the currently active profile for the user"""
    try:
        from sqlalchemy import select, and_, desc
        
        # Get all profiles for the user
        query = select(UserProfile).where(
            and_(
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        
        result = await db.execute(query)
        profiles = result.scalars().all()
        
        if not profiles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No profiles found"
            )
        
        # Find the active profile (most recently used, or primary if none used)
        active_profile = None
        
        # First, try to find a profile with last_used_at (recently switched)
        profiles_with_usage = [p for p in profiles if p.last_used_at is not None]
        if profiles_with_usage:
            # Sort by last_used_at descending to get the most recent
            active_profile = max(profiles_with_usage, key=lambda p: p.last_used_at)
        else:
            # If no profiles have been switched to, return the primary profile
            active_profile = next((p for p in profiles if p.is_primary), profiles[0])
        
        return UserProfileResponse(
            id=active_profile.id,
            user_id=active_profile.user_id,
            name=active_profile.name,
            avatar_url=active_profile.avatar_url,
            profile_type=active_profile.profile_type,
            is_primary=active_profile.is_primary,
            age_rating_limit=active_profile.age_rating_limit,
            language_preference=active_profile.language_preference,
            subtitle_preference=active_profile.subtitle_preference,
            is_active=getattr(active_profile, 'is_active', True),
            status=getattr(active_profile, 'status', 'ACTIVE'),
            created_at=active_profile.created_at,
            updated_at=active_profile.updated_at,
            last_used_at=active_profile.last_used_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching active profile: {str(e)}"
        )


@router.get("/{profile_id}", response_model=UserProfileResponse)
async def get_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get a specific profile by ID"""
    try:
        from sqlalchemy import select, and_
        
        # Get the profile directly
        query = select(UserProfile).where(
            and_(
                UserProfile.id == profile_id,
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        result = await db.execute(query)
        profile = result.scalar_one_or_none()
        
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
        from sqlalchemy import select, update, and_
        
        # Get the profile with all needed fields
        query = select(UserProfile).where(
            and_(
                UserProfile.id == switch_request.profile_id,
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        result = await db.execute(query)
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Extract all data immediately to avoid lazy loading
        profile_id = profile.id
        user_id = profile.user_id
        name = profile.name
        avatar_url = profile.avatar_url
        profile_type = profile.profile_type
        is_primary = profile.is_primary
        age_rating_limit = profile.age_rating_limit
        language_preference = profile.language_preference
        subtitle_preference = profile.subtitle_preference
        is_active = getattr(profile, 'is_active', True)
        created_at = profile.created_at
        updated_at = profile.updated_at
        last_used_at = profile.last_used_at
        
        # Update the last_used_at timestamp to mark this as the active profile
        try:
            await db.execute(
                update(UserProfile)
                .where(UserProfile.id == switch_request.profile_id)
                .values(last_used_at=datetime.utcnow())
            )
            await db.commit()
        except Exception as e:
            print(f"Warning: Could not update last_used_at: {str(e)}")
        
        # Create response
        try:
            print(f"Creating profile response for profile: {name}")
            print(f"Profile data: id={profile_id}, name={name}, last_used_at={last_used_at}")
            
            # Create response data manually to avoid relationship access
            profile_data = {
                "id": profile_id,
                "user_id": user_id,
                "name": name,
                "avatar_url": avatar_url,
                "profile_type": profile_type,
                "is_primary": is_primary,
                "age_rating_limit": age_rating_limit,
                "language_preference": language_preference,
                "subtitle_preference": subtitle_preference,
                "is_active": is_active,
                "created_at": created_at,
                "updated_at": updated_at,
                "last_used_at": last_used_at
            }
            
            profile_response = UserProfileResponse(**profile_data)
            
            print(f"Profile response created successfully: {profile_response.name}")
            
            switch_response = ProfileSwitchResponse(
                message="Profile switched successfully",
                profile=profile_response,
                access_token="new_token_here"  # TODO: Generate actual token
            )
            
            print(f"Switch response created successfully")
            return switch_response
            
        except Exception as response_error:
            print(f"Error creating response: {str(response_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating response: {str(response_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Main exception in switch_profile: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error switching profile: {str(e)}"
        )


# NEW ENDPOINTS - Profile Switching & Active Profile Management

@router.post("/{profile_id}/switch", response_model=ProfileSwitchResponse)
async def switch_to_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Switch to a specific profile by ID"""
    try:
        from sqlalchemy import select, update, and_
        
        # Get the profile with all needed fields
        query = select(UserProfile).where(
            and_(
                UserProfile.id == profile_id,
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        result = await db.execute(query)
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Extract all data immediately to avoid lazy loading
        profile_id = profile.id
        user_id = profile.user_id
        name = profile.name
        avatar_url = profile.avatar_url
        profile_type = profile.profile_type
        is_primary = profile.is_primary
        age_rating_limit = profile.age_rating_limit
        language_preference = profile.language_preference
        subtitle_preference = profile.subtitle_preference
        is_active = getattr(profile, 'is_active', True)
        created_at = profile.created_at
        updated_at = profile.updated_at
        last_used_at = profile.last_used_at
        
        # Update the last_used_at timestamp to mark this as the active profile
        try:
            await db.execute(
                update(UserProfile)
                .where(UserProfile.id == profile_id)
                .values(last_used_at=datetime.utcnow())
            )
            await db.commit()
        except Exception as e:
            print(f"Warning: Could not update last_used_at: {str(e)}")
        
        # Create response data manually to avoid relationship access
        profile_data = {
            "id": profile_id,
            "user_id": user_id,
            "name": name,
            "avatar_url": avatar_url,
            "profile_type": profile_type,
            "is_primary": is_primary,
            "age_rating_limit": age_rating_limit,
            "language_preference": language_preference,
            "subtitle_preference": subtitle_preference,
            "is_active": is_active,
            "created_at": created_at,
            "updated_at": updated_at,
            "last_used_at": last_used_at
        }
        
        profile_response = UserProfileResponse(**profile_data)
        
        return ProfileSwitchResponse(
            message="Profile switched successfully",
            profile=profile_response,
            access_token="new_token_here"  # TODO: Generate actual token with profile context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error switching to profile: {str(e)}"
        )


# ===== PROFILE-SPECIFIC FEATURES =====

@router.get("/{profile_id}/watchlist")
async def get_profile_watchlist(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get watchlist for a specific profile"""
    try:
        from sqlalchemy import select, and_
        from app.models.content import UserContentInteraction, Content
        from app.schemas.watchlist import WatchlistResponse, WatchlistContentItem, GenreInfo
        
        # Verify profile belongs to user
        profile_query = select(UserProfile).where(
            and_(
                UserProfile.id == profile_id,
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        profile_result = await db.execute(profile_query)
        profile = profile_result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Get watchlist content for this profile
        query = select(Content).join(
            UserContentInteraction, Content.id == UserContentInteraction.content_id
        ).where(
            and_(
                UserContentInteraction.user_id == current_user.id,
                UserContentInteraction.profile_id == profile_id,
                UserContentInteraction.interaction_type == "watchlist",
                Content.is_deleted == False
            )
        )
        
        result = await db.execute(query)
        watchlist_content = result.scalars().all()
        
        # Separate movies and TV shows
        movies = []
        tv_shows = []
        
        for content in watchlist_content:
            # Convert genres
            genres = [GenreInfo(id=str(genre.id), name=genre.name) for genre in content.genres]
            
            item = WatchlistContentItem(
                id=str(content.id),
                title=content.title,
                slug=content.slug,
                description=content.description,
                poster_url=content.poster_url,
                backdrop_url=content.backdrop_url,
                content_type=content.content_type,
                release_date=content.release_date.isoformat() if content.release_date else None,
                platform_rating=content.platform_rating,
                platform_votes=content.platform_votes or 0,
                genres=genres,
                added_at=content.created_at.isoformat()
            )
            
            if content.content_type == "movie":
                movies.append(item)
            else:
                tv_shows.append(item)
        
        return WatchlistResponse(
            movies=movies,
            tv_shows=tv_shows,
            total_movies=len(movies),
            total_tv_shows=len(tv_shows),
            total_watchlist=len(watchlist_content)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile watchlist: {str(e)}"
        )


@router.post("/{profile_id}/watchlist/{content_id}")
async def add_to_profile_watchlist(
    profile_id: UUID,
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add content to a specific profile's watchlist"""
    try:
        from sqlalchemy import select, and_
        from app.models.content import UserContentInteraction, Content
        from app.schemas.watchlist import WatchlistActionResponse
        
        # Verify profile belongs to user
        profile_query = select(UserProfile).where(
            and_(
                UserProfile.id == profile_id,
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        profile_result = await db.execute(profile_query)
        profile = profile_result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Check if content exists
        content_query = select(Content).where(
            and_(Content.id == content_id, Content.is_deleted == False)
        )
        content_result = await db.execute(content_query)
        content = content_result.scalar_one_or_none()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check if already in profile watchlist
        existing_query = select(UserContentInteraction).where(
            and_(
                UserContentInteraction.user_id == current_user.id,
                UserContentInteraction.profile_id == profile_id,
                UserContentInteraction.content_id == content_id,
                UserContentInteraction.interaction_type == "watchlist"
            )
        )
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            return WatchlistActionResponse(
                message="Content already in profile watchlist", 
                status="already_added"
            )
        
        # Add to profile watchlist
        watchlist_item = UserContentInteraction(
            user_id=current_user.id,
            profile_id=profile_id,
            content_id=content_id,
            interaction_type="watchlist"
        )
        db.add(watchlist_item)
        await db.commit()
        
        return WatchlistActionResponse(
            message="Content added to profile watchlist", 
            status="added"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding to profile watchlist: {str(e)}"
        )


@router.delete("/{profile_id}/watchlist/{content_id}")
async def remove_from_profile_watchlist(
    profile_id: UUID,
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove content from a specific profile's watchlist"""
    try:
        from sqlalchemy import select, and_
        from app.models.content import UserContentInteraction
        from app.schemas.watchlist import WatchlistActionResponse
        
        # Verify profile belongs to user
        profile_query = select(UserProfile).where(
            and_(
                UserProfile.id == profile_id,
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        profile_result = await db.execute(profile_query)
        profile = profile_result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Find the profile watchlist entry
        query = select(UserContentInteraction).where(
            and_(
                UserContentInteraction.user_id == current_user.id,
                UserContentInteraction.profile_id == profile_id,
                UserContentInteraction.content_id == content_id,
                UserContentInteraction.interaction_type == "watchlist"
            )
        )
        result = await db.execute(query)
        watchlist_entry = result.scalar_one_or_none()
        
        if not watchlist_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found in profile watchlist"
            )
        
        await db.delete(watchlist_entry)
        await db.commit()
        
        return WatchlistActionResponse(
            message="Content removed from profile watchlist", 
            status="removed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing from profile watchlist: {str(e)}"
        )


@router.get("/{profile_id}/watch-history")
async def get_profile_watch_history(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get watch history for a specific profile"""
    try:
        from sqlalchemy import select, and_, desc
        from app.models.content import UserWatchHistory, Content
        from app.schemas.user_profile import ProfileWatchHistoryResponse, ProfileWatchHistoryItem
        
        # Verify profile belongs to user
        profile_query = select(UserProfile).where(
            and_(
                UserProfile.id == profile_id,
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        profile_result = await db.execute(profile_query)
        profile = profile_result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Get watch history for this profile
        query = select(UserWatchHistory, Content).join(
            Content, UserWatchHistory.content_id == Content.id
        ).where(
            and_(
                UserWatchHistory.user_id == current_user.id,
                UserWatchHistory.profile_id == profile_id,
                Content.is_deleted == False
            )
        ).order_by(desc(UserWatchHistory.last_watched_at))
        
        result = await db.execute(query)
        watch_history_data = result.all()
        
        watch_history = []
        for history, content in watch_history_data:
            item = ProfileWatchHistoryItem(
                content_id=str(content.id),
                title=content.title,
                slug=content.slug,
                content_type=content.content_type,
                poster_url=content.poster_url,
                current_position_seconds=history.current_position_seconds,
                total_episodes_watched=history.total_episodes_watched,
                is_completed=history.is_completed,
                is_currently_watching=history.is_currently_watching,
                last_watched_at=history.last_watched_at,
                first_watched_at=history.first_watched_at
            )
            watch_history.append(item)
        
        return ProfileWatchHistoryResponse(
            profile_id=str(profile_id),
            profile_name=profile.name,
            watch_history=watch_history,
            total_watched=len(watch_history)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile watch history: {str(e)}"
        )


@router.get("/{profile_id}/recommendations")
async def get_profile_recommendations(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized recommendations for a specific profile"""
    try:
        from sqlalchemy import select, and_
        from app.schemas.recommendations import RecommendationResponse, RecommendationItem
        from app.utils.recommendation_utils import get_hardcoded_recommendations
        from app.schemas.recommendations import RecommendationQueryParams
        
        # Verify profile belongs to user
        profile_query = select(UserProfile).where(
            and_(
                UserProfile.id == profile_id,
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        profile_result = await db.execute(profile_query)
        profile = profile_result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Get profile-specific recommendations
        # For now, we'll use the existing recommendation system but filter by profile preferences
        query_params = RecommendationQueryParams(limit=10)
        
        # Get base recommendations
        base_recommendations = get_hardcoded_recommendations(
            user_id=str(current_user.id),
            query_params=query_params
        )
        
        # Filter recommendations based on profile preferences
        filtered_recommendations = []
        for rec in base_recommendations.recommendations:
            # Apply age rating filter
            if hasattr(rec, 'platform_rating') and rec.platform_rating:
                if profile.age_rating_limit < 18 and rec.platform_rating > 4.0:
                    continue  # Skip highly rated content for child profiles
            
            # Apply language preference filter
            if profile.language_preference != "en":
                # For non-English profiles, prioritize content in their language
                # This is a simplified filter - in real implementation, you'd check content language
                pass
            
            filtered_recommendations.append(rec)
        
        # Update the response with profile-specific data
        return RecommendationResponse(
            user_id=current_user.id,
            recommendations=filtered_recommendations,
            total_recommendations=len(filtered_recommendations),
            recommendation_type="profile_specific",
            generated_at=datetime.utcnow().isoformat(),
            message=f"Personalized recommendations for {profile.name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile recommendations: {str(e)}"
        )


@router.put("/{profile_id}/preferences")
async def update_profile_preferences(
    profile_id: UUID,
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update preferences for a specific profile"""
    try:
        from sqlalchemy import select, and_, update
        
        # Verify profile belongs to user
        profile_query = select(UserProfile).where(
            and_(
                UserProfile.id == profile_id,
                UserProfile.user_id == current_user.id,
                UserProfile.is_deleted == False
            )
        )
        profile_result = await db.execute(profile_query)
        profile = profile_result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Update profile preferences
        update_data = {}
        
        # Update language preferences
        if "language_preference" in preferences:
            update_data["language_preference"] = preferences["language_preference"]
        
        if "subtitle_preference" in preferences:
            update_data["subtitle_preference"] = preferences["subtitle_preference"]
        
        # Update age rating limit
        if "age_rating_limit" in preferences:
            update_data["age_rating_limit"] = preferences["age_rating_limit"]
        
        # Update parental controls
        if "parental_controls" in preferences:
            pc = preferences["parental_controls"]
            if isinstance(pc, dict):
                update_data["parental_controls_enabled"] = pc.get("enabled", False)
                update_data["content_restrictions"] = pc.get("content_restrictions")
                update_data["viewing_time_limit"] = pc.get("viewing_time_limit")
                update_data["bedtime_start"] = pc.get("bedtime_start")
                update_data["bedtime_end"] = pc.get("bedtime_end")
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            
            update_query = update(UserProfile).where(
                UserProfile.id == profile_id
            ).values(**update_data)
            
            await db.execute(update_query)
            await db.commit()
        
        return {
            "success": True,
            "message": "Profile preferences updated successfully",
            "data": {
                "profile_id": str(profile_id),
                "updated_preferences": update_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile preferences: {str(e)}"
        )
