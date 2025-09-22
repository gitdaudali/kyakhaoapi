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

# General Messages
SUCCESS = "Success"
ERROR = "Error"
UNAUTHORIZED = "Unauthorized"
FORBIDDEN = "Forbidden"
NOT_FOUND = "Not found"
BAD_REQUEST = "Bad request"
INTERNAL_SERVER_ERROR = "Internal server error"
