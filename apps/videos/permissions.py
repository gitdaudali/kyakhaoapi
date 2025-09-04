from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the video.
        return obj.uploaded_by == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins to access an object.
    """
    
    def has_object_permission(self, request, view, obj):
        # Allow admins to access everything
        if request.user.is_staff or request.user.role == 'admin':
            return True
        
        # Allow owners to access their own videos
        return obj.uploaded_by == request.user


class CanUploadVideo(permissions.BasePermission):
    """
    Custom permission to check if user can upload videos.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Allow all authenticated users to upload videos
        # You can add additional checks here (e.g., user role, subscription status)
        return True


class CanViewVideo(permissions.BasePermission):
    """
    Custom permission to check if user can view videos.
    """
    
    def has_permission(self, request, view):
        # Allow public access to view videos
        return True
    
    def has_object_permission(self, request, view, obj):
        # Allow public access to view videos
        return True
