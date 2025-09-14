"""
Centralized response messages for the application.
All error messages and success messages are defined here for consistency.
"""

# Authentication Messages
EMAIL_EXISTS = "Email already registered"
USERNAME_EXISTS = "Username already taken"
INVALID_CREDENTIALS = "Incorrect email or password"
ACCOUNT_DEACTIVATED = "User account is deactivated"
INVALID_REFRESH_TOKEN = "Invalid refresh token"
CURRENT_PASSWORD_INCORRECT = "Current password is incorrect"
PASSWORD_CHANGED_SUCCESS = "Password changed successfully"
PASSWORD_RESET_SENT = "If the email exists, a password reset link has been sent"
PASSWORD_RESET_SUCCESS = "Password reset successfully"
PASSWORD_RESET_TOKEN_INVALID = "Invalid or expired reset token"
PASSWORD_RESET_TOKEN_USED = "Reset token has already been used"
EMAIL_VERIFICATION_SUCCESS = "Email verified successfully"
EMAIL_VERIFICATION_TOKEN_INVALID = "Invalid or expired verification token"
EMAIL_VERIFICATION_TOKEN_USED = "Verification token has already been used"
LOGOUT_SUCCESS = "Successfully logged out"
LOGOUT_ALL_SUCCESS = "Successfully logged out from all devices"
LOGOUT_NO_TOKENS = "Logout successful (no tokens to revoke)"

# User Messages
USER_NOT_FOUND = "User not found"
USER_ALREADY_EXISTS = "User already exists"
USER_CREATED_SUCCESS = "User created successfully"
USER_UPDATED_SUCCESS = "User updated successfully"
USER_DELETED_SUCCESS = "User deleted successfully"

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

# General Messages
SUCCESS = "Success"
ERROR = "Error"
UNAUTHORIZED = "Unauthorized"
FORBIDDEN = "Forbidden"
NOT_FOUND = "Not found"
BAD_REQUEST = "Bad request"
INTERNAL_SERVER_ERROR = "Internal server error"
