from django.urls import path

from .views import (
    UserActivityView,
    UserDetailView,
    UserListView,
    UserPermissionView,
    UserProfileView,
)

app_name = "users"

urlpatterns = [
    # User management
    path("", UserListView.as_view(), name="user_list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    # User activities and permissions
    path("activities/", UserActivityView.as_view(), name="user_activities"),
    path("permissions/", UserPermissionView.as_view(), name="user_permissions"),
]
