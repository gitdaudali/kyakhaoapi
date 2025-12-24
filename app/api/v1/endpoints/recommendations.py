"""
Dish recommendation endpoints.
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.recommendation_engine import RecommendationEngine, ScoreBreakdown
from app.core.database import get_db
from app.core.response_handler import error_response, success_response
from app.models.food import (
    Cuisine,
    Dish,
    Restaurant,
    UserAllergyAssociation,
    UserCuisineAssociation,
)
from app.models.recommendation import (
    DietaryTag,
    DishDietaryTagAssociation,
    InteractionType,
    UserInteraction,
    UserPreference,
)
from app.models.user import User
from app.schemas.recommendation import (
    InteractionTrackRequest,
    InteractionTrackResponse,
    RecommendationRequest,
    RecommendationResponse,
    RecommendedDish,
    ScoreBreakdownResponse,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


async def get_user_preferences(
    user_id: uuid.UUID,
    db: AsyncSession,
) -> Dict:
    """Get user preferences for recommendations."""
    stmt = select(UserPreference).where(UserPreference.user_id == user_id)
    result = await db.execute(stmt)
    pref = result.scalar_one_or_none()
    
    if not pref:
        return {}
    
    # Parse JSON fields
    preferred_dietary_tags = []
    if pref.preferred_dietary_tags:
        try:
            preferred_dietary_tags = json.loads(pref.preferred_dietary_tags)
        except (json.JSONDecodeError, TypeError):
            preferred_dietary_tags = []
    
    return {
        "min_budget": float(pref.min_budget) if pref.min_budget else None,
        "max_budget": float(pref.max_budget) if pref.max_budget else None,
        "preferred_dietary_tags": [uuid.UUID(tag_id) for tag_id in preferred_dietary_tags],
        "preferred_spice_level": pref.preferred_spice_level,
    }


async def get_user_favorite_cuisines(
    user_id: uuid.UUID,
    db: AsyncSession,
) -> List[uuid.UUID]:
    """Get list of user's favorite cuisine IDs."""
    stmt = (
        select(Cuisine.id)
        .join(UserCuisineAssociation, Cuisine.id == UserCuisineAssociation.c.cuisine_id)
        .where(
            UserCuisineAssociation.c.user_id == user_id,
            Cuisine.is_deleted.is_(False),
        )
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


async def get_user_allergies(
    user_id: uuid.UUID,
    db: AsyncSession,
) -> List[uuid.UUID]:
    """Get list of user's allergy IDs."""
    from app.models.food import Allergy
    
    stmt = (
        select(Allergy.id)
        .join(UserAllergyAssociation, Allergy.id == UserAllergyAssociation.c.allergy_id)
        .where(
            UserAllergyAssociation.c.user_id == user_id,
            Allergy.is_deleted.is_(False),
        )
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


async def get_user_interactions(
    user_id: uuid.UUID,
    db: AsyncSession,
) -> Dict[uuid.UUID, Dict[str, int]]:
    """Get user interaction counts grouped by dish_id."""
    stmt = (
        select(
            UserInteraction.dish_id,
            UserInteraction.interaction_type,
            func.count(UserInteraction.id).label("count"),
        )
        .where(UserInteraction.user_id == user_id)
        .group_by(UserInteraction.dish_id, UserInteraction.interaction_type)
    )
    result = await db.execute(stmt)
    
    interactions = {}
    for row in result.all():
        dish_id = row[0]
        interaction_type = row[1]
        count = row[2]
        
        if dish_id not in interactions:
            interactions[dish_id] = {}
        interactions[dish_id][interaction_type] = count
    
    return interactions


async def get_dish_dietary_tags(
    dish_ids: List[uuid.UUID],
    db: AsyncSession,
) -> Dict[uuid.UUID, List[uuid.UUID]]:
    """Get dietary tags for multiple dishes."""
    if not dish_ids:
        return {}
    
    stmt = (
        select(
            DishDietaryTagAssociation.c.dish_id,
            DishDietaryTagAssociation.c.dietary_tag_id,
        )
        .where(DishDietaryTagAssociation.c.dish_id.in_(dish_ids))
    )
    result = await db.execute(stmt)
    
    dish_tags = {}
    for row in result.all():
        dish_id = row[0]
        tag_id = row[1]
        if dish_id not in dish_tags:
            dish_tags[dish_id] = []
        dish_tags[dish_id].append(tag_id)
    
    return dish_tags


@router.get("/dishes", response_model=RecommendationResponse)
async def get_dish_recommendations(
    request: RecommendationRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get personalized dish recommendations for the current user.
    
    Returns dishes ranked by match score (0-100) based on:
    - User taste preferences (spice level, cuisine)
    - Budget range
    - Dietary tags
    - Past interactions (clicks, reservations, orders)
    - Dish rating
    """
    try:
        # Get user preferences and data
        user_preferences = await get_user_preferences(current_user.id, db)
        user_favorite_cuisines = await get_user_favorite_cuisines(current_user.id, db)
        user_allergies = await get_user_allergies(current_user.id, db)
        user_interactions = await get_user_interactions(current_user.id, db)
        
        # Also check user's spice_level_preference from User model
        if not user_preferences.get("preferred_spice_level") and current_user.spice_level_preference:
            user_preferences["preferred_spice_level"] = current_user.spice_level_preference
        
        # Build base query for dishes
        stmt = select(Dish).where(Dish.is_deleted.is_(False))
        
        # Apply filters
        if request.cuisine_id:
            stmt = stmt.where(Dish.cuisine_id == request.cuisine_id)
        if request.restaurant_id:
            stmt = stmt.where(Dish.restaurant_id == request.restaurant_id)
        
        # Execute query to get all matching dishes
        result = await db.execute(stmt)
        dishes = result.scalars().all()
        
        if not dishes:
            return RecommendationResponse(
                recommendations=[],
                total_count=0,
                user_id=current_user.id,
                filters_applied={
                    "cuisine_id": str(request.cuisine_id) if request.cuisine_id else None,
                    "restaurant_id": str(request.restaurant_id) if request.restaurant_id else None,
                },
            )
        
        # Get dietary tags for all dishes
        dish_ids = [dish.id for dish in dishes]
        dish_tags_map = await get_dish_dietary_tags(dish_ids, db)
        
        # Initialize recommendation engine
        engine = RecommendationEngine()
        
        # Calculate scores for each dish
        scored_dishes = []
        for dish in dishes:
            dish_dict = {
                "id": dish.id,
                "price": float(dish.price) if dish.price else None,
                "cuisine_id": dish.cuisine_id,
                "rating": float(dish.rating) if dish.rating else None,
                "spice_level": getattr(dish, "spice_level", None),  # May not exist yet
            }
            
            dish_tags = dish_tags_map.get(dish.id, [])
            
            score, breakdown = await engine.calculate_match_score(
                dish=dish_dict,
                user_preferences=user_preferences,
                user_favorite_cuisines=user_favorite_cuisines,
                user_allergies=user_allergies,
                user_interactions=user_interactions,
                dish_dietary_tags=dish_tags,
                db=db,
            )
            
            # Filter by min_score if specified
            if score < request.min_score:
                continue
            
            # Get cuisine and restaurant names
            cuisine_stmt = select(Cuisine).where(Cuisine.id == dish.cuisine_id)
            cuisine_result = await db.execute(cuisine_stmt)
            cuisine = cuisine_result.scalar_one_or_none()
            
            restaurant_stmt = select(Restaurant).where(Restaurant.id == dish.restaurant_id)
            restaurant_result = await db.execute(restaurant_stmt)
            restaurant = restaurant_result.scalar_one_or_none()
            
            # Build recommendation object
            recommendation = RecommendedDish(
                dish_id=dish.id,
                name=dish.name,
                description=dish.description,
                price=float(dish.price) if dish.price else None,
                rating=float(dish.rating) if dish.rating else None,
                cuisine_id=dish.cuisine_id,
                cuisine_name=cuisine.name if cuisine else None,
                restaurant_id=dish.restaurant_id,
                restaurant_name=restaurant.name if restaurant else None,
                match_score=round(score, 2),
                score_breakdown=ScoreBreakdownResponse(**breakdown.to_dict()) if request.include_explanation else None,
                explanation=breakdown.get_explanation() if request.include_explanation else None,
            )
            
            scored_dishes.append((score, recommendation))
        
        # Sort by score (descending) and limit
        scored_dishes.sort(key=lambda x: x[0], reverse=True)
        recommendations = [dish for _, dish in scored_dishes[: request.limit]]
        
        return RecommendationResponse(
            recommendations=recommendations,
            total_count=len(recommendations),
            user_id=current_user.id,
            filters_applied={
                "cuisine_id": str(request.cuisine_id) if request.cuisine_id else None,
                "restaurant_id": str(request.restaurant_id) if request.restaurant_id else None,
                "min_score": str(request.min_score),
            },
        )
        
    except Exception as e:
        return error_response(
            message=f"Error generating recommendations: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/interactions/track", response_model=InteractionTrackResponse)
async def track_interaction(
    request: InteractionTrackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Track a user interaction with a dish.
    
    This endpoint stores user interactions (clicks, views, reservations, etc.)
    for future ML training and recommendation improvements.
    """
    try:
        # Validate interaction type
        valid_types = [e.value for e in InteractionType]
        if request.interaction_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid interaction_type. Must be one of: {', '.join(valid_types)}",
            )
        
        # Verify dish exists
        dish_stmt = select(Dish).where(Dish.id == request.dish_id, Dish.is_deleted.is_(False))
        dish_result = await db.execute(dish_stmt)
        dish = dish_result.scalar_one_or_none()
        
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dish not found",
            )
        
        # Create interaction record
        metadata_json = json.dumps(request.metadata) if request.metadata else None
        
        interaction = UserInteraction(
            user_id=current_user.id,
            dish_id=request.dish_id,
            interaction_type=request.interaction_type,
            metadata=metadata_json,
        )
        
        db.add(interaction)
        await db.commit()
        await db.refresh(interaction)
        
        return InteractionTrackResponse(
            success=True,
            interaction_id=interaction.id,
            message=f"Interaction '{request.interaction_type}' tracked successfully",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        return error_response(
            message=f"Error tracking interaction: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

