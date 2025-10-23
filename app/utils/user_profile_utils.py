from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user_profile import UserProfile, ProfileType, ProfileStatus
from app.models.user import User
from app.models.watch_progress import UserWatchProgress
from app.models.content import UserContentInteraction
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate, ParentalControls


async def create_user_profile(
    user_id: UUID,
    profile_data: UserProfileCreate,
    db: AsyncSession
) -> UserProfile:
    """Create a new user profile"""
    
    # Check if this is the first profile (make it primary)
    existing_profiles = await get_user_profiles(user_id, db)
    is_primary = len(existing_profiles) == 0
    
    # Handle parental controls safely
    parental_controls = getattr(profile_data, 'parental_controls', None)
    parental_controls_enabled = parental_controls.enabled if parental_controls else False
    content_restrictions = parental_controls.content_restrictions if parental_controls else None
    viewing_time_limit = parental_controls.viewing_time_limit if parental_controls else None
    bedtime_start = parental_controls.bedtime_start if parental_controls else None
    bedtime_end = parental_controls.bedtime_end if parental_controls else None
    
    # Create profile
    profile = UserProfile(
        user_id=user_id,
        name=profile_data.name,
        avatar_url=profile_data.avatar_url,
        profile_type=profile_data.profile_type,
        is_primary=is_primary,
        is_kids_profile=profile_data.profile_type == "CHILD",
        age_rating_limit=profile_data.age_rating_limit,
        language_preference=profile_data.language_preference,
        subtitle_preference=profile_data.subtitle_preference,
        parental_controls_enabled=parental_controls_enabled,
        content_restrictions=content_restrictions,
        viewing_time_limit=viewing_time_limit,
        bedtime_start=bedtime_start,
        bedtime_end=bedtime_end,
        last_used_at=datetime.utcnow()
    )
    
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    return profile


async def get_user_profiles(
    user_id: UUID,
    db: AsyncSession
) -> List[UserProfile]:
    """Get all profiles for a user"""
    query = select(UserProfile).where(
        and_(
            UserProfile.user_id == user_id,
            UserProfile.is_deleted == False
        )
    ).order_by(desc(UserProfile.is_primary), desc(UserProfile.last_used_at))
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_profile_by_id(
    profile_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> Optional[UserProfile]:
    """Get a specific profile by ID"""
    query = select(UserProfile).where(
        and_(
            UserProfile.id == profile_id,
            UserProfile.user_id == user_id,
            UserProfile.is_deleted == False
        )
    )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_user_profile(
    profile_id: UUID,
    user_id: UUID,
    profile_data: UserProfileUpdate,
    db: AsyncSession
) -> Optional[UserProfile]:
    """Update a user profile"""
    profile = await get_profile_by_id(profile_id, user_id, db)
    if not profile:
        return None
    
    # Update fields
    if profile_data.name is not None:
        profile.name = profile_data.name
    if profile_data.avatar_url is not None:
        profile.avatar_url = profile_data.avatar_url
    if profile_data.profile_type is not None:
        profile.profile_type = profile_data.profile_type
    # Derive is_kids_profile from profile_type
    if profile_data.profile_type is not None:
        profile.is_kids_profile = profile_data.profile_type == "CHILD"
    if profile_data.age_rating_limit is not None:
        profile.age_rating_limit = profile_data.age_rating_limit
    if profile_data.language_preference is not None:
        profile.language_preference = profile_data.language_preference
    if profile_data.subtitle_preference is not None:
        profile.subtitle_preference = profile_data.subtitle_preference
    
    # Update parental controls
    if profile_data.parental_controls is not None:
        profile.parental_controls_enabled = profile_data.parental_controls.enabled
        profile.content_restrictions = profile_data.parental_controls.content_restrictions
        profile.viewing_time_limit = profile_data.parental_controls.viewing_time_limit
        profile.bedtime_start = profile_data.parental_controls.bedtime_start
        profile.bedtime_end = profile_data.parental_controls.bedtime_end
    
    profile.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


async def delete_user_profile(
    profile_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> bool:
    """Delete a user profile (soft delete)"""
    profile = await get_profile_by_id(profile_id, user_id, db)
    if not profile:
        return False
    
    # Don't allow deleting the primary profile if there are other profiles
    if profile.is_primary:
        other_profiles = await get_user_profiles(user_id, db)
        if len(other_profiles) > 1:
            return False
    
    # Soft delete
    profile.is_deleted = True
    profile.updated_at = datetime.utcnow()
    
    # If this was the primary profile, make another one primary
    if profile.is_primary:
        other_profiles = await get_user_profiles(user_id, db)
        if other_profiles:
            other_profiles[0].is_primary = True
            other_profiles[0].updated_at = datetime.utcnow()
    
    await db.commit()
    return True


async def set_primary_profile(
    profile_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> bool:
    """Set a profile as primary"""
    profile = await get_profile_by_id(profile_id, user_id, db)
    if not profile:
        return False
    
    # Remove primary from all other profiles
    query = select(UserProfile).where(
        and_(
            UserProfile.user_id == user_id,
            UserProfile.id != profile_id,
            UserProfile.is_deleted == False
        )
    )
    result = await db.execute(query)
    other_profiles = result.scalars().all()
    
    for other_profile in other_profiles:
        other_profile.is_primary = False
        other_profile.updated_at = datetime.utcnow()
    
    # Set this profile as primary
    profile.is_primary = True
    profile.updated_at = datetime.utcnow()
    
    await db.commit()
    return True


async def update_profile_last_used(
    profile_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> bool:
    """Update the last used timestamp for a profile"""
    from sqlalchemy import update
    
    try:
        # Direct update without fetching the profile first
        await db.execute(
            update(UserProfile)
            .where(
                and_(
                    UserProfile.id == profile_id,
                    UserProfile.user_id == user_id
                )
            )
            .values(last_used_at=datetime.utcnow())
        )
        await db.commit()
        return True
    except Exception:
        return False


async def get_profile_stats(
    profile_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> dict:
    """Get statistics for a profile"""
    profile = await get_profile_by_id(profile_id, user_id, db)
    if not profile:
        return {}
    
    # Get watch time
    watch_time_query = select(func.sum(UserWatchProgress.total_duration_seconds)).where(
        and_(
            UserWatchProgress.profile_id == profile_id,
            UserWatchProgress.is_completed == True
        )
    )
    watch_time_result = await db.execute(watch_time_query)
    total_seconds = watch_time_result.scalar() or 0
    total_hours = total_seconds / 3600
    
    # Get content counts
    movies_query = select(func.count(UserWatchProgress.id)).where(
        and_(
            UserWatchProgress.profile_id == profile_id,
            UserWatchProgress.is_completed == True,
            UserWatchProgress.content.has(content_type="movie")
        )
    )
    movies_result = await db.execute(movies_query)
    movies_watched = movies_result.scalar() or 0
    
    tv_query = select(func.count(UserWatchProgress.id)).where(
        and_(
            UserWatchProgress.profile_id == profile_id,
            UserWatchProgress.is_completed == True,
            UserWatchProgress.content.has(content_type="tv_series")
        )
    )
    tv_result = await db.execute(tv_query)
    tv_episodes_watched = tv_result.scalar() or 0
    
    # Get last watched
    last_watched_query = select(UserWatchProgress.last_watched_at).where(
        UserWatchProgress.profile_id == profile_id
    ).order_by(desc(UserWatchProgress.last_watched_at)).limit(1)
    last_watched_result = await db.execute(last_watched_query)
    last_watched = last_watched_result.scalar_one_or_none()
    
    return {
        "total_watch_time_hours": round(total_hours, 2),
        "movies_watched": movies_watched,
        "tv_episodes_watched": tv_episodes_watched,
        "favorite_genres": [],  # TODO: Implement genre analysis
        "last_watched_at": last_watched
    }


async def get_primary_profile(
    user_id: UUID,
    db: AsyncSession
) -> Optional[UserProfile]:
    """Get the primary profile for a user"""
    query = select(UserProfile).where(
        and_(
            UserProfile.user_id == user_id,
            UserProfile.is_primary == True,
            UserProfile.is_deleted == False
        )
    )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()
