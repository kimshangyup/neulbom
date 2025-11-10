"""
Health check views for monitoring and infrastructure
"""
from django.http import JsonResponse
from django.utils import timezone
from django.db import connection
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Basic health check endpoint that verifies:
    - Application is running
    - Database connectivity

    Returns JSON with status and timestamp.
    Response codes:
    - 200: Healthy
    - 503: Service Unavailable (database connection failed)
    """
    try:
        # Test database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        logger.info("Health check passed")

        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'service': 'neulbom'
        }, status=200)

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")

        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'disconnected',
            'error': str(e),
            'service': 'neulbom'
        }, status=503)
