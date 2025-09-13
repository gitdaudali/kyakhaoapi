from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, UserActivity, UserPermission

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (admin use).
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'is_active', 'is_email_verified', 'date_joined',
            'last_login', 'last_login_ip'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_email', 'user_username', 'bio', 'website',
            'location', 'facebook_url', 'twitter_url', 'instagram_url',
            'linkedin_url', 'language', 'timezone', 'notification_preferences',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for UserActivity model.
    """
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'activity_type_display', 'description',
            'ip_address', 'user_agent', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for UserPermission model.
    """
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    granted_by_email = serializers.EmailField(source='granted_by.email', read_only=True)
    
    class Meta:
        model = UserPermission
        fields = [
            'id', 'user', 'user_email', 'permission_type', 'permission_type_display',
            'is_active', 'granted_by', 'granted_by_email', 'granted_at', 'expires_at'
        ]
        read_only_fields = ['id', 'granted_at']
    
    def validate(self, attrs):
        # Check if permission already exists for this user
        if self.instance is None:  # Creating new permission
            existing = UserPermission.objects.filter(
                user=attrs['user'],
                permission_type=attrs['permission_type']
            ).first()
            if existing:
                raise serializers.ValidationError(
                    f"Permission {attrs['permission_type']} already exists for this user."
                )
        return attrs


class UserStatsSerializer(serializers.Serializer):
    """
    Serializer for user statistics.
    """
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    users_by_role = serializers.DictField()
    recent_activities = serializers.ListField()


class UserSearchSerializer(serializers.Serializer):
    """
    Serializer for user search functionality.
    """
    query = serializers.CharField(max_length=100)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    is_active = serializers.BooleanField(required=False)
    is_email_verified = serializers.BooleanField(required=False)










