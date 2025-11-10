# neulbom Product Requirements Document (PRD)

**Author:** Shang
**Date:** 2025-11-03
**Project Level:** 2
**Target Scale:** Medium project - 5-15 stories

---

## Goals and Background Context

### Goals

- Automate instructor operational workflows to reduce student/space management time by 50%
- Enable real-time monitoring and data-driven decision making for 13 university administrators
- Create a sustainable student portfolio ecosystem with public visibility for showcasing educational achievements

### Background Context

Seoul's Neulbom after-school education program spans 13 universities and serves approximately 2,000 elementary students. Currently, instructors manually create and manage student accounts and ZEP spaces, spending an average of 2 hours per week on administrative tasks. Administrators lack real-time visibility into program-wide activities, relying on manual reporting from individual instructors.

The platform addresses three critical needs: (1) automating bulk student registration and space creation with preset permissions, (2) providing centralized monitoring capabilities for program administrators, and (3) establishing a long-term portfolio system where student work accumulates over semesters. The system must launch by December 2025 for instructors, with official rollout in March 2026, requiring a tightly scoped MVP that delivers immediate operational value while establishing foundation for future enhancements.

---

## Requirements

### Functional Requirements

**Authentication & Authorization**
- FR001: System shall support ID/PW based authentication for all user roles (administrator, instructor, student)
- FR002: System shall enforce role-based access control with three permission levels: administrator, instructor, and student

**Instructor Management (Administrator Functions)**
- FR003: Administrators shall be able to create, view, search, and manage instructor accounts
- FR004: System shall maintain instructor profile information including affiliated school, class assignments, and training completion status
- FR005: Administrators shall be able to manually record instructor training completion status

**Bulk Student Registration (Instructor Functions)**
- FR006: Instructors shall be able to upload student rosters via CSV/Excel file format
- FR007: System shall automatically generate student accounts with system-generated email addresses upon roster upload
- FR008: System shall automatically create individual ZEP spaces for each student and link them to student accounts
- FR009: System shall automatically configure permissions (student as owner, instructor and administrator as staff) for all created spaces

**Space Management**
- FR010: System shall maintain a hierarchical data structure linking schools, classes, and student spaces
- FR011: System shall display searchable tables of all spaces (school/class/student) with associated ZEP URLs
- FR012: System shall support configuration of public visibility settings for student spaces (sections can be marked public or private)

**Public Landing Page**
- FR013: System shall provide a public landing page accessible without authentication displaying program branding, participating schools, and selectively public student space content

**Administrator Dashboard**
- FR014: System shall provide administrators with real-time metrics including total schools, instructors, students, active spaces, and visitor counts (daily/weekly/monthly)
- FR015: System shall display instructor-level operational status and activity summaries

### Non-Functional Requirements

- NFR001: System shall support 500 concurrent users with page load times under 3 seconds
- NFR002: System shall process bulk uploads of 100 students within 30 seconds
- NFR003: System shall maintain 99% uptime after production launch
- NFR004: System shall comply with Korean personal data protection regulations for elementary student data

---

## User Journeys

### Journey 1: Instructor Bulk Student Registration (Primary Use Case)

**Actor:** Instructor
**Goal:** Register 30 students for new semester and create their ZEP spaces

**Steps:**
1. Instructor logs into platform using ID/PW credentials
2. Navigates to "Student Management" section
3. Downloads CSV template with required fields (student name, grade, etc.)
4. Fills out template with student roster information offline
5. Uploads completed CSV file via upload interface
6. System validates file format and displays preview of students to be created
7. Instructor confirms creation
8. System automatically:
   - Creates 30 student accounts with generated email addresses
   - Creates 30 individual ZEP spaces
   - Links spaces to student accounts
   - Sets permissions (students as owners, instructor as staff)
9. System displays success confirmation with links to all created spaces
10. Instructor verifies space creation and shares login credentials with students

**Success Criteria:** All 30 students successfully registered with spaces created within 30 seconds, instructor spends less than 10 minutes on entire process (vs. 2+ hours manual creation)

**Alternative Paths:**
- If CSV validation fails: System displays specific errors, instructor corrects and re-uploads
- If ZEP API fails: System queues creation for retry and notifies instructor of pending status

---

## UX Design Principles

1. **Simplicity First:** Instructors should complete bulk registration in under 10 minutes with minimal training required
2. **Clarity and Transparency:** All automated processes (account creation, space generation) provide clear status feedback and confirmation
3. **Error Recovery:** System guides users through error correction with specific, actionable error messages
4. **Accessibility:** WCAG 2.1 AA compliance for all user-facing interfaces

---

## User Interface Design Goals

**Platform & Screens:**
- **Platform:** Responsive web application (desktop primary, tablet support)
- **Browser Support:** Chrome, Safari, Edge (latest versions)
- **Core Screens:**
  - Public landing page (unauthenticated)
  - Login page
  - Administrator dashboard (instructor management, system metrics)
  - Instructor dashboard (student bulk upload, space management)

**Key Interaction Patterns:**
- Table-based data display with search and filter capabilities
- File upload with drag-and-drop support
- Modal confirmations for destructive actions
- Real-time status updates during bulk operations

**Design Constraints:**
- Seoul.zep.us domain branding integration
- Bootstrap or Tailwind CSS framework for rapid development
- Must work seamlessly with ZEP embedded space iframes

---

## Epic List

**Epic 1: Platform Foundation & Authentication**
- Goal: Establish core infrastructure with user authentication and role-based access control
- Estimated Stories: 3-4 stories
- Delivers: Working authentication system, deployment infrastructure, admin/instructor/student role separation

**Epic 2: Bulk Student Management & ZEP Integration**
- Goal: Enable instructors to bulk register students with automatic ZEP space creation and permission management
- Estimated Stories: 5-7 stories
- Delivers: CSV upload, automatic account creation, ZEP API integration, space linking, permission automation

**Epic 3: Dashboard & Monitoring**
- Goal: Provide administrators with real-time visibility into program operations and instructors with space management capabilities
- Estimated Stories: 3-4 stories
- Delivers: Admin dashboard with metrics, instructor space management interface, public landing page

> **Note:** Detailed epic breakdown with full story specifications is available in [epics.md](./epics.md)

---

## Out of Scope

**Deferred to Phase 2:**
- Automated LMS (Ubion) integration for instructor training status synchronization
- Advanced analytics and learning data analysis
- Student portfolio ownership transfer workflow
- Notification system for instructors and administrators
- Student-facing UI (students interact only through ZEP spaces)

**Not Planned:**
- Mobile native applications (iOS/Android)
- Multi-language support beyond Korean/English
- Integration with platforms other than ZEP
- Real-time collaboration features within the management platform
- Automated content recommendations or AI-powered features

**Clarifications:**
- System manages accounts and spaces but does not provide learning content
- Public visibility applies only to designated student space sections, not entire spaces
- Student email addresses are system-generated for account purposes only
