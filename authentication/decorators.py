"""
Permission decorators for role-based access control.

This module provides decorators to restrict view access based on user roles.
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


def role_required(*allowed_roles):
    """
    Decorator that restricts view access to users with specified roles.

    Usage:
        @role_required('admin', 'instructor')
        def my_view(request):
            ...

    Args:
        *allowed_roles: Variable number of role strings that are allowed to access the view.
                       Valid values: 'admin', 'instructor', 'student'

    Returns:
        Decorated view function that enforces role-based access control.

    Raises:
        PermissionDenied: If authenticated user's role is not in allowed_roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                logger.warning(
                    f"Unauthorized access attempt by {request.user.username} "
                    f"(role: {request.user.role}) to view requiring roles: {allowed_roles}"
                )
                raise PermissionDenied
        return wrapper
    return decorator


# Convenience decorators for common role combinations
admin_required = role_required('admin')
admin_required.__doc__ = """
Decorator that restricts view access to administrator users only.

Usage:
    @admin_required
    def admin_view(request):
        ...
"""

instructor_required = role_required('admin', 'instructor')
instructor_required.__doc__ = """
Decorator that restricts view access to administrators and instructors.

Usage:
    @instructor_required
    def instructor_view(request):
        ...
"""

student_required = role_required('student')
student_required.__doc__ = """
Decorator that restricts view access to student users only.

Usage:
    @student_required
    def student_view(request):
        ...
"""
