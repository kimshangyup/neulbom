# Decision Architecture

## Executive Summary

This architecture defines the technical foundation for neulbom, a Django-based web platform managing Seoul's after-school education program across 13 universities serving approximately 2,000 elementary students. The architecture prioritizes operational efficiency through bulk automation (CSV-based student registration with automatic ZEP space creation), real-time monitoring for administrators, and a sustainable student portfolio ecosystem. Key architectural decisions emphasize simplicity and proven technology choices, using Django 4.2 LTS with MySQL 8.0, traditional server deployment (DigitalOcean + Nginx + uWSGI), and server-side rendering with Tailwind CSS for rapid development targeting a December 2025 instructor launch and March 2026 official rollout.

## Project Initialization

**Command:**
```bash
django-admin startproject neulbom
cd neulbom
python manage.py startapp accounts
python manage.py startapp instructors
python manage.py startapp students
python manage.py startapp spaces
python manage.py startapp dashboard
python manage.py startapp core
```

**Initial Setup Steps:**
1. Create Django project with standard structure
2. Create five functional apps (accounts, instructors, students, spaces, dashboard) plus core utilities
3. Configure MySQL 8.0 database connection with mysqlclient driver
4. Configure Tailwind CSS build process
5. Set up Nginx + uWSGI on DigitalOcean droplet
6. Configure static files for Nginx direct serving

**Note:** This is a manual Django project setup (no starter template used) to maintain full control over dependencies and configuration, particularly for MySQL and DigitalOcean deployment requirements.

## Decision Summary

| Category | Decision | Version | Affects Epics | Rationale |
| -------- | -------- | ------- | ------------- | --------- |
| Python | Python | 3.8.x | All Epics | Short-term development use (EOL Oct 2024, upgrade to 3.10+ before production recommended) |
| Framework | Django | 4.2 LTS | All Epics | Long-term support until April 2026, Python 3.8 compatible, production-ready |
| Database | MySQL | 8.0 | All Epics | Legacy LTS (EOL April 2026), user preference |
| DB Driver | mysqlclient | Latest stable | All Epics | High performance C-based driver, 3-4x faster than PyMySQL, Django recommended |
| Project Structure | Multi-app (functional) | N/A | All Epics | accounts, instructors, students, spaces, dashboard - maps to Epic boundaries |
| Authentication | Django built-in auth | Django 4.2 | Epic 1 | ID/PW authentication sufficient, CustomUser with role field, no social login needed |
| Deployment | DigitalOcean + Nginx + uWSGI | N/A | All Epics | User managed deployment, cost-efficient, manual control |
| ZEP API Integration | Synchronous sequential | N/A | Epic 2 | Simple implementation, no Celery dependency (performance testing required for NFR002) |
| Static Files | Nginx direct serving | N/A | All Epics | Optimal for DigitalOcean setup, zero additional cost, high performance |
| Frontend | Django Templates + Tailwind CSS | Tailwind latest | Epic 1, 2, 3 | Server-side rendering, modern styling, rapid development, no SPA complexity |
| CSV Processing | pandas | Latest stable | Epic 2 | Unified CSV/Excel handling, data validation capabilities, Django ecosystem standard |
| Error Handling | Auto-retry (3x) + exponential backoff | N/A | Epic 2 | PRD requirement, automatic recovery from transient failures, admin review queue |
| Session Management | Database sessions | Django 4.2 | All Epics | No Redis dependency, few concurrent logins (admins + instructors), MySQL reuse |
| Logging | Python logging + RotatingFileHandler | Python stdlib | All Epics | Standard logging, 10MB rotation, 5 backups, /var/log/neulbom/django.log |
| Date/Time | UTC storage, Asia/Seoul display | N/A | All Epics | Korean timezone for users, UTC for database consistency, ISO 8601 for APIs |
| Testing | Django unittest | Django 4.2 | All Epics | Built-in framework, no additional dependencies, sufficient for Level 2 project |

## Project Structure

```
neulbom/
├── manage.py
├── requirements.txt
├── .env                          # Environment variables (DB, ZEP API key)
├── .gitignore
├── README.md
│
├── neulbom/                      # Project settings
│   ├── __init__.py
│   ├── settings.py               # Django configuration
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py                   # uWSGI entry point
│   └── asgi.py
│
├── accounts/                     # Authentication & user management
│   ├── __init__.py
│   ├── models.py                 # CustomUser model (role field: admin/instructor/student)
│   ├── views.py                  # Login, logout views
│   ├── forms.py                  # Login forms
│   ├── urls.py
│   ├── admin.py
│   ├── decorators.py             # @admin_required, @instructor_required
│   ├── tests.py
│   └── templates/
│       └── accounts/
│           ├── login.html
│           └── logout.html
│
├── instructors/                  # Instructor management (admin functions)
│   ├── __init__.py
│   ├── models.py                 # Instructor profile
│   ├── views.py                  # Instructor CRUD
│   ├── forms.py                  # Instructor create/edit forms
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   └── templates/
│       └── instructors/
│           ├── list.html
│           ├── create.html
│           └── detail.html
│
├── students/                     # Student management (instructor functions)
│   ├── __init__.py
│   ├── models.py                 # Student, School, Class models
│   ├── views.py                  # CSV upload, student list
│   ├── forms.py                  # CSV upload form
│   ├── urls.py
│   ├── admin.py
│   ├── csv_processor.py          # pandas CSV/Excel parsing
│   ├── bulk_operations.py        # BulkStudentCreator, BulkOperationResult
│   ├── tests.py
│   └── templates/
│       └── students/
│           ├── upload_csv.html
│           ├── preview.html
│           ├── list.html
│           └── bulk_result.html
│
├── spaces/                       # ZEP space management
│   ├── __init__.py
│   ├── models.py                 # FailedSpaceCreation model
│   ├── views.py                  # Space list, public visibility settings
│   ├── zep_api.py                # ZEPAPIClient class
│   ├── space_service.py          # Space creation logic + retry
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   └── templates/
│       └── spaces/
│           ├── list.html
│           └── failed_list.html
│
├── dashboard/                    # Dashboards (admin, instructor)
│   ├── __init__.py
│   ├── views.py                  # Admin/instructor dashboards
│   ├── urls.py
│   ├── metrics.py                # Metrics calculation logic
│   ├── tests.py
│   └── templates/
│       └── dashboard/
│           ├── admin_dashboard.html
│           ├── instructor_dashboard.html
│           └── public_landing.html
│
├── core/                         # Common utilities
│   ├── __init__.py
│   ├── utils.py                  # Helper functions
│   ├── mixins.py                 # View mixins
│   └── exceptions.py             # Custom exceptions
│
├── static/                       # Static files (development)
│   ├── css/
│   │   └── tailwind.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── logo.png
│
├── staticfiles/                  # collectstatic output (production)
│
├── media/                        # Uploaded files
│   └── uploads/
│       └── csv/
│
├── templates/                    # Global templates
│   ├── base.html                 # Base layout with Tailwind
│   ├── navbar.html
│   ├── footer.html
│   └── errors/
│       ├── 404.html
│       ├── 500.html
│       └── 403.html
│
├── logs/                         # Log files (development)
│   └── django.log
│
└── scripts/                      # Utility scripts
    ├── initial_setup.sh
    └── deploy.sh
```

## Epic to Architecture Mapping

| Epic | Primary Apps | Key Models | Core Functionality | Story Coverage |
|------|--------------|------------|-------------------|----------------|
| **Epic 1: Platform Foundation & Authentication** | accounts, dashboard | User (CustomUser) | Login/logout, role-based permissions (@admin_required, @instructor_required decorators), public landing page | Stories 1.1-1.4 (4 stories) |
| **Epic 2: Bulk Student Management & ZEP Integration** | students, spaces | Student, School, Class, FailedSpaceCreation | CSV upload (pandas), bulk student creation (BulkStudentCreator), ZEP space creation (ZEPAPIClient), permission configuration, retry logic | Stories 2.1-2.7 (7 stories) |
| **Epic 3: Dashboard & Monitoring** | dashboard, instructors, spaces | (Aggregates from all models) | Admin metrics dashboard, instructor activity tracking, space management interface, public visibility toggle | Stories 3.1-3.4 (4 stories) |

**Integration Points Between Epics:**
- **accounts → instructors**: User.role='instructor' links to Instructor profile
- **instructors → students**: Instructor manages Class, Class contains Students
- **students → spaces**: Student creation triggers ZEP space creation via BulkStudentCreator
- **spaces → dashboard**: Space creation status reflected in admin dashboard metrics
- **All apps → accounts**: Permission decorators control access across all features

## Technology Stack Details

### Core Technologies

**Backend Framework:**
- Django 4.2 LTS (Long-term support until April 2026)
- Python 3.8.x (⚠️ EOL October 2024, upgrade to 3.10+ recommended before production)
- uWSGI for WSGI server (DigitalOcean deployment)

**Database:**
- MySQL 8.0 (EOL April 2026)
- mysqlclient driver (C-based, high performance)
- Database sessions for user session management

**Frontend:**
- Django Templates (server-side rendering)
- Tailwind CSS (modern utility-first CSS framework)
- Minimal JavaScript (form validation, loading states)

**Data Processing:**
- pandas (CSV/Excel parsing and validation)

**External APIs:**
- ZEP API (space creation, permission management)
  - Base URL: `ZEP_API_URL` (environment variable)
  - Authentication: Bearer token (`ZEP_API_KEY`)
  - Timeout: 10 seconds per request
  - Retry: 3 attempts with exponential backoff (1s, 2s, 4s)

**Deployment Stack:**
- DigitalOcean Droplet (user-managed VPS)
- Nginx (reverse proxy + static file serving)
- uWSGI (WSGI application server)
- systemd (process management)

### Integration Points

**1. CSV Upload → Student Creation Flow:**
```
Instructor uploads CSV
    ↓
pandas parses and validates file
    ↓
BulkStudentCreator.execute()
    ↓
Phase 1: Create student accounts (atomic transaction)
Phase 2: Create ZEP spaces (sequential with retry)
Phase 3: Set permissions (student=owner, instructor+admins=staff)
    ↓
BulkOperationResult (successful, failed, errors)
    ↓
Display results to instructor
```

**2. Authentication → Authorization Flow:**
```
User logs in (ID/PW)
    ↓
Django auth validates credentials
    ↓
Session created (database-backed)
    ↓
View checks @admin_required or @instructor_required
    ↓
User.role determines access
```

**3. Dashboard Metrics Flow:**
```
Admin accesses dashboard
    ↓
dashboard/metrics.py aggregates:
  - Total schools (School.objects.count())
  - Total instructors (User.objects.filter(role='instructor').count())
  - Total students (Student.objects.count())
  - Active spaces (Student.objects.exclude(zep_space_url='').count())
  - Failed creations (FailedSpaceCreation.objects.filter(retry_status='pending').count())
    ↓
Rendered in admin_dashboard.html
```

**4. ZEP API Communication:**
```
students/bulk_operations.py
    ↓
spaces/zep_api.py (ZEPAPIClient)
    ↓
HTTP POST to ZEP_API_URL/spaces
    ↓
Response: {space_url, space_id}
    ↓
Save to Student.zep_space_url
```

## Novel Pattern: Bulk Operation with Partial Success

**Pattern Name:** Bulk Operation with Partial Success Pattern

**Purpose:** Handle large-scale operations where partial failures are acceptable and must be tracked without rolling back successful operations.

**Problem Solved:** When creating 100 student accounts and ZEP spaces, if 5 fail due to API timeouts, the 95 successful creations should be preserved and the 5 failures tracked for manual review.

**Components:**

**1. BulkOperationResult (Data Class)**
```python
# students/bulk_operations.py

class BulkOperationResult:
    """Tracks results of bulk operations"""
    def __init__(self):
        self.successful = []      # List of successful Student objects
        self.failed = []          # List of failed Student objects
        self.total = 0            # Total attempted
        self.errors = {}          # {student_id: error_message}

    @property
    def success_rate(self):
        return len(self.successful) / self.total if self.total > 0 else 0
```

**2. BulkStudentCreator (Orchestrator)**
```python
class BulkStudentCreator:
    """Orchestrates multi-phase bulk student creation workflow"""

    def __init__(self, instructor, csv_data):
        self.instructor = instructor
        self.csv_data = csv_data
        self.result = BulkOperationResult()

    def execute(self):
        """Execute complete workflow: accounts → spaces → permissions"""
        self.result.total = len(self.csv_data)

        # Phase 1: Atomic student account creation
        students = self._create_student_accounts()

        # Phase 2: Sequential ZEP space creation with individual retry
        for student in students:
            try:
                space_url = self._create_zep_space_with_retry(student)
                student.zep_space_url = space_url
                student.save()

                # Phase 3: Permission configuration
                self._set_space_permissions(student, space_url)

                self.result.successful.append(student)
            except Exception as e:
                self.result.failed.append(student)
                self.result.errors[student.id] = str(e)
                logger.error(f"Failed to create space for {student.name}: {e}")

        return self.result
```

**3. Retry Logic**
```python
def _create_zep_space_with_retry(self, student, max_retries=3):
    """Create ZEP space with exponential backoff retry"""
    for attempt in range(1, max_retries + 1):
        try:
            space_name = f"{student.name}_portfolio_2025"
            result = zep_api.create_space(space_name)
            return result['space_url']
        except Exception as e:
            if attempt == max_retries:
                # Final failure - record for admin review
                FailedSpaceCreation.objects.create(
                    student=student,
                    error_message=str(e),
                    attempt_count=max_retries
                )
                raise
            time.sleep(2 ** (attempt - 1))  # 1s, 2s, 4s
```

**Usage in Views:**
```python
# students/views.py

@instructor_required
def bulk_create_students(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        csv_data = parse_csv(csv_file)

        creator = BulkStudentCreator(
            instructor=request.user.instructor_profile,
            csv_data=csv_data
        )
        result = creator.execute()

        # Display partial success message
        messages.success(
            request,
            f"✅ {len(result.successful)}명 성공 / "
            f"❌ {len(result.failed)}명 실패 "
            f"(성공률: {result.success_rate * 100:.1f}%)"
        )

        if result.failed:
            return render(request, 'students/bulk_result.html', {
                'result': result
            })

        return redirect('students:list')
```

**Affects Stories:**
- Story 2.5: Automated Student Account Creation
- Story 2.6: Automated ZEP Space Creation and Linking
- Story 2.7: Automated Permission Configuration

**Why This Pattern Matters:**
- Without this pattern, each AI agent might implement bulk operations differently (all-or-nothing transactions vs. partial success tracking)
- This pattern ensures consistent behavior: preserve successes, track failures, provide clear user feedback
- Aligns with PRD requirement: "Failed space creations are queued for manual review by administrator"

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### Naming Conventions

**Database (MySQL):**
- Table names: Lowercase singular + app prefix (e.g., `students_student`, `students_school`)
- Column names: `snake_case` (e.g., `student_id`, `generated_email`, `zep_space_url`)
- Foreign keys: `{model}_id` (e.g., `instructor_id`, `class_id`)
- Boolean fields: `is_` prefix or status name (e.g., `is_active`, `training_completed`)

**Python Code:**
- Class names: `PascalCase` (e.g., `Student`, `BulkOperationResult`, `ZEPAPIClient`)
- Functions/methods: `snake_case` (e.g., `create_student`, `bulk_create_students`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES = 3`, `ZEP_API_TIMEOUT = 10`)
- Private methods: `_leading_underscore` (e.g., `_create_zep_space_with_retry`)

**URL Patterns:**
- Format: `kebab-case` (e.g., `/students/upload-csv/`, `/dashboard/admin/`)
- URL names: `app_namespace:action` (e.g., `students:upload_csv`, `dashboard:admin`)
- Parameters: `<int:pk>` or `<slug:slug>` (e.g., `/students/<int:student_id>/`)

**Template Files:**
- File names: `snake_case.html` (e.g., `upload_csv.html`, `admin_dashboard.html`)
- Location: `{app}/templates/{app}/{filename}.html`

### Code Organization

**Import Order (All Python Files):**
```python
# 1. Standard library
import os
import time
from datetime import datetime

# 2. Third-party libraries
import pandas as pd
from django.db import models
from django.contrib.auth.decorators import login_required

# 3. Local apps
from accounts.models import User
from students.csv_processor import parse_csv
```

**Test Organization:**
- Small apps: Single `tests.py` file
- Large apps: `tests/` folder with `test_models.py`, `test_views.py`, etc.

**View Structure (Consistent Pattern):**
```python
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.decorators import instructor_required

@instructor_required
def view_name(request):
    """Docstring explaining view purpose"""
    if request.method == 'POST':
        # Handle form submission
        form = SomeForm(request.POST, request.FILES)
        if form.is_valid():
            # Process data
            messages.success(request, '성공 메시지')
            return redirect('app:success_url')
        else:
            messages.error(request, '에러 메시지')
    else:
        form = SomeForm()

    context = {'form': form}
    return render(request, 'app/template.html', context)
```

### Error Handling Strategy

**All Agents MUST Follow These Rules:**

1. **External API Calls Must Be Wrapped:**
```python
try:
    result = zep_api.create_space(space_name)
except requests.exceptions.Timeout:
    logger.error(f"ZEP API timeout: {space_name}")
    # Retry or fail gracefully
except requests.exceptions.RequestException as e:
    logger.error(f"ZEP API error: {e}")
    # Retry or fail gracefully
```

2. **User-Facing Messages (Korean, Friendly):**
```python
messages.success(request, f'{count}명의 학생이 성공적으로 생성되었습니다.')
messages.error(request, 'CSV 파일 형식이 올바르지 않습니다. 필수 컬럼: student_name, student_id, grade')
messages.warning(request, '일부 공간 생성이 실패했습니다. 관리자 확인이 필요합니다.')
```

3. **Log Messages (English, Technical):**
```python
logger.info(f"Bulk student creation started: {len(csv_data)} students")
logger.error(f"Failed to create ZEP space for student_id={student.id}: {e}")
logger.critical(f"Database connection lost: {e}")
```

4. **Partial Success Reporting:**
```python
# ALWAYS show both success and failure counts
messages.success(
    request,
    f"✅ {len(successful)}명 성공 / ❌ {len(failed)}명 실패 "
    f"(성공률: {success_rate:.1f}%)"
)
```

5. **Critical Errors Trigger Admin Notification:**
```python
if error_level == 'critical':
    # Future: Send email/Slack notification to admins
    logger.critical(f"Critical error requires immediate attention: {error}")
```

### Logging Configuration

```python
# settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/neulbom/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'students': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'spaces': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

**Usage in Code:**
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed debug information")
logger.info("Normal operation info")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical system failure")
```

## Data Architecture

### Core Data Models

**accounts/models.py:**
```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom user model with role-based access"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    affiliated_school = models.ForeignKey('students.School', null=True, blank=True, on_delete=models.SET_NULL)
    training_completed = models.BooleanField(default=False)
```

**students/models.py:**
```python
class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_email = models.EmailField()
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)

class Class(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    instructor = models.ForeignKey('accounts.User', on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    academic_year = models.IntegerField()
    semester = models.CharField(max_length=20)

class Student(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=50, unique=True)
    grade = models.IntegerField()
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    generated_email = models.EmailField(unique=True)  # {student_id}@seoul.zep.internal
    zep_space_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**spaces/models.py:**
```python
class FailedSpaceCreation(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    error_message = models.TextField()
    attempt_count = models.IntegerField(default=0)
    retry_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('retrying', 'Retrying'),
        ('success', 'Success'),
        ('failed_again', 'Failed Again'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Data Relationships

```
School (1) ──→ (N) Class
              ↓
User (Instructor) (1) ──→ (N) Class
                          ↓
                   Class (1) ──→ (N) Student
                                 ↓
                          Student (1) ──→ (0..1) ZEP Space (external)
                                 ↓
                          Student (1) ──→ (0..N) FailedSpaceCreation
```

## ZEP API Contracts

### 1. Create Space
**Endpoint:** `POST /api/v1/spaces`

**Request:**
```json
{
  "name": "홍길동_portfolio_2025",
  "template": "portfolio",
  "visibility": "private"
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "space_id": "space_abc123",
    "space_url": "https://zep.us/play/abc123",
    "created_at": "2025-11-03T14:30:00Z"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "API rate limit exceeded",
  "error_code": "RATE_LIMIT"
}
```

### 2. Set Space Permissions
**Endpoint:** `POST /api/v1/spaces/{space_id}/permissions`

**Request:**
```json
{
  "user_email": "student@seoul.zep.internal",
  "role": "owner"  // or "staff"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Permission set successfully"
}
```

## Security Architecture

### Authentication & Authorization

1. **Password Security:**
   - Django's PBKDF2 algorithm (default)
   - Minimum 8 characters, must include letters and numbers
   - Password reset via Django auth system

2. **Session Security:**
```python
SESSION_COOKIE_SECURE = True          # HTTPS only
SESSION_COOKIE_HTTPONLY = True        # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'       # CSRF protection
SESSION_COOKIE_AGE = 86400            # 24 hours
```

3. **Role-Based Access Control:**
```python
# accounts/decorators.py
@admin_required      # Only administrators
@instructor_required # Administrators + instructors
# Students have no UI access (ZEP only)
```

4. **CSRF Protection:**
   - Django CSRF middleware enabled
   - All POST forms include `{% csrf_token %}`

5. **SQL Injection Prevention:**
   - Django ORM (parameterized queries)
   - Never use raw SQL without parameterization

6. **XSS Prevention:**
   - Django template auto-escaping enabled
   - Use `|safe` filter only for trusted content

### Data Protection

1. **Personal Data (GDPR/Korean PIPA Compliance):**
   - Student names, IDs stored encrypted at rest (MySQL encryption)
   - Access logs for all personal data access
   - Data retention policy: 3 years after graduation

2. **Environment Variables:**
```bash
# .env (never commit to git)
DB_NAME=neulbom_prod
DB_USER=neulbom_user
DB_PASSWORD=<strong_password>
DB_HOST=localhost
DB_PORT=3306
ZEP_API_KEY=<api_key>
ZEP_API_URL=https://api.zep.us
SECRET_KEY=<django_secret_key>
DEBUG=False
```

3. **HTTPS Enforcement:**
```python
# settings.py (production)
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

## Performance Considerations

### Performance Requirements (from PRD)

- **NFR001:** 500 concurrent users, page load < 3 seconds
- **NFR002:** 100 students bulk upload < 30 seconds
- **NFR003:** 99% uptime

### Optimization Strategies

1. **Database Optimization:**
   - Indexes on foreign keys (Django default)
   - Indexes on `student_id`, `generated_email` (unique constraints)
   - Database connection pooling (mysqlclient default)

2. **Query Optimization:**
```python
# Use select_related for foreign keys
students = Student.objects.select_related('class_assigned', 'class_assigned__school')

# Use prefetch_related for reverse relations
classes = Class.objects.prefetch_related('students')
```

3. **Static File Optimization:**
   - Nginx serves static files directly (no Django)
   - Tailwind CSS: Purge unused CSS in production
   - Gzip compression enabled in Nginx

4. **Template Caching:**
```python
# Cache dashboard metrics for 5 minutes
from django.core.cache import cache

def get_dashboard_metrics():
    metrics = cache.get('dashboard_metrics')
    if metrics is None:
        metrics = calculate_metrics()
        cache.set('dashboard_metrics', metrics, 300)  # 5 minutes
    return metrics
```

5. **ZEP API Performance:**
   - ⚠️ **Known Issue:** Sequential processing may exceed 30s for 100 students
   - **Mitigation:** Performance test with actual ZEP API response times
   - **Future Upgrade Path:** If needed, migrate to ThreadPoolExecutor for parallel API calls

## Deployment Architecture

### Production Stack (DigitalOcean)

```
Internet
    ↓
[Nginx] (Port 80/443)
    ├─→ Static files (/static/) → /var/www/neulbom/staticfiles/
    ├─→ Media files (/media/) → /var/www/neulbom/media/
    └─→ Dynamic requests → uWSGI (Unix socket)
                            ↓
                      [Django Application]
                            ↓
                      [MySQL 8.0]
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name seoul.zep.us;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name seoul.zep.us;

    ssl_certificate /etc/letsencrypt/live/seoul.zep.us/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seoul.zep.us/privkey.pem;

    location /static/ {
        alias /var/www/neulbom/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/neulbom/media/;
        expires 7d;
    }

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/run/uwsgi/neulbom.sock;
    }
}
```

### uWSGI Configuration

```ini
# /etc/uwsgi/apps-enabled/neulbom.ini
[uwsgi]
chdir = /var/www/neulbom
module = neulbom.wsgi:application
home = /var/www/neulbom/venv

master = true
processes = 4
threads = 2
socket = /run/uwsgi/neulbom.sock
chmod-socket = 666
vacuum = true

die-on-term = true
```

### Systemd Service

```ini
# /etc/systemd/system/neulbom.service
[Unit]
Description=neulbom uWSGI application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/neulbom
Environment="PATH=/var/www/neulbom/venv/bin"
ExecStart=/var/www/neulbom/venv/bin/uwsgi --ini /etc/uwsgi/apps-enabled/neulbom.ini

[Install]
WantedBy=multi-user.target
```

## Development Environment

### Prerequisites

- Python 3.8.x
- MySQL 8.0
- Node.js 18+ (for Tailwind CSS)
- pip
- virtualenv

### Setup Commands

```bash
# 1. Create virtual environment
python3.8 -m venv venv
source venv/bin/activate

# 2. Install Python dependencies
pip install --upgrade pip
pip install django==4.2
pip install mysqlclient
pip install pandas
pip install requests

# 3. Create .env file
cp .env.example .env
# Edit .env with your database credentials and ZEP API key

# 4. Create MySQL database
mysql -u root -p
CREATE DATABASE neulbom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'neulbom_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON neulbom.* TO 'neulbom_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Install Tailwind CSS
npm install -D tailwindcss
npx tailwindcss init

# 8. Build Tailwind CSS
npx tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.css --watch

# 9. Run development server
python manage.py runserver
```

### requirements.txt

```txt
Django==4.2
mysqlclient>=2.2.0
pandas>=2.0.0
requests>=2.31.0
python-decouple>=3.8  # For .env file management
```

## Architecture Decision Records (ADRs)

### ADR-001: Use Python 3.8 Despite EOL
**Status:** Accepted (with warnings)
**Context:** User specified Python 3.8 requirement
**Decision:** Use Python 3.8 for development
**Consequences:** Security risk after October 2024 EOL. MUST upgrade to Python 3.10+ before production deployment.

### ADR-002: Sequential ZEP API Processing
**Status:** Accepted (with performance caveat)
**Context:** User rejected Celery and parallel processing
**Decision:** Use sequential synchronous API calls with retry logic
**Consequences:** May not meet NFR002 (100 students in 30 seconds). Performance testing required. ThreadPoolExecutor upgrade path documented if needed.

### ADR-003: Django Templates Over SPA
**Status:** Accepted
**Context:** PRD specifies traditional web application, rapid development timeline
**Decision:** Server-side rendering with Django Templates + Tailwind CSS
**Consequences:** Simpler architecture, faster development. Limited dynamic UI. Acceptable for admin/instructor users (not public-facing consumers).

### ADR-004: Database Sessions Over Redis
**Status:** Accepted
**Context:** No Redis/Celery infrastructure, low concurrent logins (admins + instructors)
**Decision:** Use Django database sessions
**Consequences:** Slight performance overhead vs. cache, but acceptable for user base. Easy to upgrade to cached_db later if needed.

### ADR-005: Manual DigitalOcean Deployment
**Status:** Accepted
**Context:** User preference for manual control
**Decision:** Traditional Nginx + uWSGI deployment on DigitalOcean droplet
**Consequences:** User responsible for deployment configuration, monitoring, and maintenance. Cost-efficient. Full control over infrastructure.

---

**Document Metadata:**
- Generated by: BMAD Decision Architecture Workflow v1.3.2
- Date: 2025-11-03
- For: Shang
- Project: neulbom (Level 2)
- Total Decisions: 15
- Total Epics: 3 (14 stories)
