"""
Permission mixins and decorators for role-based access control.

This module provides both mixins for class-based views and decorators for
function-based views to restrict access based on user roles.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin that restricts class-based view access to users with specified roles.

    Usage:
        class MyView(RoleRequiredMixin, View):
            allowed_roles = ['admin', 'instructor']

            def get(self, request):
                ...

    Attributes:
        allowed_roles: List of role strings that are allowed to access the view.
                      Valid values: 'admin', 'instructor', 'student'

    Raises:
        PermissionDenied: If authenticated user's role is not in allowed_roles.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to check user role before processing request.

        Args:
            request: HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Response from parent dispatch if user has required role.

        Raises:
            PermissionDenied: If user role not in allowed_roles.
        """
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.role not in self.allowed_roles:
            logger.warning(
                f"Unauthorized access attempt by {request.user.username} "
                f"(role: {request.user.role}) to view requiring roles: {self.allowed_roles}"
            )
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    """
    Mixin that restricts access to administrator users only.

    Usage:
        class AdminOnlyView(AdminRequiredMixin, View):
            def get(self, request):
                ...
    """
    allowed_roles = ['admin']


class InstructorRequiredMixin(RoleRequiredMixin):
    """
    Mixin that restricts access to administrators and instructors.

    Usage:
        class InstructorView(InstructorRequiredMixin, View):
            def get(self, request):
                ...
    """
    allowed_roles = ['admin', 'instructor']


class StudentRequiredMixin(RoleRequiredMixin):
    """
    Mixin that restricts access to student users only.

    Usage:
        class StudentView(StudentRequiredMixin, View):
            def get(self, request):
                ...
    """
    allowed_roles = ['student']


# Function-based view decorators

def role_required(*roles):
    """
    Decorator to restrict function-based view access to users with specified roles.

    Usage:
        @role_required('admin', 'instructor')
        def my_view(request):
            ...

    Args:
        *roles: Variable number of role strings ('admin', 'instructor', 'student')

    Returns:
        Decorated function that checks user role before execution

    Raises:
        PermissionDenied: If authenticated user's role is not in specified roles
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                logger.warning(
                    f"Unauthorized access attempt by {request.user.username} "
                    f"(role: {request.user.role}) to view requiring roles: {roles}"
                )
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator to restrict function-based view access to administrators only.

    Usage:
        @admin_required
        def admin_view(request):
            ...

    Args:
        view_func: Function to decorate

    Returns:
        Decorated function that checks for admin role

    Raises:
        PermissionDenied: If user is not an administrator
    """
    return role_required('admin')(view_func)


def instructor_required(view_func):
    """
    Decorator to restrict function-based view access to administrators and instructors.

    Usage:
        @instructor_required
        def instructor_view(request):
            ...

    Args:
        view_func: Function to decorate

    Returns:
        Decorated function that checks for admin or instructor role

    Raises:
        PermissionDenied: If user is not an administrator or instructor
    """
    return role_required('admin', 'instructor')(view_func)
