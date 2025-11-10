# neulbom - Epic Breakdown

**Project:** neulbom
**Date:** 2025-11-03
**Author:** Shang
**Project Level:** 2

---

## Epic Overview

This document provides detailed story breakdown for all epics defined in [PRD.md](./PRD.md).

**Epic Summary:**
- Epic 1: Platform Foundation & Authentication (3-4 stories)
- Epic 2: Bulk Student Management & ZEP Integration (5-7 stories)
- Epic 3: Dashboard & Monitoring (3-4 stories)

**Total Estimated Stories:** 11-15 stories

---

## Epic 1: Platform Foundation & Authentication

**Epic Goal:** Establish core Django infrastructure with user authentication and role-based access control, enabling secure access for administrators, instructors, and students.

**Value Delivery:** Creates deployable foundation with working authentication that all subsequent features will build upon. Establishes development workflow and initial production environment.

---

**Story 1.1: Django Project Setup and Deployment Pipeline**

As a developer,
I want a configured Django project with deployment infrastructure,
So that we have a reliable foundation for building features.

**Acceptance Criteria:**
1. Django project initialized with PostgreSQL database configured
2. Project structure includes apps for authentication, instructors, students, and spaces
3. Docker containerization configured for local development
4. CI/CD pipeline established for automated testing and deployment
5. Production environment configured on AWS/GCP with HTTPS
6. seoul.zep.us domain configured and SSL certificate installed
7. Basic health check endpoint returns 200 status

**Prerequisites:** None (foundational story)

---

**Story 1.2: User Model and Role-Based Authentication**

As a system,
I want user accounts with role differentiation (administrator, instructor, student),
So that users can authenticate with appropriate permissions.

**Acceptance Criteria:**
1. Custom User model extends Django AbstractUser with role field (admin/instructor/student)
2. ID/PW authentication implemented using Django authentication system
3. Login page created with form validation and error handling
4. Logout functionality implemented
5. Password security follows Django best practices (hashing, strength requirements)
6. Session management configured with appropriate timeout
7. User creation via Django admin works for all three roles

**Prerequisites:** Story 1.1 (requires Django project foundation)

---

**Story 1.3: Role-Based Access Control and Permissions**

As an administrator,
I want role-based access control enforced throughout the application,
So that users can only access features appropriate to their role.

**Acceptance Criteria:**
1. Permission decorators/mixins created for role-based view protection
2. Administrator role has access to instructor management and system metrics
3. Instructor role has access to student management and space management
4. Student role has access only to login (no management UI per requirements)
5. Unauthorized access attempts redirect to appropriate error page
6. Django admin access restricted to administrator role only
7. Middleware enforces authentication for all non-public routes

**Prerequisites:** Story 1.2 (requires user model and authentication)

---

**Story 1.4: Public Landing Page**

As a visitor,
I want to view a public landing page without authentication,
So that I can learn about the Neulbom program.

**Acceptance Criteria:**
1. Public landing page accessible at root URL without authentication
2. Page displays Neulbom branding and program introduction
3. Participating schools section with placeholder for school logos/list
4. Login button redirects to authentication page
5. Page is responsive (desktop and tablet)
6. Page loads in under 3 seconds
7. WCAG 2.1 AA accessibility compliance verified

**Prerequisites:** Story 1.1 (requires Django project foundation)

---
## Epic 2: Bulk Student Management & ZEP Integration

**Epic Goal:** Enable instructors to efficiently manage student accounts through bulk CSV upload with automatic ZEP space creation, linking, and permission configuration.

**Value Delivery:** Reduces instructor operational time from 2+ hours to under 10 minutes for registering a class of 30 students. Automates the entire student onboarding workflow.

---

**Story 2.1: Instructor Management (Administrator)**

As an administrator,
I want to create and manage instructor accounts,
So that instructors can access the system and manage their students.

**Acceptance Criteria:**
1. Administrator dashboard includes "Instructors" section
2. Admin can create new instructor accounts with username, password, affiliated school, and class assignment
3. Admin can view list of all instructors with search and filter capabilities
4. Admin can edit instructor profile information (school, class, training status)
5. Admin can manually mark instructor training completion status
6. Instructor list displays: name, school, class count, training status, last login
7. Form validation prevents duplicate usernames

**Prerequisites:** Story 1.3 (requires role-based access control)

---

**Story 2.2: School and Class Data Models**

As a developer,
I want hierarchical data models for schools, classes, and students,
So that the system can maintain organizational structure.

**Acceptance Criteria:**
1. School model created with fields: name, logo, address, contact info
2. Class model created with fields: name, school (FK), instructor (FK), academic year, semester
3. Student model created with fields: name, student_id, class (FK), generated_email, zep_space_url
4. Database migrations created and applied successfully
5. Django admin interface allows CRUD operations for schools and classes
6. Models include appropriate indexes for performance
7. Cascade delete configured appropriately (e.g., deleting class doesn't delete students)

**Prerequisites:** Story 1.2 (requires user model foundation)

---

**Story 2.3: CSV Template and Upload Interface**

As an instructor,
I want to download a CSV template and upload student rosters,
So that I can efficiently register multiple students at once.

**Acceptance Criteria:**
1. Instructor dashboard includes "Student Management" section
2. "Download Template" button generates CSV with required fields: student_name, student_id, grade, notes
3. File upload interface accepts CSV/Excel files with drag-and-drop support
4. System validates file format and displays clear error messages for invalid files
5. After validation, system displays preview table of students to be created
6. Preview shows: student name, generated email, class assignment
7. Instructor can review and confirm or cancel the upload

**Prerequisites:** Story 1.3, Story 2.2 (requires instructor access and data models)

---

**Story 2.4: ZEP API Integration Service**

As a developer,
I want a service layer for ZEP API integration,
So that the system can create spaces and manage permissions programmatically.

**Acceptance Criteria:**
1. ZEP API client service created with authentication configuration
2. Service includes methods: create_space(), set_space_permissions(), get_space_info()
3. API credentials stored securely in environment variables
4. Error handling for API failures with retry logic (3 attempts)
5. Rate limiting implemented to respect ZEP API constraints
6. Service logs all API calls for debugging and monitoring
7. Unit tests verify API service methods work correctly (mocked)

**Prerequisites:** Story 1.1 (requires Django project foundation)

---

**Story 2.5: Automated Student Account Creation**

As an instructor,
I want student accounts automatically created from my CSV upload,
So that I don't have to manually create accounts one by one.

**Acceptance Criteria:**
1. Upon confirmation, system generates fake emails in format: {student_id}@seoul.zep.internal
2. System creates User accounts with student role for each student in CSV
3. System generates secure random passwords for each student account
4. Student records created in database linked to the instructor's class
5. Bulk creation completes within 30 seconds for 100 students
6. Transaction rollback occurs if any student creation fails (atomic operation)
7. Success confirmation displays list of created accounts with credentials

**Prerequisites:** Story 2.3 (requires CSV upload interface)


---

## Epic 3: Dashboard & Monitoring

**Epic Goal:** Provide administrators with real-time visibility into program operations and enable instructors to manage spaces while offering public visibility into student achievements.

**Value Delivery:** Enables data-driven decision making for administrators, simplifies space management for instructors, and showcases program success to external stakeholders.

---

**Story 3.1: Administrator Dashboard - Core Metrics**

As an administrator,
I want to view real-time program metrics on my dashboard,
So that I can monitor program health and make informed decisions.

**Acceptance Criteria:**
1. Administrator dashboard displays key metrics: total schools, instructors, students, active spaces
2. Visitor analytics show daily, weekly, and monthly visitor counts
3. Metrics update in real-time (no manual refresh required)
4. Dashboard loads in under 3 seconds
5. Responsive design works on desktop and tablet
6. Charts/visualizations use accessible color schemes
7. Export functionality allows downloading metrics as CSV

**Prerequisites:** Story 1.3, Story 2.2 (requires admin access and data models)

---

**Story 3.2: Administrator Dashboard - Instructor Activity**

As an administrator,
I want to see instructor-level operational status,
So that I can identify which instructors need support.

**Acceptance Criteria:**
1. Dashboard includes "Instructor Activity" section
2. Table displays: instructor name, school, class count, student count, last login, spaces created
3. Search and filter by school, activity status (active/inactive)
4. Sortable columns for all metrics
5. Click on instructor row navigates to detailed instructor view
6. Inactive instructors (no login > 30 days) highlighted
7. Data refreshes every 5 minutes automatically

**Prerequisites:** Story 3.1 (builds on dashboard foundation)

---

**Story 3.3: Instructor Space Management Interface**

As an instructor,
I want to view and manage all student spaces in my classes,
So that I can monitor student progress and access their spaces.

**Acceptance Criteria:**
1. Instructor dashboard includes "My Students" section
2. Searchable table displays: student name, class, space URL, space status, last activity
3. Click on space URL opens ZEP space in new tab
4. Filter by class and search by student name
5. Bulk actions: select multiple students, perform operations (e.g., send credentials)
6. Table pagination for classes with 50+ students
7. Export student list with credentials as CSV

**Prerequisites:** Story 2.6 (requires spaces to be created)

---
