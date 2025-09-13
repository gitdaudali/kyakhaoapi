from django.urls import path

from .views import (
    EmailVerificationView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    TokenRefreshView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserRegistrationView,
)

app_name = "authentication"

urlpatterns = [
    # Authentication endpoints
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Profile management
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    # Password reset
    path(
        "password/reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Email verification
    path("email/verify/", EmailVerificationView.as_view(), name="email_verification"),
]
