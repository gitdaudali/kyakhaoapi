from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'videos', views.VideoViewSet, basename='video')

# The API URLs are now determined automatically by the router
urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Individual API view URLs (alternative to ViewSet)
    path('list/', views.VideoListAPIView.as_view(), name='video-list'),
    path('detail/<uuid:id>/', views.VideoDetailAPIView.as_view(), name='video-detail'),
    path('create/', views.VideoCreateAPIView.as_view(), name='video-create'),
    path('update/<uuid:id>/', views.VideoUpdateAPIView.as_view(), name='video-update'),
    path('delete/<uuid:id>/', views.VideoDeleteAPIView.as_view(), name='video-delete'),
    path('like/', views.VideoLikeToggleAPIView.as_view(), name='video-like-toggle'),
]
