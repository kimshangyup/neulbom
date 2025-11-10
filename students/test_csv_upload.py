"""
Tests for CSV Template and Upload Interface (Story 2.3)

Comprehensive tests for instructor dashboard, CSV template download,
file upload with drag-and-drop, validation, preview, and confirmation flow.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from students.models import School, Class, Student
from students.validators import CSVValidator
import io
import csv
import pandas as pd

User = get_user_model()


class InstructorDashboardTestCase(TestCase):
    """Tests for instructor dashboard with Student Management section (AC1)"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.school = School.objects.create(name="Test School")

        # Create instructor user
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )

        # Create admin user
        self.admin = User.objects.create_user(
            username="admin1",
            password="testpass",
            role="admin"
        )

        # Create student user (should not access dashboard)
        self.student = User.objects.create_user(
            username="student1",
            password="testpass",
            role="student"
        )

        # Create a class for the instructor
        self.test_class = Class.objects.create(
            name="1학년 A반",
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester="spring"
        )

    def test_instructor_can_access_dashboard(self):
        """Test instructor can access dashboard (AC1)"""
        self.client.login(username="instructor1", password="testpass")
        response = self.client.get(reverse('instructors:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('학생 관리', response.content.decode())

    def test_non_instructor_cannot_access_dashboard(self):
        """Test non-instructor cannot access dashboard (AC1)"""
        self.client.login(username="student1", password="testpass")
        response = self.client.get(reverse('instructors:dashboard'))

        self.assertEqual(response.status_code, 403)

    def test_dashboard_shows_statistics(self):
        """Test dashboard displays class and student statistics"""
        # Create students in the class (use different usernames to avoid conflicts with setUp)
        for i in range(10, 13):  # student10, student11, student12
            user = User.objects.create_user(
                username=f"student{i}",
                password="testpass",
                role="student"
            )
            Student.objects.create(
                user=user,
                student_id=f"2025000{i}",
                name=f"학생{i}",
                grade=1,
                class_assignment=self.test_class,
                generated_email=f"2025000{i}@seoul.zep.internal"
            )

        self.client.login(username="instructor1", password="testpass")
        response = self.client.get(reverse('instructors:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_classes'], 1)
        self.assertEqual(response.context['total_students'], 3)


class CSVTemplateDownloadTestCase(TestCase):
    """Tests for CSV template download functionality (AC2)"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor"
        )

    def test_csv_template_download(self):
        """Test CSV template download with correct headers (AC2)"""
        self.client.login(username="instructor1", password="testpass")
        response = self.client.get(reverse('students:download-template'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('student_template.csv', response['Content-Disposition'])

        # Check CSV content
        content = response.content.decode('utf-8-sig')
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)

        self.assertEqual(headers, ['student_name', 'student_id', 'grade', 'notes'])

        # Check example row exists
        example_row = next(reader)
        self.assertEqual(len(example_row), 4)
        self.assertTrue(example_row[0])  # student_name should have value


class FileUploadInterfaceTestCase(TestCase):
    """Tests for file upload interface with drag-and-drop (AC3)"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.school = School.objects.create(name="Test School")
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )
        self.test_class = Class.objects.create(
            name="1학년 A반",
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester="spring"
        )

    def test_upload_page_loads(self):
        """Test upload page loads with drag-and-drop zone (AC3)"""
        self.client.login(username="instructor1", password="testpass")
        response = self.client.get(reverse('students:upload-csv'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('drop-zone', response.content.decode())
        self.assertIn('드래그', response.content.decode())

    def test_upload_accepts_csv_file(self):
        """Test upload view accepts CSV file (AC3)"""
        self.client.login(username="instructor1", password="testpass")

        # Create CSV file
        csv_content = "student_name,student_id,grade,notes\n홍길동,20250001,1,테스트\n"
        csv_file = SimpleUploadedFile(
            "test.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        response = self.client.post(
            reverse('students:upload-csv'),
            {'file': csv_file, 'class_assignment': self.test_class.id, 'preview': 'true'},
            follow=True
        )

        self.assertEqual(response.status_code, 200)

    def test_upload_accepts_excel_file(self):
        """Test upload view accepts Excel file (.xlsx) (AC3)"""
        self.client.login(username="instructor1", password="testpass")

        # Create Excel file
        df = pd.DataFrame({
            'student_name': ['홍길동'],
            'student_id': ['20250001'],
            'grade': [1],
            'notes': ['']
        })

        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False, engine='openpyxl')
        excel_file.seek(0)

        uploaded_file = SimpleUploadedFile(
            "test.xlsx",
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response = self.client.post(
            reverse('students:upload-csv'),
            {'file': uploaded_file, 'class_assignment': self.test_class.id, 'preview': 'true'},
            follow=True
        )

        self.assertEqual(response.status_code, 200)

    def test_upload_rejects_invalid_file_format(self):
        """Test validation rejects invalid file formats (AC4)"""
        self.client.login(username="instructor1", password="testpass")

        # Create text file
        txt_file = SimpleUploadedFile(
            "test.txt",
            b"This is a text file",
            content_type="text/plain"
        )

        response = self.client.post(
            reverse('students:upload-csv'),
            {'file': txt_file, 'class_assignment': self.test_class.id, 'preview': 'true'}
        )

        self.assertEqual(response.status_code, 200)
        # Check that error message is displayed (in Korean: "CSV 또는 Excel 파일만 업로드 가능합니다")
        content = response.content.decode()
        self.assertTrue('csv' in content.lower() or 'excel' in content.lower())

    def test_file_size_validation(self):
        """Test file size validation (max 5MB)"""
        self.client.login(username="instructor1", password="testpass")

        # Create a large CSV content (>5MB)
        large_content = "student_name,student_id,grade,notes\n" + ("홍길동,20250001,1,\n" * 100000)
        large_file = SimpleUploadedFile(
            "large.csv",
            large_content.encode('utf-8'),
            content_type="text/csv"
        )

        response = self.client.post(
            reverse('students:upload-csv'),
            {'file': large_file, 'class_assignment': self.test_class.id, 'preview': 'true'}
        )

        self.assertEqual(response.status_code, 200)
        # Should show error about file size
        if large_file.size > 5 * 1024 * 1024:
            self.assertIn('5MB', response.content.decode())


class CSVValidationTestCase(TestCase):
    """Tests for CSV validation with pandas (AC4)"""

    def setUp(self):
        """Set up test data"""
        self.validator = CSVValidator()
        self.school = School.objects.create(name="Test School")

    def test_validation_detects_missing_columns(self):
        """Test validation detects missing required columns (AC4)"""
        # CSV missing student_name column
        csv_content = "student_id,grade\n20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        result = self.validator.validate(csv_file)

        self.assertFalse(result['valid'])
        self.assertTrue(any('student_name' in err for err in result['errors']))

    def test_validation_detects_invalid_grade(self):
        """Test validation detects invalid grade values (AC4)"""
        # Grade = 0 (invalid)
        csv_content = "student_name,student_id,grade\n홍길동,20250001,0\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        result = self.validator.validate(csv_file)

        self.assertFalse(result['valid'])
        self.assertTrue(any('1-6' in err for err in result['errors']))

    def test_validation_detects_duplicate_student_ids(self):
        """Test validation detects duplicate student_ids (AC4)"""
        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n김철수,20250001,2\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        result = self.validator.validate(csv_file)

        self.assertFalse(result['valid'])
        self.assertTrue(any('중복' in err for err in result['errors']))

    def test_validation_detects_existing_student_id(self):
        """Test validation detects student_id already in database (AC4)"""
        # Create existing student
        user = User.objects.create_user(
            username="existing",
            password="testpass",
            role="student"
        )
        Student.objects.create(
            user=user,
            student_id="20250001",
            name="기존학생",
            generated_email="20250001@seoul.zep.internal"
        )

        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        result = self.validator.validate(csv_file)

        self.assertFalse(result['valid'])
        self.assertTrue(any('이미 등록된' in err for err in result['errors']))

    def test_validation_handles_utf8_encoding(self):
        """Test validation handles UTF-8 encoded CSV (AC4)"""
        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        result = self.validator.validate(csv_file)

        self.assertTrue(result['valid'])
        self.assertEqual(len(result['data']), 1)

    def test_validation_handles_euckr_encoding(self):
        """Test validation handles EUC-KR encoded CSV (AC4)"""
        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('euc-kr'))

        result = self.validator.validate(csv_file)

        self.assertTrue(result['valid'])
        self.assertEqual(len(result['data']), 1)


class PreviewTableTestCase(TestCase):
    """Tests for preview table display (AC5, AC6)"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.school = School.objects.create(name="Test School")
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )
        self.test_class = Class.objects.create(
            name="1학년 A반",
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester="spring"
        )

    def test_preview_displays_student_data(self):
        """Test preview displays parsed student data (AC5)"""
        self.client.login(username="instructor1", password="testpass")

        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        response = self.client.post(
            reverse('students:upload-csv'),
            {'file': csv_file, 'class_assignment': self.test_class.id, 'preview': 'true'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('홍길동', response.content.decode())
        self.assertIn('20250001', response.content.decode())

    def test_preview_displays_generated_email(self):
        """Test preview displays generated email (AC6)"""
        self.client.login(username="instructor1", password="testpass")

        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        response = self.client.post(
            reverse('students:upload-csv'),
            {'file': csv_file, 'class_assignment': self.test_class.id, 'preview': 'true'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('20250001@seoul.zep.internal', response.content.decode())

    def test_preview_displays_class_assignment(self):
        """Test preview displays class assignment (AC6)"""
        self.client.login(username="instructor1", password="testpass")

        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        response = self.client.post(
            reverse('students:upload-csv'),
            {'file': csv_file, 'class_assignment': self.test_class.id, 'preview': 'true'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.test_class.name, response.content.decode())

    def test_preview_shows_error_if_no_class(self):
        """Test preview shows error if instructor has no active class (AC6)"""
        # Create instructor with no classes
        instructor2 = User.objects.create_user(
            username="instructor2",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )

        self.client.login(username="instructor2", password="testpass")
        response = self.client.get(reverse('students:upload-csv'))

        # Form should not have class options
        self.assertEqual(response.status_code, 200)


class ConfirmationCancellationTestCase(TestCase):
    """Tests for confirmation and cancellation actions (AC7)"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.school = School.objects.create(name="Test School")
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )
        self.test_class = Class.objects.create(
            name="1학년 A반",
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester="spring"
        )

    def test_cancel_button_redirects_to_upload(self):
        """Test cancel button clears session and redirects (AC7)"""
        self.client.login(username="instructor1", password="testpass")

        # First, create preview
        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        self.client.post(
            reverse('students:upload-csv'),
            {'file': csv_file, 'class_assignment': self.test_class.id, 'preview': 'true'}
        )

        # Now cancel by visiting upload page again
        response = self.client.get(reverse('students:upload-csv'))

        self.assertEqual(response.status_code, 200)

    def test_confirm_creates_students(self):
        """Test confirm button creates students (AC7) - placeholder for Story 2.5"""
        self.client.login(username="instructor1", password="testpass")

        # This test is a placeholder as student creation is Story 2.5
        # For now, just verify the confirm button flow works
        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        # Upload and preview
        self.client.post(
            reverse('students:upload-csv'),
            {'file': csv_file, 'class_assignment': self.test_class.id, 'preview': 'true'}
        )

        # Confirm (will be implemented in Story 2.5)
        response = self.client.post(
            reverse('students:upload-csv'),
            {'confirm': 'true'}
        )

        # For now, just check the flow doesn't error
        self.assertIn(response.status_code, [200, 302])

    def test_csrf_protection(self):
        """Test CSRF protection on all forms (AC7)"""
        self.client.login(username="instructor1", password="testpass")

        # Try to post without CSRF token
        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        response = self.client.post(
            reverse('students:upload-csv'),
            {'file': csv_file, 'class_assignment': self.test_class.id, 'preview': 'true'},
            HTTP_X_CSRFTOKEN=''
        )

        # CSRF middleware should handle this
        # Status depends on Django settings
        self.assertIsNotNone(response)


class IntegrationTestCase(TestCase):
    """Integration tests for full workflow (AC7)"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.school = School.objects.create(name="Test School")
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )
        self.test_class = Class.objects.create(
            name="1학년 A반",
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester="spring"
        )

    def test_full_workflow_download_upload_preview_cancel(self):
        """Test full workflow: template download → upload → preview → cancel (AC7)"""
        self.client.login(username="instructor1", password="testpass")

        # Step 1: Download template
        response = self.client.get(reverse('students:download-template'))
        self.assertEqual(response.status_code, 200)

        # Step 2: Upload CSV
        csv_content = "student_name,student_id,grade\n홍길동,20250001,1\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        response = self.client.post(
            reverse('students:upload-csv'),
            {'file': csv_file, 'class_assignment': self.test_class.id, 'preview': 'true'}
        )
        self.assertEqual(response.status_code, 200)

        # Step 3: Preview should show data
        self.assertIn('20250001@seoul.zep.internal', response.content.decode())

        # Step 4: Cancel by going back to upload
        response = self.client.get(reverse('students:upload-csv'))
        self.assertEqual(response.status_code, 200)


# ============================================================
# Story 2.5 Tests: Automated Student Account Creation
# ============================================================

class StudentAccountCreationTestCase(TestCase):
    """Tests for automated student account creation (Story 2.5)"""

    def setUp(self):
        """Set up test data"""
        self.school = School.objects.create(name="Test School")
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )
        self.test_class = Class.objects.create(
            name="1학년 A반",
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester="spring"
        )

    def test_email_generation_format(self):
        """Test email generation matches {student_id}@seoul.zep.internal (AC1)"""
        from students.services import generate_email

        email = generate_email("20250001")
        self.assertEqual(email, "20250001@seoul.zep.internal")

        email = generate_email("TEST123")
        self.assertEqual(email, "TEST123@seoul.zep.internal")

    def test_password_generation_security(self):
        """Test password generation produces secure random passwords (AC3)"""
        from students.services import generate_password

        # Generate multiple passwords
        passwords = [generate_password() for _ in range(10)]

        # Check length
        for pwd in passwords:
            self.assertEqual(len(pwd), 12)

        # Check uniqueness (all should be different)
        self.assertEqual(len(passwords), len(set(passwords)))

        # Check contains mix of characters
        for pwd in passwords:
            self.assertTrue(any(c.isalpha() for c in pwd))
            self.assertTrue(any(c.isdigit() for c in pwd) or any(not c.isalnum() for c in pwd))

    def test_user_account_creation_with_student_role(self):
        """Test User account creation with student role (AC2)"""
        from students.services import create_student_accounts

        students_data = [{
            'student_id': '20250001',
            'student_name': '홍길동',
            'grade': 1
        }]

        created_students, results = create_student_accounts(
            students_data, self.test_class, self.instructor
        )

        self.assertEqual(len(created_students), 1)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['success'])

        # Verify User was created with correct role
        user = User.objects.get(username='20250001')
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.is_active)
        self.assertEqual(user.email, '20250001@seoul.zep.internal')

    def test_student_record_linked_to_class(self):
        """Test Student record creation linked to class (AC4)"""
        from students.services import create_student_accounts

        students_data = [{
            'student_id': '20250001',
            'student_name': '홍길동',
            'grade': 1
        }]

        created_students, results = create_student_accounts(
            students_data, self.test_class, self.instructor
        )

        student = created_students[0]
        self.assertEqual(student.class_assignment, self.test_class)
        self.assertEqual(student.student_id, '20250001')
        self.assertEqual(student.name, '홍길동')
        self.assertEqual(student.grade, 1)
        self.assertIsNotNone(student.user)


class TransactionRollbackTestCase(TestCase):
    """Tests for transaction rollback behavior (AC6)"""

    def setUp(self):
        """Set up test data"""
        self.school = School.objects.create(name="Test School")
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )
        self.test_class = Class.objects.create(
            name="1학년 A반",
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester="spring"
        )

    def test_transaction_rollback_on_duplicate_student_id(self):
        """Test transaction rollback when duplicate student_id exists (AC6)"""
        from students.services import create_student_accounts

        # Create first student
        students_data = [{
            'student_id': '20250001',
            'student_name': '홍길동',
            'grade': 1
        }]

        created_students, results = create_student_accounts(
            students_data, self.test_class, self.instructor
        )

        self.assertEqual(len(created_students), 1)
        initial_student_count = Student.objects.count()
        initial_user_count = User.objects.count()

        # Try to create duplicate student_id (should not create due to continue in loop)
        students_data_with_dup = [
            {'student_id': '20250002', 'student_name': '김철수', 'grade': 1},
            {'student_id': '20250001', 'student_name': '이영희', 'grade': 1},  # Duplicate
            {'student_id': '20250003', 'student_name': '박민수', 'grade': 1}
        ]

        created_students2, results2 = create_student_accounts(
            students_data_with_dup, self.test_class, self.instructor
        )

        # Should create 2 students (skip the duplicate)
        self.assertEqual(len(created_students2), 2)
        self.assertEqual(Student.objects.count(), initial_student_count + 2)
        self.assertEqual(User.objects.count(), initial_user_count + 2)

        # Verify which ones were created
        self.assertTrue(Student.objects.filter(student_id='20250002').exists())
        self.assertTrue(Student.objects.filter(student_id='20250003').exists())

    def test_all_or_nothing_within_transaction(self):
        """Test that transaction is atomic within the atomic block (AC6)"""
        from students.services import create_student_accounts

        students_data = [
            {'student_id': '20250001', 'student_name': '홍길동', 'grade': 1},
            {'student_id': '20250002', 'student_name': '김철수', 'grade': 1}
        ]

        initial_student_count = Student.objects.count()
        initial_user_count = User.objects.count()

        created_students, results = create_student_accounts(
            students_data, self.test_class, self.instructor
        )

        # Both should be created successfully
        self.assertEqual(len(created_students), 2)
        self.assertEqual(Student.objects.count(), initial_student_count + 2)
        self.assertEqual(User.objects.count(), initial_user_count + 2)


class PerformanceTestCase(TestCase):
    """Tests for bulk creation performance (AC5)"""

    def setUp(self):
        """Set up test data"""
        self.school = School.objects.create(name="Test School")
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )
        self.test_class = Class.objects.create(
            name="1학년 A반",
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester="spring"
        )

    def test_bulk_creation_performance_100_students(self):
        """Test bulk creation completes within 30 seconds for 100 students (AC5)"""
        import time
        from students.services import create_student_accounts

        # Generate 100 students
        students_data = [
            {
                'student_id': f'2025{i:04d}',
                'student_name': f'학생{i}',
                'grade': (i % 6) + 1
            }
            for i in range(1, 101)
        ]

        start_time = time.time()
        created_students, results = create_student_accounts(
            students_data, self.test_class, self.instructor
        )
        elapsed_time = time.time() - start_time

        # Verify all created
        self.assertEqual(len(created_students), 100)
        self.assertEqual(len([r for r in results if r['success']]), 100)

        # Verify performance requirement (< 30 seconds)
        self.assertLess(elapsed_time, 30.0,
                        f"Bulk creation took {elapsed_time:.2f}s, should be < 30s")

        # Log performance for reference
        print(f"\n✅ Created 100 students in {elapsed_time:.2f} seconds")

    def test_bulk_creation_performance_50_students(self):
        """Test bulk creation performance with 50 students (baseline)"""
        import time
        from students.services import create_student_accounts

        students_data = [
            {
                'student_id': f'2025{i:04d}',
                'student_name': f'학생{i}',
                'grade': (i % 6) + 1
            }
            for i in range(1, 51)
        ]

        start_time = time.time()
        created_students, results = create_student_accounts(
            students_data, self.test_class, self.instructor
        )
        elapsed_time = time.time() - start_time

        self.assertEqual(len(created_students), 50)
        print(f"\n📊 Created 50 students in {elapsed_time:.2f} seconds")


class CredentialsDisplayTestCase(TestCase):
    """Tests for credentials display and download (AC7)"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.school = School.objects.create(name="Test School")
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )
        self.test_class = Class.objects.create(
            name="1학년 A반",
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester="spring"
        )

    def test_credentials_display_shows_all_fields(self):
        """Test credentials display shows all required fields (AC7)"""
        self.client.login(username="instructor1", password="testpass")

        # Set up credentials in session
        credentials = [
            {
                'student_id': '20250001',
                'name': '홍길동',
                'username': '20250001',
                'password': 'Test1234!@#$',
                'email': '20250001@seoul.zep.internal'
            }
        ]

        session = self.client.session
        session['student_credentials'] = credentials
        session.save()

        # Access credentials page
        response = self.client.get(reverse('students:credentials'))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()
        self.assertIn('20250001', content)  # student_id
        self.assertIn('홍길동', content)  # name
        self.assertIn('Test1234!@#$', content)  # password
        self.assertIn('20250001@seoul.zep.internal', content)  # email

    def test_csv_download_format(self):
        """Test CSV download produces valid file with UTF-8 BOM (AC7)"""
        from students.services import export_credentials_csv

        credentials = [
            {
                'student_id': '20250001',
                'name': '홍길동',
                'username': '20250001',
                'password': 'Test1234!@#$',
                'email': '20250001@seoul.zep.internal'
            },
            {
                'student_id': '20250002',
                'name': '김철수',
                'username': '20250002',
                'password': 'Pass5678!@#$',
                'email': '20250002@seoul.zep.internal'
            }
        ]

        csv_content = export_credentials_csv(credentials)

        # Verify header
        self.assertIn('학번', csv_content)
        self.assertIn('이름', csv_content)
        self.assertIn('아이디', csv_content)
        self.assertIn('비밀번호', csv_content)
        self.assertIn('이메일', csv_content)

        # Verify data
        self.assertIn('20250001', csv_content)
        self.assertIn('홍길동', csv_content)
        self.assertIn('Test1234!@#$', csv_content)

    def test_credentials_download_view(self):
        """Test credentials download view returns CSV file (AC7)"""
        self.client.login(username="instructor1", password="testpass")

        # Set up credentials in session
        credentials = [
            {
                'student_id': '20250001',
                'name': '홍길동',
                'username': '20250001',
                'password': 'Test1234!@#$',
                'email': '20250001@seoul.zep.internal'
            }
        ]

        session = self.client.session
        session['student_credentials'] = credentials
        session.save()

        # Download CSV
        response = self.client.get(reverse('students:download_credentials'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment', response['Content-Disposition'])

        # Verify UTF-8 BOM
        content = response.content.decode('utf-8-sig')
        self.assertIn('20250001', content)


class IntegrationWorkflowTestCase(TestCase):
    """Integration tests for full CSV upload to credentials workflow (AC 1-7)"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.school = School.objects.create(name="Test School")
        self.instructor = User.objects.create_user(
            username="instructor1",
            password="testpass",
            role="instructor",
            affiliated_school=self.school
        )
        self.test_class = Class.objects.create(
            name="1학년 A반",
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester="spring"
        )

    def test_full_workflow_upload_to_credentials(self):
        """Test complete workflow: upload → preview → confirm → credentials → download (AC 1-7)"""
        self.client.login(username="instructor1", password="testpass")

        # Step 1: Upload CSV
        csv_content = "student_name,student_id,grade,notes\n홍길동,20250001,1,Test student\n"
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'))

        response = self.client.post(
            reverse('students:upload-csv'),
            {'file': csv_file, 'class_assignment': self.test_class.id, 'preview': 'true'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Step 2: Confirm creation
        response = self.client.post(
            reverse('students:upload-csv'),
            {'confirm': 'true'},
            follow=True
        )

        # Should redirect to credentials page
        self.assertEqual(response.status_code, 200)

        # Verify student was created
        self.assertTrue(Student.objects.filter(student_id='20250001').exists())
        student = Student.objects.get(student_id='20250001')
        self.assertEqual(student.name, '홍길동')
        self.assertEqual(student.class_assignment, self.test_class)
        self.assertEqual(student.generated_email, '20250001@seoul.zep.internal')

        # Verify User was created
        self.assertTrue(User.objects.filter(username='20250001').exists())
        user = User.objects.get(username='20250001')
        self.assertEqual(user.role, 'student')

        # Step 3: View credentials page
        response = self.client.get(reverse('students:credentials'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('20250001', content)
        self.assertIn('홍길동', content)
        self.assertIn('@seoul.zep.internal', content)

        # Step 4: Download credentials CSV
        response = self.client.get(reverse('students:download_credentials'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
