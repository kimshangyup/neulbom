from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import HttpResponse
from django.views import View
from students.models import School
from authentication.decorators import (
    role_required, admin_required, instructor_required, student_required
)
from authentication.mixins import (
    RoleRequiredMixin, AdminRequiredMixin, InstructorRequiredMixin, StudentRequiredMixin
)

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for custom User model"""

    def setUp(self):
        """Set up test data"""
        self.school = School.objects.create(name='Test School')

    def test_create_admin_user(self):
        """Test creating admin user"""
        user = User.objects.create_user(
            username='admin_user',
            password='testpass123',
            email='admin@test.com',
            role='admin'
        )
        self.assertEqual(user.username, 'admin_user')
        self.assertEqual(user.role, 'admin')
        self.assertFalse(user.training_completed)
        self.assertIsNone(user.affiliated_school)
        self.assertTrue(user.check_password('testpass123'))

    def test_create_instructor_user(self):
        """Test creating instructor user with school affiliation"""
        user = User.objects.create_user(
            username='instructor_user',
            password='testpass123',
            email='instructor@test.com',
            role='instructor',
            affiliated_school=self.school,
            training_completed=True
        )
        self.assertEqual(user.username, 'instructor_user')
        self.assertEqual(user.role, 'instructor')
        self.assertEqual(user.affiliated_school, self.school)
        self.assertTrue(user.training_completed)

    def test_create_student_user(self):
        """Test creating student user with school affiliation"""
        user = User.objects.create_user(
            username='student_user',
            password='testpass123',
            email='student@test.com',
            role='student',
            affiliated_school=self.school
        )
        self.assertEqual(user.username, 'student_user')
        self.assertEqual(user.role, 'student')
        self.assertEqual(user.affiliated_school, self.school)

    def test_create_superuser(self):
        """Test creating superuser"""
        user = User.objects.create_superuser(
            username='superuser',
            password='testpass123',
            email='super@test.com',
            role='admin'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.role, 'admin')

    def test_role_choices(self):
        """Test that role choices are enforced"""
        user = User.objects.create_user(
            username='test_user',
            password='testpass123',
            role='admin'
        )
        self.assertIn(user.role, ['admin', 'instructor', 'student'])

    def test_school_affiliation_nullable(self):
        """Test that affiliated_school can be null"""
        user = User.objects.create_user(
            username='no_school_user',
            password='testpass123',
            role='admin'
        )
        self.assertIsNone(user.affiliated_school)

    def test_user_string_representation(self):
        """Test User model __str__ method"""
        user = User.objects.create_user(
            username='test_user',
            password='testpass123',
            role='student'
        )
        self.assertEqual(str(user), 'test_user (Student)')


class PasswordValidationTest(TestCase):
    """Test cases for password validation"""

    def test_password_minimum_length(self):
        """Test password must be at least 8 characters"""
        with self.assertRaises(ValidationError):
            validate_password('short')

    def test_password_not_all_numeric(self):
        """Test password cannot be all numeric"""
        with self.assertRaises(ValidationError):
            validate_password('12345678')

    def test_password_not_common(self):
        """Test password cannot be too common"""
        with self.assertRaises(ValidationError):
            validate_password('password')

    def test_valid_password(self):
        """Test valid password passes validation"""
        try:
            validate_password('testpass123')
        except ValidationError:
            self.fail('Valid password should not raise ValidationError')


class LoginViewTest(TestCase):
    """Test cases for login view"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.login_url = reverse('authentication:login')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com',
            role='student'
        )

    def test_login_page_loads(self):
        """Test login page loads successfully"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, '아이디 또는 비밀번호가 올바르지 않습니다.')

    def test_login_with_missing_username(self):
        """Test login with missing username"""
        response = self.client.post(self.login_url, {
            'username': '',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '아이디와 비밀번호를 모두 입력해주세요.')

    def test_login_with_missing_password(self):
        """Test login with missing password"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '아이디와 비밀번호를 모두 입력해주세요.')

    def test_login_redirect_to_next_url(self):
        """Test login redirects to 'next' parameter"""
        next_url = '/some-page/'
        response = self.client.post(f'{self.login_url}?next={next_url}', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, next_url, fetch_redirect_response=False)


class LogoutViewTest(TestCase):
    """Test cases for logout view"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.logout_url = reverse('authentication:logout')
        self.login_url = reverse('authentication:login')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com',
            role='student'
        )

    def test_logout_redirects_to_login(self):
        """Test logout redirects to login page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)

    def test_logout_clears_session(self):
        """Test logout clears user session"""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(self.logout_url)
        response = self.client.get(self.login_url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_shows_success_message(self):
        """Test logout shows success message"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.logout_url, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '로그아웃되었습니다.')


class SessionConfigurationTest(TestCase):
    """Test cases for session configuration"""

    def test_session_cookie_age(self):
        """Test session cookie age is set to 24 hours"""
        from django.conf import settings
        self.assertEqual(settings.SESSION_COOKIE_AGE, 86400)

    def test_session_cookie_httponly(self):
        """Test session cookie is HTTP only"""
        from django.conf import settings
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)

    def test_session_cookie_samesite(self):
        """Test session cookie SameSite is set to Lax"""
        from django.conf import settings
        self.assertEqual(settings.SESSION_COOKIE_SAMESITE, 'Lax')


class AdminUserCreationTest(TestCase):
    """Test cases for user creation via Django admin"""

    def setUp(self):
        """Set up test data"""
        self.school = School.objects.create(name='Admin Test School')

    def test_create_admin_via_objects(self):
        """Test creating admin user via User.objects.create_user"""
        user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin',
            email='admin@test.com'
        )
        self.assertEqual(user.role, 'admin')
        self.assertTrue(User.objects.filter(username='admin_test').exists())

    def test_create_instructor_via_objects(self):
        """Test creating instructor user via User.objects.create_user"""
        user = User.objects.create_user(
            username='instructor_test',
            password='testpass123',
            role='instructor',
            email='instructor@test.com',
            affiliated_school=self.school
        )
        self.assertEqual(user.role, 'instructor')
        self.assertEqual(user.affiliated_school, self.school)

    def test_create_student_via_objects(self):
        """Test creating student user via User.objects.create_user"""
        user = User.objects.create_user(
            username='student_test',
            password='testpass123',
            role='student',
            email='student@test.com',
            affiliated_school=self.school
        )
        self.assertEqual(user.role, 'student')
        self.assertEqual(user.affiliated_school, self.school)


class RoleDecoratorTest(TestCase):
    """Test cases for role-based permission decorators"""

    def setUp(self):
        """Set up test users and request factory"""
        self.factory = RequestFactory()
        self.school = School.objects.create(name='Test School')

        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin',
            email='admin@test.com'
        )

        self.instructor_user = User.objects.create_user(
            username='instructor_test',
            password='testpass123',
            role='instructor',
            email='instructor@test.com',
            affiliated_school=self.school
        )

        self.student_user = User.objects.create_user(
            username='student_test',
            password='testpass123',
            role='student',
            email='student@test.com',
            affiliated_school=self.school
        )

    def test_admin_required_decorator_with_admin(self):
        """Test admin_required allows admin users"""
        @admin_required
        def admin_view(request):
            return HttpResponse('Success')

        request = self.factory.get('/admin-only/')
        request.user = self.admin_user
        response = admin_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')

    def test_admin_required_decorator_with_instructor(self):
        """Test admin_required denies instructor users"""
        @admin_required
        def admin_view(request):
            return HttpResponse('Success')

        request = self.factory.get('/admin-only/')
        request.user = self.instructor_user

        with self.assertRaises(PermissionDenied):
            admin_view(request)

    def test_admin_required_decorator_with_student(self):
        """Test admin_required denies student users"""
        @admin_required
        def admin_view(request):
            return HttpResponse('Success')

        request = self.factory.get('/admin-only/')
        request.user = self.student_user

        with self.assertRaises(PermissionDenied):
            admin_view(request)

    def test_instructor_required_decorator_with_admin(self):
        """Test instructor_required allows admin users"""
        @instructor_required
        def instructor_view(request):
            return HttpResponse('Success')

        request = self.factory.get('/instructor-area/')
        request.user = self.admin_user
        response = instructor_view(request)
        self.assertEqual(response.status_code, 200)

    def test_instructor_required_decorator_with_instructor(self):
        """Test instructor_required allows instructor users"""
        @instructor_required
        def instructor_view(request):
            return HttpResponse('Success')

        request = self.factory.get('/instructor-area/')
        request.user = self.instructor_user
        response = instructor_view(request)
        self.assertEqual(response.status_code, 200)

    def test_instructor_required_decorator_with_student(self):
        """Test instructor_required denies student users"""
        @instructor_required
        def instructor_view(request):
            return HttpResponse('Success')

        request = self.factory.get('/instructor-area/')
        request.user = self.student_user

        with self.assertRaises(PermissionDenied):
            instructor_view(request)

    def test_student_required_decorator_with_student(self):
        """Test student_required allows student users"""
        @student_required
        def student_view(request):
            return HttpResponse('Success')

        request = self.factory.get('/student-area/')
        request.user = self.student_user
        response = student_view(request)
        self.assertEqual(response.status_code, 200)

    def test_student_required_decorator_with_admin(self):
        """Test student_required denies admin users"""
        @student_required
        def student_view(request):
            return HttpResponse('Success')

        request = self.factory.get('/student-area/')
        request.user = self.admin_user

        with self.assertRaises(PermissionDenied):
            student_view(request)

    def test_role_required_decorator_multiple_roles(self):
        """Test role_required with multiple allowed roles"""
        @role_required('admin', 'instructor')
        def multi_role_view(request):
            return HttpResponse('Success')

        # Admin should access
        request = self.factory.get('/multi-role/')
        request.user = self.admin_user
        response = multi_role_view(request)
        self.assertEqual(response.status_code, 200)

        # Instructor should access
        request.user = self.instructor_user
        response = multi_role_view(request)
        self.assertEqual(response.status_code, 200)

        # Student should not access
        request.user = self.student_user
        with self.assertRaises(PermissionDenied):
            multi_role_view(request)


class RoleMixinTest(TestCase):
    """Test cases for role-based permission mixins"""

    def setUp(self):
        """Set up test users and request factory"""
        self.factory = RequestFactory()
        self.school = School.objects.create(name='Test School')

        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin',
            email='admin@test.com'
        )

        self.instructor_user = User.objects.create_user(
            username='instructor_test',
            password='testpass123',
            role='instructor',
            email='instructor@test.com',
            affiliated_school=self.school
        )

        self.student_user = User.objects.create_user(
            username='student_test',
            password='testpass123',
            role='student',
            email='student@test.com',
            affiliated_school=self.school
        )

    def test_admin_required_mixin_with_admin(self):
        """Test AdminRequiredMixin allows admin users"""
        class AdminView(AdminRequiredMixin, View):
            def get(self, request):
                return HttpResponse('Success')

        view = AdminView.as_view()
        request = self.factory.get('/admin-only/')
        request.user = self.admin_user
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_admin_required_mixin_with_instructor(self):
        """Test AdminRequiredMixin denies instructor users"""
        class AdminView(AdminRequiredMixin, View):
            def get(self, request):
                return HttpResponse('Success')

        view = AdminView.as_view()
        request = self.factory.get('/admin-only/')
        request.user = self.instructor_user

        with self.assertRaises(PermissionDenied):
            view(request)

    def test_instructor_required_mixin_with_admin(self):
        """Test InstructorRequiredMixin allows admin users"""
        class InstructorView(InstructorRequiredMixin, View):
            def get(self, request):
                return HttpResponse('Success')

        view = InstructorView.as_view()
        request = self.factory.get('/instructor-area/')
        request.user = self.admin_user
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_instructor_required_mixin_with_instructor(self):
        """Test InstructorRequiredMixin allows instructor users"""
        class InstructorView(InstructorRequiredMixin, View):
            def get(self, request):
                return HttpResponse('Success')

        view = InstructorView.as_view()
        request = self.factory.get('/instructor-area/')
        request.user = self.instructor_user
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_instructor_required_mixin_with_student(self):
        """Test InstructorRequiredMixin denies student users"""
        class InstructorView(InstructorRequiredMixin, View):
            def get(self, request):
                return HttpResponse('Success')

        view = InstructorView.as_view()
        request = self.factory.get('/instructor-area/')
        request.user = self.student_user

        with self.assertRaises(PermissionDenied):
            view(request)

    def test_student_required_mixin_with_student(self):
        """Test StudentRequiredMixin allows student users"""
        class StudentView(StudentRequiredMixin, View):
            def get(self, request):
                return HttpResponse('Success')

        view = StudentView.as_view()
        request = self.factory.get('/student-area/')
        request.user = self.student_user
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_student_required_mixin_with_admin(self):
        """Test StudentRequiredMixin denies admin users"""
        class StudentView(StudentRequiredMixin, View):
            def get(self, request):
                return HttpResponse('Success')

        view = StudentView.as_view()
        request = self.factory.get('/student-area/')
        request.user = self.admin_user

        with self.assertRaises(PermissionDenied):
            view(request)

    def test_role_required_mixin_custom_roles(self):
        """Test RoleRequiredMixin with custom role list"""
        class MultiRoleView(RoleRequiredMixin, View):
            allowed_roles = ['admin', 'instructor']

            def get(self, request):
                return HttpResponse('Success')

        view = MultiRoleView.as_view()

        # Admin should access
        request = self.factory.get('/multi-role/')
        request.user = self.admin_user
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # Instructor should access
        request.user = self.instructor_user
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # Student should not access
        request.user = self.student_user
        with self.assertRaises(PermissionDenied):
            view(request)


class PermissionDeniedHandlerTest(TestCase):
    """Test cases for 403 error handling"""

    def setUp(self):
        """Set up test users"""
        self.client = Client()
        self.school = School.objects.create(name='Test School')

        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin',
            email='admin@test.com'
        )

        self.student_user = User.objects.create_user(
            username='student_test',
            password='testpass123',
            role='student',
            email='student@test.com',
            affiliated_school=self.school
        )

    def test_403_error_page_renders(self):
        """Test that 403 error page renders with proper template"""
        from neulbom.views import permission_denied
        from django.http import HttpRequest

        request = HttpRequest()
        request.method = 'GET'

        response = permission_denied(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'403', response.content)
        self.assertIn('접근 권한이 없습니다'.encode('utf-8'), response.content)


class AdminSiteAccessTest(TestCase):
    """Test cases for Django admin access restriction"""

    def setUp(self):
        """Set up test users"""
        self.client = Client()
        self.school = School.objects.create(name='Test School')

        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin',
            email='admin@test.com',
            is_staff=True
        )

        self.instructor_user = User.objects.create_user(
            username='instructor_test',
            password='testpass123',
            role='instructor',
            email='instructor@test.com',
            affiliated_school=self.school,
            is_staff=True
        )

        self.student_user = User.objects.create_user(
            username='student_test',
            password='testpass123',
            role='student',
            email='student@test.com',
            affiliated_school=self.school,
            is_staff=True
        )

    def test_admin_user_can_access_admin_site(self):
        """Test that admin role users can access Django admin"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get('/admin/')

        # Should get 200 OK or redirect to admin index
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 302:
            # Follow redirect and verify we reach admin
            response = self.client.get(response.url)
            self.assertEqual(response.status_code, 200)

    def test_instructor_user_cannot_access_admin_site(self):
        """Test that instructor role users cannot access Django admin"""
        self.client.login(username='instructor_test', password='testpass123')
        response = self.client.get('/admin/')

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            '/accounts/login/' in response.url or '/admin/login/' in response.url,
            f"Expected redirect to login page, got: {response.url}"
        )

    def test_student_user_cannot_access_admin_site(self):
        """Test that student role users cannot access Django admin"""
        self.client.login(username='student_test', password='testpass123')
        response = self.client.get('/admin/')

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            '/accounts/login/' in response.url or '/admin/login/' in response.url,
            f"Expected redirect to login page, got: {response.url}"
        )

    def test_unauthenticated_user_redirected_to_login(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get('/admin/')

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            '/accounts/login/' in response.url or '/admin/login/' in response.url,
            f"Expected redirect to login page, got: {response.url}"
        )


class AuthenticationMiddlewareTest(TestCase):
    """Test cases for authentication enforcement middleware"""

    def setUp(self):
        """Set up test client and users"""
        self.client = Client()
        self.school = School.objects.create(name='Test School')

        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin',
            email='admin@test.com'
        )

    def test_public_routes_accessible_without_authentication(self):
        """Test that public routes are accessible without authentication"""
        public_routes = [
            '/accounts/login/',
            '/health/',
        ]

        for route in public_routes:
            response = self.client.get(route)
            # Should not redirect to login (200 or other non-302)
            self.assertNotEqual(
                response.status_code, 302,
                f"Public route {route} should not redirect to login"
            )

    def test_protected_routes_redirect_unauthenticated_users(self):
        """Test that protected routes redirect unauthenticated users to login"""
        # Admin route should be protected
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            '/accounts/login/' in response.url or '/admin/login/' in response.url,
            f"Expected redirect to login, got: {response.url}"
        )

    def test_authenticated_user_can_access_protected_routes(self):
        """Test that authenticated users can access protected routes"""
        self.client.login(username='admin_test', password='testpass123')

        # Admin user should access admin routes
        response = self.client.get('/admin/')
        # Should not redirect to /accounts/login/ (may redirect to admin index)
        if response.status_code == 302:
            self.assertNotIn('/accounts/login/', response.url)

    def test_middleware_preserves_next_parameter(self):
        """Test that middleware preserves 'next' parameter for login redirect"""
        response = self.client.get('/admin/')

        # Should redirect to login with next parameter
        self.assertEqual(response.status_code, 302)
        # Either our middleware redirects with ?next= or admin login does
        self.assertTrue(
            'next=' in response.url or '/admin/login/' in response.url,
            f"Expected 'next' parameter in redirect, got: {response.url}"
        )
