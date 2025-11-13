from __future__ import annotations

from typing import List

from pydantic import BaseModel

from app.schemas.cuisine import CuisineOut
from app.schemas.dish import DishOut
from app.schemas.restaurant import RestaurantOut


class SearchResponse(BaseModel):
    query: str
    dishes: List[DishOut]
    restaurants: List[RestaurantOut]
    cuisines: List[CuisineOut]
