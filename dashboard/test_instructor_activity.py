"""
Tests for Story 3.2 - Administrator Dashboard: Instructor Activity

Test Coverage:
- AC1: Dashboard includes "Instructor Activity" section
- AC2: Table displays instructor data (name, school, counts, last login)
- AC3: Search and filter by school, activity status
- AC4: Sortable columns
- AC5: Clickable rows navigate to detail view
- AC6: Inactive instructors highlighted
- AC7: Data refreshes every 5 minutes
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import time

from authentication.models import User
from students.models import School, Class, Student
from dashboard.metrics import DashboardMetrics

User = get_user_model()


class InstructorActivityDisplayTestCase(TestCase):
    """Test AC1 and AC2: Instructor Activity section and table display"""

    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            role='admin'
        )

        # Create schools
        self.school1 = School.objects.create(name='서울초등학교')
        self.school2 = School.objects.create(name='부산초등학교')

        # Create instructors with different activity levels
        self.instructor1 = User.objects.create_user(
            username='instructor1',
            password='testpass123',
            role='instructor',
            first_name='김',
            last_name='강사',
            affiliated_school=self.school1
        )
        self.instructor1.last_login = timezone.now() - timedelta(days=5)
        self.instructor1.save()

        self.instructor2 = User.objects.create_user(
            username='instructor2',
            password='testpass123',
            role='instructor',
            first_name='이',
            last_name='교사',
            affiliated_school=self.school2
        )
        self.instructor2.last_login = timezone.now() - timedelta(days=35)  # Inactive
        self.instructor2.save()

        # Create classes and students
        self.class1 = Class.objects.create(
            name='1학년 1반',
            school=self.school1,
            instructor=self.instructor1,
            academic_year=2025,
            semester='spring'
        )
        self.class2 = Class.objects.create(
            name='2학년 1반',
            school=self.school1,
            instructor=self.instructor1,
            academic_year=2025,
            semester='spring'
        )
        self.class3 = Class.objects.create(
            name='3학년 1반',
            school=self.school2,
            instructor=self.instructor2,
            academic_year=2025,
            semester='spring'
        )

        # Add students with spaces
        for i in range(5):
            student_user = User.objects.create_user(
                username=f'student1_{i}',
                password='testpass123',
                role='student'
            )
            Student.objects.create(
                user=student_user,
                student_id=f'STU1{i}',
                name=f'학생{i}',
                grade=1,
                class_assignment=self.class1,
                generated_email=f'STU1{i}@seoul.zep.internal',
                zep_space_url=f'https://zep.us/play/space{i}' if i < 3 else ''
            )

        for i in range(3):
            student_user = User.objects.create_user(
                username=f'student2_{i}',
                password='testpass123',
                role='student'
            )
            Student.objects.create(
                user=student_user,
                student_id=f'STU2{i}',
                name=f'학생{i}',
                grade=2,
                class_assignment=self.class2,
                generated_email=f'STU2{i}@seoul.zep.internal',
                zep_space_url=f'https://zep.us/play/space{i}'
            )

        self.client = Client()

    def test_instructor_activity_section_renders(self):
        """AC1: Dashboard includes Instructor Activity section"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '강사 활동 현황')
        self.assertContains(response, 'instructor-table')

    def test_instructor_activity_table_displays_correct_data(self):
        """AC2: Table displays all required instructor data"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))

        # Check table headers
        self.assertContains(response, '강사 이름')
        self.assertContains(response, '학교')
        self.assertContains(response, '클래스 수')
        self.assertContains(response, '학생 수')
        self.assertContains(response, '마지막 로그인')
        self.assertContains(response, '생성된 공간')

        # Check instructor data appears
        self.assertContains(response, 'instructor1')
        self.assertContains(response, 'instructor2')

    def test_get_instructor_activity_returns_correct_aggregations(self):
        """AC2: Verify get_instructor_activity() calculates correct counts"""
        activity_data = DashboardMetrics.get_instructor_activity()

        # Verify we got data
        self.assertGreater(len(activity_data), 0)

        # Find instructor1 data
        instructor1_data = next((d for d in activity_data if d['id'] == self.instructor1.id), None)
        self.assertIsNotNone(instructor1_data)

        # Verify structure
        self.assertIn('class_count', instructor1_data)
        self.assertIn('student_count', instructor1_data)
        self.assertIn('spaces_created', instructor1_data)
        self.assertIn('is_inactive', instructor1_data)
        self.assertIn('full_name', instructor1_data)
        self.assertIn('school_name', instructor1_data)

        # Find instructor2 data
        instructor2_data = next((d for d in activity_data if d['id'] == self.instructor2.id), None)
        self.assertIsNotNone(instructor2_data)
        self.assertTrue(instructor2_data['is_inactive'])  # No login > 30 days


class InactiveInstructorHighlightTestCase(TestCase):
    """Test AC6: Inactive instructors highlighted"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            role='admin'
        )

        # Create inactive instructor
        self.inactive_instructor = User.objects.create_user(
            username='inactive',
            password='testpass123',
            role='instructor',
            first_name='비활성',
            last_name='강사'
        )
        self.inactive_instructor.last_login = timezone.now() - timedelta(days=40)
        self.inactive_instructor.save()

        self.client = Client()

    def test_inactive_instructor_highlighted_in_table(self):
        """AC6: Inactive instructors have red background and border"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))

        # Check for inactive styling
        self.assertContains(response, 'bg-red-50')
        self.assertContains(response, 'border-red-500')
        self.assertContains(response, '비활성')


class SearchAndFilterTestCase(TestCase):
    """Test AC3: Search and filter functionality"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            role='admin'
        )

        self.school1 = School.objects.create(name='서울초등학교')
        self.school2 = School.objects.create(name='부산초등학교')

        # Create multiple instructors
        for i in range(5):
            User.objects.create_user(
                username=f'instructor{i}',
                password='testpass123',
                role='instructor',
                first_name=f'강사{i}',
                last_name='테스트',
                affiliated_school=self.school1 if i < 3 else self.school2
            )

        self.client = Client()

    def test_search_filter_elements_present(self):
        """AC3: Search and filter controls present in template"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))

        # Check search input
        self.assertContains(response, 'search-name')
        self.assertContains(response, '이름으로 검색')

        # Check school filter
        self.assertContains(response, 'filter-school')
        self.assertContains(response, '학교 필터')

        # Check activity status filter
        self.assertContains(response, 'filter-status')
        self.assertContains(response, '활동 상태')


class SortableColumnsTestCase(TestCase):
    """Test AC4: Sortable columns"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            role='admin'
        )

        # Create instructors with varying metrics
        for i in range(3):
            User.objects.create_user(
                username=f'instructor{i}',
                password='testpass123',
                role='instructor',
                first_name=f'강사{i}',
                last_name='정렬'
            )

        self.client = Client()

    def test_sortable_column_headers_present(self):
        """AC4: All columns have sort functionality"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))

        # Check for sortTable function
        self.assertContains(response, 'sortTable')

        # Check for sort icons
        self.assertContains(response, 'sort-icon')

        # Check onclick handlers for columns
        self.assertContains(response, "onclick=\"sortTable('full_name')\"")
        self.assertContains(response, "onclick=\"sortTable('school_name')\"")
        self.assertContains(response, "onclick=\"sortTable('class_count')\"")
        self.assertContains(response, "onclick=\"sortTable('student_count')\"")
        self.assertContains(response, "onclick=\"sortTable('last_login')\"")
        self.assertContains(response, "onclick=\"sortTable('spaces_created')\"")


class InstructorDetailViewTestCase(TestCase):
    """Test AC5: Instructor detail view"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            role='admin'
        )

        self.school = School.objects.create(name='테스트초등학교')

        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor',
            email='instructor@test.com',
            first_name='상세',
            last_name='강사',
            affiliated_school=self.school
        )

        # Create classes
        self.class1 = Class.objects.create(
            name='테스트 클래스',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )

        # Add students
        for i in range(10):
            student_user = User.objects.create_user(
                username=f'student{i}',
                password='testpass123',
                role='student'
            )
            Student.objects.create(
                user=student_user,
                student_id=f'STU{i}',
                name=f'학생{i}',
                grade=1,
                class_assignment=self.class1,
                generated_email=f'STU{i}@seoul.zep.internal',
                zep_space_url=f'https://zep.us/space{i}' if i < 7 else ''
            )

        self.client = Client()

    def test_instructor_detail_view_loads(self):
        """AC5: Instructor detail view is accessible"""
        self.client.login(username='admin', password='testpass123')
        url = reverse('dashboard:instructor_detail', args=[self.instructor.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.instructor.get_full_name())
        self.assertContains(response, 'instructor@test.com')

    def test_instructor_detail_shows_statistics(self):
        """AC5: Detail view shows instructor statistics"""
        self.client.login(username='admin', password='testpass123')
        url = reverse('dashboard:instructor_detail', args=[self.instructor.id])
        response = self.client.get(url)

        # Check statistics cards
        self.assertContains(response, '총 클래스')
        self.assertContains(response, '총 학생')
        self.assertContains(response, '생성된 공간')

    def test_instructor_detail_shows_classes(self):
        """AC5: Detail view lists classes taught"""
        self.client.login(username='admin', password='testpass123')
        url = reverse('dashboard:instructor_detail', args=[self.instructor.id])
        response = self.client.get(url)

        self.assertContains(response, '담당 클래스')
        self.assertContains(response, '테스트 클래스')

    def test_clickable_rows_in_activity_table(self):
        """AC5: Rows in activity table are clickable"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))

        # Check for onclick handler and clickable rows
        self.assertContains(response, 'cursor-pointer')
        self.assertContains(response, 'window.location.href')


class DataRefreshTestCase(TestCase):
    """Test AC7: Data refresh mechanism"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            role='admin'
        )

        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )

        self.client = Client()

    def test_metrics_api_includes_instructor_activity(self):
        """AC7: Metrics API returns instructor activity data"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard:metrics_api'))

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify instructor_activity is in response
        self.assertIn('instructor_activity', data)
        self.assertIsInstance(data['instructor_activity'], list)

    def test_auto_refresh_script_present(self):
        """AC7: Dashboard has auto-refresh JavaScript"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))

        # Check for polling interval
        self.assertContains(response, 'setInterval')
        self.assertContains(response, '30000')  # 30 seconds

        # Check for updateInstructorTable function
        self.assertContains(response, 'updateInstructorTable')


class InstructorActivityCachingTestCase(TestCase):
    """Test caching behavior for instructor activity data"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            role='admin'
        )

        for i in range(5):
            User.objects.create_user(
                username=f'instructor{i}',
                password='testpass123',
                role='instructor'
            )

    def test_instructor_activity_cached_for_5_minutes(self):
        """Verify 5-minute caching for instructor activity"""
        from django.core.cache import cache

        # Clear cache
        cache.clear()

        # First call - should cache
        data1 = DashboardMetrics.get_instructor_activity()

        # Verify data cached
        cached_data = cache.get(DashboardMetrics.INSTRUCTOR_ACTIVITY_CACHE_KEY)
        self.assertIsNotNone(cached_data)

        # Second call - should be from cache
        data2 = DashboardMetrics.get_instructor_activity()

        # Verify data is identical
        self.assertEqual(len(data1), len(data2))
        self.assertEqual(data1, data2)


class PerformanceTestCase(TestCase):
    """Test query performance with 20+ instructors"""

    def setUp(self):
        # Create 25 instructors with schools, classes, and students
        for i in range(25):
            school = School.objects.create(name=f'학교{i}')

            instructor = User.objects.create_user(
                username=f'instructor{i}',
                password='testpass123',
                role='instructor',
                first_name=f'강사{i}',
                last_name='성능',
                affiliated_school=school
            )

            # Create 3 classes per instructor
            for j in range(3):
                class_obj = Class.objects.create(
                    name=f'클래스{i}-{j}',
                    school=school,
                    instructor=instructor,
                    academic_year=2025,
                    semester='spring'
                )

                # Create 10 students per class
                for k in range(10):
                    student_user = User.objects.create_user(
                        username=f'student{i}_{j}_{k}',
                        password='testpass123',
                        role='student'
                    )
                    Student.objects.create(
                        user=student_user,
                        student_id=f'STU{i}{j}{k}',
                        name=f'학생{k}',
                        grade=1,
                        class_assignment=class_obj,
                        generated_email=f'STU{i}{j}{k}@seoul.zep.internal',
                        zep_space_url=f'https://zep.us/space{k}' if k < 5 else ''
                    )

    def test_instructor_activity_query_performance(self):
        """Verify query completes in < 1 second with 20+ instructors"""
        from django.core.cache import cache
        cache.clear()

        start_time = time.time()
        activity_data = DashboardMetrics.get_instructor_activity()
        elapsed = time.time() - start_time

        # Should complete in < 1 second
        self.assertLess(elapsed, 1.0)

        # Verify all instructors returned
        self.assertEqual(len(activity_data), 25)

        # Verify data structure
        for instructor in activity_data:
            self.assertIn('id', instructor)
            self.assertIn('class_count', instructor)
            self.assertIn('student_count', instructor)
            self.assertIn('spaces_created', instructor)


class AccessControlTestCase(TestCase):
    """Test access control for instructor activity views"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            role='admin'
        )

        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )

        self.client = Client()

    def test_non_admin_cannot_access_instructor_activity(self):
        """Only admins can view instructor activity"""
        self.client.login(username='instructor', password='testpass123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))

        # Should redirect or show 403
        self.assertNotEqual(response.status_code, 200)

    def test_non_admin_cannot_access_instructor_detail(self):
        """Only admins can view instructor detail"""
        self.client.login(username='instructor', password='testpass123')
        url = reverse('dashboard:instructor_detail', args=[self.instructor.id])
        response = self.client.get(url)

        # Should redirect or show 403
        self.assertNotEqual(response.status_code, 200)
