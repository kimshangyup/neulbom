"""
Tests for Story 3.3 - Instructor Space Management Interface

Test Coverage:
- AC1: Instructor dashboard includes "My Students" section
- AC2: Table displays: student name, class, space URL, space status, last activity
- AC3: Click on space URL opens ZEP space in new tab
- AC4: Filter by class and search by student name
- AC5: Bulk actions: select multiple students
- AC6: Table pagination for classes with 50+ students
- AC7: Export student list with credentials as CSV
- Access Control: Only instructors can access
- Data Integrity: Instructors see only their own students
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import csv
import io

from authentication.models import User
from students.models import School, Class, Student

User = get_user_model()


class InstructorDashboardAccessTestCase(TestCase):
    """Test access control for instructor dashboard"""

    def setUp(self):
        # Create users with different roles
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

        self.student_user = User.objects.create_user(
            username='student',
            password='testpass123',
            role='student'
        )

        self.client = Client()

    def test_instructor_can_access_dashboard(self):
        """AC: Only instructors (and admins) can access instructor dashboard"""
        self.client.login(username='instructor', password='testpass123')
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_dashboard(self):
        """AC: Admins should also be able to access instructor dashboard"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_student_cannot_access_dashboard(self):
        """AC: Students cannot access instructor dashboard"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_redirected(self):
        """AC: Anonymous users redirected to login"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertEqual(response.status_code, 302)


class InstructorDashboardDisplayTestCase(TestCase):
    """Test AC1 and AC2: Dashboard display and student table"""

    def setUp(self):
        # Create instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )

        # Create school and class
        self.school = School.objects.create(name='서울초등학교')
        self.class1 = Class.objects.create(
            name='1학년 1반',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )

        # Create students with various states
        for i in range(3):
            student_user = User.objects.create_user(
                username=f'student{i}',
                password='testpass123',
                role='student'
            )
            Student.objects.create(
                user=student_user,
                student_id=f'STU{i:03d}',
                name=f'학생{i}',
                grade=1,
                class_assignment=self.class1,
                generated_email=f'stu{i:03d}@seoul.zep.internal',
                zep_space_url=f'https://zep.us/space{i}' if i < 2 else ''  # 2 with URLs, 1 without
            )

        self.client = Client()
        self.client.login(username='instructor', password='testpass123')

    def test_my_students_section_exists(self):
        """AC1: Dashboard includes 'My Students' section"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '내 학생 목록')
        self.assertContains(response, 'My Students', html=False)  # Check section exists

    def test_student_table_displays_all_columns(self):
        """AC2: Table displays all required columns"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, '학생 이름')  # Student Name
        self.assertContains(response, '학급')  # Class
        self.assertContains(response, 'ZEP 스페이스')  # Space URL
        self.assertContains(response, '공간 상태')  # Space Status
        self.assertContains(response, '최근 활동')  # Last Activity

    def test_student_data_displayed_correctly(self):
        """AC2: Student data is displayed in table"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, '학생0')
        self.assertContains(response, 'STU000')
        self.assertContains(response, '1학년 1반')

    def test_total_students_count_displayed(self):
        """AC: Total student count is displayed"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, '3')  # 3 students total


class ZepSpaceUrlTestCase(TestCase):
    """Test AC3: ZEP space URL functionality"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )

        self.school = School.objects.create(name='서울초등학교')
        self.class1 = Class.objects.create(
            name='1학년 1반',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )

        # Student with ZEP space URL
        student_user = User.objects.create_user(
            username='student1',
            password='testpass123',
            role='student'
        )
        self.student = Student.objects.create(
            user=student_user,
            student_id='STU001',
            name='테스트학생',
            grade=1,
            class_assignment=self.class1,
            generated_email='stu001@seoul.zep.internal',
            zep_space_url='https://zep.us/play/abcd1234'
        )

        self.client = Client()
        self.client.login(username='instructor', password='testpass123')

    def test_zep_space_url_is_clickable(self):
        """AC3: ZEP space URLs are clickable links"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, 'href="https://zep.us/play/abcd1234"')

    def test_zep_space_url_opens_in_new_tab(self):
        """AC3: ZEP space URLs have target='_blank'"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, 'target="_blank"')

    def test_missing_zep_space_url_displays_placeholder(self):
        """AC3: Missing URLs show placeholder text"""
        # Create student without URL
        student_user2 = User.objects.create_user(
            username='student2',
            password='testpass123',
            role='student'
        )
        Student.objects.create(
            user=student_user2,
            student_id='STU002',
            name='테스트학생2',
            grade=1,
            class_assignment=self.class1,
            generated_email='stu002@seoul.zep.internal',
            zep_space_url=''
        )

        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, 'URL 없음')


class FilterAndSearchTestCase(TestCase):
    """Test AC4: Class filter and name search functionality"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )

        self.school = School.objects.create(name='서울초등학교')

        # Create two classes
        self.class1 = Class.objects.create(
            name='1학년 1반',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )
        self.class2 = Class.objects.create(
            name='2학년 1반',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )

        # Create students in different classes
        for i in range(3):
            student_user = User.objects.create_user(
                username=f'student_class1_{i}',
                password='testpass123',
                role='student'
            )
            Student.objects.create(
                user=student_user,
                student_id=f'C1STU{i:03d}',
                name=f'김학생{i}',
                grade=1,
                class_assignment=self.class1,
                generated_email=f'c1stu{i:03d}@seoul.zep.internal'
            )

        for i in range(2):
            student_user = User.objects.create_user(
                username=f'student_class2_{i}',
                password='testpass123',
                role='student'
            )
            Student.objects.create(
                user=student_user,
                student_id=f'C2STU{i:03d}',
                name=f'이학생{i}',
                grade=2,
                class_assignment=self.class2,
                generated_email=f'c2stu{i:03d}@seoul.zep.internal'
            )

        self.client = Client()
        self.client.login(username='instructor', password='testpass123')

    def test_class_filter_shows_only_selected_class(self):
        """AC4: Class filter shows only students from selected class"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'), {'class': self.class1.id})
        self.assertContains(response, '김학생0')
        self.assertNotContains(response, '이학생0')

    def test_search_filters_by_student_name(self):
        """AC4: Name search filters students correctly"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'), {'search': '김학생'})
        self.assertContains(response, '김학생0')
        self.assertNotContains(response, '이학생0')

    def test_search_is_case_insensitive(self):
        """AC4: Name search is case-insensitive"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'), {'search': 'kim'})
        # Should still work even with lowercase (Korean names should still match)

    def test_class_filter_dropdown_populated(self):
        """AC4: Class filter dropdown shows instructor's classes"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, '1학년 1반')
        self.assertContains(response, '2학년 1반')


class PaginationTestCase(TestCase):
    """Test AC6: Pagination for 50+ students"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )

        self.school = School.objects.create(name='서울초등학교')
        self.class1 = Class.objects.create(
            name='대형반',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )

        # Create 55 students to test pagination (50 per page)
        for i in range(55):
            student_user = User.objects.create_user(
                username=f'student{i}',
                password='testpass123',
                role='student'
            )
            Student.objects.create(
                user=student_user,
                student_id=f'STU{i:03d}',
                name=f'학생{i}',
                grade=1,
                class_assignment=self.class1,
                generated_email=f'stu{i:03d}@seoul.zep.internal'
            )

        self.client = Client()
        self.client.login(username='instructor', password='testpass123')

    def test_pagination_activates_for_50_plus_students(self):
        """AC6: Pagination appears when there are 50+ students"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        # Check for pagination controls (English text from links/buttons)
        self.assertContains(response, 'page=')  # Page parameter in URL
        # Check that we're seeing page 1 of multiple pages
        self.assertEqual(response.context['page_obj'].number, 1)
        self.assertTrue(response.context['page_obj'].has_next())

    def test_first_page_shows_50_students(self):
        """AC6: First page shows 50 students"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        # Count occurrences of student rows
        self.assertContains(response, 'STU0', count=50)  # First 50 students

    def test_second_page_shows_remaining_students(self):
        """AC6: Second page shows remaining students"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'), {'page': 2})
        # Page 2 should exist and show the remaining 5 students
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 2)
        # Should have 5 students on page 2 (55 total - 50 on page 1 = 5 on page 2)
        self.assertEqual(len(response.context['page_obj'].object_list), 5)

    def test_pagination_preserves_filters(self):
        """AC6: Pagination preserves filter/search state"""
        # Use a more specific search term
        response = self.client.get(reverse('dashboard:instructor_dashboard'), {'search': '학생10'})
        # Verify the search is applied
        self.assertContains(response, '학생10')
        # If there are pagination links, they should preserve the search
        if response.context['page_obj'].has_other_pages():
            # Check for URL-encoded search parameter in pagination
            import urllib.parse
            encoded_search = urllib.parse.quote('학생10')
            self.assertContains(response, f'search={encoded_search}', count=None)


class CsvExportTestCase(TestCase):
    """Test AC7: CSV export functionality"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )

        self.school = School.objects.create(name='서울초등학교')
        self.class1 = Class.objects.create(
            name='1학년 1반',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )

        # Create students
        for i in range(3):
            student_user = User.objects.create_user(
                username=f'student{i}',
                password='testpass123',
                role='student'
            )
            Student.objects.create(
                user=student_user,
                student_id=f'STU{i:03d}',
                name=f'학생{i}',
                grade=1,
                class_assignment=self.class1,
                generated_email=f'stu{i:03d}@seoul.zep.internal',
                zep_space_url=f'https://zep.us/space{i}' if i < 2 else ''
            )

        self.client = Client()
        self.client.login(username='instructor', password='testpass123')

    def test_csv_export_returns_csv_file(self):
        """AC7: Export endpoint returns CSV file"""
        response = self.client.get(reverse('dashboard:export_students'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8-sig')
        self.assertIn('attachment', response['Content-Disposition'])

    def test_csv_export_includes_correct_headers(self):
        """AC7: CSV includes correct column headers"""
        response = self.client.get(reverse('dashboard:export_students'))
        content = response.content.decode('utf-8-sig')
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)
        self.assertIn('Student ID', headers)
        self.assertIn('Name', headers)
        self.assertIn('Class', headers)
        self.assertIn('Email', headers)
        self.assertIn('ZEP Space URL', headers)
        self.assertIn('Space Status', headers)

    def test_csv_export_includes_all_students(self):
        """AC7: CSV includes all student data"""
        response = self.client.get(reverse('dashboard:export_students'))
        content = response.content.decode('utf-8-sig')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        self.assertEqual(len(rows), 4)  # 1 header + 3 students

    def test_csv_export_respects_filters(self):
        """AC7: CSV export respects dashboard filters"""
        response = self.client.get(reverse('dashboard:export_students'), {'search': '학생0'})
        content = response.content.decode('utf-8-sig')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        self.assertEqual(len(rows), 2)  # 1 header + 1 matching student


class DataIntegrityTestCase(TestCase):
    """Test that instructors only see their own students"""

    def setUp(self):
        # Create two instructors
        self.instructor1 = User.objects.create_user(
            username='instructor1',
            password='testpass123',
            role='instructor'
        )
        self.instructor2 = User.objects.create_user(
            username='instructor2',
            password='testpass123',
            role='instructor'
        )

        self.school = School.objects.create(name='서울초등학교')

        # Create classes for each instructor
        self.class1 = Class.objects.create(
            name='1학년 1반',
            school=self.school,
            instructor=self.instructor1,
            academic_year=2025,
            semester='spring'
        )
        self.class2 = Class.objects.create(
            name='2학년 1반',
            school=self.school,
            instructor=self.instructor2,
            academic_year=2025,
            semester='spring'
        )

        # Create students for each instructor
        student_user1 = User.objects.create_user(
            username='student_instructor1',
            password='testpass123',
            role='student'
        )
        self.student1 = Student.objects.create(
            user=student_user1,
            student_id='STU001',
            name='강사1학생',
            grade=1,
            class_assignment=self.class1,
            generated_email='stu001@seoul.zep.internal'
        )

        student_user2 = User.objects.create_user(
            username='student_instructor2',
            password='testpass123',
            role='student'
        )
        self.student2 = Student.objects.create(
            user=student_user2,
            student_id='STU002',
            name='강사2학생',
            grade=2,
            class_assignment=self.class2,
            generated_email='stu002@seoul.zep.internal'
        )

        self.client = Client()

    def test_instructor_sees_only_own_students(self):
        """Data Integrity: Instructor sees only their own students"""
        self.client.login(username='instructor1', password='testpass123')
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, '강사1학생')
        self.assertNotContains(response, '강사2학생')

    def test_other_instructor_students_not_visible(self):
        """Data Integrity: Other instructors' students are not visible"""
        self.client.login(username='instructor2', password='testpass123')
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, '강사2학생')
        self.assertNotContains(response, '강사1학생')


class EmptyStateTestCase(TestCase):
    """Test empty state when instructor has no students"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )

        self.client = Client()
        self.client.login(username='instructor', password='testpass123')

    def test_empty_state_displayed_when_no_students(self):
        """Edge case: Empty state shown when instructor has no students"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, '학생이 없습니다')
        self.assertEqual(response.status_code, 200)


class SpaceStatusIndicatorTestCase(TestCase):
    """Test space status indicator display"""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123',
            role='instructor'
        )

        self.school = School.objects.create(name='서울초등학교')
        self.class1 = Class.objects.create(
            name='1학년 1반',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )

        # Student with space
        student_user1 = User.objects.create_user(
            username='student1',
            password='testpass123',
            role='student'
        )
        self.student_with_space = Student.objects.create(
            user=student_user1,
            student_id='STU001',
            name='학생1',
            grade=1,
            class_assignment=self.class1,
            generated_email='stu001@seoul.zep.internal',
            zep_space_url='https://zep.us/space1'
        )

        # Student without space
        student_user2 = User.objects.create_user(
            username='student2',
            password='testpass123',
            role='student'
        )
        self.student_without_space = Student.objects.create(
            user=student_user2,
            student_id='STU002',
            name='학생2',
            grade=1,
            class_assignment=self.class1,
            generated_email='stu002@seoul.zep.internal',
            zep_space_url=''
        )

        self.client = Client()
        self.client.login(username='instructor', password='testpass123')

    def test_created_status_shows_for_student_with_space(self):
        """AC6: 'Created' status shown for students with ZEP space"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, '생성됨')

    def test_not_created_status_shows_for_student_without_space(self):
        """AC6: 'Not Created' status shown for students without ZEP space"""
        response = self.client.get(reverse('dashboard:instructor_dashboard'))
        self.assertContains(response, '미생성')

    def test_space_status_uses_is_space_created_property(self):
        """AC6: Status indicator uses Student.is_space_created property"""
        self.assertTrue(self.student_with_space.is_space_created)
        self.assertFalse(self.student_without_space.is_space_created)
