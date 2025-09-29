"""
Unit tests for authentication endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status


class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_new_user_success(self, client, mock_email_tasks):
        """Test successful user registration."""
        data = {
            "email": "newuser@example.com",
            "password": "NewPassword123!",
            "password_confirm": "NewPassword123!"
        }

        response = client.post("/api/v1/auth/register", json=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "Registration successful. Please check your email for verification code."
        mock_email_tasks['registration'].assert_called_once()

    def test_register_existing_user_conflict(self, client, test_user):
        """Test registration with existing user."""
        data = {
            "email": test_user.email,
            "password": "NewPassword123!",
            "password_confirm": "NewPassword123!"
        }

        response = client.post("/api/v1/auth/register", json=data)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "Account already registered and verified" in response.json()["detail"]

    def test_register_invalid_password(self, client):
        """Test registration with invalid password."""
        data = {
            "email": "test@example.com",
            "password": "short",
            "password_confirm": "short"
        }

        response = client.post("/api/v1/auth/register", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_password_mismatch(self, client):
        """Test registration with password mismatch."""
        data = {
            "email": "test@example.com",
            "password": "Password123!",
            "password_confirm": "DifferentPassword123!"
        }

        response = client.post("/api/v1/auth/register", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successful login."""
        data = {
            "email": test_user.email,
            "password": "TestPassword123!",
            "remember_me": False
        }

        response = client.post("/api/v1/auth/login", json=data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "user" in response_data
        assert "tokens" in response_data
        assert response_data["user"]["email"] == test_user.email
        assert "access_token" in response_data["tokens"]

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!",
            "remember_me": False
        }

        response = client.post("/api/v1/auth/login", json=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Account not found" in response.json()["detail"]

    def test_login_unverified_email(self, client, test_user_pending):
        """Test login with unverified email."""
        data = {
            "email": test_user_pending.email,
            "password": "TestPassword123!",
            "remember_me": False
        }

        response = client.post("/api/v1/auth/login", json=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Please verify your email address before logging in" in response.json()["detail"]

    def test_login_inactive_user(self, client, test_user_inactive):
        """Test login with inactive user."""
        data = {
            "email": test_user_inactive.email,
            "password": "TestPassword123!",
            "remember_me": False
        }

        response = client.post("/api/v1/auth/login", json=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User account is deactivated" in response.json()["detail"]


class TestTokenRefresh:
    """Test token refresh endpoint."""

    def test_refresh_token_success(self, client, test_user):
        """Test successful token refresh."""
        # Login first
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123!",
            "remember_me": False
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["tokens"]["refresh_token"]

        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_token"}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserLogout:
    """Test user logout endpoint."""

    def test_logout_success(self, client, test_user):
        """Test successful logout."""
        # Login first
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123!",
            "remember_me": False
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()["tokens"]

        # Logout
        logout_data = {
            "refresh_token": tokens["refresh_token"],
            "logout_all_devices": False
        }
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.post("/api/v1/auth/logout", json=logout_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert "Successfully logged out" in response.json()["message"]

    def test_logout_all_devices(self, client, test_user):
        """Test logout from all devices."""
        # Login first
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123!",
            "remember_me": False
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["tokens"]["access_token"]

        # Logout all devices
        logout_data = {"logout_all_devices": True}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/auth/logout", json=logout_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert "Successfully logged out from all devices" in response.json()["message"]

    def test_logout_unauthorized(self, client):
        """Test logout without authentication."""
        logout_data = {"logout_all_devices": False}
        response = client.post("/api/v1/auth/logout", json=logout_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetCurrentUser:
    """Test get current user endpoint."""

    def test_get_current_user_success(self, client, test_user, auth_headers):
        """Test successful get current user."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert user_data["email"] == test_user.email
        assert user_data["first_name"] == test_user.first_name

    def test_get_current_user_unauthorized(self, client):
        """Test get current user without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestChangePassword:
    """Test change password endpoint."""

    def test_change_password_success(self, client, test_user, auth_headers):
        """Test successful password change."""
        data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!",
            "new_password_confirm": "NewPassword123!"
        }

        response = client.post("/api/v1/auth/change-password", json=data, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "Password changed successfully" in response.json()["message"]

    def test_change_password_wrong_current(self, client, test_user, auth_headers):
        """Test password change with wrong current password."""
        data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!",
            "new_password_confirm": "NewPassword123!"
        }

        response = client.post("/api/v1/auth/change-password", json=data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Current password is incorrect" in response.json()["detail"]

    def test_change_password_unauthorized(self, client):
        """Test password change without authentication."""
        data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!",
            "new_password_confirm": "NewPassword123!"
        }

        response = client.post("/api/v1/auth/change-password", json=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPasswordReset:
    """Test password reset endpoints."""

    def test_request_password_reset_success(self, client, test_user, mock_email_tasks):
        """Test successful password reset request."""
        data = {"email": test_user.email}
        response = client.post("/api/v1/auth/password/reset", json=data)

        assert response.status_code == status.HTTP_200_OK
        assert "Password reset OTP sent" in response.json()["message"]
        mock_email_tasks['password_reset'].assert_called_once()

    def test_request_password_reset_user_not_found(self, client):
        """Test password reset request for non-existent user."""
        data = {"email": "nonexistent@example.com"}
        response = client.post("/api/v1/auth/password/reset", json=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Account not found" in response.json()["detail"]


class TestOTPVerification:
    """Test OTP verification endpoint."""

    def test_verify_otp_success(self, client, test_user_pending):
        """Test successful OTP verification."""
        # Mock OTP validation to return success
        with patch('app.api.v1.endpoints.auth.validate_email_verification_otp') as mock_validate, \
             patch('app.api.v1.endpoints.auth.mark_email_verification_otp_used') as mock_mark:

            mock_validate.return_value = AsyncMock(otp_code="123456")
            mock_mark.return_value = AsyncMock()

            data = {
                "email": test_user_pending.email,
                "otp_code": "123456"
            }
            response = client.post("/api/v1/auth/verify-otp", json=data)

            assert response.status_code == status.HTTP_200_OK
            assert "Email verified successfully. You can now login." in response.json()["message"]

    def test_verify_otp_already_verified(self, client, test_user):
        """Test OTP verification for already verified user."""
        data = {
            "email": test_user.email,
            "otp_code": "123456"
        }
        response = client.post("/api/v1/auth/verify-otp", json=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already verified" in response.json()["detail"]

    def test_verify_otp_invalid(self, client, test_user_pending):
        """Test OTP verification with invalid OTP."""
        # Mock OTP validation to return None (invalid)
        with patch('app.api.v1.endpoints.auth.validate_email_verification_otp') as mock_validate:
            mock_validate.return_value = None

            data = {
                "email": test_user_pending.email,
                "otp_code": "000000"
            }
            response = client.post("/api/v1/auth/verify-otp", json=data)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Invalid or expired verification code" in response.json()["detail"]


class TestGoogleOAuth:
    """Test Google OAuth endpoint."""

    def test_google_oauth_new_user_success(self, client, mock_google_oauth):
        """Test successful Google OAuth for new user."""
        data = {"access_token": "valid_google_token"}
        response = client.post("/api/v1/auth/social/google", json=data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["is_new_user"] is True
        assert response_data["user"]["email"] == "google@example.com"
        assert response_data["user"]["signup_type"] == "google"

    def test_google_oauth_existing_user_success(self, client, test_user, mock_google_oauth):
        """Test Google OAuth for existing user."""
        # Mock to return existing user's email
        mock_google_oauth.return_value = AsyncMock(
            id="google_123",
            email=test_user.email,  # Existing user's email
            verified_email=True,
            name="Google User",
            given_name="Google",
            family_name="User"
        )

        data = {"access_token": "valid_google_token"}
        response = client.post("/api/v1/auth/social/google", json=data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error during Google OAuth authentication" in response.json()["detail"]

    def test_google_oauth_invalid_token(self, client, mock_google_oauth):
        """Test Google OAuth with invalid token."""
        # Mock to raise exception
        mock_google_oauth.side_effect = Exception("Invalid token")

        data = {"access_token": "invalid_token"}
        response = client.post("/api/v1/auth/social/google", json=data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error during Google OAuth authentication" in response.json()["detail"]

    def test_google_oauth_unverified_email(self, client, mock_google_oauth):
        """Test Google OAuth with unverified email."""
        # Mock unverified email
        mock_google_oauth.return_value = AsyncMock(
            id="google_123",
            email="unverified@example.com",
            verified_email=False,  # Unverified
            name="Unverified User"
        )

        data = {"access_token": "valid_google_token"}
        response = client.post("/api/v1/auth/social/google", json=data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error during Google OAuth authentication" in response.json()["detail"]


class TestTokenInfo:
    """Test token info endpoint."""

    def test_get_token_info_success(self, client, test_user, auth_headers):
        """Test successful token info retrieval."""
        response = client.get("/api/v1/auth/token-info", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        token_info = response.json()
        assert token_info["token_type"] == "bearer"
        assert token_info["is_valid"] is True
        assert token_info["user_id"] == str(test_user.id)

    def test_get_token_info_unauthorized(self, client):
        """Test token info without authentication."""
        response = client.get("/api/v1/auth/token-info")
        assert response.status_code == status.HTTP_403_FORBIDDEN
