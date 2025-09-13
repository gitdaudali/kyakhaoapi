from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import Video, VideoLike, VideoView

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model in video context."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class VideoViewSerializer(serializers.ModelSerializer):
    """Serializer for VideoView model."""

    viewer = UserSerializer(read_only=True)

    class Meta:
        model = VideoView
        fields = ["id", "viewer", "ip_address", "viewed_at"]
        read_only_fields = ["viewer", "ip_address", "viewed_at"]


class VideoLikeSerializer(serializers.ModelSerializer):
    """Serializer for VideoLike model."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = VideoLike
        fields = ["id", "user", "created_at"]
        read_only_fields = ["user", "created_at"]


class VideoListSerializer(serializers.ModelSerializer):
    """Serializer for listing videos."""

    uploaded_by = UserSerializer(read_only=True)
    duration_formatted = serializers.ReadOnlyField()
    file_size_formatted = serializers.ReadOnlyField()

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "description",
            "thumbnail_url",
            "duration",
            "duration_formatted",
            "views_count",
            "likes_count",
            "status",
            "uploaded_by",
            "uploaded_at",
            "file_size_formatted",
        ]


class VideoDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed video view."""

    uploaded_by = UserSerializer(read_only=True)
    duration_formatted = serializers.ReadOnlyField()
    file_size_formatted = serializers.ReadOnlyField()
    views = VideoViewSerializer(many=True, read_only=True)
    likes = VideoLikeSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "description",
            "file_url",
            "thumbnail_url",
            "duration",
            "duration_formatted",
            "views_count",
            "likes_count",
            "status",
            "uploaded_by",
            "uploaded_at",
            "updated_at",
            "file_size",
            "file_size_formatted",
            "resolution",
            "format",
            "views",
            "likes",
        ]


class VideoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating videos."""

    video_file = serializers.FileField(
        write_only=True, help_text="Video file to upload"
    )

    class Meta:
        model = Video
        fields = [
            "title",
            "description",
            "video_file",
            "duration",
            "thumbnail_url",
            "file_size",
            "resolution",
            "format",
        ]

    def validate_video_file(self, value):
        """Validate video file."""
        # Check file size (e.g., max 500MB)
        max_size = 500 * 1024 * 1024  # 500MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size must be no more than {max_size / (1024*1024)}MB."
            )

        # Check file extension
        allowed_extensions = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"]
        file_extension = value.name.lower()
        if not any(file_extension.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )

        return value

    def validate_duration(self, value):
        """Validate duration."""
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0.")
        return value

    def create(self, validated_data):
        """Create video instance."""
        video_file = validated_data.pop("video_file")
        user = self.context["request"].user

        # For now, we'll set a placeholder URL
        # In a real implementation, this would be handled by the S3 upload service
        validated_data["file_url"] = f"https://placeholder-s3-url.com/{video_file.name}"
        validated_data["uploaded_by"] = user
        validated_data["status"] = "uploading"

        return super().create(validated_data)


class VideoUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating videos."""

    video_file = serializers.FileField(
        write_only=True,
        required=False,
        help_text="New video file to replace existing one",
    )

    class Meta:
        model = Video
        fields = [
            "title",
            "description",
            "video_file",
            "duration",
            "thumbnail_url",
            "file_size",
            "resolution",
            "format",
        ]

    def validate_video_file(self, value):
        """Validate video file."""
        if value:
            # Check file size (e.g., max 500MB)
            max_size = 500 * 1024 * 1024  # 500MB
            if value.size > max_size:
                raise serializers.ValidationError(
                    f"File size must be no more than {max_size / (1024*1024)}MB."
                )

            # Check file extension
            allowed_extensions = [
                ".mp4",
                ".avi",
                ".mov",
                ".mkv",
                ".wmv",
                ".flv",
                ".webm",
            ]
            file_extension = value.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                raise serializers.ValidationError(
                    f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
                )

        return value

    def validate_duration(self, value):
        """Validate duration."""
        if value and value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0.")
        return value

    def update(self, instance, validated_data):
        """Update video instance."""
        video_file = validated_data.pop("video_file", None)

        if video_file:
            # In a real implementation, this would handle S3 file replacement
            # For now, we'll update the URL
            instance.file_url = f"https://placeholder-s3-url.com/{video_file.name}"
            instance.status = "uploading"  # Reset status for new upload

        return super().update(instance, validated_data)


class VideoLikeToggleSerializer(serializers.Serializer):
    """Serializer for toggling video likes."""

    video_id = serializers.UUIDField()

    def validate_video_id(self, value):
        """Validate video exists."""
        try:
            Video.objects.get(id=value)
        except Video.DoesNotExist:
            raise serializers.ValidationError("Video not found.")
        return value


class VideoViewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating video views."""

    class Meta:
        model = VideoView
        fields = ["video"]

    def create(self, validated_data):
        """Create video view with user and IP address."""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["viewer"] = request.user
            validated_data["ip_address"] = self.get_client_ip(request)
            validated_data["user_agent"] = request.META.get("HTTP_USER_AGENT", "")

        return super().create(validated_data)

    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
