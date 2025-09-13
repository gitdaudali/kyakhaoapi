import boto3
import logging
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

logger = logging.getLogger(__name__)

from .models import Video, VideoView, VideoLike
from .serializers import (
    VideoListSerializer, VideoDetailSerializer, VideoCreateSerializer,
    VideoUpdateSerializer, VideoLikeToggleSerializer, VideoViewCreateSerializer
)
from .permissions import IsOwnerOrReadOnly


class VideoViewSet(ModelViewSet):
    """
    ViewSet for Video CRUD operations.
    """
    queryset = Video.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['uploaded_at', 'views_count', 'likes_count', 'title']
    ordering = ['-uploaded_at']
    filterset_fields = ['status', 'uploaded_by', 'format']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'list':
            return VideoListSerializer
        elif self.action == 'create':
            return VideoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VideoUpdateSerializer
        elif self.action == 'retrieve':
            return VideoDetailSerializer
        return VideoListSerializer
    
    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Return filtered queryset."""
        queryset = Video.objects.select_related('uploaded_by').prefetch_related('views', 'likes')
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(uploaded_by_id=user_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create video with file upload to S3."""
        video_file = self.request.FILES.get('video_file')
        
        if video_file:
            # Upload to S3 (placeholder implementation)
            s3_url = self.upload_to_s3(video_file)
            serializer.save(
                uploaded_by=self.request.user,
                file_url=s3_url,
                status='uploading'
            )
        else:
            serializer.save(uploaded_by=self.request.user)
    
    def perform_update(self, serializer):
        """Update video with optional file replacement."""
        video_file = self.request.FILES.get('video_file')
        
        if video_file:
            # Delete old file from S3 if exists
            old_video = self.get_object()
            if old_video.s3_key:
                self.delete_from_s3(old_video.s3_bucket, old_video.s3_key)
            
            # Upload new file to S3
            s3_url = self.upload_to_s3(video_file)
            serializer.save(file_url=s3_url, status='uploading')
        else:
            serializer.save()
    
    def perform_destroy(self, instance):
        """Delete video and associated S3 file."""
        # Delete from S3
        if instance.s3_key:
            self.delete_from_s3(instance.s3_bucket, instance.s3_key)
        
        # Delete from database
        instance.delete()
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve video and increment view count."""
        instance = self.get_object()
        
        # Increment view count
        instance.increment_views()
        
        # Create view record
        VideoView.objects.create(
            video=instance,
            viewer=request.user if request.user.is_authenticated else None,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Toggle like for a video."""
        video = self.get_object()
        user = request.user
        
        try:
            like = VideoLike.objects.get(video=video, user=user)
            like.delete()
            video.decrement_likes()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        except VideoLike.DoesNotExist:
            VideoLike.objects.create(video=video, user=user)
            video.increment_likes()
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def views(self, request, pk=None):
        """Get video views."""
        video = self.get_object()
        views = video.views.all()
        serializer = VideoViewCreateSerializer(views, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        """Get video likes."""
        video = self.get_object()
        likes = video.likes.all()
        serializer = VideoViewCreateSerializer(likes, many=True)
        return Response(serializer.data)
    
    def upload_to_s3(self, file_obj):
        """Upload file to S3 and return URL."""
        from .utils import upload_video_to_s3
        
        try:
            # Use the S3 utility function
            result = upload_video_to_s3(file_obj)
            
            if result['success']:
                return result['url']
            else:
                raise Exception(f"Failed to upload file to S3: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            # Log error and raise exception
            logger.error(f"Failed to upload file to S3: {str(e)}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def delete_from_s3(self, bucket_name, key):
        """Delete file from S3."""
        from .utils import delete_video_from_s3
        
        try:
            # Use the S3 utility function
            result = delete_video_from_s3(bucket_name, key)
            
            if not result['success']:
                logger.error(f"Failed to delete file from S3: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            # Log error but don't raise exception to avoid blocking deletion
            logger.error(f"Failed to delete file from S3: {str(e)}")
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class VideoListAPIView(generics.ListAPIView):
    """
    API view for listing videos with filtering and pagination.
    """
    serializer_class = VideoListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['uploaded_at', 'views_count', 'likes_count', 'title']
    ordering = ['-uploaded_at']
    filterset_fields = ['status', 'uploaded_by', 'format']
    
    def get_queryset(self):
        """Return filtered queryset."""
        queryset = Video.objects.select_related('uploaded_by').filter(status='ready')
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(uploaded_by_id=user_id)
        
        return queryset


class VideoDetailAPIView(generics.RetrieveAPIView):
    """
    API view for retrieving video details.
    """
    serializer_class = VideoDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Return queryset with related data."""
        return Video.objects.select_related('uploaded_by').prefetch_related('views', 'likes')
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve video and increment view count."""
        instance = self.get_object()
        
        # Increment view count
        instance.increment_views()
        
        # Create view record
        VideoView.objects.create(
            video=instance,
            viewer=request.user if request.user.is_authenticated else None,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class VideoCreateAPIView(generics.CreateAPIView):
    """
    API view for creating videos with file upload.
    """
    serializer_class = VideoCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def perform_create(self, serializer):
        """Create video with file upload to S3."""
        video_file = self.request.FILES.get('video_file')
        
        if video_file:
            # Upload to S3 (placeholder implementation)
            s3_url = self.upload_to_s3(video_file)
            serializer.save(
                uploaded_by=self.request.user,
                file_url=s3_url,
                status='uploading'
            )
        else:
            serializer.save(uploaded_by=self.request.user)
    
    def upload_to_s3(self, file_obj):
        """Upload file to S3 and return URL."""
        from .utils import upload_video_to_s3
        
        try:
            result = upload_video_to_s3(file_obj)
            
            if result['success']:
                return result['url']
            else:
                raise Exception(f"Failed to upload file to S3: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")


class VideoUpdateAPIView(generics.UpdateAPIView):
    """
    API view for updating videos.
    """
    serializer_class = VideoUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'id'
    
    def get_queryset(self):
        """Return queryset."""
        return Video.objects.all()
    
    def perform_update(self, serializer):
        """Update video with optional file replacement."""
        video_file = self.request.FILES.get('video_file')
        
        if video_file:
            # Delete old file from S3 if exists
            old_video = self.get_object()
            if old_video.s3_key:
                self.delete_from_s3(old_video.s3_bucket, old_video.s3_key)
            
            # Upload new file to S3
            s3_url = self.upload_to_s3(video_file)
            serializer.save(file_url=s3_url, status='uploading')
        else:
            serializer.save()
    
    def upload_to_s3(self, file_obj):
        """Upload file to S3 and return URL."""
        from .utils import upload_video_to_s3
        
        try:
            result = upload_video_to_s3(file_obj)
            
            if result['success']:
                return result['url']
            else:
                raise Exception(f"Failed to upload file to S3: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def delete_from_s3(self, bucket_name, key):
        """Delete file from S3."""
        from .utils import delete_video_from_s3
        
        try:
            result = delete_video_from_s3(bucket_name, key)
            
            if not result['success']:
                logger.error(f"Failed to delete file from S3: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")


class VideoDeleteAPIView(generics.DestroyAPIView):
    """
    API view for deleting videos.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Return queryset."""
        return Video.objects.all()
    
    def perform_destroy(self, instance):
        """Delete video and associated S3 file."""
        # Delete from S3
        if instance.s3_key:
            self.delete_from_s3(instance.s3_bucket, instance.s3_key)
        
        # Delete from database
        instance.delete()
    
    def delete_from_s3(self, bucket_name, key):
        """Delete file from S3."""
        from .utils import delete_video_from_s3
        
        try:
            result = delete_video_from_s3(bucket_name, key)
            
            if not result['success']:
                logger.error(f"Failed to delete file from S3: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")


class VideoLikeToggleAPIView(generics.GenericAPIView):
    """
    API view for toggling video likes.
    """
    serializer_class = VideoLikeToggleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Toggle like for a video."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        video_id = serializer.validated_data['video_id']
        video = get_object_or_404(Video, id=video_id)
        user = request.user
        
        try:
            like = VideoLike.objects.get(video=video, user=user)
            like.delete()
            video.decrement_likes()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        except VideoLike.DoesNotExist:
            VideoLike.objects.create(video=video, user=user)
            video.increment_likes()
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
