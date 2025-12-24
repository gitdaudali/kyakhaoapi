"""Repository layer for data access abstraction."""

from app.repositories.base import BaseRepository
from app.repositories.dish_repository import DishRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.cuisine_repository import CuisineRepository

__all__ = [
    "BaseRepository",
    "DishRepository",
    "RestaurantRepository",
    "CuisineRepository",
]

