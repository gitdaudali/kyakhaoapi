"""
ML Pipeline for Kyakhao Recommendation System.

This module implements the ML training and inference pipeline using Scikit-learn.
Designed for offline training and real-time inference.
"""
from __future__ import annotations

import pickle
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.food import Dish, Cuisine
from app.models.recommendation import UserInteraction, UserPreference
from app.models.user import User


class FeatureExtractor:
    """Extract features from database for ML training."""
    
    def __init__(self):
        self.spice_encoder = LabelEncoder()
        self.spice_encoder.fit(["Mild", "Medium", "Spicy", "Extra Spicy"])
        
        self.cuisine_encoder = LabelEncoder()
    
    async def extract_user_features(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> Dict:
        """Extract user features."""
        # Get user preferences
        stmt = select(UserPreference).where(UserPreference.user_id == user_id)
        result = await db.execute(stmt)
        pref = result.scalar_one_or_none()
        
        # Get user
        user_stmt = select(User).where(User.id == user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        # Get favorite cuisines count
        from app.models.food import UserCuisineAssociation
        cuisine_stmt = (
            select(func.count())
            .select_from(UserCuisineAssociation)
            .where(UserCuisineAssociation.c.user_id == user_id)
        )
        cuisine_result = await db.execute(cuisine_stmt)
        num_favorite_cuisines = cuisine_result.scalar_one() or 0
        
        # Get total interactions
        interaction_stmt = (
            select(func.count())
            .select_from(UserInteraction)
            .where(UserInteraction.user_id == user_id)
        )
        interaction_result = await db.execute(interaction_stmt)
        total_interactions = interaction_result.scalar_one() or 0
        
        # Calculate average budget
        avg_budget = None
        if pref and pref.min_budget and pref.max_budget:
            avg_budget = (float(pref.min_budget) + float(pref.max_budget)) / 2.0
        
        # Encode spice level
        spice_level = pref.preferred_spice_level if pref else user.spice_level_preference if user else None
        spice_encoded = 0
        if spice_level:
            try:
                spice_encoded = self.spice_encoder.transform([spice_level])[0]
            except ValueError:
                spice_encoded = 0
        
        return {
            'spice_level_encoded': spice_encoded,
            'avg_budget': avg_budget or 0.0,
            'num_favorite_cuisines': num_favorite_cuisines,
            'total_interactions': total_interactions,
        }
    
    async def extract_dish_features(
        self,
        dish_id: uuid.UUID,
        db: AsyncSession,
    ) -> Dict:
        """Extract dish features."""
        stmt = select(Dish).where(Dish.id == dish_id)
        result = await db.execute(stmt)
        dish = result.scalar_one_or_none()
        
        if not dish:
            return {}
        
        # Encode spice level
        spice_encoded = 0
        if dish.spice_level:
            try:
                spice_encoded = self.spice_encoder.transform([dish.spice_level])[0]
            except ValueError:
                spice_encoded = 0
        
        # Encode cuisine (need to fit encoder first)
        cuisine_encoded = 0  # Will be set during training
        
        return {
            'price': float(dish.price) if dish.price else 0.0,
            'rating': float(dish.rating) if dish.rating else 0.0,
            'spice_level_encoded': spice_encoded,
            'cuisine_id': str(dish.cuisine_id),
            'is_featured': 1 if dish.is_featured else 0,
        }
    
    async def extract_match_features(
        self,
        user_features: Dict,
        dish_features: Dict,
        user_favorite_cuisines: List[uuid.UUID],
        dish_cuisine_id: uuid.UUID,
        db: AsyncSession,
    ) -> Dict:
        """Extract match features."""
        # Spice level match
        spice_match = 0.0
        if user_features.get('spice_level_encoded') is not None and dish_features.get('spice_level_encoded') is not None:
            diff = abs(user_features['spice_level_encoded'] - dish_features['spice_level_encoded'])
            if diff == 0:
                spice_match = 1.0
            elif diff == 1:
                spice_match = 0.7
            elif diff == 2:
                spice_match = 0.4
            else:
                spice_match = 0.1
        
        # Cuisine match
        cuisine_match = 1.0 if dish_cuisine_id in user_favorite_cuisines else 0.0
        
        # Budget match
        budget_match = 0.5  # Default neutral
        avg_budget = user_features.get('avg_budget', 0)
        dish_price = dish_features.get('price', 0)
        
        if avg_budget > 0 and dish_price > 0:
            if dish_price <= avg_budget * 1.2:  # Within 20% of budget
                budget_match = 1.0
            elif dish_price <= avg_budget * 1.5:
                budget_match = 0.5
            else:
                budget_match = 0.0
        
        return {
            'spice_level_match': spice_match,
            'cuisine_match': cuisine_match,
            'budget_match': budget_match,
        }
    
    async def extract_interaction_features(
        self,
        user_id: uuid.UUID,
        dish_id: uuid.UUID,
        db: AsyncSession,
    ) -> Dict:
        """Extract interaction features."""
        stmt = (
            select(
                UserInteraction.interaction_type,
                func.count(UserInteraction.id).label('count')
            )
            .where(
                UserInteraction.user_id == user_id,
                UserInteraction.dish_id == dish_id,
            )
            .group_by(UserInteraction.interaction_type)
        )
        result = await db.execute(stmt)
        
        interactions = {}
        for row in result.all():
            interactions[row[0]] = row[1]
        
        return {
            'clicks': interactions.get('click', 0),
            'views': interactions.get('view', 0),
            'orders': interactions.get('order', 0),
            'favorites': interactions.get('favorite', 0),
            'reservations': interactions.get('reservation', 0),
        }


class MLModelTrainer:
    """Train ML models for recommendation."""
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Args:
            model_type: 'random_forest' or 'gradient_boosting'
        """
        self.model_type = model_type
        self.model = None
        self.feature_extractor = FeatureExtractor()
    
    def _create_model(self):
        """Create model based on type."""
        if self.model_type == 'random_forest':
            return RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1,
            )
        elif self.model_type == 'gradient_boosting':
            return GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42,
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    async def prepare_training_data(
        self,
        db: AsyncSession,
        days_back: int = 30,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from database.
        
        Args:
            db: Database session
            days_back: How many days of data to use
            
        Returns:
            Tuple of (X features, y targets)
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get all user-dish pairs with interactions
        stmt = (
            select(
                UserInteraction.user_id,
                UserInteraction.dish_id,
                UserInteraction.interaction_type,
                UserInteraction.interaction_timestamp,
            )
            .where(UserInteraction.interaction_timestamp >= cutoff_date)
        )
        result = await db.execute(stmt)
        interactions = result.all()
        
        # Build feature matrix
        X = []
        y = []
        
        processed_pairs = set()
        
        for interaction in interactions:
            user_id = interaction.user_id
            dish_id = interaction.dish_id
            pair_key = (user_id, dish_id)
            
            if pair_key in processed_pairs:
                continue
            
            processed_pairs.add(pair_key)
            
            # Extract features
            user_features = await self.feature_extractor.extract_user_features(user_id, db)
            dish_features = await self.feature_extractor.extract_dish_features(dish_id, db)
            
            # Get favorite cuisines
            from app.models.food import UserCuisineAssociation
            cuisine_stmt = (
                select(UserCuisineAssociation.c.cuisine_id)
                .where(UserCuisineAssociation.c.user_id == user_id)
            )
            cuisine_result = await db.execute(cuisine_stmt)
            favorite_cuisines = [row[0] for row in cuisine_result.all()]
            
            match_features = await self.feature_extractor.extract_match_features(
                user_features,
                dish_features,
                favorite_cuisines,
                dish_features.get('cuisine_id'),
                db,
            )
            
            interaction_features = await self.feature_extractor.extract_interaction_features(
                user_id, dish_id, db
            )
            
            # Combine features
            feature_vector = [
                user_features['spice_level_encoded'],
                user_features['avg_budget'],
                user_features['num_favorite_cuisines'],
                user_features['total_interactions'],
                dish_features['price'],
                dish_features['rating'],
                dish_features['spice_level_encoded'],
                dish_features['is_featured'],
                match_features['spice_level_match'],
                match_features['cuisine_match'],
                match_features['budget_match'],
                interaction_features['clicks'],
                interaction_features['views'],
                interaction_features['orders'],
                interaction_features['favorites'],
            ]
            
            X.append(feature_vector)
            
            # Target: Did user interact positively? (order, favorite, reservation)
            positive_interactions = ['order', 'favorite', 'reservation']
            has_positive = any(
                i.interaction_type in positive_interactions
                for i in interactions
                if i.user_id == user_id and i.dish_id == dish_id
            )
            y.append(1 if has_positive else 0)
        
        return np.array(X), np.array(y)
    
    async def train(
        self,
        db: AsyncSession,
        model_save_path: Optional[str] = None,
    ) -> Dict:
        """
        Train the ML model.
        
        Returns:
            Dictionary with training metrics
        """
        # Prepare data
        X, y = await self.prepare_training_data(db)
        
        if len(X) == 0:
            raise ValueError("No training data available. Need user interactions.")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model = self._create_model()
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0.0,
            'train_size': len(X_train),
            'test_size': len(X_test),
        }
        
        # Save model
        if model_save_path:
            Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(model_save_path, 'wb') as f:
                pickle.dump(self.model, f)
            metrics['model_path'] = model_save_path
        
        return metrics


class MLRecommendationEngine:
    """ML-based recommendation engine for real-time inference."""
    
    def __init__(self, model_path: str):
        """
        Args:
            model_path: Path to saved model file
        """
        self.model_path = model_path
        self.model = self._load_model()
        self.feature_extractor = FeatureExtractor()
    
    def _load_model(self):
        """Load trained model."""
        with open(self.model_path, 'rb') as f:
            return pickle.load(f)
    
    async def predict_score(
        self,
        user_id: uuid.UUID,
        dish_id: uuid.UUID,
        db: AsyncSession,
    ) -> float:
        """
        Predict match score for a user-dish pair.
        
        Returns:
            Score from 0.0 to 100.0
        """
        # Extract features
        user_features = await self.feature_extractor.extract_user_features(user_id, db)
        dish_features = await self.feature_extractor.extract_dish_features(dish_id, db)
        
        # Get favorite cuisines
        from app.models.food import UserCuisineAssociation
        cuisine_stmt = (
            select(UserCuisineAssociation.c.cuisine_id)
            .where(UserCuisineAssociation.c.user_id == user_id)
        )
        cuisine_result = await db.execute(cuisine_stmt)
        favorite_cuisines = [row[0] for row in cuisine_result.all()]
        
        match_features = await self.feature_extractor.extract_match_features(
            user_features,
            dish_features,
            favorite_cuisines,
            uuid.UUID(dish_features.get('cuisine_id', '00000000-0000-0000-0000-000000000000')),
            db,
        )
        
        interaction_features = await self.feature_extractor.extract_interaction_features(
            user_id, dish_id, db
        )
        
        # Build feature vector (same order as training)
        feature_vector = np.array([[
            user_features['spice_level_encoded'],
            user_features['avg_budget'],
            user_features['num_favorite_cuisines'],
            user_features['total_interactions'],
            dish_features['price'],
            dish_features['rating'],
            dish_features['spice_level_encoded'],
            dish_features['is_featured'],
            match_features['spice_level_match'],
            match_features['cuisine_match'],
            match_features['budget_match'],
            interaction_features['clicks'],
            interaction_features['views'],
            interaction_features['orders'],
            interaction_features['favorites'],
        ]])
        
        # Predict probability
        probability = self.model.predict_proba(feature_vector)[0][1]
        
        # Convert to 0-100 score
        return float(probability * 100)


# Example usage:
# trainer = MLModelTrainer(model_type='random_forest')
# metrics = await trainer.train(db, model_save_path='app/ai/models/recommendation_model.pkl')
# 
# engine = MLRecommendationEngine('app/ai/models/recommendation_model.pkl')
# score = await engine.predict_score(user_id, dish_id, db)

