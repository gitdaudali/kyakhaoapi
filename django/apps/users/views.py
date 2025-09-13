from rest_framework import generics, permissions, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .models import UserActivity, UserPermission, UserProfile
from .serializers import (
    UserActivitySerializer,
    UserPermissionSerializer,
    UserProfileSerializer,
    UserSerializer,
)

User = get_user_model()


class UserListView(generics.ListAPIView):
    """
    View for listing users (admin only).
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "code": 200,
            "message": "Users retrieved successfully",
            "data": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for user detail, update, and delete (admin only).
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        response_data = {
            "code": 200,
            "message": "User retrieved successfully",
            "data": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_data = {
            "code": 200,
            "message": "User updated successfully",
            "data": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        response_data = {
            "code": 200,
            "message": "User deleted successfully",
            "data": None,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for user profile management.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        response_data = {
            "code": 200,
            "message": "Profile retrieved successfully",
            "data": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_data = {
            "code": 200,
            "message": "Profile updated successfully",
            "data": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserActivityView(generics.ListAPIView):
    """
    View for user activity tracking.
    """

    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "code": 200,
            "message": "User activities retrieved successfully",
            "data": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserPermissionView(generics.ListCreateAPIView):
    """
    View for user permission management.
    """

    serializer_class = UserPermissionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserPermission.objects.all()
        return UserPermission.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "code": 200,
            "message": "User permissions retrieved successfully",
            "data": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(granted_by=request.user)

        response_data = {
            "code": 201,
            "message": "Permission granted successfully",
            "data": serializer.data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
