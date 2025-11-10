"""
Dashboard metrics and analytics

Functions for calculating dashboard statistics and metrics
"""

from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from authentication.models import User
from students.models import School, Class, Student
import logging

logger = logging.getLogger(__name__)


def get_core_metrics():
    """
    Get core metrics for administrator dashboard

    Returns:
        dict: Dictionary containing core metrics
    """
    metrics = {
        'total_schools': School.objects.count(),
        'total_instructors': User.objects.filter(role='instructor').count(),
        'total_students': Student.objects.count(),
        'active_spaces': Student.objects.exclude(zep_space_url='').count(),
    }

    return metrics


def get_visitor_analytics():
    """
    Get visitor analytics (placeholder for future implementation)

    Returns:
        dict: Visitor count by time period
    """
    # TODO: Implement actual visitor tracking in Story 3.1+
    # For now, return placeholder data
    return {
        'daily': 0,
        'weekly': 0,
        'monthly': 0,
    }


def get_instructor_activity_summary():
    """
    Get summary of instructor activity

    Returns:
        list: List of instructor activity data
    """
    instructors = User.objects.filter(role='instructor').annotate(
        class_count=Count('taught_classes', distinct=True),
        student_count=Count('taught_classes__students', distinct=True)
    ).select_related('affiliated_school')

    # Calculate activity status based on last login
    thirty_days_ago = timezone.now() - timedelta(days=30)

    activity_data = []
    for instructor in instructors:
        is_active = (
            instructor.last_login and
            instructor.last_login >= thirty_days_ago
        )

        activity_data.append({
            'id': instructor.id,
            'username': instructor.username,
            'name': instructor.get_full_name() or instructor.username,
            'school': instructor.affiliated_school.name if instructor.affiliated_school else '-',
            'class_count': instructor.class_count,
            'student_count': instructor.student_count,
            'last_login': instructor.last_login,
            'is_active': is_active,
            'training_completed': instructor.training_completed,
        })

    return activity_data


def get_recent_activities(limit=10):
    """
    Get recent system activities (placeholder)

    Args:
        limit: Maximum number of activities to return

    Returns:
        list: List of recent activities
    """
    activities = []

    # Get recent students
    recent_students = Student.objects.select_related(
        'user', 'class_assignment'
    ).order_by('-created_at')[:limit]

    for student in recent_students:
        activities.append({
            'type': 'student_created',
            'description': f'학생 "{student.name}" 등록됨',
            'timestamp': student.created_at,
            'related_object': student,
        })

    # Get recent classes
    recent_classes = Class.objects.select_related(
        'school', 'instructor'
    ).order_by('-created_at')[:limit]

    for cls in recent_classes:
        activities.append({
            'type': 'class_created',
            'description': f'학급 "{cls.name}" 생성됨',
            'timestamp': cls.created_at,
            'related_object': cls,
        })

    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)

    return activities[:limit]


def get_space_statistics():
    """
    Get statistics about ZEP spaces

    Returns:
        dict: Space-related statistics
    """
    total_students = Student.objects.count()
    students_with_spaces = Student.objects.exclude(zep_space_url='').count()

    # Get failed space creations
    from students.models import FailedSpaceCreation
    failed_spaces = FailedSpaceCreation.objects.filter(resolved=False).count()

    completion_rate = 0
    if total_students > 0:
        completion_rate = round((students_with_spaces / total_students) * 100, 1)

    return {
        'total_students': total_students,
        'spaces_created': students_with_spaces,
        'spaces_pending': total_students - students_with_spaces,
        'failed_creations': failed_spaces,
        'completion_rate': completion_rate,
    }


def get_class_statistics():
    """
    Get statistics about classes

    Returns:
        dict: Class-related statistics
    """
    total_classes = Class.objects.count()

    # Classes by semester
    classes_by_semester = Class.objects.values('semester').annotate(
        count=Count('id')
    )

    # Classes by school
    classes_by_school = Class.objects.values(
        'school__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]  # Top 5 schools

    return {
        'total_classes': total_classes,
        'by_semester': list(classes_by_semester),
        'by_school': list(classes_by_school),
    }
