from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import uuid
import logging

from .models import User, JWTToken, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, EmailVerificationSerializer
)

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send email verification
        self._send_verification_email(user)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'code': 200,
            'message': 'User registered successfully. Please check your email for verification.',
            'data': {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role,
                    'isEmailVerified': user.is_email_verified
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def _send_verification_email(self, user):
        """Send email verification to user."""
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={user.email_verification_token}"
            send_mail(
                'Verify Your Email',
                f'Please click the following link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {e}")


class UserLoginView(APIView):
    """
    View for user login.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        login(request, user)
        
        # Update last login IP
        user.last_login_ip = self._get_client_ip(request)
        user.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Store refresh token in database
        JWTToken.objects.create(
            user=user,
            refresh_token=str(refresh),
            access_token_hash=str(refresh.access_token)[:255],
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        response_data = {
            'code': 200,
            'message': 'Login successful',
            'data': {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role,
                    'isEmailVerified': user.is_email_verified
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserLogoutView(APIView):
    """
    View for user logout.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                # Revoke the refresh token
                JWTToken.objects.filter(
                    user=request.user,
                    refresh_token=refresh_token
                ).update(is_revoked=True)
            
            logout(request)
            
            response_data = {
                'code': 200,
                'message': 'Logout successful',
                'data': None
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response({
                'code': 500,
                'message': 'Logout failed',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for user profile retrieval and update.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        
        response_data = {
            'code': 200,
            'message': 'Profile retrieved successfully',
            'data': serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        response_data = {
            'code': 200,
            'message': 'Profile updated successfully',
            'data': serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    """
    View for password change.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Revoke all existing tokens
        JWTToken.objects.filter(user=user).update(is_revoked=True)
        
        response_data = {
            'code': 200,
            'message': 'Password changed successfully',
            'data': None
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    View for password reset request.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate reset token
        reset_token = str(uuid.uuid4())
        PasswordResetToken.objects.create(
            user=user,
            token=reset_token,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Send reset email
        self._send_reset_email(user, reset_token)
        
        response_data = {
            'code': 200,
            'message': 'Password reset email sent successfully',
            'data': None
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _send_reset_email(self, user, token):
        """Send password reset email to user."""
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            send_mail(
                'Password Reset Request',
                f'Please click the following link to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send reset email to {user.email}: {e}")


class PasswordResetConfirmView(APIView):
    """
    View for password reset confirmation.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_token = serializer.validated_data['reset_token']
        user = reset_token.user
        
        # Update password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Mark token as used
        reset_token.is_used = True
        reset_token.save()
        
        # Revoke all existing tokens
        JWTToken.objects.filter(user=user).update(is_revoked=True)
        
        response_data = {
            'code': 200,
            'message': 'Password reset successfully',
            'data': None
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class EmailVerificationView(APIView):
    """
    View for email verification.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['token']
        user.is_email_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        user.save()
        
        response_data = {
            'code': 200,
            'message': 'Email verified successfully',
            'data': None
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class TokenRefreshView(APIView):
    """
    View for token refresh.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'code': 400,
                'message': 'Refresh token is required',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check if token exists and is not revoked
            jwt_token = JWTToken.objects.get(
                refresh_token=refresh_token,
                is_revoked=False,
                expires_at__gt=timezone.now()
            )
            
            # Generate new tokens
            refresh = RefreshToken(refresh_token)
            new_refresh = RefreshToken.for_user(jwt_token.user)
            
            # Update token in database
            jwt_token.refresh_token = str(new_refresh)
            jwt_token.access_token_hash = str(new_refresh.access_token)[:255]
            jwt_token.save()
            
            response_data = {
                'code': 200,
                'message': 'Token refreshed successfully',
                'data': {
                    'tokens': {
                        'access': str(new_refresh.access_token),
                        'refresh': str(new_refresh)
                    }
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except JWTToken.DoesNotExist:
            return Response({
                'code': 401,
                'message': 'Invalid or expired refresh token',
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return Response({
                'code': 500,
                'message': 'Token refresh failed',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

