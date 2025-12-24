"""
Rule-based dish recommendation engine.

This module provides a deterministic, explainable scoring system for dish recommendations.
The engine is designed to be modular so ML models can be plugged in later.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ScoringWeights:
    """Configurable weights for different scoring factors."""
    spice_level: float = 0.20
    cuisine_match: float = 0.25
    budget_match: float = 0.15
    dietary_tags: float = 0.20
    past_interactions: float = 0.15
    dish_rating: float = 0.05
    
    def validate(self) -> None:
        """Ensure weights sum to approximately 1.0."""
        total = sum([
            self.spice_level,
            self.cuisine_match,
            self.budget_match,
            self.dietary_tags,
            self.past_interactions,
            self.dish_rating,
        ])
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")


@dataclass
class ScoreBreakdown:
    """Breakdown of how a dish score was calculated."""
    spice_level_score: float = 0.0
    cuisine_match_score: float = 0.0
    budget_match_score: float = 0.0
    dietary_tags_score: float = 0.0
    past_interactions_score: float = 0.0
    dish_rating_score: float = 0.0
    total_score: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for API response."""
        return {
            "spice_level": round(self.spice_level_score, 2),
            "cuisine_match": round(self.cuisine_match_score, 2),
            "budget_match": round(self.budget_match_score, 2),
            "dietary_tags": round(self.dietary_tags_score, 2),
            "past_interactions": round(self.past_interactions_score, 2),
            "dish_rating": round(self.dish_rating_score, 2),
            "total": round(self.total_score, 2),
        }
    
    def get_explanation(self) -> List[str]:
        """Generate human-readable explanation of the score."""
        explanations = []
        
        if self.spice_level_score > 0:
            explanations.append(f"Spice level match: {self.spice_level_score:.1f} points")
        if self.cuisine_match_score > 0:
            explanations.append(f"Cuisine preference: {self.cuisine_match_score:.1f} points")
        if self.budget_match_score > 0:
            explanations.append(f"Budget fit: {self.budget_match_score:.1f} points")
        if self.dietary_tags_score > 0:
            explanations.append(f"Dietary tags match: {self.dietary_tags_score:.1f} points")
        if self.past_interactions_score > 0:
            explanations.append(f"Based on your past activity: {self.past_interactions_score:.1f} points")
        if self.dish_rating_score > 0:
            explanations.append(f"Dish rating: {self.dish_rating_score:.1f} points")
        
        return explanations


class RecommendationEngine:
    """
    Rule-based recommendation engine for dish matching.
    
    This engine calculates a match score (0-100) for each dish based on:
    - User taste preferences (spice level, cuisine)
    - Budget range
    - Dietary tags
    - Past interactions (clicks, reservations, orders)
    - Dish rating
    
    The engine is deterministic and explainable, making it easy to debug and adjust.
    """
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        """Initialize the recommendation engine with scoring weights."""
        self.weights = weights or ScoringWeights()
        self.weights.validate()
    
    async def calculate_match_score(
        self,
        dish: Dict,
        user_preferences: Dict,
        user_favorite_cuisines: List[uuid.UUID],
        user_allergies: List[uuid.UUID],
        user_interactions: Dict[uuid.UUID, Dict[str, int]],
        dish_dietary_tags: List[uuid.UUID],
        db: AsyncSession,
    ) -> Tuple[float, ScoreBreakdown]:
        """
        Calculate match score for a dish.
        
        Args:
            dish: Dish data dictionary with fields like price, cuisine_id, rating, etc.
            user_preferences: User preference dict with spice_level, min_budget, max_budget, etc.
            user_favorite_cuisines: List of cuisine IDs the user likes
            user_allergies: List of allergy IDs the user has
            user_interactions: Dict mapping dish_id to interaction counts
            dish_dietary_tags: List of dietary tag IDs for the dish
            db: Database session
            
        Returns:
            Tuple of (score: float, breakdown: ScoreBreakdown)
        """
        breakdown = ScoreBreakdown()
        
        # 1. Spice Level Match (0-20 points)
        breakdown.spice_level_score = self._score_spice_level(
            dish.get("spice_level"),
            user_preferences.get("preferred_spice_level"),
        ) * self.weights.spice_level * 100
        
        # 2. Cuisine Match (0-25 points)
        breakdown.cuisine_match_score = self._score_cuisine_match(
            dish.get("cuisine_id"),
            user_favorite_cuisines,
        ) * self.weights.cuisine_match * 100
        
        # 3. Budget Match (0-15 points)
        breakdown.budget_match_score = self._score_budget_match(
            dish.get("price"),
            user_preferences.get("min_budget"),
            user_preferences.get("max_budget"),
        ) * self.weights.budget_match * 100
        
        # 4. Dietary Tags Match (0-20 points)
        breakdown.dietary_tags_score = self._score_dietary_tags(
            dish_dietary_tags,
            user_preferences.get("preferred_dietary_tags", []),
            user_allergies,
        ) * self.weights.dietary_tags * 100
        
        # 5. Past Interactions (0-15 points)
        dish_id = dish.get("id")
        breakdown.past_interactions_score = self._score_past_interactions(
            dish_id,
            user_interactions,
        ) * self.weights.past_interactions * 100
        
        # 6. Dish Rating (0-5 points)
        breakdown.dish_rating_score = self._score_dish_rating(
            dish.get("rating"),
        ) * self.weights.dish_rating * 100
        
        # Calculate total score (0-100)
        breakdown.total_score = sum([
            breakdown.spice_level_score,
            breakdown.cuisine_match_score,
            breakdown.budget_match_score,
            breakdown.dietary_tags_score,
            breakdown.past_interactions_score,
            breakdown.dish_rating_score,
        ])
        
        # Ensure score is between 0 and 100
        breakdown.total_score = max(0.0, min(100.0, breakdown.total_score))
        
        return breakdown.total_score, breakdown
    
    def _score_spice_level(
        self,
        dish_spice_level: Optional[str],
        user_preferred_spice: Optional[str],
    ) -> float:
        """
        Score spice level match (0.0 to 1.0).
        
        Scoring:
        - Exact match: 1.0
        - One level difference: 0.7
        - Two levels difference: 0.4
        - Three+ levels difference: 0.1
        - No preference: 0.5 (neutral)
        """
        if not dish_spice_level or not user_preferred_spice:
            return 0.5  # Neutral if missing data
        
        spice_levels = ["Mild", "Medium", "Spicy", "Extra Spicy"]
        
        try:
            dish_idx = spice_levels.index(dish_spice_level)
            user_idx = spice_levels.index(user_preferred_spice)
            diff = abs(dish_idx - user_idx)
            
            if diff == 0:
                return 1.0
            elif diff == 1:
                return 0.7
            elif diff == 2:
                return 0.4
            else:
                return 0.1
        except ValueError:
            return 0.5  # Unknown spice level, neutral
    
    def _score_cuisine_match(
        self,
        dish_cuisine_id: Optional[uuid.UUID],
        user_favorite_cuisines: List[uuid.UUID],
    ) -> float:
        """
        Score cuisine match (0.0 to 1.0).
        
        Scoring:
        - Exact match: 1.0
        - No favorite cuisines: 0.5 (neutral)
        - No match: 0.0
        """
        if not dish_cuisine_id:
            return 0.0
        
        if not user_favorite_cuisines:
            return 0.5  # Neutral if user has no preferences
        
        if dish_cuisine_id in user_favorite_cuisines:
            return 1.0
        
        return 0.0
    
    def _score_budget_match(
        self,
        dish_price: Optional[float],
        min_budget: Optional[float],
        max_budget: Optional[float],
    ) -> float:
        """
        Score budget match (0.0 to 1.0).
        
        Scoring:
        - Within budget: 1.0
        - 10% over budget: 0.7
        - 20% over budget: 0.4
        - 30%+ over budget: 0.0
        - Below min budget (if set): 0.8
        - No budget preference: 0.5 (neutral)
        """
        if dish_price is None:
            return 0.5  # Neutral if price unknown
        
        if min_budget is None and max_budget is None:
            return 0.5  # No budget preference
        
        if max_budget is not None:
            if dish_price <= max_budget:
                # Within budget
                if min_budget is not None and dish_price < min_budget:
                    return 0.8  # Below min, but acceptable
                return 1.0
            else:
                # Over budget
                overage = (dish_price - max_budget) / max_budget
                if overage <= 0.10:
                    return 0.7
                elif overage <= 0.20:
                    return 0.4
                else:
                    return 0.0
        
        # Only min_budget set
        if min_budget is not None:
            if dish_price >= min_budget:
                return 1.0
            else:
                return 0.8
        
        return 0.5
    
    def _score_dietary_tags(
        self,
        dish_dietary_tags: List[uuid.UUID],
        user_preferred_tags: List[uuid.UUID],
        user_allergies: List[uuid.UUID],
    ) -> float:
        """
        Score dietary tags match (0.0 to 1.0).
        
        Scoring:
        - Has preferred tags: +0.5 per tag (max 1.0)
        - Has allergy tags: -1.0 (disqualifier, but we return 0.0)
        - No preferences: 0.5 (neutral)
        """
        # Check for allergies first (disqualifier)
        if user_allergies and dish_dietary_tags:
            # In a real system, you'd check if dish tags conflict with allergies
            # For MVP, we assume dietary tags are positive (vegetarian, vegan, etc.)
            # and allergies are tracked separately
            pass
        
        if not user_preferred_tags:
            return 0.5  # Neutral if no preferences
        
        if not dish_dietary_tags:
            return 0.3  # Dish has no dietary tags, slight penalty
        
        # Count matches
        matches = len(set(dish_dietary_tags) & set(user_preferred_tags))
        if matches == 0:
            return 0.3  # No match
        elif matches == 1:
            return 0.7
        elif matches >= 2:
            return 1.0
        
        return 0.5
    
    def _score_past_interactions(
        self,
        dish_id: Optional[uuid.UUID],
        user_interactions: Dict[uuid.UUID, Dict[str, int]],
    ) -> float:
        """
        Score based on past interactions (0.0 to 1.0).
        
        Scoring:
        - Reservation/Order: +0.5 per interaction (max 1.0)
        - Click/View: +0.2 per interaction (max 0.6)
        - Favorite: +0.3 per interaction (max 0.9)
        - Review: +0.4 per interaction (max 1.0)
        - Combined max: 1.0
        """
        if not dish_id or dish_id not in user_interactions:
            return 0.0
        
        interactions = user_interactions[dish_id]
        score = 0.0
        
        # Weight different interaction types
        reservation_count = interactions.get("reservation", 0) + interactions.get("order", 0)
        click_count = interactions.get("click", 0) + interactions.get("view", 0)
        favorite_count = interactions.get("favorite", 0)
        review_count = interactions.get("review", 0)
        
        # Calculate weighted score
        score += min(reservation_count * 0.5, 1.0)
        score += min(click_count * 0.2, 0.6)
        score += min(favorite_count * 0.3, 0.9)
        score += min(review_count * 0.4, 1.0)
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _score_dish_rating(
        self,
        dish_rating: Optional[float],
    ) -> float:
        """
        Score based on dish rating (0.0 to 1.0).
        
        Scoring:
        - 5.0 stars: 1.0
        - 4.0 stars: 0.8
        - 3.0 stars: 0.6
        - 2.0 stars: 0.4
        - 1.0 stars: 0.2
        - No rating: 0.5 (neutral)
        """
        if dish_rating is None:
            return 0.5  # Neutral if no rating
        
        # Normalize 1-5 scale to 0-1
        return (dish_rating - 1.0) / 4.0


# Default engine instance
default_engine = RecommendationEngine()

