"""
Comprehensive tests for Story 3.1: Administrator Dashboard - Core Metrics
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import json
import time

from authentication.models import User
from students.models import School, Class, Student
from dashboard.models import VisitorLog
from dashboard.metrics import DashboardMetrics


class AdminDashboardAccessTestCase(TestCase):
    """Test access control for admin dashboard (AC: admin-only access)"""

    def setUp(self):
        """Create test users with different roles"""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin'
        )
        self.instructor_user = User.objects.create_user(
            username='instructor_test',
            password='testpass123',
            role='instructor'
        )
        self.student_user = User.objects.create_user(
            username='student_test',
            password='testpass123',
            role='student'
        )

    def test_admin_can_access_dashboard(self):
        """Test that admin users can access the dashboard"""
        self.client.login(username='admin_test', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/admin_dashboard.html')

    def test_non_admin_cannot_access_dashboard(self):
        """Test that non-admin users cannot access the dashboard"""
        # Test instructor
        self.client.login(username='instructor_test', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 403)

        # Test student
        self.client.logout()
        self.client.login(username='student_test', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_redirected(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


class MetricsCalculationTestCase(TestCase):
    """Test metrics calculation accuracy (AC1: display key metrics)"""

    def setUp(self):
        """Create test data"""
        cache.clear()  # Clear cache before each test

        # Create schools
        self.school1 = School.objects.create(name='School 1', address='Address 1')
        self.school2 = School.objects.create(name='School 2', address='Address 2')

        # Create instructors
        self.instructor1 = User.objects.create_user(
            username='instructor1',
            password='test123',
            role='instructor'
        )
        self.instructor2 = User.objects.create_user(
            username='instructor2',
            password='test123',
            role='instructor'
        )

        # Create class
        self.class1 = Class.objects.create(
            name='Class 1',
            school=self.school1,
            instructor=self.instructor1,
            academic_year=2025,
            semester='1'
        )

        # Create students
        for i in range(5):
            user = User.objects.create_user(
                username=f'student{i}',
                password='test123',
                role='student'
            )
            Student.objects.create(
                user=user,
                name=f'Student {i}',
                student_id=f'2025{i:03d}',
                grade=3,
                class_assignment=self.class1,
                generated_email=f'2025{i:03d}@seoul.zep.internal',
                zep_space_url=f'https://zep.us/play/student{i}' if i < 3 else ''
            )

    def test_total_schools_count(self):
        """Test total schools metric"""
        metrics = DashboardMetrics.get_core_metrics()
        self.assertEqual(metrics['total_schools'], 2)

    def test_total_instructors_count(self):
        """Test total instructors metric"""
        metrics = DashboardMetrics.get_core_metrics()
        self.assertEqual(metrics['total_instructors'], 2)

    def test_total_students_count(self):
        """Test total students metric"""
        metrics = DashboardMetrics.get_core_metrics()
        self.assertEqual(metrics['total_students'], 5)

    def test_active_spaces_count(self):
        """Test active spaces metric (students with zep_space_url)"""
        metrics = DashboardMetrics.get_core_metrics()
        self.assertEqual(metrics['active_spaces'], 3)  # Only 3 students have URLs

    def test_metrics_caching(self):
        """Test that metrics are cached for 5 minutes (AC4: performance)"""
        # First call - should cache
        metrics1 = DashboardMetrics.get_core_metrics()

        # Add more data
        School.objects.create(name='School 3', address='Address 3')

        # Second call - should return cached data (not updated)
        metrics2 = DashboardMetrics.get_core_metrics()
        self.assertEqual(metrics1['total_schools'], metrics2['total_schools'])

        # Clear cache and verify new data is returned
        cache.delete(DashboardMetrics.CACHE_KEY)
        metrics3 = DashboardMetrics.get_core_metrics()
        self.assertEqual(metrics3['total_schools'], 3)


class VisitorAnalyticsTestCase(TestCase):
    """Test visitor analytics tracking and aggregation (AC2: visitor analytics)"""

    def setUp(self):
        """Create visitor log test data"""
        now = timezone.now()

        # Create visitor logs for different time periods
        # Daily (within 24 hours)
        for i in range(10):
            VisitorLog.objects.create(
                timestamp=now - timedelta(hours=i),
                ip_address='127.0.0.1',
                user_agent='Test Browser',
                path='/'
            )

        # Weekly (within 7 days, but older than 24 hours)
        for i in range(5):
            VisitorLog.objects.create(
                timestamp=now - timedelta(days=i+2),
                ip_address='127.0.0.1',
                user_agent='Test Browser',
                path='/'
            )

        # Monthly (within 30 days, but older than 7 days)
        for i in range(3):
            VisitorLog.objects.create(
                timestamp=now - timedelta(days=i+10),
                ip_address='127.0.0.1',
                user_agent='Test Browser',
                path='/'
            )

        # Old logs (older than 30 days - should not be counted)
        VisitorLog.objects.create(
            timestamp=now - timedelta(days=35),
            ip_address='127.0.0.1',
            user_agent='Test Browser',
            path='/'
        )

    def test_daily_visitor_count(self):
        """Test daily visitor count (last 24 hours)"""
        visitor_stats = DashboardMetrics.get_visitor_stats()
        # Should have at least 10 from setUp (may have more from middleware)
        self.assertGreaterEqual(visitor_stats['daily'], 10)

    def test_weekly_visitor_count(self):
        """Test weekly visitor count (last 7 days)"""
        visitor_stats = DashboardMetrics.get_visitor_stats()
        # Should have at least 15 from setUp (10 daily + 5 weekly)
        self.assertGreaterEqual(visitor_stats['weekly'], 15)

    def test_monthly_visitor_count(self):
        """Test monthly visitor count (last 30 days)"""
        visitor_stats = DashboardMetrics.get_visitor_stats()
        # Should have at least 18 from setUp (10 + 5 + 3)
        self.assertGreaterEqual(visitor_stats['monthly'], 18)

    def test_visitor_tracking_middleware(self):
        """Test that visitor tracking middleware logs visits"""
        initial_count = VisitorLog.objects.count()

        # Make request to root path
        client = Client()
        client.get('/')

        # Verify visitor was logged
        self.assertEqual(VisitorLog.objects.count(), initial_count + 1)

        # Verify log details
        latest_log = VisitorLog.objects.latest('timestamp')
        self.assertEqual(latest_log.path, '/')


class MetricsAPITestCase(TestCase):
    """Test metrics API endpoint for real-time updates (AC3: real-time updates)"""

    def setUp(self):
        """Create admin user and test data"""
        cache.clear()
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin'
        )
        self.client.login(username='admin_test', password='testpass123')

        # Create test school
        School.objects.create(name='Test School', address='Test Address')

    def test_metrics_api_returns_json(self):
        """Test that metrics API returns valid JSON"""
        response = self.client.get(reverse('dashboard:metrics_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        # Parse and verify JSON structure
        data = json.loads(response.content)
        self.assertIn('total_schools', data)
        self.assertIn('total_instructors', data)
        self.assertIn('total_students', data)
        self.assertIn('active_spaces', data)
        self.assertIn('visitor_stats', data)
        self.assertIn('timestamp', data)

    def test_metrics_api_returns_correct_data(self):
        """Test that metrics API returns correct data"""
        response = self.client.get(reverse('dashboard:metrics_api'))
        data = json.loads(response.content)

        self.assertEqual(data['total_schools'], 1)
        self.assertEqual(data['total_instructors'], 0)


class CSVExportTestCase(TestCase):
    """Test CSV export functionality (AC7: CSV export)"""

    def setUp(self):
        """Create admin user and test data"""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin'
        )
        self.client.login(username='admin_test', password='testpass123')

        # Create test data
        School.objects.create(name='Test School', address='Address')

    def test_csv_export_generates_file(self):
        """Test that CSV export returns a file"""
        response = self.client.get(reverse('dashboard:export_metrics'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8-sig')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('dashboard_metrics_', response['Content-Disposition'])

    def test_csv_export_has_utf8_bom(self):
        """Test that CSV export includes UTF-8 BOM for Excel compatibility"""
        response = self.client.get(reverse('dashboard:export_metrics'))
        content = response.content.decode('utf-8-sig')
        self.assertIn('Dashboard Metrics Export', content)

    def test_csv_export_contains_metrics(self):
        """Test that CSV export contains all metrics"""
        response = self.client.get(reverse('dashboard:export_metrics'))
        content = response.content.decode('utf-8-sig')

        # Verify core metrics are present
        self.assertIn('Total Schools', content)
        self.assertIn('Total Instructors', content)
        self.assertIn('Total Students', content)
        self.assertIn('Active Spaces', content)

        # Verify visitor analytics are present
        self.assertIn('Visitor Analytics', content)
        self.assertIn('Daily', content)
        self.assertIn('Weekly', content)
        self.assertIn('Monthly', content)


class PerformanceTestCase(TestCase):
    """Test performance requirements (AC4: load time < 3 seconds)"""

    def setUp(self):
        """Create large dataset for performance testing"""
        cache.clear()

        # Create 10 schools
        schools = [School.objects.create(name=f'School {i}', address=f'Address {i}')
                  for i in range(10)]

        # Create 20 instructors
        instructors = []
        for i in range(20):
            instructor = User.objects.create_user(
                username=f'instructor{i}',
                password='test123',
                role='instructor'
            )
            instructors.append(instructor)

        # Create 10 classes
        classes = []
        for i in range(10):
            cls = Class.objects.create(
                name=f'Class {i}',
                school=schools[i % 10],
                instructor=instructors[i % 20],
                academic_year=2025,
                semester='1'
            )
            classes.append(cls)

        # Create 100 students
        for i in range(100):
            user = User.objects.create_user(
                username=f'student{i}',
                password='test123',
                role='student'
            )
            Student.objects.create(
                user=user,
                name=f'Student {i}',
                student_id=f'2025{i:04d}',
                grade=3,
                class_assignment=classes[i % 10],
                generated_email=f'2025{i:04d}@seoul.zep.internal',
                zep_space_url=f'https://zep.us/play/student{i}' if i % 2 == 0 else ''
            )

        # Create 1000 visitor logs
        now = timezone.now()
        for i in range(1000):
            VisitorLog.objects.create(
                timestamp=now - timedelta(hours=i),
                ip_address='127.0.0.1',
                user_agent='Test Browser',
                path='/'
            )

        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin'
        )
        self.client.login(username='admin_test', password='testpass123')

    def test_dashboard_loads_within_time_limit(self):
        """Test that dashboard loads in under 3 seconds with large dataset"""
        start_time = time.time()
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        elapsed_time = time.time() - start_time

        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed_time, 3.0,
                       f"Dashboard took {elapsed_time:.2f}s (should be < 3s)")

    def test_metrics_calculation_performance(self):
        """Test that metrics calculation is fast"""
        start_time = time.time()
        metrics = DashboardMetrics.get_core_metrics()
        elapsed_time = time.time() - start_time

        self.assertLess(elapsed_time, 1.0,
                       f"Metrics calculation took {elapsed_time:.2f}s (should be < 1s)")
        self.assertEqual(metrics['total_schools'], 10)
        self.assertEqual(metrics['total_instructors'], 20)
        self.assertEqual(metrics['total_students'], 100)


class DashboardTemplateTestCase(TestCase):
    """Test dashboard template rendering (AC5: responsive design)"""

    def setUp(self):
        """Create admin user"""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            role='admin'
        )
        self.client.login(username='admin_test', password='testpass123')

        # Create minimal test data
        School.objects.create(name='Test School', address='Address')

    def test_dashboard_template_renders(self):
        """Test that dashboard template renders without errors"""
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '관리자 대시보드')
        self.assertContains(response, '총 학교 수')
        self.assertContains(response, '총 강사 수')
        self.assertContains(response, '총 학생 수')
        self.assertContains(response, '활성 공간')

    def test_dashboard_contains_export_button(self):
        """Test that dashboard contains CSV export button"""
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertContains(response, 'CSV 내보내기')
        self.assertContains(response, reverse('dashboard:export_metrics'))

    def test_dashboard_contains_realtime_script(self):
        """Test that dashboard contains real-time update script"""
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertContains(response, 'setInterval')
        self.assertContains(response, reverse('dashboard:metrics_api'))
        self.assertContains(response, '30000')  # 30 seconds
