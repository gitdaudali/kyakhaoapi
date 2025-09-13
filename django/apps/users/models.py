from guardian.shortcuts import assign_perm

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserProfile(models.Model):
    """
    Extended user profile model with additional user information.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )

    # Additional profile fields
    bio = models.TextField(max_length=500, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    # Social media links
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    # Preferences
    language = models.CharField(max_length=10, default="en")
    timezone = models.CharField(max_length=50, default="UTC")
    notification_preferences = models.JSONField(default=dict)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_user_profile"
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self):
        return f"Profile for {self.user.email}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # Assign default permissions based on user role
            self._assign_default_permissions()

    def _assign_default_permissions(self):
        """Assign default permissions based on user role."""
        if self.user.role == "admin":
            # Admin gets all permissions
            assign_perm("authentication.view_user", self.user, self.user)
            assign_perm("authentication.change_user", self.user, self.user)
            assign_perm("authentication.delete_user", self.user, self.user)
        elif self.user.role == "user":
            # Regular user gets basic permissions
            assign_perm("authentication.view_user", self.user, self.user)
            assign_perm("authentication.change_user", self.user, self.user)
        elif self.user.role == "tv_client":
            # TV client gets limited permissions
            assign_perm("authentication.view_user", self.user, self.user)


class UserSession(models.Model):
    """
    Model to track user sessions for analytics and security.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_user_session"
        ordering = ["-last_activity"]

    def __str__(self):
        return f"Session for {self.user.email}"


class UserActivity(models.Model):
    """
    Model to track user activities for analytics.
    """

    ACTIVITY_TYPES = [
        ("login", "Login"),
        ("logout", "Logout"),
        ("profile_update", "Profile Update"),
        ("password_change", "Password Change"),
        ("email_verification", "Email Verification"),
        ("password_reset", "Password Reset"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users_user_activity"
        ordering = ["-created_at"]
        verbose_name = _("User Activity")
        verbose_name_plural = _("User Activities")

    def __str__(self):
        return f"{self.activity_type} by {self.user.email}"


class UserPermission(models.Model):
    """
    Custom user permissions model for granular access control.
    """

    PERMISSION_TYPES = [
        ("stream_create", "Create Stream"),
        ("stream_edit", "Edit Stream"),
        ("stream_delete", "Delete Stream"),
        ("user_manage", "Manage Users"),
        ("content_manage", "Manage Content"),
        ("analytics_view", "View Analytics"),
        ("settings_manage", "Manage Settings"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="custom_permissions"
    )
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    is_active = models.BooleanField(default=True)
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_permissions",
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "users_user_permission"
        unique_together = ["user", "permission_type"]
        ordering = ["-granted_at"]

    def __str__(self):
        return f"{self.permission_type} for {self.user.email}"

    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone

            return timezone.now() > self.expires_at
        return False
