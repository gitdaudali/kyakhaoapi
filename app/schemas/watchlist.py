from pydantic import BaseModel
from typing import Optional, List

class GenreInfo(BaseModel):
    id: str
    name: str

class WatchlistContentItem(BaseModel):
    id: str
    title: str
    slug: str
    description: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    content_type: str
    release_date: Optional[str] = None
    platform_rating: Optional[float] = None
    platform_votes: int = 0
    genres: List[GenreInfo] = []
    added_at: str

class WatchlistResponse(BaseModel):
    movies: List[WatchlistContentItem]
    tv_shows: List[WatchlistContentItem]
    total_movies: int
    total_tv_shows: int
    total_watchlist: int

class WatchlistActionResponse(BaseModel):
    message: str
    status: str
