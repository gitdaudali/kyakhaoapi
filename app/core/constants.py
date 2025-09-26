"""
Application constants for content discovery and filtering.
"""
from app.models.content import ContentType

MOVIE_CONTENT_TYPES = {ContentType.MOVIE, ContentType.ANIME}
SERIES_CONTENT_TYPES = {ContentType.TV_SERIES, ContentType.MINI_SERIES}
DOCUMENTARY_CONTENT_TYPES = {ContentType.DOCUMENTARY}


# Content Discovery Constants
MOST_REVIEWED_MIN_RATING = 3.0
MOST_REVIEWED_MIN_REVIEWS = 2

# Pagination Constants
DEFAULT_DISCOVERY_PAGE_SIZE = 10
MAX_DISCOVERY_PAGE_SIZE = 50

# Content Discovery Section Names
FEATURED_SECTION = "featured"
TRENDING_SECTION = "trending"
MOST_REVIEWED_SECTION = "most_reviewed"
NEW_RELEASES_SECTION = "new_releases"

# Content Discovery Section Titles
FEATURED_TITLE = "Featured Content"
TRENDING_TITLE = "Trending Now"
MOST_REVIEWED_TITLE = "Most Reviewed This Month"
NEW_RELEASES_TITLE = "New Releases"

# Content Discovery Section Descriptions
FEATURED_DESCRIPTION = "Handpicked content we think you'll love"
TRENDING_DESCRIPTION = "What's popular right now"
MOST_REVIEWED_DESCRIPTION = "Highly rated content with recent reviews"
NEW_RELEASES_DESCRIPTION = "Fresh content released in the last 30 days"


# CONSTANT API ENDPOINTS
GOOGLE_USER_INFO_API_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
