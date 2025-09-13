from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Video, VideoView, VideoLike


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for Video model."""
    list_display = [
        'title', 'uploaded_by', 'status', 'duration_formatted', 
        'views_count', 'likes_count', 'uploaded_at', 'file_size_formatted'
    ]
    list_filter = [
        'status', 'uploaded_at', 'format', 'uploaded_by__role'
    ]
    search_fields = ['title', 'description', 'uploaded_by__email', 'uploaded_by__username']
    readonly_fields = [
        'id', 'uploaded_at', 'updated_at', 'views_count', 'likes_count',
        'duration_formatted', 'file_size_formatted', 'file_url_link'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'uploaded_by')
        }),
        ('File Information', {
            'fields': ('file_url_link', 'file_size', 'file_size_formatted', 'duration', 'duration_formatted', 'format', 'resolution')
        }),
        ('Media URLs', {
            'fields': ('thumbnail_url',)
        }),
        ('S3 Information', {
            'fields': ('s3_bucket', 's3_key'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count', 'status')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_url_link(self, obj):
        """Display file URL as a clickable link."""
        if obj.file_url:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.file_url, 'View File')
        return '-'
    file_url_link.short_description = 'File URL'
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('uploaded_by')
    
    def has_add_permission(self, request):
        """Only allow admins to add videos."""
        return request.user.is_superuser or request.user.role == 'admin'
    
    def has_change_permission(self, request, obj=None):
        """Allow admins and video owners to edit videos."""
        if request.user.is_superuser or request.user.role == 'admin':
            return True
        if obj and obj.uploaded_by == request.user:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only allow admins to delete videos."""
        return request.user.is_superuser or request.user.role == 'admin'


@admin.register(VideoView)
class VideoViewAdmin(admin.ModelAdmin):
    """Admin configuration for VideoView model."""
    list_display = ['video', 'viewer', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at', 'video__status']
    search_fields = ['video__title', 'viewer__email', 'viewer__username', 'ip_address']
    readonly_fields = ['viewed_at']
    date_hierarchy = 'viewed_at'
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('video', 'viewer')
    
    def has_add_permission(self, request):
        """Disable manual addition of video views."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of video views."""
        return False


@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    """Admin configuration for VideoLike model."""
    list_display = ['video', 'user', 'created_at']
    list_filter = ['created_at', 'video__status']
    search_fields = ['video__title', 'user__email', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('video', 'user')
    
    def has_add_permission(self, request):
        """Disable manual addition of video likes."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of video likes."""
        return False
