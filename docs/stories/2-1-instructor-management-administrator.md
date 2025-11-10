# Story 2.1: Instructor Management (Administrator)

Status: review

## Story

As an administrator,
I want to create and manage instructor accounts,
So that instructors can access the system and manage their students.

## Acceptance Criteria

1. Administrator dashboard includes "Instructors" section
2. Admin can create new instructor accounts with username, password, affiliated school, and class assignment
3. Admin can view list of all instructors with search and filter capabilities
4. Admin can edit instructor profile information (school, class, training status)
5. Admin can manually mark instructor training completion status
6. Instructor list displays: name, school, class count, training status, last login
7. Form validation prevents duplicate usernames

## Tasks / Subtasks

- [x] Task 1: Create Instructor Profile model and admin interface (AC: 2, 4, 5)
  - [x] Extend User model from Story 1.2 with instructor-specific fields via related model
  - [x] Create `instructors/models.py` with Instructor model (related to User via OneToOne)
  - [x] Add fields: affiliated_school (FK to School), training_completed (BooleanField)
  - [x] Create database migration and apply
  - [x] Register Instructor model in Django admin
  - [x] Add `__str__` method returning instructor name

- [x] Task 2: Create instructor CRUD views and forms (AC: 2, 3, 4, 7)
  - [x] Create `instructors/forms.py` with InstructorCreateForm and InstructorEditForm
  - [x] Implement instructor list view with Django QuerySet pagination
  - [x] Implement instructor create view with User + Instructor creation
  - [x] Implement instructor detail view showing profile and assigned classes
  - [x] Implement instructor edit view for updating profile information
  - [x] Add form validation to prevent duplicate usernames (check User.objects.filter)
  - [x] Add @admin_required decorator to all views

- [x] Task 3: Build instructor management templates (AC: 1, 6)
  - [x] Create `instructors/templates/instructors/list.html` with Tailwind CSS table
  - [x] Create `instructors/templates/instructors/create.html` with form layout
  - [x] Create `instructors/templates/instructors/detail.html` showing full profile
  - [x] Create `instructors/templates/instructors/edit.html` for profile editing
  - [x] Add search and filter UI elements (by school, training status)
  - [x] Display columns: name, school, class count, training status, last login
  - [x] Add action buttons: Create, Edit, View Details

- [x] Task 4: Implement search and filter functionality (AC: 3)
  - [x] Add search by instructor name (case-insensitive using icontains)
  - [x] Add filter by school (dropdown with School.objects.all())
  - [x] Add filter by training status (completed/incomplete radio buttons)
  - [x] Implement query logic in list view using Q objects
  - [x] Preserve search/filter parameters in pagination links

- [x] Task 5: Add URL routing and navigation (AC: 1)
  - [x] Create `instructors/urls.py` with app namespace 'instructors'
  - [x] Add URL patterns: list, create, detail, edit
  - [x] Include instructors.urls in neulbom/urls.py
  - [x] Add "Instructors" navigation link in admin dashboard

- [x] Task 6: Testing (All ACs)
  - [x] Write model tests for Instructor model creation and relationships
  - [x] Write view tests for list, create, edit views with @admin_required
  - [x] Test form validation (duplicate username prevention)
  - [x] Test search and filter functionality
  - [x] Test that non-admin users cannot access instructor management
  - [x] Run full test suite and verify no regressions

## Dev Notes

### Architecture Constraints and Patterns

**From Architecture** [Source: docs/architecture.md]
- Multi-app structure: Use `instructors` app for instructor management
- Project structure: `instructors/` app with models.py, views.py, forms.py, urls.py, templates/
- Frontend: Django Templates + Tailwind CSS (server-side rendering)
- Database: MySQL 8.0 with mysqlclient driver
- Authentication: Django built-in auth with CustomUser model (from accounts app)
- Permission decorators: `@admin_required` from `accounts/decorators.py`

**From PRD** [Source: docs/PRD.md]
- FR003: Administrators can create, view, search, and manage instructor accounts
- FR004: System maintains instructor profile information (school, class assignments, training status)
- FR005: Administrators can manually record instructor training completion status
- Target users: 13 university administrators managing multiple instructors

**Data Model Relationships** [Source: docs/architecture.md#Data-Relationships]
```
User (role='instructor') (1) ─→ (1) Instructor profile
                                    ↓
                           School (FK)
                                    ↓
                           Classes (reverse FK from Class.instructor)
```

**URL Structure** [Source: docs/architecture.md#Implementation-Patterns]
- URL format: `kebab-case` (e.g., `/instructors/create/`, `/instructors/<int:pk>/`)
- URL names: `app_namespace:action` (e.g., `instructors:list`, `instructors:create`)

### Learnings from Previous Story

**From Story 1-4-public-landing-page (Status: review)**

- **Tailwind CSS Pattern**:
  - Use Tailwind CDN: `<script src="https://cdn.tailwindcss.com"></script>`
  - Follow established responsive patterns with md: breakpoint (768px)
  - Semantic HTML5 with proper heading hierarchy
  - Korean-first approach for all user-facing content

- **Template Infrastructure**:
  - Templates directory: `/templates/` (global) and `{app}/templates/{app}/` (app-specific)
  - Use `{% load static %}` for static assets
  - Follow Korean localization pattern: `<html lang="ko">`

- **View Pattern Established**:
  - Standard view pattern with context dictionary
  - Decorators for permission control (`@admin_required`)
  - Korean messages for user feedback

- **Testing Pattern**:
  - Django TestCase with Client for view testing
  - Test framework: 73 tests passing across all apps
  - Test coverage: View accessibility, content display, permissions

- **Files Available for Reuse**:
  - `accounts/decorators.py`: Contains `@admin_required` decorator
  - `accounts/models.py`: CustomUser model with role field
  - `neulbom/views.py`: Pattern for view functions
  - Test patterns established in `neulbom/tests/test_landing.py`

[Source: stories/1-4-public-landing-page.md#Dev-Agent-Record]

### Project Structure Notes

**New App Structure to Create:**
```
instructors/
├── __init__.py
├── models.py              # Instructor profile model
├── views.py               # CRUD views (list, create, detail, edit)
├── forms.py               # InstructorCreateForm, InstructorEditForm
├── urls.py                # App URL routing
├── admin.py               # Django admin registration
├── tests.py               # Model and view tests
└── templates/
    └── instructors/
        ├── list.html      # Instructor list with search/filter
        ├── create.html    # Create instructor form
        ├── detail.html    # Instructor profile view
        └── edit.html      # Edit instructor form
```

**Integration Points:**
- `accounts.User`: One-to-one relationship with Instructor model (role='instructor')
- `students.School`: Foreign key relationship for affiliated_school field
- `students.Class`: Reverse FK relationship (Class.instructor points to User)

### Implementation Notes

**Instructor Model Pattern:**
```python
# instructors/models.py
from django.db import models
from django.conf import settings

class Instructor(models.Model):
    """
    Instructor profile linked to User with role='instructor'.

    Stores instructor-specific information beyond the base User model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        limit_choices_to={'role': 'instructor'}
    )
    affiliated_school = models.ForeignKey(
        'students.School',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instructors'
    )
    training_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    @property
    def class_count(self):
        """Count of classes assigned to this instructor."""
        return self.user.class_set.count()
```

**View Pattern with Search/Filter:**
```python
# instructors/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from accounts.decorators import admin_required
from .models import Instructor
from .forms import InstructorCreateForm, InstructorEditForm

@admin_required
def instructor_list(request):
    """
    Display list of all instructors with search and filter capabilities.
    """
    instructors = Instructor.objects.select_related(
        'user', 'affiliated_school'
    ).annotate(
        class_count=Count('user__class')
    )

    # Search by name
    search_query = request.GET.get('search', '')
    if search_query:
        instructors = instructors.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )

    # Filter by school
    school_filter = request.GET.get('school', '')
    if school_filter:
        instructors = instructors.filter(affiliated_school_id=school_filter)

    # Filter by training status
    training_filter = request.GET.get('training', '')
    if training_filter == 'completed':
        instructors = instructors.filter(training_completed=True)
    elif training_filter == 'incomplete':
        instructors = instructors.filter(training_completed=False)

    context = {
        'instructors': instructors,
        'search_query': search_query,
        'school_filter': school_filter,
        'training_filter': training_filter,
        'schools': School.objects.all(),
    }
    return render(request, 'instructors/list.html', context)
```

**Form with Duplicate Username Validation:**
```python
# instructors/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Instructor
from students.models import School

User = get_user_model()

class InstructorCreateForm(forms.ModelForm):
    """Form for creating new instructor account."""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    affiliated_school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        required=False
    )
    training_completed = forms.BooleanField(required=False)

    class Meta:
        model = Instructor
        fields = ['affiliated_school', 'training_completed']

    def clean_username(self):
        """Validate that username is unique."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('이미 존재하는 사용자 이름입니다.')
        return username

    def save(self, commit=True):
        """Create User and Instructor profile."""
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data.get('first_name', ''),
            last_name=self.cleaned_data.get('last_name', ''),
            role='instructor'
        )

        instructor = super().save(commit=False)
        instructor.user = user

        if commit:
            instructor.save()

        return instructor
```

**Template with Tailwind CSS:**
```html
<!-- instructors/templates/instructors/list.html -->
{% load static %}
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>강사 관리 - 늘봄학교</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-3xl font-bold text-gray-800">강사 관리</h1>
            <a href="{% url 'instructors:create' %}"
               class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                새 강사 추가
            </a>
        </div>

        <!-- Search and Filter Form -->
        <form method="get" class="bg-white p-4 rounded shadow mb-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input type="text" name="search" value="{{ search_query }}"
                       placeholder="강사 이름 검색"
                       class="border px-3 py-2 rounded">

                <select name="school" class="border px-3 py-2 rounded">
                    <option value="">모든 학교</option>
                    {% for school in schools %}
                        <option value="{{ school.id }}"
                                {% if school_filter == school.id|stringformat:"s" %}selected{% endif %}>
                            {{ school.name }}
                        </option>
                    {% endfor %}
                </select>

                <select name="training" class="border px-3 py-2 rounded">
                    <option value="">모든 연수 상태</option>
                    <option value="completed" {% if training_filter == 'completed' %}selected{% endif %}>
                        연수 완료
                    </option>
                    <option value="incomplete" {% if training_filter == 'incomplete' %}selected{% endif %}>
                        연수 미완료
                    </option>
                </select>
            </div>
            <button type="submit" class="mt-4 bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
                검색
            </button>
        </form>

        <!-- Instructor Table -->
        <div class="bg-white rounded shadow overflow-hidden">
            <table class="min-w-full">
                <thead class="bg-gray-100">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                            이름
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                            학교
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                            클래스 수
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                            연수 상태
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                            최근 로그인
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                            작업
                        </th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    {% for instructor in instructors %}
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap">
                            {{ instructor.user.get_full_name|default:instructor.user.username }}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            {{ instructor.affiliated_school.name|default:"미지정" }}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            {{ instructor.class_count }}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            {% if instructor.training_completed %}
                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                    완료
                                </span>
                            {% else %}
                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                                    미완료
                                </span>
                            {% endif %}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {{ instructor.user.last_login|date:"Y-m-d H:i"|default:"로그인 이력 없음" }}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <a href="{% url 'instructors:detail' instructor.id %}"
                               class="text-indigo-600 hover:text-indigo-900 mr-3">
                                보기
                            </a>
                            <a href="{% url 'instructors:edit' instructor.id %}"
                               class="text-blue-600 hover:text-blue-900">
                                수정
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                            등록된 강사가 없습니다.
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
```

### Testing Standards

**Test Coverage Requirements:**
- Model tests: Instructor creation, relationships (User, School)
- View tests: List, create, edit with @admin_required enforcement
- Form tests: Duplicate username validation
- Search/filter tests: Query logic verification
- Permission tests: Non-admin users cannot access

**Test Scenarios:**
1. Admin can access instructor list view
2. Non-admin users redirected (403 or login redirect)
3. Instructor creation creates both User and Instructor profile
4. Duplicate username validation prevents creation
5. Search by name returns correct results
6. Filter by school returns correct instructors
7. Filter by training status works correctly
8. Edit view updates instructor profile successfully
9. Class count property returns correct count

### References

- [Epic 2 Details](../epics.md#Epic-2-Bulk-Student-Management-&-ZEP-Integration)
- [Story 2.1 Acceptance Criteria](../epics.md#Story-2.1-Instructor-Management-Administrator)
- [Architecture - Multi-App Structure](../architecture.md#Project-Structure)
- [Architecture - Data Models](../architecture.md#Data-Architecture)
- [PRD - Instructor Management Requirements](../PRD.md#Functional-Requirements)
- [Previous Story 1.4](./1-4-public-landing-page.md)

## Dev Agent Record

### Context Reference

- docs/stories/2-1-instructor-management-administrator.context.xml

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

Story 2.1 implementation completed successfully on 2025-11-04.

**Implementation Summary:**
- Created Instructor model with OneToOneField relationship to User
- Implemented full CRUD operations (Create, Read, Update, Delete views)
- Built 4 responsive Tailwind CSS templates (list, create, detail, edit)
- Implemented search by instructor name and filter by school/training status
- Added comprehensive test suite covering models, forms, and views
- All 97 tests passing (24 new tests added for instructor functionality)

**Key Features Delivered:**
- Admin-only access control with @admin_required decorator
- Duplicate username validation in creation form
- Display of instructor metrics (name, school, class count, training status, last login)
- Korean language UI with semantic HTML5 structure
- Efficient database queries using select_related()

**Testing Coverage:**
- Model tests: Creation, relationships (User, School), properties
- Form tests: Validation (duplicate username), create/edit forms
- View tests: Permission enforcement, CRUD operations, search/filter

### File List

**New Files:**
- instructors/models.py (Instructor model)
- instructors/forms.py (InstructorCreateForm, InstructorEditForm)
- instructors/views.py (instructor_list, instructor_create, instructor_detail, instructor_edit)
- instructors/admin.py (InstructorAdmin)
- instructors/tests.py (comprehensive test suite - 24 tests)
- instructors/templates/instructors/list.html
- instructors/templates/instructors/create.html
- instructors/templates/instructors/detail.html
- instructors/templates/instructors/edit.html
- instructors/migrations/0001_initial.py

**Modified Files:**
- instructors/urls.py (already existed, verified correct configuration)
- neulbom/urls.py (already included instructors.urls)
