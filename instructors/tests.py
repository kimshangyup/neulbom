from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Instructor
from .forms import InstructorCreateForm, InstructorEditForm
from students.models import School

User = get_user_model()


class InstructorModelTest(TestCase):
    """Test cases for Instructor model."""

    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(name='Test School')
        self.user = User.objects.create_user(
            username='test_instructor',
            password='testpass123',
            role='instructor'
        )
        self.instructor = Instructor.objects.create(
            user=self.user,
            affiliated_school=self.school,
            training_completed=False
        )

    def test_instructor_creation(self):
        """Test instructor profile creation."""
        self.assertEqual(self.instructor.user.username, 'test_instructor')
        self.assertEqual(self.instructor.affiliated_school, self.school)
        self.assertFalse(self.instructor.training_completed)

    def test_instructor_str(self):
        """Test instructor string representation."""
        # Without full name
        self.assertEqual(str(self.instructor), 'test_instructor')

        # With full name
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'
        self.user.save()
        self.assertEqual(str(self.instructor), 'John Doe')

    def test_instructor_class_count(self):
        """Test class_count property."""
        self.assertEqual(self.instructor.class_count, 0)

        # This will be fully testable after Story 2.2 (Class model)
        # For now, just verify the property exists and returns integer
        self.assertIsInstance(self.instructor.class_count, int)

    def test_instructor_user_relationship(self):
        """Test OneToOne relationship with User."""
        self.assertEqual(self.instructor.user, self.user)
        self.assertEqual(self.user.instructor_profile, self.instructor)

    def test_instructor_school_relationship(self):
        """Test ForeignKey relationship with School."""
        self.assertEqual(self.instructor.affiliated_school, self.school)
        self.assertIn(self.instructor, self.school.instructors.all())


class InstructorFormTest(TestCase):
    """Test cases for Instructor forms."""

    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(name='Test School')
        self.existing_user = User.objects.create_user(
            username='existing',
            password='testpass123',
            role='instructor'
        )

    def test_instructor_create_form_valid(self):
        """Test valid instructor creation form."""
        form_data = {
            'username': 'new_instructor',
            'password': 'testpass123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'affiliated_school': self.school.id,
            'training_completed': True
        }
        form = InstructorCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_instructor_create_form_duplicate_username(self):
        """Test duplicate username validation."""
        form_data = {
            'username': 'existing',  # Duplicate
            'password': 'testpass123',
            'affiliated_school': self.school.id,
        }
        form = InstructorCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_instructor_create_form_saves_correctly(self):
        """Test form saves User and Instructor correctly."""
        form_data = {
            'username': 'new_instructor',
            'password': 'testpass123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'affiliated_school': self.school.id,
            'training_completed': True
        }
        form = InstructorCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

        instructor = form.save()

        # Verify User created
        self.assertEqual(instructor.user.username, 'new_instructor')
        self.assertEqual(instructor.user.role, 'instructor')
        self.assertEqual(instructor.user.first_name, 'Jane')

        # Verify Instructor profile created
        self.assertEqual(instructor.affiliated_school, self.school)
        self.assertTrue(instructor.training_completed)

    def test_instructor_edit_form_valid(self):
        """Test valid instructor edit form."""
        instructor = Instructor.objects.create(
            user=self.existing_user,
            affiliated_school=self.school,
            training_completed=False
        )

        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'affiliated_school': self.school.id,
            'training_completed': True
        }
        form = InstructorEditForm(data=form_data, instance=instructor)
        self.assertTrue(form.is_valid())

    def test_instructor_edit_form_updates_correctly(self):
        """Test edit form updates both User and Instructor."""
        instructor = Instructor.objects.create(
            user=self.existing_user,
            affiliated_school=self.school,
            training_completed=False
        )

        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'affiliated_school': self.school.id,
            'training_completed': True
        }
        form = InstructorEditForm(data=form_data, instance=instructor)
        self.assertTrue(form.is_valid())

        updated_instructor = form.save()

        # Verify User updated
        self.assertEqual(updated_instructor.user.first_name, 'Updated')
        self.assertEqual(updated_instructor.user.last_name, 'Name')

        # Verify Instructor updated
        self.assertTrue(updated_instructor.training_completed)


class InstructorViewTest(TestCase):
    """Test cases for Instructor views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.school = School.objects.create(name='Test School')

        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            role='admin'
        )

        # Create non-admin user (student)
        self.student_user = User.objects.create_user(
            username='student',
            password='studentpass',
            role='student'
        )

        # Create instructor
        self.instructor_user = User.objects.create_user(
            username='instructor1',
            password='instrpass',
            role='instructor'
        )
        self.instructor = Instructor.objects.create(
            user=self.instructor_user,
            affiliated_school=self.school,
            training_completed=True
        )

    def test_instructor_list_requires_admin(self):
        """Test that instructor list requires admin role."""
        # Not logged in
        response = self.client.get(reverse('instructors:list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Logged in as student
        self.client.login(username='student', password='studentpass')
        response = self.client.get(reverse('instructors:list'))
        self.assertEqual(response.status_code, 403)  # Permission denied

    def test_instructor_list_accessible_by_admin(self):
        """Test that admin can access instructor list."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('instructors:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '강사 관리')

    def test_instructor_list_displays_instructors(self):
        """Test that instructor list displays all instructors."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('instructors:list'))
        self.assertContains(response, 'instructor1')

    def test_instructor_list_search(self):
        """Test search functionality."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('instructors:list'), {'search': 'instructor1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'instructor1')

    def test_instructor_list_filter_by_school(self):
        """Test filter by school."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('instructors:list'), {'school': self.school.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'instructor1')

    def test_instructor_list_filter_by_training_status(self):
        """Test filter by training status."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('instructors:list'), {'training': 'completed'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'instructor1')

    def test_instructor_create_requires_admin(self):
        """Test that instructor create requires admin role."""
        # Not logged in
        response = self.client.get(reverse('instructors:create'))
        self.assertEqual(response.status_code, 302)

        # Logged in as student
        self.client.login(username='student', password='studentpass')
        response = self.client.get(reverse('instructors:create'))
        self.assertEqual(response.status_code, 403)

    def test_instructor_create_accessible_by_admin(self):
        """Test that admin can access instructor create."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('instructors:create'))
        self.assertEqual(response.status_code, 200)

    def test_instructor_create_post(self):
        """Test creating instructor via POST."""
        self.client.login(username='admin', password='adminpass')
        data = {
            'username': 'new_instructor',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'Instructor',
            'affiliated_school': self.school.id,
            'training_completed': False
        }
        response = self.client.post(reverse('instructors:create'), data)

        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)

        # Verify instructor created
        self.assertTrue(User.objects.filter(username='new_instructor').exists())
        new_user = User.objects.get(username='new_instructor')
        self.assertTrue(hasattr(new_user, 'instructor_profile'))

    def test_instructor_detail_requires_admin(self):
        """Test that instructor detail requires admin role."""
        url = reverse('instructors:detail', args=[self.instructor.id])

        # Not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Logged in as student
        self.client.login(username='student', password='studentpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_instructor_detail_accessible_by_admin(self):
        """Test that admin can access instructor detail."""
        self.client.login(username='admin', password='adminpass')
        url = reverse('instructors:detail', args=[self.instructor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'instructor1')

    def test_instructor_edit_requires_admin(self):
        """Test that instructor edit requires admin role."""
        url = reverse('instructors:edit', args=[self.instructor.id])

        # Not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Logged in as student
        self.client.login(username='student', password='studentpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_instructor_edit_accessible_by_admin(self):
        """Test that admin can access instructor edit."""
        self.client.login(username='admin', password='adminpass')
        url = reverse('instructors:edit', args=[self.instructor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_instructor_edit_post(self):
        """Test editing instructor via POST."""
        self.client.login(username='admin', password='adminpass')
        url = reverse('instructors:edit', args=[self.instructor.id])
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'affiliated_school': self.school.id,
            'training_completed': False  # Changed from True
        }
        response = self.client.post(url, data)

        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)

        # Verify instructor updated
        self.instructor.refresh_from_db()
        self.instructor.user.refresh_from_db()
        self.assertEqual(self.instructor.user.first_name, 'Updated')
        self.assertFalse(self.instructor.training_completed)
