from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
import logging
from .models import User

logger = logging.getLogger(__name__)


class RoleBasedAdminSite(AdminSite):
    """
    Custom AdminSite that restricts access to users with 'admin' role only.
    """
    site_header = "늘봄학교 관리"
    site_title = "늘봄학교 관리자"
    index_title = "관리자 대시보드"

    def has_permission(self, request):
        """
        Only allow admin role users or superusers to access Django admin.

        Args:
            request: HTTP request object

        Returns:
            bool: True if user is authenticated, active, and has 'admin' role or is superuser
        """
        is_allowed = (
            request.user.is_active
            and request.user.is_authenticated
            and (request.user.role == 'admin' or request.user.is_superuser)
        )

        if request.user.is_authenticated and not is_allowed:
            logger.warning(
                f"Admin access denied for {request.user.username} (role: {request.user.role})"
            )

        return is_allowed

    def login(self, request, extra_context=None):
        """
        Redirect to main login page instead of admin login.

        Args:
            request: HTTP request object
            extra_context: Extra context dictionary (optional)

        Returns:
            Redirect response
        """
        if request.method == 'GET' and self.has_permission(request):
            return redirect('admin:index')
        return redirect_to_login(request.get_full_path(), login_url='/accounts/login/')


# Replace default admin site with role-based admin site
admin_site = RoleBasedAdminSite(name='admin')


class UserAdmin(BaseUserAdmin):
    """
    Custom User admin interface with role-based fields
    """
    list_display = ('username', 'email', 'role', 'affiliated_school', 'training_completed', 'is_staff', 'is_active')
    list_filter = ('role', 'training_completed', 'is_staff', 'is_superuser', 'is_active', 'affiliated_school')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Role & Affiliation'), {'fields': ('role', 'affiliated_school', 'training_completed')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        (_('Role & Affiliation'), {
            'fields': ('role', 'affiliated_school', 'training_completed'),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )


# Register User model with custom admin site
admin_site.register(User, UserAdmin)
