import uuid
from datetime import timedelta

from rest_framework import serializers

from django.contrib.auth import authenticate
from django.utils import timezone

from .models import JWTToken, PasswordResetToken, User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "role",
            "phone_number",
            "date_of_birth",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)

        # Generate email verification token
        user.email_verification_token = str(uuid.uuid4())
        user.email_verification_expires = timezone.now() + timedelta(hours=24)
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            attrs["user"] = user
        else:
            raise serializers.ValidationError("Must include email and password.")

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "date_of_birth",
            "profile_picture",
            "is_email_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "role",
            "is_email_verified",
            "created_at",
            "updated_at",
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """

    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError("Passwords don't match.")

        try:
            reset_token = PasswordResetToken.objects.get(
                token=attrs["token"], is_used=False, expires_at__gt=timezone.now()
            )
            attrs["reset_token"] = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired reset token.")

        return attrs


class JWTTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for JWT tokens.
    """

    class Meta:
        model = JWTToken
        fields = [
            "refresh_token",
            "access_token_hash",
            "is_revoked",
            "created_at",
            "expires_at",
        ]
        read_only_fields = [
            "refresh_token",
            "access_token_hash",
            "created_at",
            "expires_at",
        ]


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    """

    token = serializers.CharField()

    def validate_token(self, value):
        try:
            user = User.objects.get(
                email_verification_token=value,
                email_verification_expires__gt=timezone.now(),
                is_email_verified=False,
            )
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired verification token.")
