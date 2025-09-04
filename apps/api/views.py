from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)


class BaseAPIView(APIView):
    """
    Base API view with standardized response formatting.
    """
    
    def success_response(self, data=None, message="Success", code=200):
        """
        Return a standardized success response.
        """
        response_data = {
            'code': code,
            'message': message,
            'data': data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def error_response(self, message="Error", code=400, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Return a standardized error response.
        """
        response_data = {
            'code': code,
            'message': message,
            'data': None
        }
        return Response(response_data, status=status_code)
    
    def not_found_response(self, message="Resource not found"):
        """
        Return a standardized 404 response.
        """
        return self.error_response(
            message=message,
            code=404,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    def unauthorized_response(self, message="Unauthorized"):
        """
        Return a standardized 401 response.
        """
        return self.error_response(
            message=message,
            code=401,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    def forbidden_response(self, message="Forbidden"):
        """
        Return a standardized 403 response.
        """
        return self.error_response(
            message=message,
            code=403,
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    def server_error_response(self, message="Internal server error"):
        """
        Return a standardized 500 response.
        """
        return self.error_response(
            message=message,
            code=500,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class HealthCheckView(BaseAPIView):
    """
    Health check endpoint for monitoring.
    """
    permission_classes = []
    
    def get(self, request):
        """
        Return health status of the API.
        """
        try:
            health_data = {
                'status': 'healthy',
                'timestamp': '2024-01-01T00:00:00Z',
                'version': '1.0.0'
            }
            return self.success_response(
                data=health_data,
                message="API is healthy"
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return self.server_error_response("Health check failed")


class APIInfoView(BaseAPIView):
    """
    API information endpoint.
    """
    permission_classes = []
    
    def get(self, request):
        """
        Return API information.
        """
        api_info = {
            'name': 'Cup Streaming API',
            'version': '1.0.0',
            'description': 'API for Cup Streaming platform',
            'endpoints': {
                'authentication': '/api/v1/auth/',
                'users': '/api/v1/users/',
                'health': '/api/v1/health/'
            }
        }
        return self.success_response(
            data=api_info,
            message="API information retrieved successfully"
        )


class ProtectedView(BaseAPIView):
    """
    Example protected view requiring authentication.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Return protected data.
        """
        user_data = {
            'id': request.user.id,
            'email': request.user.email,
            'username': request.user.username,
            'role': request.user.role
        }
        return self.success_response(
            data=user_data,
            message="Protected data retrieved successfully"
        )


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(BaseAPIView):
    """
    Webhook endpoint for external integrations.
    """
    permission_classes = []
    
    def post(self, request):
        """
        Handle webhook requests.
        """
        try:
            # Process webhook data
            webhook_data = request.data
            
            # Log webhook for debugging
            logger.info(f"Webhook received: {webhook_data}")
            
            return self.success_response(
                data={'received': True},
                message="Webhook processed successfully"
            )
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return self.server_error_response("Webhook processing failed")










