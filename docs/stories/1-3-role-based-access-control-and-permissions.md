# Story 1.3: Role-Based Access Control and Permissions

Status: review

## Story

As an administrator,
I want role-based access control enforced throughout the application,
so that users can only access features appropriate to their role.

## Acceptance Criteria

1. Permission decorators/mixins created for role-based view protection
2. Administrator role has access to instructor management and system metrics
3. Instructor role has access to student management and space management
4. Student role has access only to login (no management UI per requirements)
5. Unauthorized access attempts redirect to appropriate error page
6. Django admin access restricted to administrator role only
7. Middleware enforces authentication for all non-public routes

## Tasks / Subtasks

- [x] Task 1: Create permission decorators and mixins (AC: 1)
  - [x] Create authentication/decorators.py with @login_required_role decorator
  - [x] Implement @admin_required decorator (checks user.role == 'admin')
  - [x] Implement @instructor_required decorator (checks user.role in ['admin', 'instructor'])
  - [x] Implement @student_required decorator (checks user.role == 'student')
  - [x] Create authentication/mixins.py with RoleRequiredMixin for class-based views
  - [x] Write unit tests for all decorators

- [x] Task 2: Implement error handling for unauthorized access (AC: 5)
  - [x] Create templates/errors/403.html with user-friendly error message
  - [x] Update decorators to redirect to 403 page on authorization failure
  - [x] Add logging for unauthorized access attempts
  - [x] Test 403 page rendering and redirect behavior

- [x] Task 3: Restrict Django admin access to administrators (AC: 6)
  - [x] Create custom AdminSite class that checks user.role == 'admin'
  - [x] Override admin login to enforce role-based access
  - [x] Update authentication/admin.py to use custom admin site
  - [x] Test admin access for all three roles (admin allowed, others denied)

- [x] Task 4: Create authentication enforcement middleware (AC: 7)
  - [x] Create authentication/middleware.py with AuthenticationEnforcementMiddleware
  - [x] Define list of public URL patterns (login, public landing page)
  - [x] Redirect unauthenticated users to login page for protected routes
  - [x] Add middleware to MIDDLEWARE setting in settings.py
  - [x] Test middleware behavior for authenticated and unauthenticated users

- [x] Task 5: Testing and validation (All ACs)
  - [x] Write integration tests for role-based access to different views
  - [x] Test admin access restriction
  - [x] Test middleware enforcement on protected routes
  - [x] Test public routes remain accessible
  - [x] Verify error page displays correctly
  - [x] Test decorator behavior with different user roles

## Dev Notes

### Architecture Constraints and Patterns

**From Architecture** [Source: docs/architecture.md#Project-Structure]
- Authentication app should include decorators.py for @admin_required, @instructor_required
- Multi-app structure: accounts, instructors, students, spaces, dashboard
- Role-based access maps to app-level boundaries
- Django built-in auth system with CustomUser role field

**From PRD** [Source: docs/PRD.md#Functional-Requirements]
- FR002: System shall enforce role-based access control with three permission levels: administrator, instructor, and student
- Administrator functions: instructor management, system metrics
- Instructor functions: student management (CSV upload), space management
- Student functions: login only (no management UI)

**Security Requirements** [Source: docs/architecture.md#Security-Architecture]
- CSRF protection enabled (Django default)
- Session-based authentication
- Unauthorized access must be logged
- Clear error messages for access denial

**URL Structure** [Source: docs/architecture.md#Implementation-Patterns]
- Public routes: /, /accounts/login/, /accounts/logout/
- Admin routes: /admin/*, /dashboard/admin/*
- Instructor routes: /students/*, /spaces/*, /dashboard/instructor/*
- Student routes: None (students only authenticate, no UI access)

### Learnings from Previous Story

**From Story 1.2: User Model and Role-Based Authentication (Status: done)**

- **User Model Available**: `authentication/models.py` has User model with role field
  - Role choices: 'admin', 'instructor', 'student'
  - User.role attribute can be checked directly
  - Model includes affiliated_school FK and training_completed boolean

- **Authentication Infrastructure**:
  - Login/logout views at `authentication/views.py` (authentication/views.py:9-50)
  - URL patterns configured at /accounts/login/ and /accounts/logout/
  - Session management configured (24-hour timeout)
  - CSRF protection enabled

- **Test Framework Established**:
  - `authentication/tests.py` has 26 comprehensive tests
  - Test patterns: Django TestCase, Client for view testing
  - Follow established patterns: Korean messages, English logs
  - Test users available: admin_test, instructor_test, student_test (all with password: testpass123)

- **Files to Reference/Extend**:
  - `authentication/models.py` - User model with role field
  - `authentication/views.py` - Login/logout implementation
  - `authentication/admin.py` - Custom UserAdmin configuration
  - `authentication/tests.py` - Test framework and patterns

- **Korean Localization Pattern**:
  - User-facing error messages in Korean
  - Log messages in English
  - Follow pattern from login view: messages.error(request, '한국어 메시지')

[Source: stories/1-2-user-model-and-role-based-authentication.md#Dev-Agent-Record]

### Implementation Notes

**Decorator Pattern:**
```python
# authentication/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

def role_required(*allowed_roles):
    """
    Decorator that restricts view access to users with specified roles.
    Usage: @role_required('admin', 'instructor')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                logger.warning(f"Unauthorized access attempt by {request.user.username} (role: {request.user.role})")
                raise PermissionDenied
        return wrapper
    return decorator

# Convenience decorators
admin_required = role_required('admin')
instructor_required = role_required('admin', 'instructor')
student_required = role_required('student')
```

**Mixin Pattern for Class-Based Views:**
```python
# authentication/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin that restricts view access to users with specified roles.
    Usage: class MyView(RoleRequiredMixin, View):
               allowed_roles = ['admin', 'instructor']
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.role not in self.allowed_roles:
            logger.warning(f"Unauthorized access attempt by {request.user.username} (role: {request.user.role})")
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
```

**Custom Admin Site:**
```python
# authentication/admin.py
from django.contrib.admin import AdminSite
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

class RoleBasedAdminSite(AdminSite):
    def has_permission(self, request):
        """
        Only allow admin role users to access Django admin
        """
        return request.user.is_active and request.user.is_authenticated and request.user.role == 'admin'

    def login(self, request, extra_context=None):
        """
        Redirect to main login page instead of admin login
        """
        if request.method == 'GET' and self.has_permission(request):
            return redirect('admin:index')
        return redirect_to_login(request.get_full_path(), login_url='authentication:login')

# Replace default admin site
admin_site = RoleBasedAdminSite(name='admin')
```

**Middleware Pattern:**
```python
# authentication/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
import re

class AuthenticationEnforcementMiddleware:
    """
    Middleware that enforces authentication for all routes except public ones
    """
    PUBLIC_URLS = [
        r'^/$',  # Landing page
        r'^/accounts/login/',
        r'^/accounts/logout/',
        r'^/static/',
        r'^/media/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            # Check if current URL is public
            path = request.path_info
            is_public = any(re.match(pattern, path) for pattern in self.PUBLIC_URLS)

            if not is_public:
                return redirect('authentication:login')

        response = self.get_response(request)
        return response
```

**403 Error Template:**
```html
<!-- templates/errors/403.html -->
{% load static %}
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>접근 권한 없음 - 늘봄학교</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="h-full bg-gray-50">
    <div class="min-h-full flex items-center justify-center py-12 px-4">
        <div class="max-w-md w-full text-center">
            <h1 class="text-6xl font-bold text-gray-900 mb-4">403</h1>
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">접근 권한이 없습니다</h2>
            <p class="text-gray-600 mb-8">
                이 페이지에 접근할 권한이 없습니다.<br>
                계정의 권한을 확인해주세요.
            </p>
            <a href="/" class="inline-block bg-indigo-600 text-white px-6 py-3 rounded-md hover:bg-indigo-700">
                홈으로 돌아가기
            </a>
        </div>
    </div>
</body>
</html>
```

### Project Structure Notes

**Expected Files to Create:**
```
authentication/
├── decorators.py           # Role-based permission decorators
├── mixins.py              # Class-based view mixins
└── middleware.py          # Authentication enforcement middleware

templates/
└── errors/
    └── 403.html           # Forbidden error page
```

**Files to Modify:**
```
authentication/admin.py     # Add custom AdminSite
authentication/tests.py     # Add decorator and permission tests
neulbom/settings.py        # Add middleware to MIDDLEWARE list
neulbom/urls.py            # Configure 403 error handler
```

### Testing Standards

**Test Coverage Requirements:**
- Unit tests for each decorator (@admin_required, @instructor_required, @student_required)
- Tests for RoleRequiredMixin with different roles
- Tests for custom AdminSite role restriction
- Tests for middleware enforcement on protected routes
- Integration tests for 403 error page rendering
- Tests for public routes remaining accessible

**Test Scenarios:**
1. Admin user accessing admin-only view → Success
2. Instructor user accessing admin-only view → 403 error
3. Student user accessing instructor view → 403 error
4. Unauthenticated user accessing protected route → Redirect to login
5. Admin accessing Django admin → Success
6. Instructor accessing Django admin → 403 or redirect
7. Public routes accessible without authentication

**Test Framework:**
- Django's built-in TestCase
- Use existing test users from Story 1.2 (admin_test, instructor_test, student_test)
- Follow patterns from authentication/tests.py

### References

- [Epic 1 Details](../epics.md#Epic-1-Platform-Foundation-&-Authentication)
- [Story 1.3 Acceptance Criteria](../epics.md#Story-1.3-Role-Based-Access-Control-and-Permissions)
- [Architecture - Authentication](../architecture.md#Decision-Summary)
- [Architecture - Project Structure](../architecture.md#Project-Structure)
- [PRD - Functional Requirements](../PRD.md#Functional-Requirements)
- [Previous Story 1.2](./1-2-user-model-and-role-based-authentication.md)

## Dev Agent Record

### Context Reference

No context file was available for this story. Implementation proceeded using story file and Dev Notes only.

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

**Implementation Plan:**
1. Created permission decorators (role_required, admin_required, instructor_required, student_required) in authentication/decorators.py
2. Created class-based view mixins (RoleRequiredMixin and convenience subclasses) in authentication/mixins.py
3. Implemented 403 error handling with Korean error page template
4. Created custom RoleBasedAdminSite to restrict Django admin to admin role only
5. Built AuthenticationEnforcementMiddleware to enforce authentication on protected routes
6. Added comprehensive test coverage (52 tests total, all passing)

**Testing Approach:**
- Unit tests for decorators and mixins with all three user roles
- Integration tests for admin site access restriction
- Middleware tests for public vs protected route handling
- 403 error page rendering validation

### Completion Notes List

✅ **All Tasks Completed Successfully**

**Task 1 - Permission Decorators/Mixins:**
- Created authentication/decorators.py with role-based decorators
- Created authentication/mixins.py with class-based view mixins
- Added 17 comprehensive unit tests (all passing)

**Task 2 - Error Handling:**
- Created templates/errors/403.html with Korean user-friendly message
- Implemented custom permission_denied view in neulbom/views.py
- Configured handler403 in urls.py
- Updated settings.py TEMPLATES to include BASE_DIR/templates

**Task 3 - Admin Access Restriction:**
- Created RoleBasedAdminSite class with role checking
- Modified authentication/admin.py to use custom admin site
- Updated neulbom/urls.py to use admin_site instead of default
- Added 4 admin access tests (all passing)

**Task 4 - Middleware:**
- Created authentication/middleware.py with AuthenticationEnforcementMiddleware
- Defined public URL patterns (/, /accounts/*, /static/*, /media/*, /health/)
- Added middleware to settings.py MIDDLEWARE list
- Added 4 middleware tests (all passing)

**Task 5 - Full Validation:**
- Ran complete authentication test suite: 52 tests, 100% passing
- Validated all 7 acceptance criteria are met
- Confirmed logging works correctly for unauthorized access attempts

**Key Implementation Decisions:**
1. Used functools.wraps to preserve decorated function metadata
2. Implemented logging at WARNING level for security events (unauthorized access)
3. Leveraged Django's PermissionDenied exception for consistent 403 handling
4. Placed authentication middleware last in stack (after AuthenticationMiddleware)
5. Used regex patterns for flexible public URL matching

### File List

**New Files Created:**
- authentication/decorators.py
- authentication/mixins.py
- authentication/middleware.py
- templates/errors/403.html
- neulbom/views.py

**Files Modified:**
- authentication/admin.py (added RoleBasedAdminSite)
- authentication/tests.py (added 26 new tests)
- neulbom/settings.py (TEMPLATES DIRS, MIDDLEWARE)
- neulbom/urls.py (admin_site, handler403)

## Change Log

- **2025-11-03**: Story completed - All 5 tasks implemented and tested (52 tests passing, 100% AC coverage)
