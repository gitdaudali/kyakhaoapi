"""
Centralized response messages for the application.
All error messages and success messages are defined here for consistency.
"""

# Authentication Messages
EMAIL_EXISTS = "Account already registered and verified"
USERNAME_EXISTS = "Username already taken"
INVALID_CREDENTIALS = "Incorrect email or password"
ACCOUNT_DEACTIVATED = "User account is deactivated"
INVALID_REFRESH_TOKEN = "Invalid refresh token"
CURRENT_PASSWORD_INCORRECT = "Current password is incorrect"
PASSWORD_CHANGED_SUCCESS = "Password changed successfully"
PASSWORD_RESET_SENT = "If the email exists, a password reset OTP has been sent"
PASSWORD_RESET_OTP_SENT = "Password reset OTP sent to your email address"
ACCOUNT_NOT_FOUND = "Account not found"
PASSWORD_RESET_SUCCESS = "Password reset successfully"
PASSWORD_RESET_TOKEN_INVALID = "Invalid or expired reset token"
PASSWORD_RESET_TOKEN_USED = "Reset token has already been used"
EMAIL_VERIFICATION_SUCCESS = "Email verified successfully"
EMAIL_VERIFICATION_TOKEN_INVALID = "Invalid or expired verification token"
EMAIL_VERIFICATION_TOKEN_USED = "Verification token has already been used"
LOGOUT_SUCCESS = "Successfully logged out"
LOGOUT_ALL_SUCCESS = "Successfully logged out from all devices"
LOGOUT_NO_TOKENS = "Logout successful (no tokens to revoke)"
EMAIL_ALREADY_VERIFIED = "Email already verified"


# Registration Messages
REGISTRATION_SUCCESS = (
    "Registration successful. Please check your email for verification code."
)
REGISTRATION_EMAIL_SENT = "Verification code sent to your email address"
OTP_INVALID = "Invalid or expired verification code"
OTP_VERIFICATION_SUCCESS = "Email verified successfully. You can now login."
OTP_VERIFICATION_FAILED = "Verification failed. Please check your code and try again."
EMAIL_NOT_VERIFIED = "Please verify your email address before logging in"
OTP_EXPIRED = "Verification code has expired. Please request a new one."
OTP_ALREADY_USED = "Verification code has already been used"
OTP_INVALID_OR_EXPIRED = "Invalid or expired verification code"
OTP_RESEND_SUCCESS = "New verification code sent to your email address"

# Google OAuth Messages
GOOGLE_OAUTH_SUCCESS = "Successfully authenticated with Google"
GOOGLE_OAUTH_INVALID_TOKEN = "Invalid Google access token"
GOOGLE_OAUTH_TOKEN_VERIFICATION_FAILED = "Failed to verify Google access token"
GOOGLE_OAUTH_EMAIL_NOT_VERIFIED = "Google email is not verified"
GOOGLE_OAUTH_ACCOUNT_CREATED = "Account created successfully with Google"
GOOGLE_OAUTH_ACCOUNT_LINKED = "Google account linked successfully"
GOOGLE_OAUTH_ACCOUNT_EXISTS = "Account already exists with this email"
GOOGLE_OAUTH_DISABLED = "Google OAuth is currently disabled"

# User Messages
USER_NOT_FOUND = "User not found"
USER_ALREADY_EXISTS = "User already exists"
USER_CREATED_SUCCESS = "User created successfully"
USER_UPDATED_SUCCESS = "User updated successfully"
USER_DELETED_SUCCESS = "User deleted successfully"
PROFILE_UPDATE_SUCCESS = "Profile updated successfully"
AVATAR_UPLOAD_SUCCESS = "Avatar uploaded successfully"
AVATAR_REMOVED_SUCCESS = "Avatar removed successfully"
AVATAR_UPDATE_FAILED = "Failed to update avatar"
INVALID_FILE_TYPE = "Invalid file type"
FILE_TOO_LARGE = "File is too large"

# Content Messages
CONTENT_NOT_FOUND = "Content not found"
CONTENT_CREATED_SUCCESS = "Content created successfully"
CONTENT_UPDATED_SUCCESS = "Content updated successfully"
CONTENT_DELETED_SUCCESS = "Content deleted successfully"
CONTENT_FEATURED_SUCCESS = "Featured content retrieved successfully"
CONTENT_TRENDING_SUCCESS = "Trending content retrieved successfully"
CONTENT_LIST_SUCCESS = "Content list retrieved successfully"

# Genre Messages
GENRE_NOT_FOUND = "Genre not found"
GENRE_ALREADY_EXISTS = "Genre already exists"
GENRE_CREATED_SUCCESS = "Genre created successfully"
GENRE_UPDATED_SUCCESS = "Genre updated successfully"
GENRE_DELETED_SUCCESS = "Genre deleted successfully"
GENRE_LIST_SUCCESS = "Genres retrieved successfully"

# Cast and Crew Messages
CAST_NOT_FOUND = "Cast not found"
CAST_LIST_SUCCESS = "Cast list retrieved successfully"
CREW_NOT_FOUND = "Crew not found"
CREW_LIST_SUCCESS = "Crew list retrieved successfully"
CAST_CREW_SUCCESS = "Cast and crew retrieved successfully"

# Review Messages
REVIEW_NOT_FOUND = "Review not found"
REVIEW_LIST_SUCCESS = "Reviews retrieved successfully"
REVIEW_CREATED_SUCCESS = "Review created successfully"
REVIEW_UPDATED_SUCCESS = "Review updated successfully"
REVIEW_DELETED_SUCCESS = "Review deleted successfully"
REVIEW_STATS_SUCCESS = "Review statistics retrieved successfully"
REVIEW_ALREADY_EXISTS = "User already has a review for this content"
REVIEW_VOTE_SUCCESS = "Review vote recorded successfully"
REVIEW_VOTE_UPDATED = "Review vote updated successfully"
REVIEW_VOTE_REMOVED = "Review vote removed successfully"
REVIEW_PERMISSION_DENIED = "You can only modify your own reviews"
REVIEW_INVALID_RATING = "Rating must be between 1.0 and 5.0"
REVIEW_CONTENT_NOT_FOUND = "Content not found"
REVIEW_USER_NOT_FOUND = "User not found"

# General Messages
INVALID_PAGINATION = "Invalid pagination parameters"
INVALID_FILTERS = "Invalid filter parameters"
INVALID_SORT_PARAMS = "Invalid sort parameters"

# Token Messages
TOKEN_EXPIRED = "Token has expired"
TOKEN_INVALID = "Invalid token"
TOKEN_REVOKED = "Token has been revoked"
TOKEN_CREATED_SUCCESS = "Token created successfully"

# Validation Messages
INVALID_EMAIL_FORMAT = "Invalid email format"
INVALID_PASSWORD_STRENGTH = "Password does not meet requirements"
PASSWORDS_DO_NOT_MATCH = "Passwords do not match"
REQUIRED_FIELD_MISSING = "Required field is missing"

# Content Discovery Messages
CONTENT_DISCOVERY_SUCCESS = "Content discovery data retrieved successfully"
CONTENT_DISCOVERY_ERROR = "Error retrieving content discovery data"
FEATURED_CONTENT_SUCCESS = "Featured content retrieved successfully"
TRENDING_CONTENT_SUCCESS = "Trending content retrieved successfully"
MOST_REVIEWED_SUCCESS = "Most reviewed content retrieved successfully"
NEW_RELEASES_SUCCESS = "New releases content retrieved successfully"

# Streaming Channel Messages
STREAMING_CHANNEL_LIST_SUCCESS = "Streaming channels retrieved successfully"
STREAMING_CHANNEL_DETAIL_SUCCESS = "Streaming channel details retrieved successfully"
STREAMING_CHANNEL_CREATED_SUCCESS = "Streaming channel created successfully"
STREAMING_CHANNEL_UPDATED_SUCCESS = "Streaming channel updated successfully"
STREAMING_CHANNEL_DELETED_SUCCESS = "Streaming channel deleted successfully"
STREAMING_CHANNEL_NOT_FOUND = "Streaming channel not found"
STREAMING_CHANNEL_ALREADY_EXISTS = "Streaming channel with this name already exists"
STREAMING_CHANNEL_INVALID_URL = "Invalid stream URL format"
STREAMING_CHANNEL_STATS_SUCCESS = "Streaming channel statistics retrieved successfully"

# Admin Messages
ADMIN_ACCESS_DENIED = "Admin access required"
ADMIN_INSUFFICIENT_PERMISSIONS = "Insufficient admin permissions"
ADMIN_OPERATION_SUCCESS = "Admin operation completed successfully"
ADMIN_BULK_OPERATION_SUCCESS = "Bulk operation completed successfully"

# Streaming Channel Admin Messages
STREAMING_CHANNEL_CREATED = "Streaming channel created successfully"
STREAMING_CHANNEL_UPDATED = "Streaming channel updated successfully"
STREAMING_CHANNEL_DELETED = "Streaming channel deleted successfully"
STREAMING_CHANNEL_NOT_FOUND = "Streaming channel not found"
STREAMING_CHANNEL_ALREADY_EXISTS = "Streaming channel with this name already exists"
STREAMING_CHANNEL_TEST_SUCCESS = "Stream URL test successful"
STREAMING_CHANNEL_TEST_FAILED = "Stream URL test failed"

# Genre Admin Messages
GENRE_CREATED = "Genre created successfully"
GENRE_UPDATED = "Genre updated successfully"
GENRE_DELETED = "Genre deleted successfully"
GENRE_NOT_FOUND = "Genre not found"
GENRE_ALREADY_EXISTS = "Genre with this name already exists"
GENRE_FEATURED = "Genre featured successfully"
GENRE_UNFEATURED = "Genre unfeatured successfully"

# Content Admin Messages
CONTENT_CREATED = "Content created successfully"
CONTENT_UPDATED = "Content updated successfully"
CONTENT_DELETED = "Content deleted successfully"
CONTENT_NOT_FOUND = "Content not found"
CONTENT_PUBLISHED = "Content published successfully"
CONTENT_UNPUBLISHED = "Content unpublished successfully"
CONTENT_FEATURED = "Content featured successfully"
CONTENT_UNFEATURED = "Content unfeatured successfully"
CONTENT_TRENDING = "Content trending status updated successfully"
CONTENT_ALREADY_EXISTS = "Content with this title already exists"

# People Admin Messages
PERSON_CREATED = "Person created successfully"
PERSON_UPDATED = "Person updated successfully"
PERSON_DELETED = "Person deleted successfully"
PERSON_NOT_FOUND = "Person not found"
PERSON_ALREADY_EXISTS = "Person with this name already exists"
PERSON_FEATURED = "Person featured successfully"
PERSON_UNFEATURED = "Person unfeatured successfully"
PERSON_VERIFIED = "Person verified successfully"
PERSON_UNVERIFIED = "Person unverified successfully"

# Season Admin Messages
SEASON_CREATED = "Season created successfully"
SEASON_UPDATED = "Season updated successfully"
SEASON_DELETED = "Season deleted successfully"
SEASON_NOT_FOUND = "Season not found"
SEASON_ALREADY_EXISTS = "Season with this number already exists"

# Episode Admin Messages
EPISODE_CREATED = "Episode created successfully"
EPISODE_UPDATED = "Episode updated successfully"
EPISODE_DELETED = "Episode deleted successfully"
EPISODE_NOT_FOUND = "Episode not found"
EPISODE_ALREADY_EXISTS = "Episode with this number already exists"

# File Admin Messages
FILE_UPLOADED = "File uploaded successfully"
FILE_DELETED = "File deleted successfully"
FILE_NOT_FOUND = "File not found"
FILE_PROCESSING_STARTED = "File processing started"
FILE_PROCESSING_FAILED = "File processing failed"
FILE_INVALID_FORMAT = "Invalid file format"

# User Admin Messages
USER_CREATED = "User created successfully"
USER_UPDATED = "User updated successfully"
USER_DELETED = "User deleted successfully"
USER_NOT_FOUND = "User not found"
USER_ALREADY_EXISTS = "User with this email already exists"
USER_SUSPENDED = "User suspended successfully"
USER_ACTIVATED = "User activated successfully"
USER_BANNED = "User banned successfully"
USER_UNBANNED = "User unbanned successfully"
USER_ROLE_UPDATED = "User role updated successfully"
USER_STATUS_UPDATED = "User status updated successfully"

# Review Admin Messages
REVIEW_UPDATED = "Review updated successfully"
REVIEW_DELETED = "Review deleted successfully"
REVIEW_FEATURED = "Review featured successfully"
REVIEW_HIDDEN = "Review hidden successfully"
REVIEW_APPROVED = "Review approved successfully"

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
INTERNAL_SERVER_ERROR = "Internal server error"
