"""
Centralized response messages for the application.
All error messages and success messages are defined here for consistency.
"""

# Authentication Messages
EMAIL_EXISTS = "Email already exists"
USERNAME_EXISTS = "Username taken"
INVALID_CREDENTIALS = "Invalid credentials"
ACCOUNT_DEACTIVATED = "Account deactivated"
INVALID_REFRESH_TOKEN = "Invalid token"
CURRENT_PASSWORD_INCORRECT = "Wrong password"
PASSWORD_CHANGED_SUCCESS = "Password changed"
PASSWORD_RESET_SENT = "Reset sent"
PASSWORD_RESET_OTP_SENT = "OTP sent"
ACCOUNT_NOT_FOUND = "Account not found"
PASSWORD_RESET_SUCCESS = "Password reset"
PASSWORD_RESET_TOKEN_INVALID = "Invalid token"
PASSWORD_RESET_TOKEN_USED = "Token used"
EMAIL_VERIFICATION_SUCCESS = "Email verified"
EMAIL_VERIFICATION_TOKEN_INVALID = "Invalid token"
EMAIL_VERIFICATION_TOKEN_USED = "Token used"
LOGOUT_SUCCESS = "Logged out"
LOGOUT_ALL_SUCCESS = "All logged out"
LOGOUT_NO_TOKENS = "No tokens"
EMAIL_ALREADY_VERIFIED = "Already verified"


# Registration Messages
REGISTRATION_SUCCESS = "Registration successful"
REGISTRATION_EMAIL_SENT = "Code sent"
OTP_INVALID = "Invalid code"
OTP_VERIFICATION_SUCCESS = "Email verified"
OTP_VERIFICATION_FAILED = "Verification failed"
EMAIL_NOT_VERIFIED = "Email not verified"
OTP_EXPIRED = "Code expired"
OTP_ALREADY_USED = "Code used"
OTP_INVALID_OR_EXPIRED = "Invalid code"
OTP_RESEND_SUCCESS = "Code resent"

# Google OAuth Messages
GOOGLE_OAUTH_SUCCESS = "Google authenticated"
GOOGLE_OAUTH_INVALID_TOKEN = "Invalid token"
GOOGLE_OAUTH_TOKEN_VERIFICATION_FAILED = "Token verification failed"
GOOGLE_OAUTH_EMAIL_NOT_VERIFIED = "Email not verified"
GOOGLE_OAUTH_ACCOUNT_CREATED = "Account created"
GOOGLE_OAUTH_ACCOUNT_LINKED = "Account linked"
GOOGLE_OAUTH_ACCOUNT_EXISTS = "Account exists"
GOOGLE_OAUTH_DISABLED = "Google OAuth is currently disabled"

# User Messages
USER_NOT_FOUND = "User not found"
USER_ALREADY_EXISTS = "User exists"
USER_CREATED_SUCCESS = "User created"
USER_UPDATED_SUCCESS = "User updated"
USER_DELETED_SUCCESS = "User deleted"
PROFILE_UPDATE_SUCCESS = "Profile updated"
AVATAR_UPLOAD_SUCCESS = "Avatar uploaded"
AVATAR_REMOVED_SUCCESS = "Avatar removed"
AVATAR_UPDATE_FAILED = "Upload failed"
INVALID_FILE_TYPE = "Invalid file"
FILE_TOO_LARGE = "File too large"

# Content Messages
CONTENT_NOT_FOUND = "Content not found"
CONTENT_CREATED_SUCCESS = "Content created"
CONTENT_UPDATED_SUCCESS = "Content updated"
CONTENT_DELETED_SUCCESS = "Content deleted"
CONTENT_FEATURED_SUCCESS = "Featured content"
CONTENT_TRENDING_SUCCESS = "Trending content"
CONTENT_LIST_SUCCESS = "Content list"

# Genre Messages
GENRE_NOT_FOUND = "Genre not found"
GENRE_ALREADY_EXISTS = "Genre exists"
GENRE_CREATED_SUCCESS = "Genre created"
GENRE_UPDATED_SUCCESS = "Genre updated"
GENRE_DELETED_SUCCESS = "Genre deleted"
GENRE_LIST_SUCCESS = "Genres retrieved"

# Cast and Crew Messages
CAST_NOT_FOUND = "Cast not found"
CAST_LIST_SUCCESS = "Cast list"
CREW_NOT_FOUND = "Crew not found"
CREW_LIST_SUCCESS = "Crew list"
CAST_CREW_SUCCESS = "Cast and crew"

# Review Messages
REVIEW_NOT_FOUND = "Review not found"
REVIEW_LIST_SUCCESS = "Reviews retrieved"
REVIEW_CREATED_SUCCESS = "Review created"
REVIEW_UPDATED_SUCCESS = "Review updated"
REVIEW_DELETED_SUCCESS = "Review deleted"
REVIEW_STATS_SUCCESS = "Review statistics"
REVIEW_ALREADY_EXISTS = "Review exists"
REVIEW_VOTE_SUCCESS = "Vote recorded"
REVIEW_VOTE_UPDATED = "Vote updated"
REVIEW_VOTE_REMOVED = "Vote removed"
REVIEW_PERMISSION_DENIED = "Permission denied"
REVIEW_INVALID_RATING = "Invalid rating"
REVIEW_CONTENT_NOT_FOUND = "Content not found"
REVIEW_USER_NOT_FOUND = "User not found"

# General Messages
INVALID_PAGINATION = "Invalid pagination"
INVALID_FILTERS = "Invalid filters"
INVALID_SORT_PARAMS = "Invalid sort"

# Token Messages
TOKEN_EXPIRED = "Token expired"
TOKEN_INVALID = "Invalid token"
TOKEN_REVOKED = "Token revoked"
TOKEN_CREATED_SUCCESS = "Token created"

# Validation Messages
INVALID_EMAIL_FORMAT = "Invalid email"
INVALID_PASSWORD_STRENGTH = "Weak password"
PASSWORDS_DO_NOT_MATCH = "Passwords mismatch"
REQUIRED_FIELD_MISSING = "Field missing"

# Content Discovery Messages
CONTENT_DISCOVERY_SUCCESS = "Discovery data"
CONTENT_DISCOVERY_ERROR = "Discovery error"
FEATURED_CONTENT_SUCCESS = "Featured content"
TRENDING_CONTENT_SUCCESS = "Trending content"
MOST_REVIEWED_SUCCESS = "Most reviewed"
NEW_RELEASES_SUCCESS = "New releases"

# Streaming Channel Messages
STREAMING_CHANNEL_LIST_SUCCESS = "Channels retrieved"
STREAMING_CHANNEL_DETAIL_SUCCESS = "Channel details"
STREAMING_CHANNEL_CREATED_SUCCESS = "Channel created"
STREAMING_CHANNEL_UPDATED_SUCCESS = "Channel updated"
STREAMING_CHANNEL_DELETED_SUCCESS = "Channel deleted"
STREAMING_CHANNEL_NOT_FOUND = "Channel not found"
STREAMING_CHANNEL_ALREADY_EXISTS = "Channel exists"
STREAMING_CHANNEL_INVALID_URL = "Invalid URL"
STREAMING_CHANNEL_STATS_SUCCESS = "Channel statistics"

# Admin Messages
ADMIN_ACCESS_DENIED = "Access denied"
ADMIN_INSUFFICIENT_PERMISSIONS = "Insufficient permissions"
ADMIN_OPERATION_SUCCESS = "Operation completed"
ADMIN_BULK_OPERATION_SUCCESS = "Bulk operation"

# Streaming Channel Admin Messages
STREAMING_CHANNEL_CREATED = "Channel created"
STREAMING_CHANNEL_UPDATED = "Channel updated"
STREAMING_CHANNEL_DELETED = "Channel deleted"
STREAMING_CHANNEL_NOT_FOUND = "Channel not found"
STREAMING_CHANNEL_ALREADY_EXISTS = "Channel exists"
STREAMING_CHANNEL_TEST_SUCCESS = "Test successful"
STREAMING_CHANNEL_TEST_FAILED = "Test failed"

# Genre Admin Messages
GENRE_CREATED = "Genre created"
GENRE_UPDATED = "Genre updated"
GENRE_DELETED = "Genre deleted"
GENRE_NOT_FOUND = "Genre not found"
GENRE_ALREADY_EXISTS = "Genre exists"
GENRE_FEATURED = "Genre featured"
GENRE_UNFEATURED = "Genre unfeatured"

# Content Admin Messages
CONTENT_CREATED = "Content created"
CONTENT_UPDATED = "Content updated"
CONTENT_DELETED = "Content deleted"
CONTENT_NOT_FOUND = "Content not found"
CONTENT_PUBLISHED = "Content published"
CONTENT_UNPUBLISHED = "Content unpublished"
CONTENT_FEATURED = "Content featured"
CONTENT_UNFEATURED = "Content unfeatured"
CONTENT_TRENDING = "Trending updated"
CONTENT_ALREADY_EXISTS = "Content exists"

# People Admin Messages
PERSON_CREATED = "Person created"
PERSON_UPDATED = "Person updated"
PERSON_DELETED = "Person deleted"
PERSON_NOT_FOUND = "Person not found"
PERSON_ALREADY_EXISTS = "Person exists"
PERSON_FEATURED = "Person featured"
PERSON_UNFEATURED = "Person unfeatured"
PERSON_VERIFIED = "Person verified"
PERSON_UNVERIFIED = "Person unverified"

# Season Admin Messages
SEASON_CREATED = "Season created"
SEASON_UPDATED = "Season updated"
SEASON_DELETED = "Season deleted"
SEASON_NOT_FOUND = "Season not found"
SEASON_ALREADY_EXISTS = "Season exists"

# Episode Admin Messages
EPISODE_CREATED = "Episode created"
EPISODE_UPDATED = "Episode updated"
EPISODE_DELETED = "Episode deleted"
EPISODE_NOT_FOUND = "Episode not found"
EPISODE_ALREADY_EXISTS = "Episode exists"

# File Admin Messages
FILE_UPLOADED = "File uploaded"
FILE_DELETED = "File deleted"
FILE_NOT_FOUND = "File not found"
FILE_PROCESSING_STARTED = "Processing started"
FILE_PROCESSING_FAILED = "Processing failed"
FILE_INVALID_FORMAT = "Invalid format"

# User Admin Messages
USER_CREATED = "User created"
USER_UPDATED = "User updated"
USER_DELETED = "User deleted"
USER_NOT_FOUND = "User not found"
USER_ALREADY_EXISTS = "User exists"
USER_SUSPENDED = "User suspended"
USER_ACTIVATED = "User activated"
USER_BANNED = "User banned"
USER_UNBANNED = "User unbanned"
USER_ROLE_UPDATED = "Role updated"
USER_STATUS_UPDATED = "Status updated"

# Review Admin Messages
REVIEW_UPDATED = "Review updated"
REVIEW_DELETED = "Review deleted"
REVIEW_FEATURED = "Review featured"
REVIEW_HIDDEN = "Review hidden"
REVIEW_APPROVED = "Review approved"

# Security Messages
SECURITY_ERROR_MISSING_HEADERS = "Missing headers"
SECURITY_ERROR_INVALID_DEVICE_TYPE = "Invalid device"
SECURITY_ERROR_INVALID_APP_VERSION = "Invalid version"
SECURITY_ERROR_HEADER_VALIDATION = "Header validation"

# Monetization Messages
CAMPAIGN_CREATED = "Campaign created successfully"
CAMPAIGN_UPDATED = "Campaign updated successfully"
CAMPAIGN_DELETED = "Campaign deleted successfully"
CAMPAIGN_NOT_FOUND = "Campaign not found"
CAMPAIGN_ALREADY_EXISTS = "Campaign with this title already exists"
CAMPAIGN_STAT_CREATED = "Campaign stat created successfully"
CAMPAIGN_STAT_NOT_FOUND = "Campaign stat not found"
ACTIVITY_CREATED = "Activity log created successfully"
ACTIVITY_NOT_FOUND = "Activity not found"
PERFORMANCE_SUMMARY_SUCCESS = "Performance summary retrieved successfully"
PERFORMANCE_TRENDS_SUCCESS = "Performance trends retrieved successfully"
ENGAGEMENT_BY_TYPE_SUCCESS = "Engagement by type retrieved successfully"
SUBSCRIBER_SEGMENTATION_SUCCESS = "Subscriber segmentation retrieved successfully"

# General Messages
SUCCESS = "Success"
ERROR = "Error"
UNAUTHORIZED = "Unauthorized"
FORBIDDEN = "Forbidden"
NOT_FOUND = "Not found"
BAD_REQUEST = "Bad request"
INTERNAL_SERVER_ERROR = "Server error"
