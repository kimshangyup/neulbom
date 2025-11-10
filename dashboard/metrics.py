"""
Dashboard metrics calculation service.
Provides core program metrics and visitor analytics with caching.
"""

from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
import logging
import time

from authentication.models import User
from students.models import School, Student

logger = logging.getLogger(__name__)


class DashboardMetrics:
    """Service class for dashboard metrics calculation"""

    CACHE_KEY = 'admin_dashboard_metrics'
    INSTRUCTOR_ACTIVITY_CACHE_KEY = 'instructor_activity_data'
    CACHE_TIMEOUT = 300  # 5 minutes

    @staticmethod
    def get_core_metrics():
        """
        Get core program metrics with 5-minute caching.

        Returns:
            dict: {
                'total_schools': int,
                'total_instructors': int,
                'total_students': int,
                'active_spaces': int,
                'visitor_stats': {'daily': int, 'weekly': int, 'monthly': int},
                'timestamp': str (ISO 8601 format)
            }
        """
        metrics = cache.get(DashboardMetrics.CACHE_KEY)
        if metrics is not None:
            logger.debug("Dashboard metrics retrieved from cache")
            return metrics

        logger.info("Calculating dashboard metrics")
        start_time = time.time()

        try:
            metrics = {
                'total_schools': School.objects.count(),
                'total_instructors': User.objects.filter(role='instructor').count(),
                # Only count students in classes with instructors
                'total_students': Student.objects.filter(
                    class_assignment__instructor__isnull=False
                ).count(),
                # Only count active spaces in classes with instructors
                'active_spaces': Student.objects.filter(
                    class_assignment__instructor__isnull=False
                ).exclude(zep_space_url='').count(),
                'visitor_stats': DashboardMetrics.get_visitor_stats(),
                'timestamp': timezone.now().isoformat(),
            }

            elapsed = time.time() - start_time
            logger.info(f"Dashboard metrics calculated in {elapsed:.2f}s")

            cache.set(DashboardMetrics.CACHE_KEY, metrics, DashboardMetrics.CACHE_TIMEOUT)
            return metrics

        except Exception as e:
            logger.error(f"Failed to calculate dashboard metrics: {e}")
            # Return empty metrics on error
            return {
                'total_schools': 0,
                'total_instructors': 0,
                'total_students': 0,
                'active_spaces': 0,
                'visitor_stats': {'daily': 0, 'weekly': 0, 'monthly': 0},
                'timestamp': timezone.now().isoformat(),
                'error': str(e)
            }

    @staticmethod
    def get_visitor_stats():
        """
        Get visitor analytics for daily, weekly, monthly periods.

        Returns:
            dict: {'daily': int, 'weekly': int, 'monthly': int}
        """
        try:
            from dashboard.models import VisitorLog

            now = timezone.now()
            return {
                'daily': VisitorLog.objects.filter(
                    timestamp__gte=now - timedelta(hours=24)
                ).count(),
                'weekly': VisitorLog.objects.filter(
                    timestamp__gte=now - timedelta(days=7)
                ).count(),
                'monthly': VisitorLog.objects.filter(
                    timestamp__gte=now - timedelta(days=30)
                ).count(),
            }
        except Exception as e:
            logger.warning(f"Failed to get visitor stats (model may not exist yet): {e}")
            # Return zeros if VisitorLog model doesn't exist yet (will be created in Task 3)
            return {'daily': 0, 'weekly': 0, 'monthly': 0}

    @staticmethod
    def get_instructor_activity():
        """
        Get instructor activity data with aggregations and 5-minute caching.

        Returns:
            list: [{
                'id': int,
                'username': str,
                'full_name': str,
                'school_name': str,
                'last_login': datetime,
                'class_count': int,
                'student_count': int,
                'spaces_created': int,
                'is_inactive': bool
            }]
        """
        # Check cache first
        cached_data = cache.get(DashboardMetrics.INSTRUCTOR_ACTIVITY_CACHE_KEY)
        if cached_data is not None:
            logger.debug("Instructor activity retrieved from cache")
            return cached_data

        logger.info("Calculating instructor activity data")
        start_time = time.time()

        try:
            thirty_days_ago = timezone.now() - timedelta(days=30)

            # Query instructors with aggregated metrics (only count classes with instructors)
            instructors = User.objects.filter(role='instructor').select_related(
                'affiliated_school'
            ).annotate(
                class_count=Count(
                    'taught_classes',
                    filter=Q(taught_classes__instructor__isnull=False),
                    distinct=True
                ),
                student_count=Count(
                    'taught_classes__students',
                    filter=Q(taught_classes__instructor__isnull=False),
                    distinct=True
                ),
                spaces_created=Count(
                    'taught_classes__students',
                    filter=Q(taught_classes__instructor__isnull=False) & ~Q(taught_classes__students__zep_space_url=''),
                    distinct=True
                )
            ).order_by('-last_login')

            # Process and structure data
            result = []
            for instructor in instructors:
                # Determine if inactive (no login > 30 days)
                is_inactive = True
                if instructor.last_login:
                    is_inactive = instructor.last_login < thirty_days_ago

                full_name = instructor.get_full_name() or instructor.username
                school_name = instructor.affiliated_school.name if instructor.affiliated_school else 'N/A'

                result.append({
                    'id': instructor.id,
                    'username': instructor.username,
                    'full_name': full_name,
                    'school_name': school_name,
                    'last_login': instructor.last_login,
                    'class_count': instructor.class_count,
                    'student_count': instructor.student_count,
                    'spaces_created': instructor.spaces_created,
                    'is_inactive': is_inactive
                })

            elapsed = time.time() - start_time
            logger.info(f"Instructor activity calculated in {elapsed:.2f}s ({len(result)} instructors)")

            # Cache the result
            cache.set(
                DashboardMetrics.INSTRUCTOR_ACTIVITY_CACHE_KEY,
                result,
                DashboardMetrics.CACHE_TIMEOUT
            )

            return result

        except Exception as e:
            logger.error(f"Failed to calculate instructor activity: {e}")
            return []
