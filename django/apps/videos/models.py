import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Video(models.Model):
    """
    Video model for storing video metadata and S3 file references.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    file_url = models.URLField(max_length=500, verbose_name=_("Video File URL"))
    duration = models.FloatField(
        verbose_name=_("Duration (seconds)"), help_text=_("Duration in seconds")
    )
    thumbnail_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name=_("Thumbnail URL")
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_videos",
        verbose_name=_("Uploaded By"),
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    views_count = models.IntegerField(default=0, verbose_name=_("Views Count"))
    likes_count = models.IntegerField(default=0, verbose_name=_("Likes Count"))

    # Additional fields for video processing
    status = models.CharField(
        max_length=20,
        choices=[
            ("uploading", "Uploading"),
            ("processing", "Processing"),
            ("ready", "Ready"),
            ("failed", "Failed"),
        ],
        default="uploading",
        verbose_name=_("Status"),
    )

    # Video metadata
    file_size = models.BigIntegerField(
        blank=True, null=True, verbose_name=_("File Size (bytes)")
    )
    resolution = models.CharField(
        max_length=20, blank=True, null=True, verbose_name=_("Resolution")
    )
    format = models.CharField(
        max_length=10, blank=True, null=True, verbose_name=_("Format")
    )

    # S3 bucket and key for file management
    s3_bucket = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("S3 Bucket")
    )
    s3_key = models.CharField(
        max_length=500, blank=True, null=True, verbose_name=_("S3 Key")
    )

    class Meta:
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")
        ordering = ["-uploaded_at"]
        db_table = "videos_video"

    def __str__(self):
        return self.title

    @property
    def duration_formatted(self):
        """Return duration in HH:MM:SS format."""
        if not self.duration:
            return "00:00:00"

        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def file_size_formatted(self):
        """Return file size in human readable format."""
        if not self.file_size:
            return "0 B"

        for unit in ["B", "KB", "MB", "GB"]:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    def increment_views(self):
        """Increment the view count."""
        self.views_count += 1
        self.save(update_fields=["views_count"])

    def increment_likes(self):
        """Increment the likes count."""
        self.likes_count += 1
        self.save(update_fields=["likes_count"])

    def decrement_likes(self):
        """Decrement the likes count."""
        if self.likes_count > 0:
            self.likes_count -= 1
            self.save(update_fields=["likes_count"])


class VideoView(models.Model):
    """
    Model to track individual video views for analytics.
    """

    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="views", verbose_name=_("Video")
    )
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="video_views",
        verbose_name=_("Viewer"),
    )
    ip_address = models.GenericIPAddressField(
        blank=True, null=True, verbose_name=_("IP Address")
    )
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Viewed At"))

    class Meta:
        verbose_name = _("Video View")
        verbose_name_plural = _("Video Views")
        ordering = ["-viewed_at"]
        db_table = "videos_video_view"

    def __str__(self):
        return f"{self.video.title} - {self.viewed_at}"


class VideoLike(models.Model):
    """
    Model to track video likes.
    """

    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="likes", verbose_name=_("Video")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="video_likes",
        verbose_name=_("User"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Video Like")
        verbose_name_plural = _("Video Likes")
        unique_together = ["video", "user"]
        ordering = ["-created_at"]
        db_table = "videos_video_like"

    def __str__(self):
        return f"{self.user.email} likes {self.video.title}"
