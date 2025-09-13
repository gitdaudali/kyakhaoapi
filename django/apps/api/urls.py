from django.urls import path

from .views import APIInfoView, HealthCheckView, ProtectedView, WebhookView

app_name = "api"

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health_check"),
    path("info/", APIInfoView.as_view(), name="api_info"),
    path("protected/", ProtectedView.as_view(), name="protected"),
    path("webhook/", WebhookView.as_view(), name="webhook"),
]
