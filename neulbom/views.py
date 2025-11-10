"""
Custom views for the neulbom project.
"""

from django.shortcuts import render
from authentication.decorators import admin_required
from .dashboard import (
    get_core_metrics,
    get_visitor_analytics,
    get_instructor_activity_summary,
    get_recent_activities,
    get_space_statistics,
    get_class_statistics,
)


def landing_page(request):
    """
    Public landing page for Neulbom program.

    Accessible without authentication. Displays program information,
    branding, and participating schools.

    Args:
        request: HTTP request object

    Returns:
        Rendered landing page
    """
    from students.models import Student, School

    # Get public student spaces
    public_spaces = Student.objects.filter(
        is_public=True,
        zep_space_url__isnull=False
    ).exclude(zep_space_url='').select_related(
        'class_assignment__school'
    ).order_by('-created_at')[:12]  # Show latest 12 public spaces

    # Get participating schools
    schools = School.objects.all().order_by('name')

    context = {
        'program_name': '늘봄학교',
        'program_description': '서울시 늘봄교육을 위한 ZEP',
        'program_mission': '13개 대학과 함께하는 초등학생 맞춤형 교육',
        'public_spaces': public_spaces,
        'schools': schools,
    }
    return render(request, 'landing.html', context)


@admin_required
def admin_dashboard(request):
    """
    Administrator dashboard with core metrics and analytics

    Displays:
    - Core metrics (schools, instructors, students, spaces)
    - Visitor analytics
    - Instructor activity summary
    - Recent activities
    - Space and class statistics

    Args:
        request: HTTP request object

    Returns:
        Rendered admin dashboard
    """
    context = {
        'core_metrics': get_core_metrics(),
        'visitor_analytics': get_visitor_analytics(),
        'instructor_activity': get_instructor_activity_summary(),
        'recent_activities': get_recent_activities(limit=10),
        'space_statistics': get_space_statistics(),
        'class_statistics': get_class_statistics(),
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


def permission_denied(request, exception=None):
    """
    Custom 403 error handler.

    Renders a user-friendly Korean error page when PermissionDenied is raised.

    Args:
        request: HTTP request object
        exception: The exception that triggered the 403 response (optional)

    Returns:
        Rendered 403 error page with 403 status code
    """
    return render(request, 'errors/403.html', status=403)
