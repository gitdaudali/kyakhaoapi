import uuid
from datetime import datetime
from typing import List, Optional
from app.schemas.recommendations import RecommendationItem, RecommendationResponse, RecommendationQueryParams


# Hardcoded movie data for recommendations
HARDCODED_MOVIES = [
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "The Dark Knight",
        "slug": "the-dark-knight",
        "content_type": "movie",
        "poster_url": "https://example.com/posters/dark-knight.jpg",
        "backdrop_url": "https://example.com/backdrops/dark-knight.jpg",
        "release_date": "2008-07-18",
        "runtime": 152,
        "platform_rating": 4.8,
        "imdb_rating": 9.0,
        "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "genres": ["Action", "Crime", "Drama", "Thriller"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440002",
        "title": "Inception",
        "slug": "inception",
        "content_type": "movie",
        "poster_url": "https://example.com/posters/inception.jpg",
        "backdrop_url": "https://example.com/backdrops/inception.jpg",
        "release_date": "2010-07-16",
        "runtime": 148,
        "platform_rating": 4.7,
        "imdb_rating": 8.8,
        "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "genres": ["Action", "Sci-Fi", "Thriller"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440003",
        "title": "Pulp Fiction",
        "slug": "pulp-fiction",
        "content_type": "movie",
        "poster_url": "https://example.com/posters/pulp-fiction.jpg",
        "backdrop_url": "https://example.com/backdrops/pulp-fiction.jpg",
        "release_date": "1994-10-14",
        "runtime": 154,
        "platform_rating": 4.9,
        "imdb_rating": 8.9,
        "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
        "genres": ["Crime", "Drama"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440004",
        "title": "The Shawshank Redemption",
        "slug": "the-shawshank-redemption",
        "content_type": "movie",
        "poster_url": "https://example.com/posters/shawshank.jpg",
        "backdrop_url": "https://example.com/backdrops/shawshank.jpg",
        "release_date": "1994-09-23",
        "runtime": 142,
        "platform_rating": 4.9,
        "imdb_rating": 9.3,
        "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "genres": ["Drama"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440005",
        "title": "The Godfather",
        "slug": "the-godfather",
        "content_type": "movie",
        "poster_url": "https://example.com/posters/godfather.jpg",
        "backdrop_url": "https://example.com/backdrops/godfather.jpg",
        "release_date": "1972-03-24",
        "runtime": 175,
        "platform_rating": 4.9,
        "imdb_rating": 9.2,
        "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "genres": ["Crime", "Drama"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440006",
        "title": "Interstellar",
        "slug": "interstellar",
        "content_type": "movie",
        "poster_url": "https://example.com/posters/interstellar.jpg",
        "backdrop_url": "https://example.com/backdrops/interstellar.jpg",
        "release_date": "2014-11-07",
        "runtime": 169,
        "platform_rating": 4.6,
        "imdb_rating": 8.6,
        "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        "genres": ["Adventure", "Drama", "Sci-Fi"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440007",
        "title": "The Matrix",
        "slug": "the-matrix",
        "content_type": "movie",
        "poster_url": "https://example.com/posters/matrix.jpg",
        "backdrop_url": "https://example.com/backdrops/matrix.jpg",
        "release_date": "1999-03-31",
        "runtime": 136,
        "platform_rating": 4.7,
        "imdb_rating": 8.7,
        "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "genres": ["Action", "Sci-Fi"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440008",
        "title": "Forrest Gump",
        "slug": "forrest-gump",
        "content_type": "movie",
        "poster_url": "https://example.com/posters/forrest-gump.jpg",
        "backdrop_url": "https://example.com/backdrops/forrest-gump.jpg",
        "release_date": "1994-07-06",
        "runtime": 142,
        "platform_rating": 4.8,
        "imdb_rating": 8.8,
        "description": "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.",
        "genres": ["Drama", "Romance"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440009",
        "title": "The Lord of the Rings: The Fellowship of the Ring",
        "slug": "lotr-fellowship",
        "content_type": "movie",
        "poster_url": "https://example.com/posters/lotr-fellowship.jpg",
        "backdrop_url": "https://example.com/backdrops/lotr-fellowship.jpg",
        "release_date": "2001-12-19",
        "runtime": 178,
        "platform_rating": 4.8,
        "imdb_rating": 8.8,
        "description": "A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth from the Dark Lord Sauron.",
        "genres": ["Action", "Adventure", "Drama", "Fantasy"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440010",
        "title": "Fight Club",
        "slug": "fight-club",
        "content_type": "movie",
        "poster_url": "https://example.com/posters/fight-club.jpg",
        "backdrop_url": "https://example.com/backdrops/fight-club.jpg",
        "release_date": "1999-10-15",
        "runtime": 139,
        "platform_rating": 4.6,
        "imdb_rating": 8.8,
        "description": "An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into much more.",
        "genres": ["Drama"]
    }
]

# TV Series data
HARDCODED_TV_SERIES = [
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440011",
        "title": "Breaking Bad",
        "slug": "breaking-bad",
        "content_type": "tv_series",
        "poster_url": "https://example.com/posters/breaking-bad.jpg",
        "backdrop_url": "https://example.com/backdrops/breaking-bad.jpg",
        "release_date": "2008-01-20",
        "runtime": 45,
        "platform_rating": 4.9,
        "imdb_rating": 9.5,
        "description": "A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family's future.",
        "genres": ["Crime", "Drama", "Thriller"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440012",
        "title": "Game of Thrones",
        "slug": "game-of-thrones",
        "content_type": "tv_series",
        "poster_url": "https://example.com/posters/got.jpg",
        "backdrop_url": "https://example.com/backdrops/got.jpg",
        "release_date": "2011-04-17",
        "runtime": 57,
        "platform_rating": 4.7,
        "imdb_rating": 9.3,
        "description": "Nine noble families fight for control over the lands of Westeros, while an ancient enemy returns after being dormant for millennia.",
        "genres": ["Action", "Adventure", "Drama", "Fantasy"]
    },
    {
        "content_id": "550e8400-e29b-41d4-a716-446655440013",
        "title": "Stranger Things",
        "slug": "stranger-things",
        "content_type": "tv_series",
        "poster_url": "https://example.com/posters/stranger-things.jpg",
        "backdrop_url": "https://example.com/backdrops/stranger-things.jpg",
        "release_date": "2016-07-15",
        "runtime": 50,
        "platform_rating": 4.6,
        "imdb_rating": 8.7,
        "description": "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces, and one strange little girl.",
        "genres": ["Drama", "Fantasy", "Horror", "Mystery", "Sci-Fi", "Thriller"]
    }
]


def get_hardcoded_recommendations(
    user_id: str,
    query_params: RecommendationQueryParams
) -> RecommendationResponse:
    """
    Generate hardcoded recommendations based on query parameters.
    This is a placeholder implementation that will be replaced with AI/ML models in the future.
    """
    
    # Combine all content
    all_content = HARDCODED_MOVIES + HARDCODED_TV_SERIES
    
    # Apply filters
    filtered_content = all_content
    
    # Filter by content type
    if query_params.content_type:
        filtered_content = [
            item for item in filtered_content 
            if item["content_type"] == query_params.content_type
        ]
    
    # Filter by genre
    if query_params.genre:
        filtered_content = [
            item for item in filtered_content 
            if query_params.genre.lower() in [g.lower() for g in item["genres"]]
        ]
    
    # Filter by minimum rating
    if query_params.min_rating:
        filtered_content = [
            item for item in filtered_content 
            if item["platform_rating"] and item["platform_rating"] >= query_params.min_rating
        ]
    
    # Filter by maximum runtime
    if query_params.max_runtime:
        filtered_content = [
            item for item in filtered_content 
            if item["runtime"] and item["runtime"] <= query_params.max_runtime
        ]
    
    # Sort by rating (highest first) and take the requested limit
    filtered_content.sort(key=lambda x: x["platform_rating"] or 0, reverse=True)
    selected_content = filtered_content[:query_params.limit]
    
    # Convert to RecommendationItem objects
    recommendations = []
    for i, content in enumerate(selected_content):
        # Generate recommendation score based on position and rating
        base_score = content["platform_rating"] / 5.0 if content["platform_rating"] else 0.5
        position_bonus = (len(selected_content) - i) / len(selected_content) * 0.2
        recommendation_score = min(1.0, base_score + position_bonus)
        
        # Generate recommendation reason
        if content["platform_rating"] and content["platform_rating"] >= 4.5:
            reason = f"Highly rated {content['content_type']} with {content['platform_rating']}/5.0 stars"
        elif content["imdb_rating"] and content["imdb_rating"] >= 8.5:
            reason = f"Critically acclaimed {content['content_type']} with {content['imdb_rating']}/10 IMDB rating"
        else:
            reason = f"Popular {content['content_type']} in your preferred genres"
        
        recommendation = RecommendationItem(
            content_id=uuid.UUID(content["content_id"]),
            title=content["title"],
            slug=content["slug"],
            content_type=content["content_type"],
            poster_url=content["poster_url"],
            backdrop_url=content["backdrop_url"],
            release_date=content["release_date"],
            runtime=content["runtime"],
            platform_rating=content["platform_rating"],
            imdb_rating=content["imdb_rating"],
            description=content["description"],
            genres=content["genres"],
            recommendation_score=recommendation_score,
            recommendation_reason=reason
        )
        recommendations.append(recommendation)
    
    return RecommendationResponse(
        user_id=uuid.UUID(user_id),
        recommendations=recommendations,
        total_recommendations=len(recommendations),
        recommendation_type="hardcoded",
        generated_at=datetime.utcnow().isoformat(),
        message="Recommendations generated successfully"
    )


def get_trending_recommendations(user_id: str, limit: int = 10) -> RecommendationResponse:
    """
    Get trending content recommendations (hardcoded for now).
    """
    # For trending, we'll return the highest rated content
    trending_content = sorted(
        HARDCODED_MOVIES + HARDCODED_TV_SERIES,
        key=lambda x: x["platform_rating"] or 0,
        reverse=True
    )[:limit]
    
    recommendations = []
    for i, content in enumerate(trending_content):
        recommendation_score = 0.9 - (i * 0.05)  # Decreasing score for lower positions
        
        recommendation = RecommendationItem(
            content_id=uuid.UUID(content["content_id"]),
            title=content["title"],
            slug=content["slug"],
            content_type=content["content_type"],
            poster_url=content["poster_url"],
            backdrop_url=content["backdrop_url"],
            release_date=content["release_date"],
            runtime=content["runtime"],
            platform_rating=content["platform_rating"],
            imdb_rating=content["imdb_rating"],
            description=content["description"],
            genres=content["genres"],
            recommendation_score=recommendation_score,
            recommendation_reason="Trending content with high ratings"
        )
        recommendations.append(recommendation)
    
    return RecommendationResponse(
        user_id=uuid.UUID(user_id),
        recommendations=recommendations,
        total_recommendations=len(recommendations),
        recommendation_type="trending",
        generated_at=datetime.utcnow().isoformat(),
        message="Trending recommendations generated successfully"
    )


def get_similar_content_recommendations(
    content_id: str, 
    user_id: str, 
    limit: int = 5
) -> RecommendationResponse:
    """
    Get recommendations based on similar content (hardcoded for now).
    """
    # For now, just return a mix of high-rated content
    similar_content = HARDCODED_MOVIES[:limit]
    
    recommendations = []
    for i, content in enumerate(similar_content):
        recommendation_score = 0.8 - (i * 0.1)
        
        recommendation = RecommendationItem(
            content_id=uuid.UUID(content["content_id"]),
            title=content["title"],
            slug=content["slug"],
            content_type=content["content_type"],
            poster_url=content["poster_url"],
            backdrop_url=content["backdrop_url"],
            release_date=content["release_date"],
            runtime=content["runtime"],
            platform_rating=content["platform_rating"],
            imdb_rating=content["imdb_rating"],
            description=content["description"],
            genres=content["genres"],
            recommendation_score=recommendation_score,
            recommendation_reason="Similar to content you've watched"
        )
        recommendations.append(recommendation)
    
    return RecommendationResponse(
        user_id=uuid.UUID(user_id),
        recommendations=recommendations,
        total_recommendations=len(recommendations),
        recommendation_type="similar",
        generated_at=datetime.utcnow().isoformat(),
        message="Similar content recommendations generated successfully"
    )
