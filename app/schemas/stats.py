from pydantic import BaseModel
from typing import Optional

class StatsResponse(BaseModel):
    count: int
    period: str  # "this_month", "total", etc.
    percentage_change: Optional[float] = None
    message: str

class HoursWatchedResponse(BaseModel):
    hours: float
    period: str
    percentage_change: Optional[float] = None
    message: str

class MoviesCompletedResponse(BaseModel):
    movies_count: int
    period: str
    percentage_change: Optional[float] = None
    message: str

class TVEpisodesResponse(BaseModel):
    episodes_count: int
    period: str
    percentage_change: Optional[float] = None
    message: str

class FavoritesResponse(BaseModel):
    favorites_count: int
    period: str
    percentage_change: Optional[float] = None
    message: str
