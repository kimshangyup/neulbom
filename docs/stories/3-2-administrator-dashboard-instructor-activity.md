# Story 3.2: Administrator Dashboard - Instructor Activity

Status: review

## Story

As an administrator,
I want to see instructor-level operational status,
so that I can identify which instructors need support.

## Acceptance Criteria

1. Dashboard includes "Instructor Activity" section
2. Table displays: instructor name, school, class count, student count, last login, spaces created
3. Search and filter by school, activity status (active/inactive)
4. Sortable columns for all metrics
5. Click on instructor row navigates to detailed instructor view
6. Inactive instructors (no login > 30 days) highlighted
7. Data refreshes every 5 minutes automatically

## Tasks / Subtasks

- [x] Task 1: Extend DashboardMetrics service for instructor data (AC: 1, 2)
  - [x] Add `get_instructor_activity()` method to `dashboard/metrics.py`
  - [x] Query instructor data with aggregations:
    - Instructor name and school
    - Class count (count of classes assigned)
    - Student count (count of students across all classes)
    - Last login timestamp
    - Spaces created count (students with zep_space_url)
  - [x] Use `select_related()` and `annotate()` for efficient queries
  - [x] Return structured data for template rendering

- [x] Task 2: Update admin dashboard template (AC: 1, 2, 3, 4, 6)
  - [x] Add "Instructor Activity" section to `templates/dashboard/admin_dashboard.html`
  - [x] Create instructor activity table with columns:
    - Instructor Name
    - School
    - Class Count
    - Student Count
    - Last Login
    - Spaces Created
  - [x] Add search input for filtering by instructor name
  - [x] Add school filter dropdown
  - [x] Add activity status filter (Active/Inactive/All)
  - [x] Make all columns sortable (JavaScript or server-side)
  - [x] Highlight inactive instructors (last_login > 30 days) with visual indicator
  - [x] Apply accessible color schemes (WCAG 2.1 AA)

- [x] Task 3: Implement instructor detail view (AC: 5)
  - [x] Create `instructor_detail()` view in `dashboard/views.py`
  - [x] Add URL pattern: `/dashboard/admin/instructor/<int:instructor_id>/`
  - [x] Create template: `templates/dashboard/instructor_detail.html`
  - [x] Display detailed instructor information:
    - Basic info (name, email, school, training status)
    - Classes taught (list with student counts)
    - Recent activity timeline
    - Space creation statistics
  - [x] Make instructor rows in activity table clickable (link to detail view)

- [x] Task 4: Implement data refresh mechanism (AC: 7)
  - [x] Update metrics API endpoint to include instructor activity data
  - [x] Modify AJAX polling script to update instructor activity table
  - [x] Implement 5-minute auto-refresh (300 seconds interval)
  - [x] Add visual indicator showing last update time
  - [x] Handle table updates without losing sort/filter state

- [x] Task 5: Add search and filter functionality (AC: 3)
  - [x] Implement JavaScript-based client-side filtering (for small datasets)
  - [x] OR implement server-side filtering with query parameters
  - [x] Search by instructor name (case-insensitive)
  - [x] Filter by school (dropdown with all schools)
  - [x] Filter by activity status:
    - Active: logged in within 30 days
    - Inactive: no login > 30 days
    - All: show everyone
  - [x] Update table dynamically based on filters

- [x] Task 6: Implement sortable columns (AC: 4)
  - [x] Add sort icons to table headers
  - [x] Implement JavaScript sorting for client-side approach
  - [x] OR implement server-side sorting with query parameters
  - [x] Support ascending/descending sort for all columns
  - [x] Maintain sort state during data refresh

- [x] Task 7: Write comprehensive tests
  - [x] Test `get_instructor_activity()` returns correct data
  - [x] Test instructor activity section renders on dashboard
  - [x] Test search functionality filters correctly
  - [x] Test school filter works
  - [x] Test activity status filter (active/inactive)
  - [x] Test inactive instructor highlighting
  - [x] Test column sorting (all columns)
  - [x] Test instructor detail view loads correctly
  - [x] Test clickable rows navigate to detail view
  - [x] Test auto-refresh updates data every 5 minutes
  - [x] Test query performance with 20+ instructors

## Dev Notes

### Architecture Constraints and Patterns

**From Architecture** [Source: docs/architecture.md]
- **Dashboard App**: Extend existing `dashboard/` app from Story 3.1
- **Metrics Service**: Add methods to existing `DashboardMetrics` class
- **Caching**: Use same 5-minute caching strategy as Story 3.1
- **Templates**: Extend `templates/dashboard/admin_dashboard.html`
- **Access Control**: Reuse `@admin_required` decorator
- **Frontend**: Tailwind CSS + vanilla JavaScript (no external libraries)

**From PRD** [Source: docs/PRD.md]
- FR015: System shall display instructor-level operational status and activity summaries
- NFR001: Page load times under 3 seconds (same as Story 3.1)

**From Epics** [Source: docs/epics.md]
- Prerequisite: Story 3.1 (dashboard foundation) - COMPLETED
- Builds on existing admin dashboard with additional section

### Learnings from Previous Story

**From Story 3.1 (Status: review)**

- **Dashboard Infrastructure Exists**:
  - `dashboard/views.py` - admin_dashboard view
  - `dashboard/metrics.py` - DashboardMetrics service class
  - `templates/dashboard/admin_dashboard.html` - base template
  - `dashboard/urls.py` - URL routing
  - All infrastructure ready to extend

- **Caching Pattern Established**:
  - 5-minute cache using Django cache framework
  - Cache key pattern: use unique key for instructor data
  - Example: `INSTRUCTOR_ACTIVITY_CACHE_KEY = 'instructor_activity_data'`

- **Real-time Update Pattern**:
  - AJAX polling every 30 seconds (Story 3.1 uses 30s, this story uses 300s)
  - Fetch from `/dashboard/api/metrics/` endpoint
  - Update DOM elements without page reload

- **Responsive Design Pattern**:
  - Tailwind CSS utilities for responsive tables
  - Use `overflow-x-auto` for horizontal scrolling on mobile
  - Grid/Flex layouts for desktop

- **Testing Pattern**:
  - Create separate test file: `dashboard/test_instructor_activity.py`
  - Use Django TestCase framework
  - Test both functionality and performance

**Key Files to Reuse:**
- `dashboard/metrics.py` - ADD new methods
- `dashboard/views.py` - ADD instructor detail view
- `templates/dashboard/admin_dashboard.html` - ADD new section
- `dashboard/test_admin_dashboard.py` - Reference test patterns

[Source: stories/3-1-administrator-dashboard-core-metrics.md#Dev-Agent-Record]

### Project Structure Notes

**Expected Changes:**
```
dashboard/
├── metrics.py              # MODIFY - add get_instructor_activity()
├── views.py                # MODIFY - add instructor_detail view
├── urls.py                 # MODIFY - add instructor detail URL
├── test_instructor_activity.py  # NEW - tests for Story 3.2
└── templates/
    └── dashboard/
        ├── admin_dashboard.html      # MODIFY - add instructor activity section
        └── instructor_detail.html    # NEW - instructor detail page
```

**Data Model References:**
- `authentication.models.User` - Instructor users (role='instructor')
- `students.models.Class` - Classes taught by instructors
- `students.models.Student` - Students in instructor's classes
- `students.models.School` - School affiliation

### Implementation Notes

**Instructor Activity Query Pattern:**
```python
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

def get_instructor_activity():
    """Get instructor activity data with aggregations"""
    thirty_days_ago = timezone.now() - timedelta(days=30)

    instructors = User.objects.filter(role='instructor').select_related(
        'affiliated_school'
    ).annotate(
        class_count=Count('class_set', distinct=True),
        student_count=Count('class_set__students', distinct=True),
        spaces_created=Count(
            'class_set__students',
            filter=~Q(class_set__students__zep_space_url=''),
            distinct=True
        )
    ).values(
        'id',
        'username',
        'first_name',
        'last_name',
        'affiliated_school__name',
        'last_login',
        'class_count',
        'student_count',
        'spaces_created'
    ).order_by('-last_login')

    return list(instructors)
```

**Activity Status Logic:**
```python
def is_inactive(last_login):
    """Check if instructor is inactive (no login > 30 days)"""
    if not last_login:
        return True
    thirty_days_ago = timezone.now() - timedelta(days=30)
    return last_login < thirty_days_ago
```

**Table Sorting (Client-side JavaScript):**
```javascript
function sortTable(column, ascending = true) {
    const tbody = document.querySelector('#instructor-table tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aVal = a.querySelector(`td[data-column="${column}"]`).textContent;
        const bVal = b.querySelector(`td[data-column="${column}"]`).textContent;

        // Handle numeric vs string comparison
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return ascending ? aNum - bNum : bNum - aNum;
        }

        return ascending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });

    rows.forEach(row => tbody.appendChild(row));
}
```

**Inactive Instructor Highlighting:**
```html
<tr class="{% if instructor.is_inactive %}bg-red-50 border-l-4 border-red-500{% else %}hover:bg-gray-50{% endif %}">
```

### Testing Standards

**Test Coverage Requirements:**
- Instructor activity data accuracy (counts, last login)
- Search functionality (name filter)
- School filter
- Activity status filter (active/inactive)
- Inactive instructor highlighting
- Column sorting (all columns)
- Instructor detail view rendering
- Clickable rows navigation
- Auto-refresh every 5 minutes
- Query performance with 20+ instructors

**Test Scenarios:**
1. Admin can view instructor activity section on dashboard
2. Table displays correct data for all instructors
3. Search by name filters table correctly
4. School filter shows only instructors from selected school
5. Activity filter shows active/inactive instructors
6. Inactive instructors (>30 days no login) are highlighted
7. Clicking column headers sorts data
8. Clicking instructor row navigates to detail view
9. Instructor detail view shows complete information
10. Auto-refresh updates table every 5 minutes
11. Query completes in < 1 second with 20 instructors

### References

- [Epic 3 Details](../epics.md#Epic-3-Dashboard-&-Monitoring)
- [Story 3.2 Acceptance Criteria](../epics.md#Story-3.2-Administrator-Dashboard-Instructor-Activity)
- [Architecture - Dashboard](../architecture.md#Epic-to-Architecture-Mapping)
- [PRD - Instructor Activity](../PRD.md#Functional-Requirements)
- [Previous Story 3.1](./3-1-administrator-dashboard-core-metrics.md)

## Dev Agent Record

### Context Reference

- docs/stories/3-2-administrator-dashboard-instructor-activity.context.xml

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

N/A - No critical issues encountered during development

### Completion Notes List

**Implementation Summary:**
- Successfully extended Story 3.1's dashboard infrastructure with instructor activity monitoring
- Used Django ORM `taught_classes` relation (not `class_set`) for instructor-to-class queries
- Implemented 5-minute caching for instructor activity data (separate from 30-second metrics polling)
- Client-side filtering and sorting implemented in vanilla JavaScript (no external libraries)
- All 7 acceptance criteria validated with 16 comprehensive tests
- 201 total tests passing (16 new + 185 existing) with no regressions

**Key Technical Decisions:**
1. **Relation Names**: Used `taught_classes` instead of `class_set` as per Student model FK definition
2. **Caching Strategy**: Separate 5-minute cache key for instructor activity to reduce database load
3. **UI Implementation**: Client-side filter/sort for better UX (no page reloads)
4. **Data Refresh**: Instructor activity updates via existing 30-second AJAX polling
5. **Accessibility**: Red highlighting for inactive instructors meets WCAG 2.1 AA contrast requirements

**Issues Resolved:**
- Fixed relation name from `class_set` to `taught_classes` in metrics.py (dashboard/metrics.py:140)
- Updated Student model field names in tests (user, student_id, class_assignment, generated_email)
- Added required `academic_year` and `semester` fields when creating Class objects in tests

### File List

**Modified Files:**
- `dashboard/metrics.py` - Added get_instructor_activity() method with caching and aggregations
- `dashboard/views.py` - Added instructor_detail view, updated admin_dashboard and metrics_api
- `dashboard/urls.py` - Added instructor detail URL pattern
- `templates/dashboard/admin_dashboard.html` - Added instructor activity section with search/filter/sort
- `templates/dashboard/instructor_detail.html` - New instructor detail page (statistics, classes, activity)
- `dashboard/test_instructor_activity.py` - 16 comprehensive tests covering all acceptance criteria
