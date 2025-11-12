from __future__ import annotations

from typing import List

from pydantic import BaseModel

from app.schemas.dish import DishOut


class AISuggestionsResponse(BaseModel):
    strategy: str
    dishes: List[DishOut]
