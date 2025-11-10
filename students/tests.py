from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import School, Class, Student, FailedSpaceCreation

User = get_user_model()


class SchoolModelTest(TestCase):
    """Test cases for School model."""

    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(
            name='Test Elementary School',
            address='서울시 강남구 테스트로 123',
            contact_phone='02-1234-5678',
            contact_email='test@school.edu'
        )

    def test_school_creation(self):
        """Test School model creation with all required fields (AC1)."""
        self.assertEqual(self.school.name, 'Test Elementary School')
        self.assertEqual(self.school.address, '서울시 강남구 테스트로 123')
        self.assertEqual(self.school.contact_phone, '02-1234-5678')
        self.assertEqual(self.school.contact_email, 'test@school.edu')
        self.assertIsNotNone(self.school.created_at)
        self.assertIsNotNone(self.school.updated_at)

    def test_school_str(self):
        """Test School __str__ returns name (AC1)."""
        self.assertEqual(str(self.school), 'Test Elementary School')

    def test_school_name_index(self):
        """Test that School.name has index for performance (AC6)."""
        # Django creates indexes automatically based on Meta.indexes
        # This test verifies the model is configured correctly
        indexes = [index.name for index in School._meta.indexes]
        self.assertTrue(any('name' in str(index.fields) for index in School._meta.indexes))

    def test_school_class_count_zero(self):
        """Test School.class_count() returns 0 when no classes (AC1)."""
        self.assertEqual(self.school.class_count(), 0)

    def test_school_class_count_multiple(self):
        """Test School.class_count() returns correct count (AC1)."""
        # Create instructor
        instructor = User.objects.create_user(
            username='instructor1',
            password='testpass',
            role='instructor'
        )

        # Create classes
        Class.objects.create(
            name='1학년 A반',
            school=self.school,
            instructor=instructor,
            academic_year=2025,
            semester='spring'
        )
        Class.objects.create(
            name='1학년 B반',
            school=self.school,
            instructor=instructor,
            academic_year=2025,
            semester='spring'
        )

        self.assertEqual(self.school.class_count(), 2)

    def test_school_optional_fields(self):
        """Test School can be created with minimal fields."""
        minimal_school = School.objects.create(name='Minimal School')
        self.assertEqual(minimal_school.name, 'Minimal School')
        self.assertEqual(minimal_school.address, '')
        self.assertEqual(minimal_school.contact_phone, '')
        self.assertEqual(minimal_school.contact_email, '')


class ClassModelTest(TestCase):
    """Test cases for Class model."""

    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(name='Test School')
        self.instructor = User.objects.create_user(
            username='instructor1',
            password='testpass',
            role='instructor'
        )
        self.class_obj = Class.objects.create(
            name='1학년 A반',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring',
            description='Spring semester first grade class'
        )

    def test_class_creation_with_all_fields(self):
        """Test Class model creation with all fields (AC2)."""
        self.assertEqual(self.class_obj.name, '1학년 A반')
        self.assertEqual(self.class_obj.school, self.school)
        self.assertEqual(self.class_obj.instructor, self.instructor)
        self.assertEqual(self.class_obj.academic_year, 2025)
        self.assertEqual(self.class_obj.semester, 'spring')
        self.assertEqual(self.class_obj.description, 'Spring semester first grade class')
        self.assertIsNotNone(self.class_obj.created_at)
        self.assertIsNotNone(self.class_obj.updated_at)

    def test_class_str(self):
        """Test Class __str__ returns formatted string with school and academic info (AC2)."""
        expected = f"{self.school.name} - 1학년 A반 (2025 1학기)"
        self.assertEqual(str(self.class_obj), expected)

    def test_class_school_relationship(self):
        """Test Class ForeignKey relationship with School (AC2)."""
        self.assertEqual(self.class_obj.school, self.school)
        self.assertIn(self.class_obj, self.school.classes.all())

    def test_class_instructor_relationship(self):
        """Test Class ForeignKey relationship with Instructor (AC2)."""
        self.assertEqual(self.class_obj.instructor, self.instructor)
        self.assertIn(self.class_obj, self.instructor.taught_classes.all())

    def test_class_student_count_zero(self):
        """Test Class.student_count() returns 0 when no students (AC2)."""
        self.assertEqual(self.class_obj.student_count(), 0)

    def test_class_student_count_multiple(self):
        """Test Class.student_count() returns correct count (AC2)."""
        # Create students
        for i in range(3):
            user = User.objects.create_user(
                username=f'student{i}',
                password='testpass',
                role='student'
            )
            Student.objects.create(
                user=user,
                student_id=f'2025{i:04d}',
                name=f'학생{i}',
                grade=1,
                class_assignment=self.class_obj,
                generated_email=f'2025{i:04d}@seoul.zep.internal'
            )

        self.assertEqual(self.class_obj.student_count(), 3)

    def test_class_indexes(self):
        """Test Class has indexes on school, academic_year, semester (AC6)."""
        # Verify indexes exist in model Meta
        indexes = Class._meta.indexes
        self.assertTrue(len(indexes) > 0)
        # Check for composite index on school, academic_year, semester
        index_fields = [list(index.fields) for index in indexes]
        self.assertIn(['school', 'academic_year', 'semester'], index_fields)

    def test_class_cascade_delete_from_school(self):
        """Test School deletion cascades to Class (AC7)."""
        class_id = self.class_obj.id
        self.school.delete()

        # Class should be deleted
        self.assertFalse(Class.objects.filter(id=class_id).exists())

    def test_class_instructor_set_null(self):
        """Test User (instructor) deletion SET_NULL for Class (AC7)."""
        instructor_id = self.instructor.id
        self.instructor.delete()

        # Class should still exist but instructor should be None
        self.class_obj.refresh_from_db()
        self.assertIsNone(self.class_obj.instructor)


class StudentModelTest(TestCase):
    """Test cases for Student model."""

    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(name='Test School')
        self.instructor = User.objects.create_user(
            username='instructor1',
            password='testpass',
            role='instructor'
        )
        self.class_obj = Class.objects.create(
            name='1학년 A반',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )
        self.user = User.objects.create_user(
            username='student1',
            password='testpass',
            role='student'
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id='20250001',
            name='김철수',
            grade=1,
            class_assignment=self.class_obj,
            generated_email='20250001@seoul.zep.internal',
            zep_space_url='https://zep.us/play/abc123'
        )

    def test_student_creation_with_all_fields(self):
        """Test Student model creation with all required fields (AC3)."""
        self.assertEqual(self.student.user, self.user)
        self.assertEqual(self.student.student_id, '20250001')
        self.assertEqual(self.student.name, '김철수')
        self.assertEqual(self.student.grade, 1)
        self.assertEqual(self.student.class_assignment, self.class_obj)
        self.assertEqual(self.student.generated_email, '20250001@seoul.zep.internal')
        self.assertEqual(self.student.zep_space_url, 'https://zep.us/play/abc123')
        self.assertIsNotNone(self.student.created_at)
        self.assertIsNotNone(self.student.updated_at)

    def test_student_str(self):
        """Test Student __str__ returns name and student_id (AC3)."""
        self.assertEqual(str(self.student), '김철수 (20250001)')

    def test_student_id_unique_constraint(self):
        """Test Student.student_id unique constraint (AC3)."""
        another_user = User.objects.create_user(
            username='student2',
            password='testpass',
            role='student'
        )

        with self.assertRaises(IntegrityError):
            Student.objects.create(
                user=another_user,
                student_id='20250001',  # Duplicate
                name='김영희',
                generated_email='duplicate@seoul.zep.internal'
            )

    def test_student_user_relationship(self):
        """Test Student OneToOne relationship with User (AC3)."""
        self.assertEqual(self.student.user, self.user)
        self.assertEqual(self.user.student_profile, self.student)

    def test_student_class_relationship(self):
        """Test Student ForeignKey relationship with Class (AC3)."""
        self.assertEqual(self.student.class_assignment, self.class_obj)
        self.assertIn(self.student, self.class_obj.students.all())

    def test_student_is_space_created_true(self):
        """Test Student.is_space_created property returns True when URL exists (AC3)."""
        self.assertTrue(self.student.is_space_created)

    def test_student_is_space_created_false(self):
        """Test Student.is_space_created property returns False when URL is empty (AC3)."""
        student_no_space = Student.objects.create(
            user=User.objects.create_user(
                username='student_no_space',
                password='testpass',
                role='student'
            ),
            student_id='20250002',
            name='박민수',
            generated_email='20250002@seoul.zep.internal',
            zep_space_url=''  # Empty URL
        )
        self.assertFalse(student_no_space.is_space_created)

    def test_student_indexes(self):
        """Test Student has indexes on student_id and class_assignment (AC6)."""
        indexes = Student._meta.indexes
        self.assertTrue(len(indexes) > 0)
        index_fields = [list(index.fields) for index in indexes]
        self.assertIn(['student_id'], index_fields)
        self.assertIn(['class_assignment'], index_fields)

    def test_student_class_deletion_set_null(self):
        """Test Class deletion SET_NULL for Students (AC7)."""
        self.class_obj.delete()

        # Student should still exist but class_assignment should be None
        self.student.refresh_from_db()
        self.assertIsNone(self.student.class_assignment)

    def test_student_user_deletion_cascade(self):
        """Test User (student) deletion CASCADE for Student profile (AC7)."""
        student_id = self.student.id
        self.user.delete()

        # Student profile should be deleted
        self.assertFalse(Student.objects.filter(id=student_id).exists())

    def test_student_without_class(self):
        """Test Student can exist without class assignment."""
        unassigned_user = User.objects.create_user(
            username='unassigned',
            password='testpass',
            role='student'
        )
        unassigned_student = Student.objects.create(
            user=unassigned_user,
            student_id='20250999',
            name='미배정학생',
            generated_email='20250999@seoul.zep.internal',
            class_assignment=None
        )
        self.assertIsNone(unassigned_student.class_assignment)


class ModelRelationshipTest(TestCase):
    """Test complex relationships between models."""

    def setUp(self):
        """Set up hierarchical test data."""
        self.school = School.objects.create(name='Hierarchy Test School')
        self.instructor = User.objects.create_user(
            username='instructor1',
            password='testpass',
            role='instructor'
        )
        self.class1 = Class.objects.create(
            name='1-A',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )
        self.class2 = Class.objects.create(
            name='1-B',
            school=self.school,
            instructor=self.instructor,
            academic_year=2025,
            semester='spring'
        )

    def test_school_to_classes_to_students_hierarchy(self):
        """Test full hierarchy: School → Classes → Students."""
        # Create students in class1
        for i in range(2):
            user = User.objects.create_user(
                username=f'student_c1_{i}',
                password='testpass',
                role='student'
            )
            Student.objects.create(
                user=user,
                student_id=f'2025100{i}',
                name=f'Class1학생{i}',
                class_assignment=self.class1,
                generated_email=f'2025100{i}@seoul.zep.internal'
            )

        # Create students in class2
        for i in range(3):
            user = User.objects.create_user(
                username=f'student_c2_{i}',
                password='testpass',
                role='student'
            )
            Student.objects.create(
                user=user,
                student_id=f'2025200{i}',
                name=f'Class2학생{i}',
                class_assignment=self.class2,
                generated_email=f'2025200{i}@seoul.zep.internal'
            )

        # Verify hierarchy
        self.assertEqual(self.school.class_count(), 2)
        self.assertEqual(self.class1.student_count(), 2)
        self.assertEqual(self.class2.student_count(), 3)

        # Verify reverse relationships
        all_classes = self.school.classes.all()
        self.assertEqual(all_classes.count(), 2)

        all_students_c1 = self.class1.students.all()
        self.assertEqual(all_students_c1.count(), 2)

    def test_cascade_delete_preserves_students(self):
        """Test that deleting class preserves students (AC7)."""
        # Create student
        user = User.objects.create_user(
            username='student1',
            password='testpass',
            role='student'
        )
        student = Student.objects.create(
            user=user,
            student_id='20250001',
            name='학생1',
            class_assignment=self.class1,
            generated_email='20250001@seoul.zep.internal'
        )

        class_id = self.class1.id
        student_id = student.id

        # Delete class
        self.class1.delete()

        # Class should be gone
        self.assertFalse(Class.objects.filter(id=class_id).exists())

        # Student should still exist but unassigned
        self.assertTrue(Student.objects.filter(id=student_id).exists())
        student.refresh_from_db()
        self.assertIsNone(student.class_assignment)


class FailedSpaceCreationModelTest(TestCase):
    """Test cases for FailedSpaceCreation model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='student1',
            password='testpass',
            role='student'
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id='20250001',
            name='김철수',
            generated_email='20250001@seoul.zep.internal'
        )
        self.failed_attempt = FailedSpaceCreation.objects.create(
            student=self.student,
            error_message='API connection timeout',
            retry_count=1
        )

    def test_failed_space_creation(self):
        """Test FailedSpaceCreation model creation."""
        self.assertEqual(self.failed_attempt.student, self.student)
        self.assertEqual(self.failed_attempt.error_message, 'API connection timeout')
        self.assertEqual(self.failed_attempt.retry_count, 1)
        self.assertFalse(self.failed_attempt.resolved)
        self.assertIsNone(self.failed_attempt.resolved_at)

    def test_failed_space_creation_str(self):
        """Test FailedSpaceCreation __str__ method."""
        expected = '김철수 - API connection timeout'
        self.assertEqual(str(self.failed_attempt), expected)

    def test_failed_space_creation_relationship(self):
        """Test relationship with Student."""
        self.assertEqual(self.failed_attempt.student, self.student)
        self.assertIn(self.failed_attempt, self.student.failed_space_attempts.all())
