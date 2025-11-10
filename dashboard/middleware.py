"""
Visitor tracking middleware for public landing page analytics.
"""

from django.utils import timezone
from dashboard.models import VisitorLog
import logging

logger = logging.getLogger(__name__)


class VisitorTrackingMiddleware:
    """
    Track visitor analytics for public landing page.
    Logs IP address, user agent, and timestamp for each visit to the root path.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track only public landing page (root path)
        if request.path == '/' and request.method == 'GET':
            try:
                VisitorLog.objects.create(
                    timestamp=timezone.now(),
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:200],
                    path=request.path
                )
                logger.debug(f"Visitor logged: {self.get_client_ip(request)}")
            except Exception as e:
                logger.error(f"Failed to log visitor: {e}")

        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request):
        """
        Get client IP address from request.
        Handles X-Forwarded-For header for reverse proxy setups.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
