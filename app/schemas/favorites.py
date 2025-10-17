from pydantic import BaseModel
from typing import Optional, List

class GenreInfo(BaseModel):
    id: str
    name: str

class FavoriteContentItem(BaseModel):
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
    favorited_at: str

class FavoritesContentResponse(BaseModel):
    movies: List[FavoriteContentItem]
    tv_shows: List[FavoriteContentItem]
    total_movies: int
    total_tv_shows: int
    total_favorites: int
