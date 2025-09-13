"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API v1
    path(
        "api/v1/",
        include(
            [
                path("auth/", include("apps.authentication.urls")),
                path("users/", include("apps.users.urls")),
                path("videos/", include("apps.videos.urls")),
                path("", include("apps.api.urls")),
            ]
        ),
    ),
    # Django Allauth URLs
    path("accounts/", include("allauth.urls")),
    # OAuth URLs
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    # Redirect root to API info
    path("", RedirectView.as_view(url="/api/v1/info/", permanent=False)),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
