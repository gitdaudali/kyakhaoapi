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

# Policy Messages
POLICY_CREATED = "Policy created successfully"
POLICY_UPDATED = "Policy updated successfully"
POLICY_DELETED = "Policy deleted successfully"
POLICY_NOT_FOUND = "Policy not found"
POLICY_ALREADY_EXISTS = "Policy already exists"
POLICY_ACCEPTED = "Policy accepted successfully"
POLICY_DECLINED = "Policy declined successfully"
POLICY_ACCEPTANCE_REQUIRED = "Policy acceptance required"
POLICY_VERSION_UPDATED = "Policy version updated"

# User Policy Messages
USER_POLICY_ACCEPTED = "User policy accepted successfully"
USER_POLICY_DECLINED = "User policy declined successfully"
USER_POLICY_NOT_FOUND = "User policy not found"
USER_POLICY_ALREADY_ACCEPTED = "User policy already accepted"
USER_POLICY_ALREADY_DECLINED = "User policy already declined"
USER_POLICY_HISTORY_RETRIEVED = "User policy history retrieved"

# Subscription Messages
SUBSCRIPTION_CREATED = "Subscription created successfully"
SUBSCRIPTION_UPDATED = "Subscription updated successfully"
SUBSCRIPTION_DELETED = "Subscription deleted successfully"
SUBSCRIPTION_NOT_FOUND = "Subscription not found"
SUBSCRIPTION_ALREADY_EXISTS = "Subscription already exists"
SUBSCRIPTION_ACTIVATED = "Subscription activated successfully"
SUBSCRIPTION_DEACTIVATED = "Subscription deactivated successfully"
SUBSCRIPTION_CANCELLED = "Subscription cancelled successfully"
SUBSCRIPTION_RENEWED = "Subscription renewed successfully"
SUBSCRIPTION_EXPIRED = "Subscription expired"
SUBSCRIPTION_PAYMENT_FAILED = "Subscription payment failed"
SUBSCRIPTION_PAYMENT_SUCCESS = "Subscription payment successful"
SUBSCRIPTION_PLAN_NOT_FOUND = "Subscription plan not found"
SUBSCRIPTION_PLAN_CREATED = "Subscription plan created successfully"
SUBSCRIPTION_PLAN_UPDATED = "Subscription plan updated successfully"
SUBSCRIPTION_PLAN_DELETED = "Subscription plan deleted successfully"

# Stripe Messages
STRIPE_PAYMENT_INTENT_CREATED = "Payment intent created successfully"
STRIPE_PAYMENT_INTENT_CONFIRMED = "Payment intent confirmed successfully"
STRIPE_PAYMENT_INTENT_FAILED = "Payment intent failed"
STRIPE_CUSTOMER_CREATED = "Stripe customer created successfully"
STRIPE_CUSTOMER_UPDATED = "Stripe customer updated successfully"
STRIPE_CUSTOMER_NOT_FOUND = "Stripe customer not found"
STRIPE_WEBHOOK_PROCESSED = "Stripe webhook processed successfully"
STRIPE_WEBHOOK_INVALID = "Invalid Stripe webhook"
STRIPE_PAYMENT_METHOD_ADDED = "Payment method added successfully"
STRIPE_PAYMENT_METHOD_REMOVED = "Payment method removed successfully"
STRIPE_PAYMENT_METHOD_UPDATED = "Payment method updated successfully"
STRIPE_PAYMENT_METHOD_NOT_FOUND = "Payment method not found"
STRIPE_INVOICE_CREATED = "Invoice created successfully"
STRIPE_INVOICE_PAID = "Invoice paid successfully"
STRIPE_INVOICE_FAILED = "Invoice payment failed"
STRIPE_REFUND_CREATED = "Refund created successfully"
STRIPE_REFUND_PROCESSED = "Refund processed successfully"
STRIPE_REFUND_FAILED = "Refund failed"

# Search Messages
SEARCH_SUCCESS = "Search completed successfully"
SEARCH_NO_RESULTS = "No results found"
SEARCH_INVALID_QUERY = "Invalid search query"
SEARCH_HISTORY_SAVED = "Search history saved successfully"
SEARCH_HISTORY_RETRIEVED = "Search history retrieved successfully"
SEARCH_HISTORY_CLEARED = "Search history cleared successfully"
SEARCH_SUGGESTIONS_RETRIEVED = "Search suggestions retrieved successfully"
SEARCH_TRENDING_RETRIEVED = "Trending searches retrieved successfully"

# Upload Messages
UPLOAD_STARTED = "Upload started successfully"
UPLOAD_COMPLETED = "Upload completed successfully"
UPLOAD_FAILED = "Upload failed"
UPLOAD_CANCELLED = "Upload cancelled successfully"
UPLOAD_PROGRESS_UPDATED = "Upload progress updated"
UPLOAD_CHUNK_RECEIVED = "Upload chunk received successfully"
UPLOAD_CHUNK_FAILED = "Upload chunk failed"
UPLOAD_FILE_TOO_LARGE = "File size exceeds maximum limit"
UPLOAD_INVALID_FORMAT = "Invalid file format"
UPLOAD_QUOTA_EXCEEDED = "Upload quota exceeded"
UPLOAD_PROCESSING_STARTED = "File processing started"
UPLOAD_PROCESSING_COMPLETED = "File processing completed"
UPLOAD_PROCESSING_FAILED = "File processing failed"

# Analytics Messages
ANALYTICS_RETRIEVED = "Analytics data retrieved successfully"
ANALYTICS_NOT_FOUND = "Analytics data not found"
ANALYTICS_GENERATED = "Analytics report generated successfully"
ANALYTICS_EXPORTED = "Analytics data exported successfully"
ANALYTICS_DASHBOARD_LOADED = "Analytics dashboard loaded successfully"
ANALYTICS_METRICS_UPDATED = "Analytics metrics updated successfully"
ANALYTICS_TRENDS_RETRIEVED = "Analytics trends retrieved successfully"
ANALYTICS_PERFORMANCE_RETRIEVED = "Performance analytics retrieved successfully"

# Notification Messages
NOTIFICATION_SENT = "Notification sent successfully"
NOTIFICATION_FAILED = "Notification failed to send"
NOTIFICATION_RETRIEVED = "Notifications retrieved successfully"
NOTIFICATION_MARKED_READ = "Notification marked as read"
NOTIFICATION_MARKED_UNREAD = "Notification marked as unread"
NOTIFICATION_DELETED = "Notification deleted successfully"
NOTIFICATION_PREFERENCES_UPDATED = "Notification preferences updated"
NOTIFICATION_TEMPLATE_CREATED = "Notification template created"
NOTIFICATION_TEMPLATE_UPDATED = "Notification template updated"
NOTIFICATION_TEMPLATE_DELETED = "Notification template deleted"

# Cache Messages
CACHE_CLEARED = "Cache cleared successfully"
CACHE_UPDATED = "Cache updated successfully"
CACHE_INVALIDATED = "Cache invalidated successfully"
CACHE_HIT = "Cache hit"
CACHE_MISS = "Cache miss"
CACHE_WARMED = "Cache warmed successfully"

# Rate Limiting Messages
RATE_LIMIT_EXCEEDED = "Rate limit exceeded"
RATE_LIMIT_RESET = "Rate limit will reset"
RATE_LIMIT_INFO = "Rate limit information"
RATE_LIMIT_HEADERS_UPDATED = "Rate limit headers updated"

# Health Check Messages
HEALTH_CHECK_PASSED = "Health check passed"
HEALTH_CHECK_FAILED = "Health check failed"
HEALTH_CHECK_DATABASE_CONNECTED = "Database connection healthy"
HEALTH_CHECK_DATABASE_DISCONNECTED = "Database connection unhealthy"
HEALTH_CHECK_REDIS_CONNECTED = "Redis connection healthy"
HEALTH_CHECK_REDIS_DISCONNECTED = "Redis connection unhealthy"
HEALTH_CHECK_S3_CONNECTED = "S3 connection healthy"
HEALTH_CHECK_S3_DISCONNECTED = "S3 connection unhealthy"

# API Version Messages
API_VERSION_DEPRECATED = "API version deprecated"
API_VERSION_UNSUPPORTED = "API version unsupported"
API_VERSION_INFO = "API version information"
API_VERSION_MIGRATION_REQUIRED = "API version migration required"

# Feature Flag Messages
FEATURE_ENABLED = "Feature enabled"
FEATURE_DISABLED = "Feature disabled"
FEATURE_NOT_AVAILABLE = "Feature not available"
FEATURE_FLAG_UPDATED = "Feature flag updated"

# Maintenance Messages
MAINTENANCE_MODE_ENABLED = "Maintenance mode enabled"
MAINTENANCE_MODE_DISABLED = "Maintenance mode disabled"
MAINTENANCE_SCHEDULED = "Maintenance scheduled"
MAINTENANCE_COMPLETED = "Maintenance completed"
MAINTENANCE_CANCELLED = "Maintenance cancelled"

# General Messages
SUCCESS = "Success"
ERROR = "Error"
UNAUTHORIZED = "Unauthorized"
FORBIDDEN = "Forbidden"
NOT_FOUND = "Not found"
BAD_REQUEST = "Bad request"
INTERNAL_SERVER_ERROR = "Server error"

# ============================================================================
# UNIFIED RESPONSE SCHEMA
# ============================================================================

# Base response schema for all API endpoints
RESPONSE_SCHEMA = {
    "success": {
        "type": "boolean",
        "description": "Indicates if the request was successful"
    },
    "message": {
        "type": "string", 
        "description": "Human-readable message describing the result"
    },
    "data": {
        "type": "object",
        "description": "Response data payload",
        "nullable": True
    }
}

# Success response examples
SUCCESS_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "Operation completed successfully",
    "data": {}
}

# Error response examples
ERROR_RESPONSE_EXAMPLE = {
    "success": False,
    "message": "An error occurred",
    "data": None
}

# Validation error response example
VALIDATION_ERROR_RESPONSE_EXAMPLE = {
    "success": False,
    "message": "Request validation failed",
    "data": {
        "field_name": ["Error message 1", "Error message 2"]
    }
}